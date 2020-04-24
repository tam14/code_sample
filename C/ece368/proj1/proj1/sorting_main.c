#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "sorting.h"
#include <math.h>

/******************************
*Michael Tam
*[Filename.c]: [Date of creation].
*tam14@purdue.edu
*Compiling: [gcc -Werror -lm -Wall -O3 sorting.c sorting_main.c -o proj1]
*******************************/



int main(int argc, char *argv[])
{
   if (argc != 5) {
      fprintf(stderr, "ERROR! Incorrect Usage\n");
      fprintf(stderr, "Usage: ./sorting_main.c i_or_s input sequence output");
      return EXIT_FAILURE;
   }

   //Parse first argument
   int sorting_algo = -1;
   if (argv[1][0] == 'i' && argv[1][1] == '\0') {
      sorting_algo = 0;
   } else if (argv[1][0] == 's' && argv[1][1] == '\0') {
      sorting_algo = 1;
   }
   if (sorting_algo == -1) {
      fprintf(stderr, "incorrect sorting algorithm specified\n");
      return EXIT_FAILURE;
   }


   int Size = 0;
   double N_Comp = 0;
   double N_Move = 0;
   double IO_Time = 0;
   double Sort_Time = 0;
   clock_t Start = 0;
   clock_t End = 0;


   //load the file and check time
   Start = clock();
   long *Array = Load_From_File(argv[2], &Size);
   End = clock();
   IO_Time += difftime(End, Start);


    if (Array == NULL) {
      fprintf(stderr, "cannot load from file\n");
      return EXIT_FAILURE;
    }

    //sort the array and check time
    Start = clock();
    if (sorting_algo == 0) 
    {
      Shell_Insertion_Sort(Array, Size, &N_Comp, &N_Move);
    }
    else
    {
      Shell_Selection_Sort(Array, Size, &N_Comp, &N_Move);
    }
    End = clock();
    Sort_Time += difftime(End, Start);


    //save array to file and check time
    Start = clock();
    int saved_size = Save_To_File(argv[4], Array, Size);
    End = clock();
    if(saved_size != Size)
    {
      printf("Warning, saved size is not equal to array size");
    }

    IO_Time += difftime(End, Start);

    //save sequence to file and check time
    Start = clock();
    int seq_length = Print_Seq(argv[3], Size);
    End = clock();
    printf("Length of sequence: %d\n", seq_length);
    IO_Time += difftime(End, Start);


    
    
    printf("Number of comparisons: %le\n", N_Comp);
    printf("Number of moves: %le\n", N_Move);
    printf("I/O time: %le\n", IO_Time/CLOCKS_PER_SEC);
    printf("Sorting time: %le\n", Sort_Time/CLOCKS_PER_SEC);

   free(Array);

   return EXIT_SUCCESS;


}