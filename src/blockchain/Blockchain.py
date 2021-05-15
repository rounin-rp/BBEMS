from hashlib import sha256
import pickle
from random import randint
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILENAME = BASE_DIR+'.blockchain.txt'
class Data():
    def __init__(self,metadata):
        self.TID = metadata['TID']
        self.FileName = metadata['FileName'] 
        self.FileSize = metadata['Size']
        self.Address = metadata['Hash']
    

class Block():
    def __init__(self,height=0,previous_hash='0'*64,data_object=None):
        self.Height = height
        self.PreviousHash = previous_hash
        self.Data = data_object
        self.Hash = None
        self.Nonce = 0
    
    def generateHash(self):
        temp_hash = sha256()
        while True:
            self.Nonce = randint(2**5,2**50)
            temp_hash.update(
                str(self.Height).encode()+
                str(self.PreviousHash).encode()+
                pickle.dumps(self.Data)+
                str(self.Nonce).encode()
            )
            hex_hash = temp_hash.hexdigest()
            if hex_hash[:2] == '00':
                break
        self.Hash = temp_hash.hexdigest()


class Blockchain():
    def __init__(self):
        self.mainChain = self._loadBlockchain()

    def _loadBlockchain(self):
        temp_blockchain = []
        try:
            file = open(FILENAME,'rb')
            temp_blockchain = pickle.load(file)
            file.close()
        except:
            print("file open error")
            temp_blockchain = []
        return temp_blockchain
    
    def _saveBlockchain(self):
        file = open(FILENAME,'wb')
        pickle.dump(self.mainChain,file)
        file.close()
        print("save hogi blockchain")
    
    def _getPreviousBlock(self):
        if len(self.mainChain) > 0:
            return self.mainChain[-1]
        return None
    
    def mineData(self,metadata):
        flag = True
        try:
            data_obj = Data(metadata)
            height = 0 
            prev_hash = '0'*64
            prev_block = self._getPreviousBlock()
            if(not prev_block == None):
                height = prev_block.Height + 1
                prev_hash = prev_block.Hash
            block_obj = Block(height,prev_hash,data_obj)
            block_obj.generateHash()
            self.mainChain.append(block_obj)
            self._saveBlockchain()
        except:
            flag = False
        return flag
    
    def getAddressFromTID(self,TID):
        return_address = False
        name_of_file = False
        for i in range(len(self.mainChain)):
            if self.mainChain[i].Data.TID == TID:
                return_address = self.mainChain[i].Data.Address
                name_of_file = self.mainChain[i].Data.FileName
                break
        return (return_address,name_of_file)
    




