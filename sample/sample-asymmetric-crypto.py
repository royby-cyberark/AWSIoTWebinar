This sample code simulates Encryption and Decryption and as such should not be used in production systems as-is

############### Sample Code for asymmetric cryptography ###############

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

#### Create the New device cert and pvt key, then encrypt them, upload to S3, generate pre-signed url for your device to download them #### 

def Encrypt(filename):         
    data = ''
    # Open and Read the Rotating cert or/and key 
    with open(filename, 'rb') as f:
        data = f.read()
    with open(filename, 'wb') as out_file:
        # Use the current device Public key to Encrypt the cert and key
        recipient_key = RSA.import_key(open('certs/public.key').read()) ### Use current device Public key to Encrypt
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

Encrypt("certs/new_device.crt")


#### Once device download the secrets, decrypt them use the current private key ####

def Descrypt(filename):
    with open(filename, 'rb') as fobj:
        # Import the private key to decrypt the cert and key
        private_key = RSA.import_key(open('certs/private.key').read())  ### Use current device Private key to Decrypt

        enc_session_key, nonce, tag, ciphertext = [ fobj.read(x) 
                                                    for x in (private_key.size_in_bytes(), 
                                                    16, 16, -1) ] # The session token used to encrypt file is 16 bytes

        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        # Decrypt
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        print(data)
    with open("new_device_decrypted.crt", 'wb') as wobj:
        wobj.write(data)

Descrypt("certs/new_device.crt")
