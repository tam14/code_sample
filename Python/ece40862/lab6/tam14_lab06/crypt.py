import esp32
import random
import os
import ubinascii
import machine
import hmac, hashlib
import json
import struct
from ucryptolib import aes

class CryptAes:

    #-----------------------------------------------COMMON-----------------------------------------------------------#   

    def __init__(self):
        self.nodeID = machine.unique_id() + bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.iv=os.urandom(16)
        self.staticiv=b'\x05\xb8\rf\xb5\xee\xd0\xff\x7f*B:v\x9do\xf1'
        self.ivkey=b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        self.datakey=b'\x00\x10\x20\x30\x40\x50\x60\x70\x80\x90\xa0\xb0\xc0\xd0\xe0\xf0'
        self.passphrase=b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
        self.sessionID = os.urandom(8)
        
        self.encrypted_iv=bytearray()
        self.encrypted_nodeID=bytearray()
        self.encrypted_data=bytearray()
        
            #------------------------------------SPINNER #1 Needs to Use These Functions--------------------------------------#   

    def encrypt(self, sensor_data):
        
        iv_aes = aes(self.ivkey, 2, self.staticiv)
        data_aes = aes(self.datakey, 2, self.iv)
        
        self.encrypted_iv = iv_aes.encrypt(self.iv)
        self.encrypted_nodeID = data_aes.encrypt(self.nodeID)
        self.encrypted_data = data_aes.encrypt(sensor_data+bytes(8))
    
    def sign_hmac(self, sessionID):
       
        message = self.encrypted_iv + self.encrypted_nodeID + sessionID + self.encrypted_data
        given_hmac = hmac.new(self.passphrase, msg=message, digestmod=hashlib.sha224).hexdigest()
        return given_hmac
        
    def send_mqtt(self, hmac_signed):
              
        outbound = { 'iv' : self.encrypted_iv, 'nodeID' : self.encrypted_nodeID, 'data' : self.encrypted_data, 'hmac' : hmac_signed }
        return bytearray(json.dumps(outbound))
        
    def regen_iv(self):
        self.iv=os.urandom(16)

    #------------------------------------SPINNER #2 Needs to Use These Functions--------------------------------------#   
    def regen(self):
        self.iv=os.urandom(16)
        self.sessionID=os.urandom(8)

    
    def verify_hmac(self, payload):
        json_dict = json.loads(payload)
        json_hmac = json_dict['hmac']
        self.encrypted_iv = bytes(json_dict['iv'], 'utf-8')
        self.encrypted_nodeID = bytes(json_dict['nodeID'], 'utf-8')
        self.encrypted_data = bytes(json_dict['data'], 'utf-8')
        message = self.encrypted_iv + self.encrypted_nodeID + self.sessionID + self.encrypted_data
        genHmac = hmac.new(self.passphrase, msg=message, digestmod=hashlib.sha224).hexdigest()
        if json_hmac == genHmac:
            return True
        else:
            return False
        
    def decrypt(self):
      
        iv_aes = aes(self.ivkey, 2, self.staticiv)
        iv = iv_aes.decrypt(self.encrypted_iv)
        data_aes = aes(self.datakey, 2, iv)
        nodeID = data_aes.decrypt(self.encrypted_nodeID)
        data = data_aes.decrypt(self.encrypted_data)
        
        return iv, nodeID, data
