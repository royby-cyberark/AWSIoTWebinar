
# This sample code simulates Encryption and Decryption and as such should not be used in production systems as-is
# Requirements: pycrypto

############### Sample Code for asymmetric cryptography ###############

import argparse

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--encrypted-file", action="store", required=True, dest="encrypted_file", help="Path to the file you want to decrypt")
parser.add_argument("-p", "--private-key", action="store", required=True, dest="private_key", help="Private key to decrypt the encrypted file with")

args = parser.parse_args()
encrypted_file = args.encrypted_file
private_key = args.private_key


#### Once device download the secrets, decrypt them use the current private key ####

def Decrypt(filename: str, private_key: str):
    with open(filename, 'rb') as fobj:
        # Import the private key to decrypt the cert and key
        private_key = RSA.import_key(open(private_key).read())  ### Use current device Private key to Decrypt

        enc_session_key, nonce, tag, ciphertext = [ fobj.read(x) 
                                                    for x in (private_key.size_in_bytes(), 
                                                    16, 16, -1) ] # The session token used to encrypt file is 16 bytes

        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        # Decrypt
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        print(data)
    with open(f'dec_{filename}', 'wb') as wobj:
        wobj.write(data)


print(f'Decrypting "{encrypted_file}" with private key: "{private_key}"')
Decrypt(filename=encrypted_file, private_key=private_key)
