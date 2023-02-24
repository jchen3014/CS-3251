import socket
import threading
import sys
from datetime import datetime, timedelta
import argparse

# Define the maximum number of clients that can be connected at a time
MAX_CLIENTS = 100

# Define the maximum length of the display name and passcode
MAX_DISPLAY_NAME_LENGTH = 8
MAX_PASSCODE_LENGTH = 5

# Define the message shortcuts
SHORTCUTS = {
	":)": "[feeling happy]",
	":(": "[feeling sad]",
	":mytime": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
	":+1hr": (datetime.now()+timedelta(hours=1)).strftime("%a %b %d %H:%M:%S %Y")
}

# Define a dictionary to keep track of connected clients
clients = {}
passcode = ''

def handle_client_connection(conn, port):
	# Get the display name and passcode from the client
	conn.send("Send username".encode())
	username = conn.recv(1024).decode()[:MAX_DISPLAY_NAME_LENGTH]
	conn.send("Send passcode".encode())
	userPass = conn.recv(1024).decode()[:MAX_PASSCODE_LENGTH]

	# Check if the passcode is valid
	if (len(userPass) > 5) or (passcode != userPass):
		conn.send("Incorrect passcode".encode())
		return
	else:
		conn.send(f"Connected to 127.0.0.1 on port {port}".encode())

	# Add the client to the list of connected clients
	clients[username] = conn

	# Notify all clients that a new client has joined
	broadcast(conn, f"{username} joined the chatroom")

	# Keep the client connection open and handle incoming messages
	while True:
		message = conn.recv(1024).decode()

		# Check for shortcuts
		if message in SHORTCUTS:
			message = f"{username}: {SHORTCUTS[message]}"
		else:
			message = f"{username}: {message}"

		# If the client types :Exit, close the connection and remove the client from the list of connected clients
		if message == f"{username}: :Exit":
			message = f"{username} left the chatroom"
			broadcast(conn, message)
			
			clients.pop(username)
			conn.close()
			return


		broadcast(conn, message)
	
def broadcast(conn,message):
	sys.stdout.write(message + '\n')
	sys.stdout.flush()
	
	for user in clients.values():
		if (user != conn):
			user.send(message.encode())

def start_server(port):
	# Create a server socket and start listening for client connections
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('localhost', port))
	server.listen(MAX_CLIENTS)

	sys.stdout.write(f'Server started on port {port}. Accepting connections\n')
	sys.stdout.flush()

	# Accept incoming client connections and handle them in separate threads
	while True:
		conn, address = server.accept()
		client = threading.Thread(target=handle_client_connection, args=(conn, port))
		client.start()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog = 'Chat Server',
		description = 'Server for Chat Program',
		epilog = '')
	
	parser.add_argument('-start',action='store_true', required=True)
	parser.add_argument('-port',action='store',dest='port',required=True,type=int)
	parser.add_argument('-passcode',action='store',dest='passcode',required=True)
	
	inputVars = parser.parse_args()
	passcode = inputVars.passcode
	
	start_server(inputVars.port)
