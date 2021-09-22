import gym
from baselines.ppo1 import pposgd_simple, cnn_policy

def train(num_timesteps):
    env = gym.make('gym_cryptoroyale:cryptoroyale-v0')
    def policy_fn(name, ob_space, ac_space):
        return cnn_policy.CnnPolicy(name=name, ob_space=ob_space, ac_space=ac_space)

    pposgd_simple.learn(env, policy_fn,
        max_timesteps=int(num_timesteps * 1.1),
        timesteps_per_actorbatch=256,
        clip_param=0.2, entcoeff=0.01,
        optim_epochs=4, optim_stepsize=1e-3, optim_batchsize=64,
        gamma=0.99, lam=0.95,
        schedule='linear'
    )
    env.close()

def main():
    train(num_timesteps=2500)

if __name__ == '__main__':
    main()
