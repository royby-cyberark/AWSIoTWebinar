
# This sample code simulates Encryption and Decryption and as such should not be used in production systems as-is
# Requirements: pycrypto

############### Sample Code for asymmetric cryptography ###############

import argparse

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--target-file", action="store", required=True, dest="target_file", help="Path to the file you want to encrypt")
parser.add_argument("-p", "--public-key", action="store", required=True, dest="public_key", help="Public key to encrypt the target file with")

args = parser.parse_args()
target_file = args.target_file
public_key = args.public_key


#### Create the New device cert and pvt key, then encrypt them, upload to S3, generate pre-signed url for your device to download them #### 

def Encrypt(filename: str, public_key: str):         
    data = ''
    # Open and Read the Rotating cert or/and key 
    with open(filename, 'rb') as f:
        data = f.read()
    with open(f'enc_{filename}', 'wb') as out_file:
        # Use the current device Public key to Encrypt the cert and key
        recipient_key = RSA.import_key(open(public_key).read()) ### Use current device Public key to Encrypt
        # Random session token will be used to encrypt file
        session_key = get_random_bytes(16)
        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        out_file.write(cipher_rsa.encrypt(session_key))
        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
       
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        out_file.write(cipher_aes.nonce)
        out_file.write(tag)
        out_file.write(ciphertext)


print(f'Encrypting "{target_file}" with public key: "{public_key}"')
Encrypt(filename=target_file, public_key=public_key)
