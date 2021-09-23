import gym
import numpy as np
from time import sleep

from stable_baselines3 import DDPG, A2C
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
from stable_baselines3.common.env_checker import check_env

env = gym.make('gym_cryptoroyale:cryptoroyale-v0')
# check_env(env)

# The noise objects for DDPG
n_actions = env.action_space.shape[-1]
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
print(action_noise)

model = DDPG("MultiInputPolicy", env, action_noise=action_noise, verbose=1)
# model = A2C('MultiInputPolicy', env, verbose=1)
model.learn(total_timesteps=1000)
model.save("models/ddpg_cryptoroyale_1")
env = model.get_env()

del model # remove to demonstrate saving and loading

model = DDPG.load("models/ddpg_cryptoroyale_1")

obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    sleep(0.1)
