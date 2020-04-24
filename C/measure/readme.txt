Kalman Filter in measure.c

Function Call:
float kalman_filter(float* p, float* k, float q, float r, float vmeas, float 
	vprev)

Arguments:
	Typically the arguments would consist of matrices, but the singular input and
	output forces the matrix size to be 1x1. The result is that the arguments are
	either floats or pointers to floats. 
	
	float* p:	covariance matrix
	float* k: 	kalman gain
	float q:	process noise vector
	float r:	measurement noise vector
	float vmeas:	measured value
	float vprev:	previous value
	
	p and k dictate whether the new point should remain close to the old 
	estimated value or follow the new measured value from the sensor. These 
	values are updated for each measurement and are unique to each filtered data 
	stream (allocate a new set for each stream). They are also specific to a 
	measurement, so initialize the values they reference to 1 at the beginning of
	a measurement.
	
	q and r are the noise vectors. Functionally, they determine how fast k favors
	the measurement over the previous estimate and thus can be modified to "tune"
	the performance of the filter. In the 1:1 case there's only really one degree
	of freedom for tuning, but they've been both kept to maintain the analogy to 
	the higher order example found in the white papers. I've found that q=0.05 
	and r=10 works for both the accelerometer channels and the gyrometer channels,
	but custom values can be passed in if we want to further tune each axes.
	
	vmeas is the new measurement value, and vprev is the previous estimated value.
	The return value of the function is the current value ("vcurr"); just pass 
	that value into the call for the next data point. Note that these should be 
	the unintegrated values.
	
Example:
// might be some C-specific errors, but it should give a pretty good idea of 
// what to do

KalmanFilter filter_gyro1;
KalmanFilter filter_gyro2;

float period = 1.0 / 200;
float q = 0.05;
float r = 10;

if (meas_begin) {
	// initialize values
	kalman_init(&filter_gyro1, q, r);
	kalman_init(&filter_gyro2, q, r);
	filter_gyro1->prev = data_gyro1;	// initialize to current sensor reading
	filter_gyro2->prev = data_gyro2;	// initialize to current sensor reading
	angle1 = 0;
	angle2 = 0;
	
	while (!meas_finish) {
		// perform processing if data is available
		if (data_updated) {
			// calculate filtered value 
			ang_vel1 = kalman_filter(&filter_gyro1, data_gyro1);
			ang_vel2 = kalman_filter(&filter_gyro2, data_gyro2);
			
			// integrate to find cumulative value
			angle1 += integrate(ang_vel1, period);
			angle2 += integrate(ang_vel2, period);
		}
	}
	
	display(angle1, angle2);
}