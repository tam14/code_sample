/*
 *	Measure header file
 */
#ifndef MEASURE_H
#define MEASURE_H

#include "arm_math.h"

struct KalmanFilter {
    float p;
    float k;
    float q;
    float r;
    float prev;
}

void kalman_init(struct KalmanFilter *kalman, float q, float r);
float kalman_filter(struct KalmanFilter *kalman, float vmeas);
void q_mult(float32_t* a, float32_t* b , float32_t* result);
void rotate_vector(float* angles, float* p, float* result);

#endif