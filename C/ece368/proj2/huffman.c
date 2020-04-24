#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdbool.h>
#include "huffman.h"

void num_of_chars(FILE *fp, long *num_array){
	fseek(fp, 0, SEEK_SET);
	int next_char = fgetc(fp);
	while (next_char != EOF){
		num_array[next_char] = num_array[next_char] + 1;
		next_char = fgetc(fp);
	}
	return;
}

int get_chars_in_file(long *num_array, Tnode **tree, long *size){	
	int non_zero_char = 0;
	for (int i = 0; i < 256; i++){
		if (num_array[i] > 0){
			*size = *size + num_array[i]
			non_zero_char++;
			Tnode *added_node = tpq_enqueue(tree, i, num_array[i]);
			if (added_node == NULL){
				fprintf(stderr, "Node could not be created, destroying linear tree\n");
				destroy_linear_tlist(*tree);
				return;
			}
		}
	}
	return non_zero_char;
}

void form_huff_tree(Tnode **tree){
	Tnode *curr_1 = *tree;
	Tnode *curr_2 = NULL;
	int weight = 0;
	while (curr != NULL){
		weight += curr->num_char;
		curr_1 = curr_1->lin_next;
	}
	while ((*tree)->num_char != weight){
		curr_1 = tpq_dequeue(tree);
		if (curr_1 == NULL){
			break;
		}
		curr_2 = tpq_dequeue(tree);
		if (curr_2 == NULL){
			break;
		}
		curr_1->lin_next = NULL;
		curr_2->lin_next = NULL;
		Tnode *combine_node = tpq_enqueue(tree, curr->node_char + curr_2->node_char + 256, curr->num_char + curr_2->num_char);
		if (combine_node == NULL){
			return;
		}
		combine_node->next_0 = curr;
		combine_node->next_1 = curr_2;
	}
	
	return;
}

void get_char_encodings(int *char_array, int *bits_of_char, Tnode **tree, int bits, int *idx) {
	if (tree->next_0 == NULL && tree->next_1 == NULL){
		char_array[*idx] = tree->node_char;
		int reverse_bit = 0;
		while (bits != 0){
			
			reverse_bit = reverse_bit * 3 + bits % 3;
			bits /= 3;
		}
		bits_of_char[*idx] = reverse_bit;
		*idx = *idx + 1;
		return;
	}else{ 
		if(tree->next_0 != NULL){
			bits = bits * 3 + 1;
			print_tree(char_array, bits_of_char, tree->next_0, bits, idx);
			bits = (bits - 1) / 3;
		}
		if(tree->next_1 != NULL){
			bits = bits * 3 + 2;
			print_tree(char_array, bits_of_char, tree->next_1, bits, idx);
		}
	}
	return;
}

char *store_file_contents(FILE *fp) {
	fseek(fp, 0, SEEK_END);
	int size = ftell(fp);
	char *file_contents = malloc(sizeof(*file_contents) * size);
	if (file_contents == NULL) {
		fprintf(stderr, "Failed to alloc memory for file contents\n"); 
		return NULL;
	}
	
	fread(file_contents, sizeof(*file_contents), size, fp);
	fclose(fp);
	
	return file_contents;
}

long calc_significant_bits(int num_non_zero, int *num_array, int *char_array, int *bits_of_char) {
	int bits = 0;
	int digits = 0;
	long sig_bits = 0;
	for (int i = 0; i < num_non_zero; i++) {
		bits = bits_of_char[i];
		while (bits != 0) {
			digits++;
			bits /= 3;
		}
		
		sig_bits += digits * num_array[(char_array[i])];
		digits = 0;		
	}
	
	return sig_bits;
}

void print_sizes(FILE *fp, int non_zero_char, long sig_bits) {	
	int header_bits = 2 * non_zero_char - 1 + non_zero_char * sizeof(char) * 8;
	fprintf(fp, "%d%ld", header_bits, sig_bits);
	
	fclose(fp);
	return;
}

void print_header (FILE *fp, Tnode **tree) {
	int filled_bits = 0;
	char bit_rep = 0;
	
	print_header_recurse(fp, tree, &filled_bits, &bit_rep);
	
	if (filled_bits > 0) {
		fprintf(fp, "%c", bit_rep);
	}
	
	return;
}

void print_char(FILE *fp, int *filled_bits, char *bit_rep) {
	if (*filled_bits == 8) {
			fprintf(fp, "%c", *bit_rep);
			*bit_rep = 0x0;
			*filled_bits = 0;
	}
	
	return;
}

void print_header_recurse(FILE *fp, Tnode **tree, int *filled_bits, char *bit_rep) {	
	if ((*tree)->node_char < 256) {
		unsigned char added_bit = 0x1 << (7 - *filled_bits);
		*bit_rep = *bit_rep | added_bit;
		*filled_bits = *filled_bits + 1;
		print_char(fp, filled_bits, bit_rep);
		
		int add_bits = 8;
		while (add_bits > 0) {			
			added_bit = (*tree)->node_char << (8 - add_bits);
			added_bit = added_bit >> *filled_bits;
			*bit_rep = *bit_rep | added_bit;
			add_bits -= 8 - *filled_bits;
			*filled_bits += 8 - *filled_bits;
			print_char(fp, filled_bits, bit_rep);
		}
	} else {
		*filled_bits = *filled_bits + 1;
		print_char(fp, filled_bits, bit_rep);
		
		print_header_recurse(fp, (*tree)->next_0, filled_bits, bit_rep);
		print_header_recurse(fp, (*tree)->next_1, filled_bits, bit_rep);
	}
	
	return;
}

void print_bit_representation(FILE *fp, int *char_array, int *bits_of_char, char *file_contents, int num_chars){
	long index = 0;
	int filled_bits = 0;
	char bit_rep = 0x0;
	unsigned char added_bit = 0x0;
	int j = 0;
	for (int i = 0; i < num_chars; i++) {
		j = 0;
		while (char_array[j] != file_contents[index]) {
			j++;
		}
		int bits = bits_of_char[j];
		while (bits > 0) {
			if ((bits % 3) - 1) {
				added_bit = 0x80 >> filled_bits;
				bit_rep = bit_rep | added_bit;
				filled_bits++;
				
				print_char(fp, &filled_bits, &bit_rep);
			} else {
				filled_bits++;
				
				print_char(fp, &filled_bits, &bit_rep);
			}
		}		
	}
	
	if (filled_bits > 0) {
		fprintf(fp, "%c", bit_rep);
	}
	
	return;
}

// tnode functions

Tnode *construct_tnode(int add_char, long num_of_char){
	Tnode *new_node = malloc(sizeof(*new_node));
	if (new_node == NULL){
		free(new_node);
		return NULL;
	}
	new_node->node_char = add_char;
	new_node->num_char = num_of_char;
	
	return new_node;
}

Tnode *tpq_enqueue(Tnode **pq, int add_char, long num_of_char){
	Tnode *new_node = construct_tnode(add_char, num_of_char);
	new_node->next_0 = NULL;
	new_node->next_1 = NULL;
	Tnode dummy = {.node_char = 0, .num_char = 0, .lin_next = *pq, .next_0 = NULL, .next_1 = NULL};
	Tnode *prev = &dummy;
	Tnode *curr = *pq;
	while (curr != NULL){		
		if (new_node->num_char < curr->num_char){
			break;
		} else if(new_node->num_char == curr->num_char){
			if (new_node->node_char < curr->node_char){
				break;
			}
		}
		prev = curr;
		curr = (*curr).lin_next;		
	}
	(*prev).lin_next = new_node;
	(*new_node).lin_next = curr;
	*pq = dummy.lin_next;
	return new_node;
}

Tnode *tpq_dequeue(Tnode **pq) {
	if (pq == NULL){
		return NULL;
	}
	Tnode *delete_node = *pq;
	if (delete_node != NULL){
		*pq = delete_node->lin_next;
		(*delete_node).lin_next = NULL;
	}
	return delete_node;
}

void destroy_tree(Tnode *tree){	
	if (tree == NULL){
		return;
	}
	if (tree->next_0 == NULL && tree->next_1 == NULL){
		free(tree);
		return;
	}else{
		if (tree->next_0 != NULL){
			destroy_tree(tree->next_0);
			tree->next_0 = NULL;
		}
		if (tree->next_1 != NULL){
			destroy_tree(tree->next_1);
			tree->next_1 = NULL;
		}
		destroy_tree(tree);
	}
	return;
}

void destroy_linear_tlist(Tnode *tree){	
	Tnode *temp_next = tree->lin_next;
	Tnode *curr_node = tree;
	while (temp_next != NULL){
		free(curr_node);
		curr_node = temp_next;
		temp_next = (*temp_next).lin_next;
	}
	free(curr_node);
	return;
}
