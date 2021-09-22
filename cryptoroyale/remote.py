from RemoteEnv import RemoteEnv

remote_env = RemoteEnv()

remote_env.env_reset()

while True:
    remote_env.env_cmd()
