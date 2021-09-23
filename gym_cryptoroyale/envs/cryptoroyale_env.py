import socket
import numpy as np
import time
import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pickle
class CryptoroyaleEnv(gym.Env):
    """
    Description:

    Source:

    Observation:

    Actions:
        Type: Box(3,)
        Num     Actions
        0       Mouse position x
        1       Mouse position y
        3       Boost

    Reward:

    Starting State:

    Episode Termination:

    """


    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.seed()
        self.tcpconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpconnection.connect(('localhost', 5005))

        # self.action_space = spaces.Dict({
        #     'mousepos_x': spaces.Box(low=0, high=1120, shape=(), dtype=np.uint16),
        #     'mousepos_y': spaces.Box(low=0, high=820, shape=(), dtype=np.uint16),
        #     'boost': spaces.MultiBinary(1)
        # })

        self.action_space = spaces.Box(
            low=np.array([0, 0, 0]),
            high=np.array([1120, 820, 1]),
            shape=(3,),
            dtype=np.uint16
        )

        self.observation_space = spaces.Dict({
            'player': spaces.Box(
                low=np.array([0, 0, 0, 0, 0, 0, -200, -200]),
                high=np.array([3, 2500, 1120, 820, 1120, 820, 200, 200]),
                shape=(8,)
            ),
            'enemies': spaces.Box(
                low=np.array([0, 0, 0, 0, 0, 0, -200, -200]),
                high=np.array([3, 2500, 1120, 820, 1120, 820, 200, 200]),
                shape=(8,)
            ),
            'loots': spaces.Box(
                low=np.array([0, 0, 0, 0]),
                high=np.array([3, 1120, 820, 1]),
                shape=(4,)
            ),
            'zone': spaces.Box(
                low=np.array([0, 0, 0, 0, 0, 0]),
                high=np.array([1120, 820, 10, 1120, 820, 10]),
                shape=(6,)
            ),
        })
        self.last_health = 100
        self.total_reward = 0


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, action):
        print('step')
        print(action)
        done = True

        self.tcpconnection.send("action".encode('utf-8'))
        if self.tcpconnection.recv(2048).decode('utf-8') == "awaiting_action":
            print('awaiting_action')
            self.tcpconnection.send(pickle.dumps(action))
        if self.tcpconnection.recv(2048).decode('utf-8') == "executed_action":
            print('executed_action')
            self.tcpconnection.send("state".encode('utf-8'))
            done, observation, infos = pickle.loads(self.tcpconnection.recv(2048))

        if infos:
            if not done:
                reward = infos['health'] - self.last_health
                self.last_health = infos['health']
            else:
                reward = infos['time'] / infos['place']
        else:
            reward = 0

        self.total_reward = self.total_reward + reward

        print("****State of current episode 1: ", done)
        if infos:
            print("****New Health: ", infos['health'])
        print("****Last Health: ", self.last_health)
        print("****Collected Reward: ", reward)
        print('****Total Reward: ', self.total_reward)
        return observation, reward, done, {} 


    def reset(self, hard_reset=False):
        if hard_reset:
            print("hard_reset")
            self.tcpconnection.send("hard_reset".encode('utf-8'))
        else:
            print("soft_reset")
            self.tcpconnection.send("soft_reset".encode('utf-8'))

        if self.tcpconnection.recv(2048).decode('utf-8') == "ok":
            self.last_health = 100
            self.total_reward = 0
            self.tcpconnection.send("state".encode('utf-8'))
            done, observation, _ = pickle.loads(self.tcpconnection.recv(4096))

            print("****State of current episode 2: ", done)
            print("****Observation: ")
            print(observation)

            return observation


    def render(self, mode='human'):
         print('render')


    def close(self):
         print('close')
