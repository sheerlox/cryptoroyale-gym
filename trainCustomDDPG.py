import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import tensorflow as tf
tf.compat.v1.disable_eager_execution()

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Activation, Flatten, Input, Concatenate
from tensorflow.keras.optimizers import Adam
from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess

import gym
import pickle

env = gym.make('gym_cryptoroyale:cryptoroyale-v0')

shape_player = env.observation_space['player'].shape
shape_enemies = env.observation_space['enemies'].shape
shape_loots = env.observation_space['loots'].shape
shape_zone = env.observation_space['zone'].shape

nb_actions = env.action_space.shape[-1]

# def make_model():
#     input_player = Input(shape=shape_player)
#     inp_user = Input(shape=(1,))
#     player_embedding = Dense(units=40, activation=Activation("relu"))(input_player)
#     user_embedding = Dense(units=40, activation=Activation("relu"))(inp_user)
#     combined = concat([player_embedding, user_embedding], 1)
#     output = Dense(units=1, activation=Activation("sigmoid"))(combined)
#     model = Model(inputs=[inp_movie, inp_user], outputs=output)
#     return model

# Next, we build a very simple model.
player_input = Input(shape=(1,) + shape_player, name='player_input')
enemies_input = Input(shape=(1,) + shape_enemies, name='enemies_input')
loots_input = Input(shape=(1,) + shape_loots, name='loots_input')
zone_input = Input(shape=(1,) + shape_zone, name='zone_input')
flattened_player = Flatten()(player_input)
flattened_enemies = Flatten()(enemies_input)
flattened_loots = Flatten()(loots_input)
flattened_zone = Flatten()(zone_input)
x = Concatenate()([flattened_player, flattened_enemies, flattened_loots, flattened_zone])
x = Dense(400)(x)
x = Activation('relu')(x)
x = Dense(300)(x)
x = Activation('relu')(x)
x = Dense(nb_actions)(x)
x = Activation('softsign')(x)
actor = Model(inputs=[player_input, enemies_input, loots_input, zone_input], outputs=x)
print(actor.summary())

action_input = Input(shape=(nb_actions,), name='action_input')
player_input = Input(shape=(1,) + shape_player, name='player_input')
enemies_input = Input(shape=(1,) + shape_enemies, name='enemies_input')
loots_input = Input(shape=(1,) + shape_loots, name='loots_input')
zone_input = Input(shape=(1,) + shape_zone, name='zone_input')
flattened_player = Flatten()(player_input)
flattened_enemies = Flatten()(enemies_input)
flattened_loots = Flatten()(loots_input)
flattened_zone = Flatten()(zone_input)
y = Concatenate()([action_input, flattened_player, flattened_enemies, flattened_loots, flattened_zone])
y = Dense(400)(y)
y = Activation('relu')(y)
y = Dense(300)(y)
y = Activation('relu')(y)
y = Dense(1)(y)
y = Activation('linear')(y)
critic = Model(inputs=[action_input, player_input, enemies_input, loots_input, zone_input], outputs=y)
print(critic.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=2000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(size=nb_actions, theta=0.6, mu=0, sigma=0.3)
agent = DDPGAgent(nb_actions=nb_actions, actor=actor, critic=critic, critic_action_input=action_input,
                  memory=memory, nb_steps_warmup_critic=2000, nb_steps_warmup_actor=10000,
                  random_process=random_process, gamma=.99, target_model_update=1e-3)
agent.compile(Adam(learning_rate=0.001, clipnorm=1.0), metrics=['mae'])

hist = agent.fit(env, nb_steps=1000, visualize=False, verbose=2, nb_max_episode_steps=1000) # train our agent and store training in hist
filename = '1kit_rn4_maior2_mem20k_target01_theta3_batch32_adam2'
# we save the history of learning, it can further be used to plot reward evolution
with open('_experiments/history_ddpg__redetorcs'+filename+'.pickle', 'wb') as handle:
     pickle.dump(hist.history, handle, protocol=pickle.HIGHEST_PROTOCOL)

# After training is done, we save the final weights.
agent.save_weights('h5f_files/ddpg_{}_weights.h5f'.format('1kit_rn4_maior2_mem20k_target01_theta3_batch32_adam2_action_lim_1'), overwrite=True)