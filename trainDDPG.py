import gym
import numpy as np
from time import sleep

from stable_baselines3 import DDPG
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback

# Use a monitor wrapper to properly report episode stats
eval_env = Monitor(gym.make('gym_cryptoroyale:cryptoroyale-v0'))

# Save a checkpoint every 1000 steps
checkpoint_callback = CheckpointCallback(save_freq=1000, save_path="./output/checkpoints/",
                                         name_prefix="ddpg_cryptoroyale_1")

# Evaluate the model periodically
# and auto-save the best model and evaluations
eval_callback = EvalCallback(eval_env, best_model_save_path="./output/models/",
                             log_path="./output/logs/", eval_freq=2000,
                             deterministic=True, render=False)

# The noise objects for DDPG
n_actions = eval_env.action_space.shape[-1]
action_noise = OrnsteinUhlenbeckActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

model = DDPG("MultiInputPolicy", eval_env, action_noise=action_noise, verbose=1)

model.learn(total_timesteps=10000, callback=[checkpoint_callback, eval_callback])
model.save("./output/models/ddpg_cryptoroyale_1")

env = model.get_env()
obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    sleep(0.1)
