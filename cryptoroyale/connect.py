import socket

tcpconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpconnection.connect(('localhost', 5005))