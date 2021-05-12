import pickle

#This function is used to receive messages from client
def receiveMessages(client_socket):
    try:
        message = pickle.loads(client_socket.recv(1024))
        if not len(message):
            return False
        return message
    except:
        return False


def sendMessage(server_socket,message_to_send):
    server_socket.send(pickle.dumps(message_to_send))