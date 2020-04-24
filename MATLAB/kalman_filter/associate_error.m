close all
clear

degree_default = 90;
degree_sweep = 10 : 10 : 180;

time_default = 1;
time_sweep = .2 : .2 : 10;

distance_default = 10;
distance_sweep = 10 : 10 : 150;

fprintf("Normal Cases\n")
error = zeros(1, 10);
mean_displacement = zeros(size(distance_sweep));
spread = zeros(size(distance_sweep));
for k = 1 : size(distance_sweep, 2)
    displacement_list = kalman_3d(distance_default, degree_default, 1, time_default, .00);
    error = 10 - displacement_list;
    mean_displacement(k) = mean(error);
    spread(k) = std(error);
end
figure(1)
hold on
subplot(2, 1, 1)
plot(distance_sweep, mean_displacement)
subplot(2, 1, 2)
plot(distance_sweep, spread)

fprintf("Laser Error\n")
error = zeros(1, 10);
mean_displacement = zeros(size(distance_sweep));
spread = zeros(size(distance_sweep));
for k = 1 : size(distance_sweep, 2)
    displacement_list = kalman_3d(distance_default, degree_default, 1, time_default, .04);
    error = 10 - displacement_list;
    mean_displacement(k) = mean(error);
    spread(k) = std(error);
end
figure(2)
hold on
subplot(2, 1, 1)
plot(distance_sweep, mean_displacement)
subplot(2, 1, 2)
plot(distance_sweep, spread)

fprintf("Change Degrees Swept\n")
mean_displacement = zeros(1, 10);
spread = zeros(size(degree_sweep));
error = zeros(size(degree_sweep));
for i = 1 : size(degree_sweep, 2)
    displacement_list = kalman_3d(distance_default, degree_sweep(i), 1, time_default, 0);
    error = distance_default - displacement_list; 
    mean_displacement(i) = mean(error);
    spread(i) = std(error);
    
end
figure(3)
hold on
subplot(2, 1, 1)
plot(degree_sweep, mean_displacement)
subplot(2, 1, 2)
plot(degree_sweep, spread)

fprintf("Change Time Taken\n")
mean_displacement = zeros(size(time_sweep));
spread = zeros(size(time_sweep));
for j = 1 : size(time_sweep, 2)
    displacement_list = kalman_3d(distance_default, degree_default, 1, time_sweep(j), 0);
    error = distance_default - displacement_list;
    mean_displacement(j) = mean(error);
    spread(j) = std(error);
end
figure(4)
hold on
subplot(2, 1, 1)
plot(time_sweep, mean_displacement)
subplot(2, 1, 2)
plot(time_sweep, spread)

fprintf("Change Distance Measured\n")
error = zeros(1, 10);
mean_displacement = zeros(size(distance_sweep));
spread = zeros(size(distance_sweep));
for k = 1 : size(distance_sweep, 2)
    displacement_list = kalman_3d(distance_sweep(k), degree_default, 1, time_default, 0);
    error = distance_sweep(k) - displacement_list;
    mean_displacement(k) = mean(error);
    spread(k) = std(error);
end
figure(5)
hold on
subplot(2, 1, 1)
plot(distance_sweep, mean_displacement)
subplot(2, 1, 2)
plot(distance_sweep, spread)