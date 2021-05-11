from encryption import AES
from random import randint
import socket 
import select 
import pickle 
import json
import hashlib
import mysql.connector

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

#This function is used to recieve messages from client
def recieveMessages(client_socket):
    try:
        message = pickle.loads(client_socket.recv(1024))
        if not len(message):
            return False
        return message
    except:
        return False

#This function will save the AES Key seed Corresponding to the transaction ID TID into the database
def storeKeyToDatabase(TID,Key):
    value = True
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="encauth",
            password="1234",
            database="development"
        )
        mycursor = mydb.cursor()
        query = f"INSERT INTO keyman (TID,AESkey) VALUES('{TID}',{Key})"
        mycursor.execute(query)
        mydb.commit()
    except:
        value = False
    return value 

#This function will fetch the AES Key seed corresponding to the transaction ID provided from database
def getKeyFromDatabase(TID):
    value = True
    data = {}
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="encauth",
            password="1234",
            database="development"
        )
        mycursor = mydb.cursor()
        query = f"SELECT * FROM keyman WHERE TID = {TID}"
        mycursor.execute(query)
        myresult = mycursor.fetchall()
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

    while True:
        readers,_,errors = select.select(socket_list,[],socket_list)
        for notified_socket in readers:
            if notified_socket == server_socket:
                client_socket,client_addr = server_socket.accept()
                clientinfo = recieveMessages(client_socket)
                if clientinfo is False:
                    continue
                print(f"connection established with {client_socket}")
                socket_list.append(client_socket)
            else:
                message = recieveMessages(notified_socket)
                if message is False:
                    print(f"disconnected from {notified_socket}")
                    socket_list.remove(notified_socket)
                else:
                    pass 




    