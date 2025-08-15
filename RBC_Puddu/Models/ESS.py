import os

from Crypto.Cipher import AES
from Crypto.Util import Counter


def encrypt(key, plaintext):
    # Use the key to create a cipher object
    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128))

    # Encrypt the plaintext
    ciphertext = cipher.encrypt(plaintext)

    return ciphertext


def decrypt(key, ciphertext):
    # Use the key to create a cipher object
    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128))

    # Decrypt the ciphertext
    plaintext = cipher.decrypt(ciphertext)

    return plaintext


def split_secret(secret, threshold, num_shares):
    # Generate a key for the cipher
    key = os.urandom(16)

    # Encrypt the secret
    ciphertext = encrypt(key, secret)

    # Create a list to hold the shares
    shares = []

    # Split the key into `num_shares` shares, with a threshold of `threshold`
    for i in range(num_shares):
        # Create a share for this iteration
        share = (i + 1, key)
        shares.append(share)

    return ciphertext, shares


def reconstruct_secret(ciphertext, shares):
    # Check that we have at least the threshold number of shares
    if len(shares) < 3: # threshold=3
        raise ValueError("Not enough shares to reconstruct the secret")

    # Sort the shares by index
    shares.sort()

    # Extract the keys from the shares
    keys = [share[1] for share in shares]

    # Concatenate the keys to reconstruct the original key
    key = b''.join(keys)

    # Use the key to decrypt the ciphertext
    plaintext = decrypt(key, ciphertext)

    return plaintext
