from brain import Brain
import random
import numpy as np
import tensorflow as tf

class MySimpleBrain(Brain):

	_globalInit = False
	teamScore = 0

    
	def _initGlobals( possibleActions, creatureStatsShape, worldViewShape ):
        #init only on first call:
		if ( MySimpleBrain._globalInit == True ):
			return
		else:
			MySimpleBrain._globalInit = True

            
		MySimpleBrain.possibleActions = possibleActions
		MySimpleBrain.creatureStatsShape = creatureStatsShape
		MySimpleBrain.worldViewShape = worldViewShape
		MySimpleBrain.sess = tf.Session()

		MySimpleBrain.state_in = tf.placeholder(shape=[1,\
			creatureStatsShape+(worldViewShape[0]*worldViewShape[1]*worldViewShape[2])],dtype=tf.float32)

		# OLD
		# MySimpleBrain.x = slim.fully_connected(MySimpleBrain.state_in, 64, activation_fn=tf.nn.relu)
		# MySimpleBrain.x = slim.fully_connected(MySimpleBrain.x, 64, activation_fn=tf.nn.relu)
		# MySimpleBrain.x = slim.fully_connected(MySimpleBrain.x, possibleActions, activation_fn=tf.nn.softmax)

		MySimpleBrain.x = tf.layers.dense(MySimpleBrain.state_in, 64, tf.nn.relu)
		MySimpleBrain.x = tf.layers.dense(MySimpleBrain.x, 64, tf.nn.relu)
		MySimpleBrain.x = tf.layers.dense(MySimpleBrain.x, possibleActions, tf.nn.softmax)

		MySimpleBrain.output = tf.reshape(MySimpleBrain.x,[-1]) #outputs of the model
		MySimpleBrain.chosen_action = tf.argmax(MySimpleBrain.output,0) #decision of NN

	    #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
	    #to compute the loss, and use it to update the network.
		MySimpleBrain.reward_holder = tf.placeholder(shape=[1],dtype=tf.float32)
		MySimpleBrain.action_holder = tf.placeholder(shape=[1],dtype=tf.int32)
		MySimpleBrain.responsible_weight = tf.slice(MySimpleBrain.output,MySimpleBrain.action_holder,[1])
		MySimpleBrain.loss = -(tf.log(MySimpleBrain.responsible_weight)*MySimpleBrain.reward_holder) #needs to be enhanced
		MySimpleBrain.optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
		MySimpleBrain.update = MySimpleBrain.optimizer.minimize(MySimpleBrain.loss)
		MySimpleBrain.e = 0.1 #Set the chance of taking a random action for exploration

		#initialization of weights
		init = tf.global_variables_initializer()
		MySimpleBrain.sess.run(init)


	def __init__( self, numberOfActions, creatureStatsShape, worldViewShape ):
	    MySimpleBrain._initGlobals( numberOfActions, creatureStatsShape, worldViewShape )

	    self.lastState = None
	    self.lastAction = None


	def getId():
	    return "MySimpleBrain"

	def birth(self, creatureStats, worldViewOfCreature, parentBrain):
		pass

	def act( self, creatureStats,worldViewOfCreature ):

		creatureStats = creatureStats.flatten()
		worldViewOfCreature = worldViewOfCreature.flatten()
		current_state = np.concatenate((creatureStats, worldViewOfCreature), axis=0).reshape(1,\
			MySimpleBrain.creatureStatsShape+(MySimpleBrain.worldViewShape[0]*MySimpleBrain.worldViewShape[1]*\
				MySimpleBrain.worldViewShape[2]))

		#if its the first action of a creature, no training at first action
		if self.lastState is None:
			self.lastState = current_state
			if np.random.rand(1) < MySimpleBrain.e:
				action = np.random.randint(MySimpleBrain.possibleActions)
			else:
				action = MySimpleBrain.sess.run(MySimpleBrain.chosen_action,feed_dict={MySimpleBrain.state_in:current_state})

			self.lastAction = action

			return action



		if np.random.rand(1) < MySimpleBrain.e:
			action = np.random.randint(MySimpleBrain.possibleActions)
		else:
			action = MySimpleBrain.sess.run(MySimpleBrain.chosen_action,feed_dict={MySimpleBrain.state_in:current_state})

        #We are evaluating the last action. Not the one we just decided.

		reward = 1 #because it is still alive after its last decision.

        #Update the network.
		feed_dict={MySimpleBrain.reward_holder:[reward],MySimpleBrain.action_holder:[self.lastAction],MySimpleBrain.state_in:self.lastState}
		MySimpleBrain.sess.run(MySimpleBrain.update, feed_dict=feed_dict)


		self.lastState = current_state
		self.lastAction = action


		return action


	def death(self, creatureStats, worldViewOfCreature, score):

		MySimpleBrain.teamScore += score
		creatureStats = creatureStats.flatten()
		worldViewOfCreature = worldViewOfCreature.flatten()
		current_state = np.concatenate((creatureStats, worldViewOfCreature), axis=0)

		#We are evaluating the last action. Not the one we just decided.

		reward = -10 #because it is dead after its last decision.

		#Update the network.
		feed_dict={MySimpleBrain.reward_holder:[reward],MySimpleBrain.action_holder:[self.lastAction],MySimpleBrain.state_in:self.lastState}
		MySimpleBrain.sess.run(MySimpleBrain.update, feed_dict=feed_dict)



	def brightness(self):
		return 0.5









