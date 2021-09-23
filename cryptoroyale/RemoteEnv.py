from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import socket
import pickle
from utils import show_mouse, clean_players, clean_loots, build_observation
'''
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
'''
class RemoteEnv:
    '''
    Initializing TCP connection; Initializing Chrome webkit
    '''
    def __init__(self, tcp_ip='localhost', tcp_port=5005, buffer_size=2048):
        tcpconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpconnection.bind((tcp_ip, tcp_port))
        tcpconnection.listen(1)
        self.conn, self.addr = tcpconnection.accept()
        self.buffer_size = buffer_size
        # self.last_length = 10
        self.player_id = None
        self.first_reset = True
        self.last_know_time = None


    def init_driver(self):
        capabilities = DesiredCapabilities().CHROME
        capabilities["pageLoadStrategy"] = "none"
        options = Options()
        options.binary_location = "/usr/bin/brave-browser"
        #options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(options=options, executable_path="/usr/bin/chromedriver", desired_capabilities=capabilities)
        self.driver.maximize_window()


    '''
    Reset enviroment
    '''
    def env_reset(self, drop_session=False):
        self.player_id = None
        self.last_know_time = None

        if drop_session:
            print('hard reset')
            if hasattr(self, 'driver'):
                print('dropping session')
                self.driver.close()
            self.init_driver()
            time.sleep(15)

            self.driver.get("https://cryptoroyale.one/training/")

        if self.first_reset:
            self.first_reset = False
        else:
            try:
                try:
                    # If we get a "Maximum number of connections exceeded" error, hard reset
                    WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Maximum number of connections')]")))
                    self.env_reset(True)
                except:
                    button_play = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Play')]")))

                    show_mouse(self.driver)
                    action = webdriver.common.action_chains.ActionChains(self.driver)
                    action.move_to_element_with_offset(button_play, 15, 15)
                    action.pause(1)
                    action.click()
                    action.move_to_element_with_offset(button_play, -50, 15) # move mouse out of the button so we don't accidentally click on it when boosting
                    action.pause(1)
                    action.perform()
            except:
                # handles things like stuck on "Trying to connect to game server" etc ...
                self.env_reset(True)
            finally:
                time.sleep(2)
                user_state = self.driver.execute_script("return user_state")
                self.player_id = user_state['cloud']['pid']


    '''
    Execute commands
    '''
    def env_cmd(self):
        data = self.conn.recv(self.buffer_size)
        if data:
            step = data.decode('utf-8')
            print("executing:", step)
            if data.decode('utf-8') == "state":
                try:
                    game_state = self.driver.execute_script("return game_state")

                    players_df = clean_players(game_state['players'])
                    our_player = players_df.loc[players_df['id'] == str(self.player_id)].iloc[0]
                    players_df = players_df.drop(players_df.loc[players_df['id'] == str(self.player_id)].index)

                    infos = {
                        'time': game_state['cycle']['timer'],
                        'health': our_player['HP'],
                        'place': our_player['place'],
                    }

                    # persist game time because it isn't available once we get to post-game
                    if not game_state['cycle']['stage'] == 'post-game':
                        self.last_know_time = game_state['cycle']['timer']

                    observation = build_observation(our_player, players_df, clean_loots(game_state['loot']), game_state['gas_area'])

                    if game_state['cycle']['stage'] == 'post-game':
                        data=pickle.dumps([True, observation, { 'time': self.last_know_time, 'place': our_player['place'] }])
                    elif our_player['HP'] == 0:
                        data=pickle.dumps([True, observation, infos])
                    else:
                        data=pickle.dumps([False, observation, infos])

                except Exception as e:
                    data=pickle.dumps([True, None, None])
                    print('An error occured while calculating state:')
                    print(e.with_traceback())

                finally:
                    self.conn.send(data)

            elif data.decode('utf-8') == "action":
                self.conn.send("awaiting_action".encode('utf-8'))
                action = pickle.loads(self.conn.recv(self.buffer_size))
                self.driver.execute_script("user_state.local.mousecoords = { 'x': %f, 'y': %f }" % (action[0] * 1120 * 0.73, action[1] * 820 * 0.73))

                if (action[2] >= 0.5):
                    action = webdriver.common.action_chains.ActionChains(self.driver)
                    action.click().perform()

                self.conn.send("executed_action".encode('utf-8'))

            elif data.decode('utf-8') == "soft_reset":
                self.env_reset()
                while self.driver.execute_script("return game_state")['cycle']['stage'] == 'pre-game':
                    time.sleep(0.1)
                self.conn.send("ok".encode('utf-8'))

            elif data.decode('utf-8') == "hard_reset":
                self.env_reset(True)
                while self.driver.execute_script("return game_state")['cycle']['stage'] == 'pre-game':
                    time.sleep(0.1)
                self.conn.send("ok".encode('utf-8'))
