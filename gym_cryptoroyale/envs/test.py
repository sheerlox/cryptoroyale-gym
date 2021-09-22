from cryptoroyale_env import CryptoroyaleEnv
env = CryptoroyaleEnv()
obs = env.reset()
n_steps = 100
for _ in range(n_steps):
    # Random action
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)