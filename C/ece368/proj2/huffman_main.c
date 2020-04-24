#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "huffman.h"

int main(int argc, char* argv[]) 
{
	// checking if there are 4 arguments after the executable call
	if (argc != 2){
		fprintf(stderr, "Not enough input arguments\n");
		return EXIT_FAILURE;
	}
	
	// initiallize array and tree
	long num_char[256] = {0};
	Tnode *tree = NULL;
	long size = 0;
	
	FILE *fp = fopen(argv[1], "r");
	if (fp == NULL) {
		fprintf(stderr, "Failed to open input file to read\n");
		return EXIT_FAILURE;
	}
	
	// create the huffman tree
	num_of_chars(fp, num_char);
	int non_zero_chars = get_chars_in_file(num_char, &tree, &size);
	Tnode *char_list = form_huff_tree(&tree);
	
	// prepare to print out encoding
	int *char_array = malloc(sizeof(*char_array) * size);
	int *bits_of_char = malloc(sizeof(*char_array) * size);
	char *contents = sort_file_contents(fp);
	fclose(fp);
	int idx = 0;
	int bits = 0;
	get_char_encodings(char_array, bits_of_char, *tree, bits, &idx);
	long sig_bits = calc_significant_bits(non_zero_chars, num_char, char_array, bits_of_char);
		
	// print out representations of the header
	FILE *fp = fopen(argv[1], "w");
	fseek(fp, 0, SEEK_SET);
	print_sizes(fp, non_zero_chars, sig_bits);
	print_header(fp, *tree);
	print_bit_representation(fp, char_array, bits_of_char, contents, num_char);
	fclose(fp);
	
	// deallocate the tree
	destroy_tree(tree);
	free(char_array);
	free(non_zero_chars);
	free(contents);
	
	return EXIT_SUCCESS;
}
