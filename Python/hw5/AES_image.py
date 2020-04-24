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


def separate_header(image_file):
    image_f = open(image_file, 'rb')
    img_header = bytes()
    for n in range(3):
        img_header += image_f.readline()
    img_data = image_f.read()
    image_f.close()

    return img_header, img_data


def ctr_aes_image(iv, image_file='image.ppm', out_file='enc_image.ppm', key_file='key.txt'):
    gen_tables()

    # get the key from the file
    key_fp = BitVector(filename=key_file)
    key_bv = key_fp.read_bits_from_file(256)
    key_fp.close_file_object()

    # get information from the file
    header, img_data = separate_header(image_file)
    num_blocks = (sys.getsizeof(img_data) + 15) // 16

    # open file for writing
    out_fp = open(out_file, 'wb+')
    out_fp.write(header)

    # coding the plaintext and writing to file block by block
    for i in range(num_blocks):
        mid_bv = encrypt(iv, key_bv)
        plaintext_bv = BitVector(rawbytes=img_data[16*i:16*i+16])
        ciphertext_bv = plaintext_bv ^ mid_bv

        out_fp.write(ciphertext_bv.get_bitvector_in_ascii().encode())

        iv = BitVector(intVal=(iv.int_val()+1), size=128)

    out_fp.close()

iv = BitVector(textstring='computersecurity')

ctr_aes_image(iv, 'image.ppm', 'enb_image.ppm', 'keyCTR.txt')
