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

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# carries out modular exponentiation
def mod_expo(A, B, n):
    result = 1
    while B > 0:
        if B & 1:
            result = (result * A) % n
        B = B >> 1
        A = (A * A) % n
    return result


def key_gen():
    # use e = 65537
    e = 65537

    # find values for p and q
    prime_generator = PrimeGenerator(bits=128)
    gcd_p = 0
    gcd_q = 0
    p = BitVector(size=0)
    q = BitVector(size=0)
    # while the generated primes don't meet the conditions, repeat the calculation
    while gcd_p != 1 and gcd_q != 1 and p == q:
        p = BitVector(intVal=prime_generator.findPrime())
        q = BitVector(intVal=prime_generator.findPrime())

        # set first two and last bit
        p[0:2] = BitVector(bitstring='11')
        p[127] = 1
        q[0:2] = BitVector(bitstring='11')
        q[127] = 1

        # check if p-1 and q-1 are co-prime to e
        gcd_p = gcd(p.int_val() - 1, e)
        gcd_q = gcd(q.int_val() - 1, e)

    return p.int_val(), q.int_val()


def encrypt(message_file, encrypted_file, p, q):
    # use e = 65537
    e = 65537

    # compute n
    n = p * q

    # pull out blocks, encrypt, and write to output
    file_size = os.stat(message_file).st_size
    block_num = (file_size + 31) // 32
    message_fp = BitVector(filename=message_file)
    encrypted_fp = open(encrypted_file, 'w')
    for i in range(block_num):
        block_bv = message_fp.read_bits_from_file(128)
        if block_bv.length() < 256:
            block_bv.pad_from_left(256-block_bv.length())

        encrypted_val = mod_expo(block_bv.int_val(), e, n)
        encrypted_bv = BitVector(intVal=encrypted_val, size=256)
        encrypted_fp.write(encrypted_bv.get_bitvector_in_hex())
    message_fp.close_file_object()
    encrypted_fp.close()

    return


def decrypt(encrypted_file, decrypted_file, p, q):
    # use e = 65537
    e = 65537

    # compute totient_n, n
    totient_n = (p-1) * (q-1)
    n = p * q

    # compute d
    e_bv = BitVector(intVal=e)
    totient_bv = BitVector(intVal=totient_n)
    d_bv = e_bv.multiplicative_inverse(totient_bv)
    d = d_bv.int_val()

    # pull out blocks, decrypt, and write to output
    file_size = os.stat(encrypted_file).st_size
    block_num = (file_size + 63) // 64
    encrypted_fp = open(encrypted_file, 'r')
    decrypted_fp = open(decrypted_file, 'wb')
    for i in range(block_num):
        hex_text = encrypted_fp.read(64)
        block_bv = BitVector(hexstring=hex_text)
        decrypted_val = mod_expo(block_bv.int_val(), d, n)
        decrypted_bv = BitVector(intVal=decrypted_val, size=256)
        decrypted_bv = decrypted_bv[128:256]
        decrypted_bv.write_to_file(decrypted_fp)
    encrypted_fp.close()
    decrypted_fp.close()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == '-g':
        p, q = key_gen()

        # save p and q into files
        p_fp = open(sys.argv[2], 'w')
        p_fp.write(str(p))
        p_fp.close()

        q_fp = open(sys.argv[3], 'w')
        q_fp.write(str(q))
        q_fp.close()
    elif len(sys.argv) == 6 and sys.argv[1] == '-e':
        # pull p and q from file
        p_fp = open(sys.argv[3], 'r')
        p = int(next(p_fp))
        p_fp.close()

        q_fp = open(sys.argv[4], 'r')
        q = int(next(q_fp))
        q_fp.close()

        # encrypt file
        encrypt(sys.argv[2], sys.argv[5], p, q)

    elif len(sys.argv) == 6 and sys.argv[1] == '-d':
        # pull p and q from file
        p_fp = open(sys.argv[3], 'r')
        p = int(next(p_fp))
        p_fp.close()

        q_fp = open(sys.argv[4], 'r')
        q = int(next(q_fp))
        q_fp.close()
        decrypt(sys.argv[2], sys.argv[5], p, q)
    else:
        print("Call syntax is incorrect")
        exit(1)
