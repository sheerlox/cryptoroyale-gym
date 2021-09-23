from time import sleep
from cryptoroyale_env import CryptoroyaleEnv
env = CryptoroyaleEnv()
obs = env.reset()
n_steps = 1000
for _ in range(n_steps):
    sleep(0.5)
    # Random action
    print(env.action_space)
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    if done:
        obs = env.reset()
