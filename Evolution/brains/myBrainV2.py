from brain import Brain
import random
import numpy as np
import tensorflow as tf
import os, sys, stat

class MyBrainV2(Brain):

	_globalInit = False
	gamma = 0.99 #discout rate of the agent
	teamScore = 0
	saved = False

	#this will discount the rewards and make responsible previous actions for their successor actions
	def discount_rewards(self,r):
	    """ take 1D float array of rewards and compute discounted reward """
	    discounted_r = np.zeros_like(r)
	    running_add = 0
	    for t in reversed(range(0, len(r))):
	        running_add = running_add * MyBrainV2.gamma + r[t]
	        discounted_r[t] = running_add
	    return list(discounted_r)


	def _initGlobals( possibleActions, creatureStatsShape, worldViewShape ):
        #init only on first call:
		if ( MyBrainV2._globalInit == True ):
			return
		else:
			MyBrainV2._globalInit = True
            
		MyBrainV2.possibleActions = possibleActions
		MyBrainV2.creatureStatsShape = creatureStatsShape
		MyBrainV2.worldViewShape = worldViewShape
		MyBrainV2.sess = tf.Session()

		#These lines established the feed-forward part of the network. The agent takes a state and produces an action.
		#row number will be the number of examples at each training batch
		MyBrainV2.state_in= tf.placeholder(shape=[None,\
			creatureStatsShape+(worldViewShape[0]*worldViewShape[1]*worldViewShape[2])],dtype=tf.float32)

		MyBrainV2.x = tf.layers.dense(MyBrainV2.state_in, 64, tf.nn.relu)
		MyBrainV2.x = tf.layers.dense(MyBrainV2.x, 64, tf.nn.relu)
		MyBrainV2.x = tf.layers.dense(MyBrainV2.x, possibleActions, tf.nn.softmax)

		MyBrainV2.chosen_action = tf.argmax(MyBrainV2.x,1)

	    #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
	    #to compute the loss, and use it to update the network.
		MyBrainV2.reward_holder = tf.placeholder(shape=[1,None],dtype=tf.float32)
		MyBrainV2.action_holder = tf.placeholder(shape=[1,None],dtype=tf.int32)
	    
		MyBrainV2.indexes = tf.range(0, tf.shape(MyBrainV2.x)[0]) * tf.shape(MyBrainV2.x)[1] + MyBrainV2.action_holder
		MyBrainV2.responsible_outputs = tf.gather(tf.reshape(MyBrainV2.x, [-1]), MyBrainV2.indexes)

		MyBrainV2.loss = -tf.reduce_mean(tf.log(MyBrainV2.responsible_outputs)*MyBrainV2.reward_holder)
	    
		MyBrainV2.optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
		MyBrainV2.update_batch = MyBrainV2.optimizer.minimize(MyBrainV2.loss)

		MyBrainV2.saver = tf.train.Saver()

		#this will going to reload paramater variables from saved model
		try:
			new_saver = tf.train.import_meta_graph('./savedmodel/my-model-1000000.meta')
			new_saver.restore(MyBrainV2.sess, tf.train.latest_checkpoint('./savedmodel/'))

		except:
			print('EXCEPT')
			#initialization of weights
			init = tf.global_variables_initializer()
			MyBrainV2.sess.run(init)

		MyBrainV2.e = 0.1 #exploration rate
		MyBrainV2.update_frequency = 20


	def __init__( self, numberOfActions, creatureStatsShape, worldViewShape ):
	    MyBrainV2._initGlobals( numberOfActions, creatureStatsShape, worldViewShape )

	    self.stateHistory = [] #this will keep the states
	    self.actionHistory = []
	    self.rewardHistory = []


	def getId():
	    return "MyBrainV2"

	def birth(self, creatureStats, worldViewOfCreature, parentBrain):
		pass


	def act( self, creatureStats,worldViewOfCreature ):

		creatureStats = creatureStats.flatten()
		worldViewOfCreature = worldViewOfCreature.flatten()
		current_state = np.concatenate((creatureStats, worldViewOfCreature), axis=0).reshape(1,\
			MyBrainV2.creatureStatsShape+(MyBrainV2.worldViewShape[0]*MyBrainV2.worldViewShape[1]*\
				MyBrainV2.worldViewShape[2]))

		#making action
		if np.random.rand(1) < MyBrainV2.e:
			action = np.random.randint(MyBrainV2.possibleActions)
		else:
			action = MyBrainV2.sess.run(MyBrainV2.chosen_action,feed_dict={MyBrainV2.state_in:current_state})

		reward = 1 #this is the reward of last action, this is + because its still alive

		#if its not the first action of the creature
		if len(self.stateHistory) != 0:

			self.rewardHistory.append(reward)
			self.rewardHistory = self.discount_rewards(self.rewardHistory)
			


		if len(self.stateHistory) == MyBrainV2.update_frequency:


			feed_dict={MyBrainV2.reward_holder : np.array(self.rewardHistory).reshape(1,-1),\
					MyBrainV2.action_holder: np.array(self.actionHistory).reshape(1,-1), MyBrainV2.state_in:np.vstack(self.stateHistory)}

			MyBrainV2.sess.run(MyBrainV2.update_batch, feed_dict=feed_dict)
			MyBrainV2.saver.save(MyBrainV2.sess, './savedmodel/my-model', global_step=1000000)
			self.change_permissions_recursive('/Users/ahmetavci/Evolution/savedmodel', 0o777)

            #clearing old actions for the sake of memory
			for i in range(int(MyBrainV2.update_frequency/2)):

				self.stateHistory.pop(i)
				self.actionHistory.pop(i)
				self.rewardHistory.pop(i)


		self.stateHistory.append(current_state)
		self.actionHistory.append(action)

		return action


	def death(self, creatureStats, worldViewOfCreature, score):

		#We are evaluating the last action. Not the one we just decided.
		MyBrainV2.teamScore += score

		reward = -100 #because it is dead after its last decision.
		self.rewardHistory.append(reward)
		self.rewardHistory = self.discount_rewards(self.rewardHistory)

		#Update the network.

		feed_dict={MyBrainV2.reward_holder : np.array(self.rewardHistory).reshape(1,-1),\
					MyBrainV2.action_holder: np.array(self.actionHistory).reshape(1,-1), MyBrainV2.state_in:np.vstack(self.stateHistory)}

		MyBrainV2.sess.run(MyBrainV2.update_batch, feed_dict=feed_dict)
		MyBrainV2.saver.save(MyBrainV2.sess, './savedmodel/my-model', global_step=1000000)
		self.change_permissions_recursive('/Users/ahmetavci/Evolution/savedmodel', 0o777)

		#to give full permission to saved model directory
		if MyBrainV2.saved == False:

			self.change_permissions_recursive('/Users/ahmetavci/Evolution', 0o777)
			MyBrainV2.saved = True


	#Necessary while working on the server.
	def change_permissions_recursive(self,path, mode):

		for root, dirs, files in os.walk(path):

			for dir in [os.path.join(root,d) for d in dirs]:
				os.chmod(dir, mode)
			for file in [os.path.join(root, f) for f in files]:
				os.chmod(file, mode)


	def brightness(self):
		return 0.5








