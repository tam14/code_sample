 #include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdbool.h>

// structure definition (tnode)
// admittedly this is not an elegant solution, but this data structure mixes elements
// of a priority queue and a tree. it will initially act as a pq, and then gradually 
// be built into a huffman tree
typedef struct _Tnode {
	int node_char;
	long num_char;
	struct _Tnode *lin_next; 
	struct _Tnode *next_0;
	struct _Tnode *next_1;
} Tnode;

// tnode functions

Tnode *construct_tnode(int add_char, long num_of_char){
	// creates a new node for the tree given a character and a weight
	Tnode *new_node = malloc(sizeof(*new_node));
	if (new_node == NULL){
		return NULL;
	}
	
	new_node->node_char = add_char;
	new_node->num_char = num_of_char;
	
	return new_node;
}

Tnode *tpq_enqueue(Tnode **pq, int add_char, long num_of_char){
	// enqueues an element onto the priority queue
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
	// pulls a node from the "priority queue" when forming the huffman tree
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
	// frees up memory allocated for the tree
	if (tree == NULL){
		return;
	}
	
	if ((*tree).next_0 == NULL && (*tree).next_1 == NULL){
		free(tree);
		return;
	}else{
		if ((*tree).next_0 != NULL){
			destroy_tree((*tree).next_0);
			(*tree).next_0 = NULL;
		}
		
		if ((*tree).next_1 != NULL){
			destroy_tree((*tree).next_1);
			(*tree).next_1 = NULL;
		}
		
		free(tree);
	}
	
	return;
}

void destroy_linear_tlist(Tnode *tree){	
// used almost exclusively to terminate the priority queue if memory cannot be allocated 
// for it
	Tnode *temp_next = (*tree).lin_next;
	Tnode *curr_node = tree;
	
	while (temp_next != NULL){
		free(curr_node);
		curr_node = temp_next;
		temp_next = (*temp_next).lin_next;
	}
	
	free(curr_node);
	return;
}

// helper functions

void num_of_chars(FILE *fp, long *num_array){
	// counts the number of time each character appears in the file
	fseek(fp, 0, SEEK_SET);
	int next_char = fgetc(fp);
	
	while (next_char != EOF){
		num_array[next_char] = num_array[next_char] + 1;
		next_char = fgetc(fp);
	}
	
	return;
}

int get_chars_in_file(long *num_array, Tnode **tree, long *size){
	// for each char that appears at least once in the file, this function adds
	// node in the priority queue for it
	int non_zero_char = 0;
	int i = 0;
	
	for (; i < 256; i++){
		if (num_array[i] > 0){
			*size = *size + num_array[i];
			non_zero_char++;
			Tnode *added_node = tpq_enqueue(tree, i, num_array[i]);
			if (added_node == NULL){
				fprintf(stderr, "Node could not be created, destroying linear tree\n");
				destroy_linear_tlist(*tree);
				return 0;
			}
		}
	}
	
	return non_zero_char;
}

void form_huff_tree(Tnode **tree){
	// pulls nodes from the pq and then combines them to form huffman subtrees,
	// eventually leading to a full tree
	Tnode *curr_1 = *tree;
	Tnode *curr_2 = NULL;
	int weight = 0;
	
	// adds up the weight of every character
	while (curr_1 != NULL){
		weight += curr_1->num_char;
		curr_1 = curr_1->lin_next;
	}
	
	// combines nodes with a node containing the weights of its childrennodes.
	// continues until there is a root node equal to the weight of all characters
	// together
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
		Tnode *combine_node = tpq_enqueue(tree, curr_1->node_char + curr_2->node_char + 256, curr_1->num_char + curr_2->num_char);
		
		if (combine_node == NULL){
			return;
		}
		
		combine_node->next_0 = curr_1;
		combine_node->next_1 = curr_2;
	}
	
	return;
}

void get_char_encodings(int *char_array, int *bits_of_char, Tnode **tree, int bits, int *idx) {
	// calculates the corresponding encodings for each character
	if ((*tree)->next_0 == NULL && (*tree)->next_1 == NULL){
		char_array[*idx] = (*tree)->node_char;
		int reverse_bit = 0;
		
		// bits are stored as a base_tree value, here they are reversed so that they
		// print out the right way
		while (bits != 0){
			reverse_bit = reverse_bit * 3 + bits % 3;
			bits /= 3;
		}

		bits_of_char[*idx] = reverse_bit;
		*idx = *idx + 1;
		
		return;
	}else{ 
		if((*tree)->next_0 != NULL){
			bits = bits * 3 + 1;
			get_char_encodings(char_array, bits_of_char, &((*tree)->next_0), bits, idx);
			bits = (bits - 1) / 3;
		}
		
		if((*tree)->next_1 != NULL){
			bits = bits * 3 + 2;
			get_char_encodings(char_array, bits_of_char, &((*tree)->next_1), bits, idx);
		}
	}
	
	return;
}

char *store_file_contents(FILE *fp) {
	// fairly straight forward, stores the contents in the file as a char array
	fseek(fp, 0, SEEK_END);
	int size = ftell(fp);
	char *file_contents = malloc(sizeof(*file_contents) * size);
	
	if (file_contents == NULL) {
		fprintf(stderr, "Failed to alloc memory for file contents\n"); 
		return NULL;
	}
	
	fseek(fp, 0, SEEK_SET);
	fread(file_contents, sizeof(*file_contents), size, fp);
	
	return file_contents;
}

long calc_significant_bits(int num_non_zero, long *num_array, int *char_array, int *bits_of_char) {
	// calculates the number of significant bits of the file that will be in the compressed
	// file. i couldn't figure out the pseudo EOF, so this will tell the unhuff program when
	// to stop uncompressing
	int bits = 0;
	int digits = 0;
	long sig_bits = 0;
	int i = 0;
	
	for (; i < num_non_zero; i++) {
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
	// store info about the length of the header and the file at the beginning of the 
	// compressed file
	unsigned int header_bits = 2 * non_zero_char - 1 + non_zero_char * sizeof(char) * 8;
	unsigned int sig_bytes = (sig_bits + 7) / 8;
	unsigned int offset = sig_bytes * 8 - sig_bits; 
	offset = offset << 29;
	sig_bytes = sig_bytes | offset;
	putw(header_bits, fp);
	putw(sig_bytes, fp);

	return;
}

void print_char(FILE *fp, int *filled_bits, char *bit_rep) {
	// if there are 8 significant bits, print them into the file
	if (*filled_bits == 8) {
			fprintf(fp, "%c", *bit_rep);
			*bit_rep = 0x0;
			*filled_bits = 0;
	}
	
	return;
}

void print_header_recurse(FILE *fp, Tnode **tree, int *filled_bits, char *bit_rep) {	
	// prints out the header for the unhuff function in a recursive manner
	if ((*tree)->node_char < 256) {
		// print out a '1' bit for a leaf node
		unsigned char added_bit = 0x1 << (7 - *filled_bits);
		*bit_rep = *bit_rep | added_bit;
		*filled_bits = *filled_bits + 1;
		print_char(fp, filled_bits, bit_rep);
		int add_bits = 8;
		int temp = 0;
		
		// prints out the char at this leaf node
		while (add_bits > 0) {		
			added_bit = (*tree)->node_char << (8 - add_bits);
			added_bit = added_bit >> *filled_bits;
			*bit_rep = *bit_rep | added_bit;
			temp = add_bits - *filled_bits;
			*filled_bits += temp;
			add_bits -= temp;
			print_char(fp, filled_bits, bit_rep);
		}
	} else {
		// prints out a '0' bit for a trunk node
		*filled_bits = *filled_bits + 1;
		print_char(fp, filled_bits, bit_rep);
		
		print_header_recurse(fp, &((*tree)->next_0), filled_bits, bit_rep);
		print_header_recurse(fp, &((*tree)->next_1), filled_bits, bit_rep);
	}
	
	return;
}

void print_header (FILE *fp, Tnode **tree) {
	// initializes values and then calls the recursion function
	int filled_bits = 0;
	char bit_rep = 0;
	
	print_header_recurse(fp, tree, &filled_bits, &bit_rep);
	
	if (filled_bits > 0) {
		fprintf(fp, "%c", bit_rep);
	}
	
	return;
}



void print_bit_representation(FILE *fp, int *char_array, int *bits_of_char, char *file_contents, int num_chars){
	// prints out the file iteratively. it pulls a char from the file, looks up the corresponding
	// bit representation, and then prints it to the file (when there are 8 sig bits)
	long index = 0;
	int filled_bits = 0;
	char bit_rep = 0x0;
	unsigned char added_bit = 0x0;
	int j = 0;
	int i = 0;
	for (; i < num_chars; i++) {
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
	
			bits /= 3;
		}
		
		index++;
	}
	
	if (filled_bits > 0) {
		fprintf(fp, "%c", bit_rep);
	}
	
	return;
}

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

	form_huff_tree(&tree);
	
	// prepare to print out encoding
	int *char_array = malloc(sizeof(*char_array) * non_zero_chars);
	int *bits_of_char = malloc(sizeof(*char_array) * non_zero_chars);
	char *contents = store_file_contents(fp);

	fclose(fp);
	int idx = 0;
	int bits = 0;
	get_char_encodings(char_array, bits_of_char, &tree, bits, &idx);
	long sig_bits = calc_significant_bits(non_zero_chars, num_char, char_array, bits_of_char);
		
	// print out representations of the header
	FILE *of = fopen(argv[1], "w");
	fseek(of, 0, SEEK_SET);
	print_sizes(of, non_zero_chars, sig_bits);
	print_header(of, &tree);
	print_bit_representation(of, char_array, bits_of_char, contents, size);
	fclose(of);
	
	// deallocate the tree
	destroy_tree(tree);
	free(char_array);
	free(bits_of_char);
	free(contents);
	
	return EXIT_SUCCESS;
}
