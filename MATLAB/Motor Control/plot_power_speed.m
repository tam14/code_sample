close all
clear
clc

% % neo brushless
% neo_free_speed = 5676;
% neo_stall_torque = 3.75;
% neo_y = [0, neo_free_speed*pi/30];
% neo_x = [neo_stall_torque, 0];

% % neverest brushed
% neverest_free_speed = 6600;
% neverest_stall_torque = .06;
% neverest_y = [0, neverest_free_speed*pi/30];
% neverest_x = [neverest_stall_torque, 0];

% BAG motor
no_load_rpm = 13180;
stall_torque = .43;

% motor curve
y = [0, no_load_rpm*pi/30];
x = [stall_torque, 0];

% initialize vector
a = (1 : 100) * stall_torque / 100;
% c = (1 : 100) * neo_stall_torque / 100;
% e = (1 : 100) * neverest_stall_torque / 100;

% torque speed requirements
o_x = 02.8246; % max torque
%o_x = 08.6150; % for eclutch

shift_dist = 15 * 2 * pi / 360;     % in rad
o_y1 = shift_dist / .1;             % average speed to shift in 100ms
o_y2 = shift_dist / .01;            % average speed to shift in 20ms
o_y3 = shift_dist / .005;           % average speed to shift in 10ms

% versaplanetary gearbox gearings
scale_vector = [100, 90, 81, 70, 63, 50, 49, 45, 40, 36, 35, 30, 28, 27, 25, 21, 20, 16, 15, 12, 10, 9, 7, 5, 4, 3, 1];
%scale_vector = [100, 90, 81, 70, 63, 50, 49, 45, 40, 36, 35, 30, 28, 27, 25, 21, 20, 16, 15, 12, 10, 9, 7];

% torque speed requirements at motor
dot_x = o_x ./ scale_vector;
dot_y1 = o_y1 .* scale_vector;
dot_y2 = o_y2 .* scale_vector;
dot_y3 = o_y3 .* scale_vector;

amps = dot_x * 132.5;

% actual speed @torque
speed_actual1 = interp1(x, y, dot_x);
b = interp1(x, y, a);
% d = interp1(neo_x, neo_y, c);
% f = interp1(neverest_x, neverest_y, e);

% motor power @torque
motor_pow_func = a .* b;
% neo_pow_func = c .* d;
% neverest_pow_func = e .* f;
motor_power = speed_actual1 .* dot_x;
pow_y1 = dot_x .* dot_y1;
pow_y2 = dot_x .* dot_y2;
pow_y3 = dot_x .* dot_y3;

for i = 1 : length(scale_vector)
    fprintf("%3d:1 ratio, %f A, %f W\n", scale_vector(i), amps(i), motor_power(i))
end

% motor torque speed requirements and curve
figure(1)
hold on
plot(dot_x, dot_y1, 'rx-')
plot(dot_x, dot_y2, 'gx-')
plot(dot_x, dot_y3, 'bx-')
plot(x, y, 'k')
% plot(neo_x, neo_y, 'c')
% plot(neverest_x, neverest_y, 'm')

xlabel("Torque (N*m)");
ylabel("Speed (rad/sec)");
% legend({'Torque-speed req for 100ms shift', 'Torque-speed req for 20ms shift', 'Torque-speed req for 10ms shift', 'BAG Motor Torque-Speed Curve', 'Neo Brushless Torque-Speed Curve', 'Neverest Brushed Torque-Speed Curve'}, 'Location', 'northeast')
legend({'Torque-speed req for 100ms shift', 'Torque-speed req for 20ms shift', 'Torque-speed req for 10ms shift', 'BAG Motor Torque-Speed Curve'}, 'Location', 'northeast')

% motor power requirements and curve
figure(2)
hold on
plot(dot_x, pow_y1, 'r-')
plot(dot_x, pow_y2, 'g-')
plot(dot_x, pow_y3, 'b-')
plot(dot_x, motor_power, 'kx')
plot(a, motor_pow_func, 'k-')
% plot(c, neo_pow_func, 'c')
% plot(e, neverest_pow_func, 'm')

xlabel("Torque (N*m)")
ylabel("Power (W)");
legend({'Power req for 100ms shift', 'Power req for 10ms shift', 'Power req for 5ms shift', 'Power @torque point', 'Power Curve'}, 'Location', 'northeast')

figure(3)
%times = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1];
%power_req = shift_dist * o_x * 1000 ./ times;

power_req = 5 : 10 : 1000;
times = shift_dist * o_x * 1000 ./ power_req;
plot(power_req, times)
ylabel("Shift Time (ms)")
xlabel("Power (W)")