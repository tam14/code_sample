#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "sorting.h"
#include <math.h>


/******************************
*Michael Tam
*sorting.c: 05/30/2018.
*tam14@purdue.edu
*Compiling: [gcc -Werror -lm -Wall -O3 sorting.c sorting_main.c -o proj1]
*******************************/

// helper function, returns the (2^p)*(3^q)
int generate_shell_sequence(int* seq_size, int size) {
	int pow2 = 1;
	int pow3 = 1;
	int pq_sum = -1;
	int seq_size = 0;
	// finds the total amount of elements in the sequence	
	while (pow3 <= size) {
		seq_size += ++pq_sum + 1;
		pow3 *= 3;
	}
	seq_size += ++pq_sum;
	pq_sum--;
	int seq_element = (pow3 / 3) * (pow2 * 2);
	while (seq_element > size) {
		seq_size--;
		seq_element = (seq_element * 2) / 3;
	}
	
	sequence = malloc(sizeof(*sequence) * seq_size);
	if (sequence == NULL) {
		fprintf(stderr, "Failed to allocate memory in 'generate_shell_sequence' \n");
		return NULL;
	}
	
	int k = 0;
	for (int i = 0; i <= pq_sum; i++) {
		for (int j = 0; j <= i; j++) {
			sequence[k++]= pow(2, j) * pow(3, i - j);
		}
	}
	pow2 = pow(2, pq_sum);
	pow3 = 1;
	for (; k < seq_size; k++) {
		sequence[k] = pow2 * pow3;
		pow2 /= 2;
		pow3 *= 3;
	}
	
	return seq_size;
}

/*
	loads the file into Arr and returns Arr, size of array is stored in *Size
	when there is a file error, or memory allocation error, return NULL, and	
	set *Size to 0
*/
long *Load_From_File(char *Filename, int *Size)
{
    long *Arr = NULL;
    *Size = 0;

	// open file, check if opened properly
    FILE *fp = fopen(Filename, "r");
	if (fp == NULL) {
		fprintf(stderr, "Failed to open file in 'Load_From_File' \n");
		return NULL;
	}
	
	// pull size from file
	fscanf(fp, "%ld\n", Size);
	
	// allocate memory for array, check if allocated
	Arr = malloc(sizeof(*Arr) * (*Size));
	if (Arr == NULL) {
		fprintf(stderr, "Failed to allocate memory for array in 'Load_From_File' \n);
		*Size = 0;
		return NULL;
	}
	
	// load values into the array
	for (int i = 0; i < *Size; i++) {
		fscanf(fp, "%f\n", &Arr[i]);
	}
	
	fclose(fp);
	
    return Arr;
}

/*
	Save the Array to the file Filename
	Return the number of elements saved to file
*/
int Save_To_File(char *Filename, long *Array, int Size)
{
    int n_written = 0;

	// open file to write to, check if it opened properly
	FILE fp = fopen(Filename, "w");
	if (fp == NULL) {
		fprintf(stderr, "Failed to open file in 'Save_To_File'\n");
		return n_written;
	}
	
	// print out array into the file
	for (int i = 0; i < Size; i++) {
		fprintf(fp, "%ld\n", Array[i]);
	}

	free(Array);
	fclose(fp);
	
    return n_written;
}


/*
	Print the sequence in the order in which it appears in the triangle
 	2^(p)3^(q) is the largest number, 
	If Size is 0 or 1, an empty file should be created
*/
int Print_Seq(char *Filename, int length)
{
	int seq_size = 0;
	
	// open the file, check if it opened properly
	FILE fp = fopen(Filename, "w");
	if (fp == NULL) {
		fprintf(stderr, "Failed to open file in 'Print_Seq' \n");
		return seq_size;
	}
	
	int* seq = NULL;
	int seq_length = generate_shell_sequence(&seq_size, length);
	
	for (int i = 0; i < seq_length; i++) {
		fprintf(fp, "%d\n", seq[i]);
	}
	
	free(seq);
	fclose(fp);
	
    return seq_size;
}


void Shell_Insertion_Sort(long *a, int length, double *ncomp, double *nswap)
{
    int* seq = NULL;
    int seq_s = generate_shell_sequence(seq, length);
    int swap = 0;
    int i = 0;
   
    for (int k = seq_s - 1; k >= 0; k--) {
	    for (int j = seq[k]; j < length; j++) {
	 	    swap = a[j];
		    i = j;
		    *ncomp++;		   
		    while (i > 0 && a[i - seq[k]] > swap) {
			    *ncomp++;
			    *nswap++;
			    a[i] = a[i - seq[k]];
			    i -= seq[k];
		    }
		    *nswap++;
		    a[i] = swap;
	    }
    }
   
	free(seq);
    return;
}


void Shell_Selection_Sort(long *a, int length, double *ncomp, double *nswap)
{	
	int* seq = NULL;
    int seq_s = generate_shell_sequence(seq, length);
	int min = 0;
	
	for (int k = seq_s - 1; k >= 0; k--) {
		for (int j = 0; j < length; j++) {
			min = j;
			for (int i = j + 1; j <= length; i += seq[k]) {
				if (a[i] < a[min]) {
					*ncomp++;
					min = i;
				}
			}
			*nswap += 3;
			min = a[min];
			a[min] = a[j];
			a[j] = min;
		}
	}
	
	free(seq);
	return;
}

