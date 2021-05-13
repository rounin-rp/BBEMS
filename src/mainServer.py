import socket
import pickle
import select

from ecdsa.keys import VerifyingKey
from database import connectDatabase,executeInsertQuery, executeSelectQuery
from ecdsa.ecdsa import Public_key, Signature
from message import receiveMessages, sendMessage
import _thread
from random import randint


def getKeyFromID(TID):
    message_to_send = ['1002',TID]
    enc_socket = socket.socket()
    enc_socket.connect(('127.0.0.1',9099))
    # sendMessage(enc_socket,True)
    sendMessage(enc_socket,message_to_send)
    message_received = receiveMessages(enc_socket)
    # message_id = message_received[0]
    # key_received = message_received[1]
    # if(message_id == '2002'):
    #     print(key_received)
    # else:
    #     print("recieved key error")
    print(message_received)
    enc_socket.close()

def saveRegistrationDataInDatabase(secret_number,public_key,grade):
    mydb = connectDatabase('localhost','encauth','1234','development')
    mycursor = mydb.cursor()
    query = f"INSERT INTO user (secret_number,public_key,grade) VALUES({secret_number},'{public_key}','{grade}')"
    executeInsertQuery(mydb,mycursor,query)
    return True

def getRegistrationDetailsFromDatabase(secret_number):
    mydb = connectDatabase('localhost','encauth','1234','development')
    mycursor = mydb.cursor()
    query = f"SELECT * FROM user WHERE  secret_number = {secret_number}"
    myresult = executeSelectQuery(mycursor,query)
    return myresult

if __name__ == '__main__':
    IP = '127.0.0.1'
    PORT = 9098
    # getKeyFromID("ABCD123456Z")
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server_socket.bind((IP,PORT))
    server_socket.listen()
    print(f"connection started at {IP} {PORT}")
    socket_list = [server_socket,]
    clients = {}
    # _thread.start_new_thread(getKeyFromID,("ABCD123456Z",))
     #Running the server live
     
    while True:
        readers,_,errors = select.select(socket_list,[],socket_list)
        for notified_socket in readers:
            if notified_socket == server_socket:
                client_socket,client_addr = server_socket.accept()
                # clientinfo = receiveMessages(client_socket)
                # if clientinfo is False:
                #     continue
                print(f"connection established with {client_socket}")
                socket_list.append(client_socket)
            else:
                message_received = receiveMessages(notified_socket)
                if message_received is False:
                    print(f"disconnected from {notified_socket}")
                    socket_list.remove(notified_socket)
                else:
                    if message_received[0] == '1111':
                        print("new registration save karna hai")
                        secret_number = message_received[1][0]
                        grade = message_received[1][1]
                        public_key = message_received[1][2]
                        print(f"secret key = {secret_number}, grade = {grade}\npublic_key={public_key}")
                        value = saveRegistrationDataInDatabase(secret_number,public_key,grade)
                        print(f"save ho gaya aur value ye hai = {value}")
                        message_to_send = ['2111',value]
                        sendMessage(notified_socket,message_to_send)
                    elif message_received[0] == '1112':
                        secret_number = message_received[1]
                        print("checking the data")
                        value = getRegistrationDetailsFromDatabase(secret_number)
                        print(value)
                        message_to_send = ['2222',value[0]]
                        sendMessage(notified_socket,message_to_send)
                    elif message_received[0] == '0001':
                        secret_number = message_received[1]
                        data = getRegistrationDetailsFromDatabase(secret_number)
                        if(data is False):
                            message_to_send = ['0002',data]
                            sendMessage(notified_socket,message_to_send)
                        else:
                            public_key = data[0][1]
                            public_key = VerifyingKey.from_pem(public_key)
                            puzzle_number = randint(1111,99999)
                            message_to_send = ['0002',puzzle_number]
                            sendMessage(notified_socket,message_to_send)
                            message_received = receiveMessages(notified_socket)
                            if(message_received[0] == '0010'):
                                signature = message_received[1]
                                if(signature is False):
                                    socket_list.remove(notified_socket)
                                    continue
                                value = public_key.verify(signature,str(puzzle_number).encode())
                                message_to_send = ['0020',value] 
                            else:
                                message_to_send = ['0020',False]

                            sendMessage(notified_socket,message_to_send)


                        

        for notified_socket in errors:
            print(f"something is wrong with {notified_socket}")
            socket_list.remove(notified_socket)
            del clients[notified_socket]
            