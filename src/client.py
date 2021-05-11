from ecdsa import SigningKey,VerifyingKey,NIST521p
import socket
import pickle
import sys
from random import randint
from os import system


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
    return (publicKey,privateKey)

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
        
        elif(arg1 == '-s' and arg2):
            print("this will show your status and details ")
        
        elif(arg1 == '-U' and arg2):
            print('upload evidence files here')
        
        elif(arg1 == '-D' and arg2):
            print('download files here')