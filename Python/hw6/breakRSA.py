'''
Homework Number: 6
Name: Michael Tam
ECN Login: tam14
Due Date: 3/3/20
'''

#!/usr/bin/env python3

from BitVector import *
from PrimeGenerator import *
import os
import sys
import rsa
from Factorize import *


def encrypt(m_file, e1_file, e2_file, e3_file, pubkey_file):
    # use standard e
    e = 65337

    # get p, q values
    p1, q1 = rsa.key_gen()
    p2, q2 = rsa.key_gen()
    p3, q3 = rsa.key_gen()

    # encrypt the files
    rsa.encrypt(message_file=m_file, encrypted_file=e1_file, p=p1, q=q1)
    rsa.encrypt(message_file=m_file, encrypted_file=e2_file, p=p2, q=q2)
    rsa.encrypt(message_file=m_file, encrypted_file=e3_file, p=p3, q=q3)

    pb_fp = open(pubkey_file, 'w')
    pb_fp.write(str(p1*q1) + '\n' + str(p2*q2) + '\n' + str(p3*q3))
    return

def crack(e1_file, e2_file, e3_file, pubkey_file, cracked_file):
    # get keys from file
    pb_fp = open(pubkey_file, 'r')
    n = [int(next(pb_fp)) for i in range(3)]

    key_factors = []
    for key in n:
        print(factorize(key))
        key_factors.append(factorize(key))

    set_0_1 = set(key_factors[0]) & set(key_factors[1])
    set_1_2 = set(key_factors[1]) & set(key_factors[2])
    set_2_0 = set(key_factors[2]) & set(key_factors[0])

    if not bool(set_0_1):
        p = set_0_1.pop()
        q = n[0] // p
        rsa.decrypt(e1_file, cracked_file, p, q)
    elif not bool(set_1_2):
        p = set_1_2.pop()
        q = n[1] // p
        rsa.decrypt(e2_file, cracked_file, p, q)
    elif not bool(set_2_0):
        p = set_2_0.pop()
        q = n[2] // p
        rsa.decrypt(e3_file, cracked_file, p, q)
    else:
        print("Can't crack files")


if __name__ == "__main__":
    if len(sys.argv) == 7 and sys.argv[1] == '-e':
        # encrypt file
        encrypt(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif len(sys.argv) == 7 and sys.argv[1] == '-c':
        #crack_file
        crack(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        print("Call syntax is incorrect")
        exit(1)
