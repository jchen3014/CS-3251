import socket
import threading
import sys 
import argparse

username = ''
passcode = ''

def receive_messages(conn):
	try:
		while True:
			message = conn.recv(1024).decode()
			sys.stdout.write(message + '\n')
			sys.stdout.flush()
	except:
	    return

def send_messages(conn):
	try:
		while True:
			message = input()
			conn.send(message.encode())
			if message == ':Exit':
				conn.close()
				break
	except:
		return

def start_client(host, port):
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((host, port))
        
	while True:
		authMessage = conn.recv(1024).decode()
		if authMessage == "Send username":
			conn.send(username.encode())
		elif authMessage == "Send passcode":
			conn.send(passcode.encode())
		elif authMessage == f"Connected to 127.0.0.1 on port {port}":
			sys.stdout.write(authMessage + '\n')
			sys.stdout.flush()
			break
		elif authMessage == "Incorrect passcode":
			sys.stdout.write(authMessage + '\n')
			sys.stdout.flush()
			conn.close()
			return
		
	receive_thread = threading.Thread(target=receive_messages, args=(conn,))
	receive_thread.start()

	send_thread = threading.Thread(target=send_messages, args=(conn,))
	send_thread.start()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog = 'Chat Client',
		description = 'Client for Chat Program',
		epilog = '')
	
	parser.add_argument('-join',action='store_true', required=True)
	parser.add_argument('-port',action='store',dest='port',required=True,type=int)
	parser.add_argument('-host',action='store',dest='host',required=True)
	parser.add_argument('-username',action='store',dest='username',required=True)
	parser.add_argument('-passcode',action='store',dest='passcode',required=True)
	
	inputVars = parser.parse_args()    
	username = inputVars.username
	passcode = inputVars.passcode
    
	start_client(inputVars.host, inputVars.port)
