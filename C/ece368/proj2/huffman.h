#ifndef HUFFMAN_H
#define HUFFMAN_H 

#include <stdio.h>

typedef struct _Tnode {
	int node_char;
	long num_char;
	struct _Tnode *lin_next;
	struct _Tnode *next_0;
	struct _Tnode *next_1;
} Tnode;

// tree building functions
void num_of_chars(FILE *fp, long *num_array);
int get_chars_in_file(long *num_array, Tnode **tree, long *size);
void form_huff_tree(Tnode **tree);
void get_char_encodings(int *char_array, int *bits_of_char, Tnode **tree, int bits, int *idx);
char *store_file_contents(FILE *fp);
long calc_significant_bits(int num_non_zero, int *num_array, int *char_array, int *bits_of_char);

// print functions

void print_sizes(FILE *fp, int non_zero_char, long sig_bits);
void print_header (FILE *fp, Tnode **tree);
void print_char(FILE *fp, int *filled_bits, char *bit_rep);
void print_header_recurse(FILE *fp, Tnode **tree, int *filled_bits, char *bit_rep);
void print_bit_representation(FILE *fp, int *char_array, int *bits_of_char, char *file_contents, int num_chars);

// node functions
Tnode *construct_tnode(int add_char, long num_of_char);
Tnode *tpq_enqueue(Tnode **pq, int add_char, long num_of_char);
Tnode *tpq_dequeue(Tnode **pq);
void destroy_tree(Tnode *tree);
void destroy_linear_tlist(Tnode *tree);

#endif