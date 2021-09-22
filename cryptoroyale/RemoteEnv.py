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
from utils import show_mouse, clean_players, clean_loots, calc_distance, calc_angle, calc_size
'''
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
'''
class RemoteEnv:
    '''
    Initializing TCP connection; Initializing Chrome webkit
    '''
    def __init__(self, tcp_ip='localhost', tcp_port=5005, buffer_size=20):
        tcpconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpconnection.bind((tcp_ip, tcp_port))
        tcpconnection.listen(1)
        self.conn, self.addr = tcpconnection.accept()
        self.buffer_size = buffer_size
        # self.last_length = 10

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
    def env_reset(self):
        self.driver.get("https://cryptoroyale.one/training/")
        # self.driver.execute_script("window.stop()")
        # assert "CryptoRoyale" in self.driver.title
        try:
            button_play = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), ' Play ')]")))

            show_mouse(self.driver)

            action = webdriver.common.action_chains.ActionChains(self.driver)
            action.move_to_element_with_offset(button_play, 15, 15)
            action.pause(2).click().perform()
        finally:
            time.sleep(3)


    '''
    Execute commands
    '''
    def env_cmd(self):
        data = self.conn.recv(self.buffer_size)
        if data:
            print("received data:", data.decode('utf-8'))
            if data.decode('utf-8') == "state":
                try:
                    data=pickle.dumps([False,int(self.driver.execute_script("return Math.floor(15 * (fpsls[snake.sct] + snake.fam / fmlts[snake.sct] - 1) - 5) / 1"))])
                except:
                    data=pickle.dumps([True,0])
                self.conn.send(data)
            elif data.decode('utf-8') == "reset":
                self.env_reset()
                self.conn.send("ok".encode('utf-8'))
            elif data.decode('utf-8') == "isalive":
                if self.driver.execute_script("document.getElementById('login').style.display")=="block":
                    self.conn.send("no".encode('utf-8'))
                else:
                    self.conn.send("yes".encode('utf-8'))
            



