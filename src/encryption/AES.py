import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode


class AESCipher(object):
    def __init__(self,key) -> None:
        super().__init__()
        self.blockSize = AES.block_size
        self.key = hashlib.sha256(str(key).encode()).digest()


    def _pad(self,plainText):
        number_of_bytes_to_pad = self.blockSize - len(plainText) % self.blockSize
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plainText = plainText + padding_str
        return padded_plainText
    
    @staticmethod
    def _unpad(plainText):
        lastChar = plainText[-1]
        bytes_to_remove = ord(lastChar)
        return plainText[:-bytes_to_remove]
    
    def encrypt(self,plaintext):
        plainText = self._pad(plaintext)
        iv = Random.new().read(self.blockSize)
        cipher = AES.new(self.key,AES.MODE_CBC, iv)
        cipherText = cipher.encrypt(plainText.encode())
        return b64encode(iv+cipherText).decode("utf-8")
    
    def decrypt(self,cipherText):
        cipherText = b64decode(cipherText)
        iv = cipherText[:self.blockSize]
        cipher = AES.new(self.key,AES.MODE_CBC,iv)
        plainText = cipher.decrypt(cipherText[self.blockSize:]).decode("utf-8")
        return self._unpad(plainText)