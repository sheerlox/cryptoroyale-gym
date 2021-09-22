from gym.envs.registration import register

register(
    id='cryptoroyale-v0',
    entry_point='gym_cryptoroyale.envs:CryptoroyaleEnv',
)