# Homework Number: 5
# Name: Michael Tam
# ECN Login: tam14
# Due Date: 02/25/2020

from BitVector import *
import sys

AES_modulus = BitVector(bitstring='100011011')
sub_bytes_table = []
inv_sub_bytes_table = []

mul_col_const = [BitVector(hexstring='02'), BitVector(hexstring='03'), BitVector(hexstring='01'),
                 BitVector(hexstring='01')]
inv_col_const = [BitVector(hexstring='0E'), BitVector(hexstring='0B'), BitVector(hexstring='0D'),
                 BitVector(hexstring='09')]


def gen_tables():
    c = BitVector(bitstring='01100011')
    d = BitVector(bitstring='00000101')
    for i in range(0, 256):
        # gen encryption sub box table
        a = BitVector(intVal=i, size=8).gf_MI(AES_modulus, 8) if i != 0 else BitVector(intVal=0)
        a1, a2, a3, a4 = [a.deep_copy() for x in range(4)]
        a ^= (a1 >> 4) ^ (a2 >> 5) ^ (a3 >> 6) ^ (a4 >> 7) ^ c
        sub_bytes_table.append(int(a))

        #gen decryption sub box table
        b = BitVector(intVal=i, size=8)
        b1, b2, b3 = [b.deep_copy() for x in range(3)]
        b = (b1 >> 2) ^ (b2 >> 5) ^ (b3 >> 7) ^ d
        check = b.gf_MI(AES_modulus, 8)
        b = check if isinstance(check, BitVector) else 0
        inv_sub_bytes_table.append(int(b))


def gee(keyword, round_constant, byte_sub_table):
    rotated_word = keyword.deep_copy()
    rotated_word << 8
    newword = BitVector(size = 0)
    for i in range(4):
        newword += BitVector(intVal=byte_sub_table[rotated_word[8*i:8*i+8].intValue()], size=8)
    newword[:8] ^= round_constant
    round_constant = round_constant.gf_multiply_modular(BitVector(intVal = 0x02), AES_modulus, 8)
    return newword, round_constant


def gen_key_schedule(key_bv, byte_sub_table):
    key_words = [None for i in range(60)]
    round_constant = BitVector(intVal=0x01, size=8)
    for i in range(8):
        key_words[i] = key_bv[i * 32: i * 32 + 32].deep_copy()
    for i in range(8, 60):
        if i % 8 == 0:
            kwd, round_constant = gee(key_words[i-1], round_constant, byte_sub_table)
            key_words[i] = key_words[i-8] ^ kwd
        elif (i - (i//8) * 8) < 4:
            key_words[i] = key_words[i-8] ^ key_words[i - 1]
        elif (i - (i//8)*8) == 4:
            key_words[i] = BitVector(size = 0)
            for j in range(4):
                key_words[i] += BitVector(intVal=byte_sub_table[key_words[i-1][8*j:8*j+8].intValue()], size = 8)
            key_words[i] ^= key_words[i-8]
        elif ((i - (i//8)*8) > 4) and ((i - (i//8)*8) < 8):
            key_words[i] = key_words[i-8] ^ key_words[i-1]
        else:
            sys.exit("error in key scheduling algo for i = %d" % i)

    key_list = []
    # combine_bv = BitVector(size=0)
    for l in range(15):
        combine_bv = key_words[4*l] + key_words[4*l+1] + key_words[4*l+2] + key_words[4*l+3]
        key_list.append(combine_bv.deep_copy())
    return key_list


def sub_bytes(state_array, s_box):
    for i in range(16):
        idx = i * 8
        state_array[idx:idx + 8] = BitVector(intVal=s_box[state_array[idx:idx + 8].int_val()], size=8)

    return state_array


def shift_rows(state_array, encrypt_bool):
    row_of_sarray = []
    shift_row_permute = []
    inverse_row_permute = []
    for i in range(128):
        row_of_sarray.append((i//8) % 4)
        shift_row_permute.append((i + 32*row_of_sarray[i]) % 128)
        inverse_row_permute.append((i - 32 * row_of_sarray[i]) % 128)

    if encrypt_bool:
        state_array = state_array.permute(shift_row_permute)
    else:
        state_array = state_array.permute(inverse_row_permute)

    return state_array


def mix_columns(state_array, const_list):
    reference_copy = state_array.deep_copy()
    new_bitvec = BitVector(size=0)
    for i in range(16):
        idx = [8*(4*(i//4) + (i+j) % 4) for j in range(4)]
        column = [reference_copy[k:k+8].deep_copy() for k in idx]
        a = column[0].gf_multiply_modular(const_list[0], AES_modulus, 8)
        for l in range(3):
            a ^= column[l+1].gf_multiply_modular(const_list[l+1], AES_modulus, 8)
        new_bitvec += a.deep_copy()
    return new_bitvec


def add_key(state_array, round_key):
    return state_array ^ round_key


def encrypt(block_bv, key_bv):
    # generate round keys
    key_rounds = gen_key_schedule(key_bv, sub_bytes_table)

    # initial round key addition
    block_bv = add_key(block_bv, key_rounds[0])

    # round processing
    for k in range(14):
        block_bv = sub_bytes(block_bv, sub_bytes_table)
        block_bv = shift_rows(block_bv, True)
        if k < 13:
            block_bv = mix_columns(block_bv, mul_col_const)
        block_bv = add_key(block_bv, key_rounds[k+1])

    return block_bv


# Arguments
#   v0 :      128-bit BitVector object containing the seed value
#   dt :      128-bit BitVector object symbolizing the date and time
#   key_file: String of file name containing the encryption key (in ASCII) for AES
#   totalNum: integer indicating the total number of desired random nums to generate
# Function Description
#   Uses the arguments with the X9.31 algorithm to generate totalNum random numbers as BitVector objects
#   Returns a list of BitVector objects, with each BitVector object representing a random number generated from X9.31
def x931(v0, dt, totalNum, key_file):
    gen_tables()

    # pull key from file
    key_fp = BitVector(filename=key_file)
    key_bv = key_fp.read_bits_from_file(256)
    key_fp.close_file_object()

    # encrypt date/time vector
    encrypted_dt = encrypt(dt, key_bv)

    # generate random numbers iteratively
    r_num_list = []
    v_j = v0
    for i in range(totalNum):
        r_j = encrypt(v_j ^ encrypted_dt, key_bv)
        v_j = encrypt(r_j ^ encrypted_dt, key_bv)
        r_num_list.append(r_j)

    return r_num_list

