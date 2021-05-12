from re import M
from encryption import AES
from random import randint
import socket 
import select 
import pickle 
import json
import hashlib
from database import connectDatabase,executeSelectQuery,executeInsertQuery
from message import receiveMessages,sendMessage

#Method to generate seed for AES KEY
def generateKey():
    key = randint(0,999999999)
    return key

#Method to generate the transaction ID used to uniquely locate a transaction
def generateTransactionID(isAuth=False):
    TID = ''
    if(isAuth):
        startLetters = "AEIOU"
        otherLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "01234567890"
        starttxt = startLetters[randint(0,4)]
        midtxt = ''
        numtxt = ''
        endtxt = otherLetters[randint(0,25)]
        while(len(midtxt) < 3):
            midtxt+=otherLetters[randint(0,25)]
        while(len(numtxt) < 6):
            numtxt+=numbers[randint(0,9)]
        TID = starttxt+midtxt+numtxt+endtxt
    else:
        startLetters = "BCDFGHJKLMNPQRSTVWXYZ"
        otherLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "01234567890"
        starttxt = startLetters[randint(0,20)]
        midtxt = ''
        numtxt = ''
        endtxt = otherLetters[randint(0,25)]
        while(len(midtxt) < 3):
            midtxt+=otherLetters[randint(0,25)]
        while(len(numtxt) < 6):
            numtxt+=numbers[randint(0,9)]
        TID = starttxt+midtxt+numtxt+endtxt
    return TID


#This function will save the AES Key seed Corresponding to the transaction ID TID into the database
def storeKeyToDatabase(TID,Key):
    value = True
    try:
        mydb = connectDatabase("localhost","encauth","1234","development")
        mycursor = mydb.cursor()
        query = f"INSERT INTO keyman (TID,AESkey) VALUES('{TID}',{Key})"
        executeInsertQuery(mydb,mycursor,query)
    except:
        value = False
    return value 

#This function will fetch the AES Key seed corresponding to the transaction ID provided from database
def getKeyFromDatabase(TID):
    value = True
    data = {}
    try:
        mydb = connectDatabase("localhost","encauth","1234","development")
        mycursor = mydb.cursor()
        query = f"SELECT * FROM keyman WHERE TID = '{TID}'"
        myresult = executeSelectQuery(mycursor,query)
        if(len(myresult) == 1):
            data['TID'] = myresult[0][0]
            data['Key'] = myresult[0][1]
        else:
            data['TID'] = data['Key'] = None
            value = False
    except:
        data['TID'] = data['Key'] = None
        value = False
    
    return (value,data)


if __name__ == '__main__':
    IP = '127.0.0.1'
    PORT = 9099
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server_socket.bind((IP,PORT))
    server_socket.listen()
    print(f"connection started at {IP} {PORT}")
    socket_list = [server_socket,]
    clients = {}

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
                    if message_received[0] == '1001':
                        authUser = message_received[1]
                        generatedKey = generateKey()
                        generatedTID = generateTransactionID(authUser)
                        message_to_send = ''
                        if(storeKeyToDatabase(generatedTID,generatedKey)):
                            message_to_send = ['2001',generatedTID,generatedKey]
                        else:
                            message_to_send = False
                        # notified_socket.send(pickle.dumps(message_to_send))
                        sendMessage(notified_socket,message_to_send)
                    elif message_received[0] == '1002':
                        print("message id 1002 received")
                        receivedTID = message_received[1]
                        print(f"received TID = {receivedTID}")
                        data_received = getKeyFromDatabase(receivedTID)
                        value,data = data_received[0],data_received[1]
                        message_to_send = ''
                        if(value):
                            message_to_send = ['2002',data]
                        else:
                            message_to_send = False
                        # notified_socket.send(pickle.dumps(message_to_send))
                        sendMessage(notified_socket,message_to_send)

        for notified_socket in errors:
            print(f"something is wrong with {notified_socket}")
            socket_list.remove(notified_socket)
            del clients[notified_socket]
                        





    