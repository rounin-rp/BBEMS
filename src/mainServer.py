import socket
import select
from ecdsa.keys import VerifyingKey
from database import connectDatabase,executeInsertQuery, executeSelectQuery
from message import receiveMessages, sendMessage
import _thread
from random import randint
from blockchain.Blockchain import Blockchain


def getKeyFromID(TID):
    message_to_send = ['1002',TID]
    enc_socket = socket.socket()
    enc_socket.connect(('127.0.0.1',9099))
    sendMessage(enc_socket,message_to_send)
    message_received = receiveMessages(enc_socket)
    print(message_received)
    enc_socket.close()

def askForNewKeyandTID(message_to_send,notified_socket):
    enc_socket = socket.socket()
    enc_socket.connect(('127.0.0.1',9099))
    sendMessage(enc_socket,message_to_send)
    message_received = receiveMessages(enc_socket)
    data = None
    if message_received[0] == '2001' and message_received[1]:
        data = message_received
    else:
        data = ['T1001',False,()]
    enc_socket.close()
    sendMessage(notified_socket,data)

def askForKeyFromTID(message_to_send):
    enc_socket = socket.socket()
    enc_socket.connect(('127.0.0.1',9099))
    sendMessage(enc_socket,message_to_send)
    message_received = receiveMessages(enc_socket)
    return message_received

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
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server_socket.bind((IP,PORT))
    server_socket.listen()
    print(f"connection started at {IP} {PORT}")
    socket_list = [server_socket,]
    authenticated = {}
    authenticated[000000] = True
     #Running the server live
     
    while True:
        readers,_,errors = select.select(socket_list,[],socket_list)
        for notified_socket in readers:
            if notified_socket == server_socket:
                client_socket,client_addr = server_socket.accept()
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
                        value = saveRegistrationDataInDatabase(secret_number,public_key,grade)
                        message_to_send = ['2111',value]
                        sendMessage(notified_socket,message_to_send)
                    elif message_received[0] == '1112':
                        secret_number = message_received[1]
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
                                authenticated[secret_number] = True
                            else:
                                message_to_send = ['0020',False]

                            sendMessage(notified_socket,message_to_send)

                    elif message_received[0] == 'T1001':
                        secret_number = message_received[1]
                        isAuth = False
                        if(secret_number):
                            isAuth = True
                        message_to_send = ['1001',isAuth]
                        if authenticated[secret_number]:
                            data = _thread.start_new_thread(askForNewKeyandTID,(message_to_send,notified_socket,))
                        else:
                            message_to_send['T1001',False,()]
                    
                    elif message_received[0] == 'M1N3':
                        metadata = message_received[1]
                        blockchain_object = Blockchain()
                        result = blockchain_object.mineData(metadata)
                        message_to_send = ['M1N3',result]
                        sendMessage(notified_socket,message_to_send)
                    
                    elif message_received[0] == 'D1D0':
                        message_from_enc = askForKeyFromTID(message_received)
                        TID = message_received[1]
                        print(f"TID dekh le bhai {TID}")
                        message_to_send = ['D1D0']
                        if message_from_enc[0] == 'D1D0' and message_from_enc[1]:
                            message_to_send.append(message_from_enc[2])
                        else:
                            message_to_send.append(False)
                        blockchain_object = Blockchain()
                        nameAndAddress = blockchain_object.getAddressFromTID(TID)
                        message_to_send.append(nameAndAddress)
                        print(message_to_send)
                        sendMessage(notified_socket,message_to_send)
                        




                        

        for notified_socket in errors:
            print(f"something is wrong with {notified_socket}")
            socket_list.remove(notified_socket)

            