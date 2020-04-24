#include "measure.h"
#include "arm_math.h"

/**
 * initializes the values for a new kalman filter object or resets an existing
 * one for a new measurement 
 * @param kalman	the filter for a data stream. contains current filter 
 * 								parameters and the previous value
 * @param q				the new process noise constant
 * @param r				the new measurement noise constant
 */
void kalman_init(struct KalmanFilter *kalman, float q, float r) {
    kalman->p = 1;
    kalman->k = 1;
    kalman->q = q;
    kalman->r = r;
    kalman->prev = 0;
}

/**
 * performs a step of kalman filtering given an kalman filter structure and a 
 * new measurement. returns the new value
 * @param kalman	the filter for a data stream. contains current filter 
 * 								parameters and the previous value
 * @param meas		the new measurement from the sensor
 */
float kalman_filter(struct KalmanFilter *kalman, float meas) {
    float vcurr = kalman->prev;
    
    kalman->p += q;	// update p
    kalman->k = kalman->p / (kalman->p + r); // update k
    vcurr = vcurr + (kalman->k)*(meas - vcurr);// calculate vcurr
    kalman->p = (1.0f - (kalman->k)) * (kalman->p); // modify p
		kalman->prev = vcurr;	// store the new value into 
 
    return vcurr;
}

/**
 * performs quaternion multiplication given a float-array containing the 
 * coefficients. operation is not commutative
 * @param a				first quaternion
 * @param b				second quaternion
 * @param result 	resulting quaternion
 */
void q_mult(float32_t* a, float32_t* b , float32_t* result) {
	result[0] = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3];
	result[1] = a[1]*b[0] + a[0]*b[1] - a[3]*b[2] + a[2]*b[3];
	result[2] = a[2]*b[0] + a[3]*b[1] + a[0]*b[2] - a[1]*b[3];
	result[3] = a[3]*b[0] - a[2]*b[1] + a[1]*b[2] + a[0]*b[3];
}

/**
 * rotates a vector back to the original orientation
 * @param	angles 	array containing 3 angles 
 * @param p				quaternion (vector) to be rotated
 * @param result 	resulting quaternion
 */
void rotate_vector(float* angles, float* p, float* result) {
	float32_t rot_x[4] = {arm_cos_f32((float32_t) -angles[0] / 2.0f), arm_sin_f32((float32_t) -angles[0] / 2.0f), 0.0f, 0.0f};
	float32_t inv_x[4] = {arm_cos_f32((float32_t) angles[0] / 2.0f), arm_sin_f32((float32_t) angles[0] / 2.0f), 0.0f, 0.0f};
	float32_t rot_y[4] = {arm_cos_f32((float32_t) -angles[1] / 2.0f), 0.0f, arm_sin_f32((float32_t) -angles[0] / 2.0f), 0.0f};
	float32_t inv_y[4] = {arm_cos_f32((float32_t) angles[1] / 2.0f), 0.0f, arm_sin_f32((float32_t) angles[0] / 2.0f), 0.0f};
	float32_t rot_z[4] = {arm_cos_f32((float32_t) -angles[2] / 2.0f), 0.0f, 0.0f, arm_sin_f32((float32_t) -angles[0] / 2.0f)};
	float32_t inv_z[4] = {arm_cos_f32((float32_t) angles[2] / 2.0f), 0.0f, 0.0f, arm_sin_f32((float32_t) angles[0] / 2.0f)};
	float32_t temp1[4];
	float32_t temp2[4];
	
	temp2[0] = 0.0f;
	temp2[1] = (float32_t) p[0];
	temp2[2] = (float32_t) p[1];
	temp2[3] = (float32_t) p[2];
	
	q_mult(rot_x, temp2, temp1);
	q_mult(temp1, inv_x, temp2);
	q_mult(rot_y, temp2, temp1);
	q_mult(temp1, inv_y, temp2);
	q_mult(rot_z, temp2, temp1);
	q_mult(temp1, inv_z, temp2);
	
	result[0] = (float) temp2[0];
	result[1] = (float) temp2[1];
	result[2] = (float) temp2[2];
	result[3] = (float) temp2[3];
}
