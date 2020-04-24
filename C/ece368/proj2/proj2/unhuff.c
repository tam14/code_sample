#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdbool.h>

// structures (tnode)
typedef struct _Tnode {
	int character;
	struct _Tnode *next_0;
	struct _Tnode *next_1;
} Tnode;

// tnode functions

Tnode *construct_tnode(int character){
	// allocates memory for a new node in the huffman tree
	Tnode *new_node = malloc(sizeof(*new_node));
	if (new_node == NULL){
		return NULL;
	}
	
	// stores the value of a char in the node (or 256 if not a leaf node)
	(*new_node).character = character;
	(*new_node).next_0 = NULL;
	(*new_node).next_1 = NULL;
	
	return new_node;
}

void destroy_tree(Tnode *tree) {
	// frees the memory in a huffman tree
	if (tree == NULL) {
		return;
	}

	if ((*tree).next_0 == NULL && (*tree).next_1 == NULL) {
		free(tree);
		return;
	} else {
		if ((*tree).next_0 != NULL) {
			destroy_tree((*tree).next_0);
			(*tree).next_0 = NULL;
		}

		if ((*tree).next_1 != NULL) {
			destroy_tree((*tree).next_1);
			(*tree).next_1 = NULL;
		}

		free(tree);
	}

	return;
}
	
Tnode *form_huff_tree_recurse(char *header, int *idx) {
//forms the huffman tree from the header. There is a mask acting as a "cursor" 
//that examines the data from the file bit by bit
	unsigned char mask = 0x80 >> (*idx % 8);
	Tnode *new_node = NULL;
	
	if ((mask & header[*idx / 8]) == mask) {
	// if "cursor" sees a 1, stores the next 8 bits as a char and makes a leaf
	// node
		*idx = *idx + 1;
		unsigned char added_byte = 0x0;

		int i = 0;
		for (; i < 8; i++) {
			mask = 0x80 >> (*idx % 8);
			added_byte = added_byte | (((mask & header[*idx / 8]) << (*idx % 8)) >> i);
			*idx = *idx + 1;
		}

		new_node = construct_tnode(added_byte);
	} else {
	// if "cursor" sees a 0, creates a trunk node and recurses this function for 
	// children of this node
		*idx = *idx + 1;
		new_node = construct_tnode(256);
		new_node->next_0 = form_huff_tree_recurse(header, idx);
		new_node->next_1 = form_huff_tree_recurse(header, idx);
	}
	
	return new_node;
}

void form_huff_tree(char *header, unsigned int header_bits, Tnode **htree) {
// mostly just initiallizes values for the recursion function above
	int total_bits = (header_bits + 7) / 8;
	int idx = 0;
	total_bits *= 8;
	*htree = form_huff_tree_recurse(header, &idx);

	return;
}

void uncompress_file(FILE *of, char *file, Tnode *huff_tree, unsigned int file_bytes, unsigned int offset) {
// decompresses a huffed file
	int i = 0;
	unsigned char mask = 0x80;
	Tnode *curr = huff_tree;
	fseek(of, 0, SEEK_SET);

	for (; i < (file_bytes * 8 - offset); i++) {
		mask = 0x80 >> (i % 8);

		if (mask & file[i / 8]) {
			curr = (*curr).next_1;
		} else {
			curr = (*curr).next_0;
		}

		if (curr->character < 256) {
			fprintf(of, "%c", (*curr).character);
			curr = huff_tree;
		}
	}

	return;
}

int main(int argc, char** argv) {
	if (argc != 2){
		fprintf(stderr, "Not enough input arguments\n");
		return EXIT_FAILURE;
	}
	
	// pull significant bits data from header
	FILE *fp = fopen(argv[1], "rb");
	if (fp == NULL) {
		fprintf(stderr, "Failed to open file correctly\n");
		return EXIT_FAILURE;
	}
	
	// pulls some header info, freads the header and file bytes into two 
	// char arrays
	fseek(fp, 0, SEEK_SET);
	volatile unsigned int header_bits = getw(fp);
	unsigned int file_bytes = getw(fp);
	unsigned int offset = (0xE0000000 & file_bytes) >> 29;
	
	file_bytes = 0x1FFFFFFF & file_bytes;	
	char *header = malloc(sizeof(*header) * ((header_bits + 7) / 8));
	char *file = malloc(sizeof(*file) * (file_bytes));
	
	
	fread(header, sizeof(*header), (header_bits + 7) / 8, fp);
	fread(file, sizeof(*file), file_bytes, fp);
	fclose(fp);
	
	// forms the huffman tree
	Tnode *h_tree = NULL;
	form_huff_tree(header, header_bits, &h_tree); 

	if (h_tree == NULL) {
		free(header);
		free(file);
		return EXIT_FAILURE;
	}
	
	FILE *of = fopen(argv[1], "wb");
	if (of == NULL) {
		free(header);
		free(file);
		destroy_tree(h_tree);
		return EXIT_FAILURE;
	}

	// print out compressed data
	uncompress_file(of, file, h_tree, file_bytes, offset);

	fclose(of);

	// frees allocated memory
	free(header);
	free(file);
	destroy_tree(h_tree);

	return EXIT_SUCCESS;
}
