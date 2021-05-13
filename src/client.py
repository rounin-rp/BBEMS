from ecdsa import SigningKey,VerifyingKey,NIST521p
import socket
from message import sendMessage,receiveMessages
import sys
from random import randint
from os import system


def sendDataToServer(message_to_send):
    server = socket.socket()
    server.connect(('127.0.0.1',9098))
    sendMessage(server,message_to_send)
    message_received = receiveMessages(server)
    server.close()
    if(message_received):
        return message_received
    else:
        return False

def checkStatus(secret_number):
    system('cls')
    print("checking your status.....")
    message_to_send = ['1112',secret_number]
    message_received = sendDataToServer(message_to_send)
    return message_received

def authenticateUser(secret_number):
    system('cls')
    returnValue = True
    print("you are required to enter the filename or full path of the filename which contains your private key")
    message_to_send = ['0001',secret_number]
    server = socket.socket()
    server.connect(('127.0.0.1',9098))
    sendMessage(server,message_to_send)
    message_received = receiveMessages(server)
    if(message_received[0] == '0002'):
        if(message_received[1] is False):
            print('no data found in corresponding to the given secret number')
            exit()
        puzzle_number = message_received[1]
        print(puzzle_number)
        privateKey = None
        filename = input('enter the filename or full path : ')
        try:
            privateKey = SigningKey.from_pem(open(filename).read())
        except:
            print('(BBEMS error: 401) File does not contain any private key information')
            sendMessage(server,['0010',False])
            server.close()
            exit()
        signature = privateKey.sign(str(puzzle_number).encode())
        message_to_send = ['0010',signature]
        sendMessage(server,message_to_send)
        message_received = receiveMessages(server)
        server.close()
        if message_received[0] == '0020' and message_received[1]:
            print('Authentication successful')
        else:
            print('authentication failed !')
            returnValue = False
    else:
        print('(BBEMS error: 0001) Failed to autenticate user')
        returnValue = False
    return returnValue

#Function for new registration
def newRegistration():
    gradeset = set(['X','Y','Z'])
    system('cls')
    print("Welcome to BBEMS New Registration!!!")
    print("Please note the following points : ")
    print("1 You are required to provide your basic information during registration")
    print("2 After successful  registration you will be provided with a secret number. You need to remember or save this secret number and make sure you dont lose it.\nYou can tell this number to anyone it really does not sabotage your account or credentials by telling this number to anyone")
    print("3 You will also be provided with a pair of public and private keys. You need to save both of them seperately. Do not lose the private key or tell anyone your private key.")
    print("Losing your private key will result in losing your account permanently. Losing your secret number will not let you to be authenticated even if you have your private key")
    print('-*-'*50)
    print("Please read the above instructions before continuing")
    print('-'*100)
    full_name = input("enter your name : ")
    while True:
        grade = input('enter your grade : ')
        if grade in gradeset:
            break
        else:
            print('invalid grade entered!!!')
    secret_number = randint(0,9999999)
    sk = SigningKey.generate(curve=NIST521p)
    vk = sk.verifying_key
    privateKey = sk.to_pem().decode()
    publicKey = vk.to_pem().decode()
    message_to_send = ['1111',(secret_number,grade,publicKey)]
    message_received = sendDataToServer(message_to_send)
    if message_received[0] == '2111':
        print("your registration has been completed successfully!\nMake sure you save the keys below to a safe environment")
        print('-*-'*100)
        print(f"your secret number(important) = {secret_number}")
        print('-*-'*100)
        print("your public key : ")
        print(publicKey)
        print('-*-'*100)
        print("your private key(important) : ")
        print(privateKey)
        print('-*-'*100)
        return (secret_number,publicKey,privateKey)
    else:
        print("(BBEMS error:) Registration falied")
        return False
if __name__ == '__main__':
    message_to_print = ''
    arg_num = len(sys.argv)
    if(arg_num < 3):
        message_to_print ="(BBEMS error:) Parameters missing \nExiting....."
        print(message_to_print)
        exit()
    elif(arg_num > 3):
        message_to_print = "(BBEMS error:) Too many parameters \nExiting....."
    else:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        if(arg1 == '-n' and arg2 == '-r'):
            keys = newRegistration()
            secret_number = keys[0]
            privateKey = keys[2]
            filename = str(secret_number)+'_PRIVATEKEY.pem'
            file = open(filename,'w')
            file.write(privateKey)
            file.close()
            print(f"your private key has been saved in {filename}")
        
        elif(arg1 == '-s' and arg2):
            print("this will show your status and details ")
            secret_number = arg2
            message_received = checkStatus(secret_number)
            if(message_received):
                print(message_received[1])
            else:
                print(f"(BBEMS error code: 404) {secret_number} not registered") 
        elif(arg1 == '-U' and arg2):
            secret_number = arg2
            success = authenticateUser(secret_number)
            if success:
                pass
            else:
                print("Authentication Failed exiting....")
                exit()

        
        elif(arg1 == '-D' and arg2):
            print('download files here')