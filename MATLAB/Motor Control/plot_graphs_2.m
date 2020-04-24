close all
clear
clc
view(3)

% torque speed requirements
%====== mod these values ======
shift_torque = 02.8246;   % max torque
shift_deg = 15;         % deg in deg
%==============================
shift_dist = shift_deg * 2 * pi / 360;

% plotted range of interest
%====== mod these values ======
max_torque = 4;     % torque in n*m
min_power = 10;               % time in ms
max_power = 600;              % time in ms
mults = 10;                  % rounds to nearest multiple
%==============================
%min_time = 5 * floor(min_time ./ 5);
min_power = mults * floor(min_power ./ mults);
max_power = mults * ceil(max_power ./ mults);
delta_torque = max_torque * mults / (max_power - min_power);
delta_time = mults;
torque_vector = 0 : delta_torque : max_torque;
power_vector = min_power : delta_time : max_power;

% shift time to power
time_vector = shift_dist * shift_torque * 1000 ./ power_vector; 

% power mesh
time_mesh = zeros(length(torque_vector), length(power_vector));
for n = 1 : length(torque_vector)
   time_mesh(n, :) = time_vector;
end
time_mesh = transpose(time_mesh);

% plot power mesh
figure(1)
hold on
mesh(torque_vector, power_vector, time_mesh);
xlabel('Average Motor Torque (n*m)')
ylabel('Motor Power (W)')
zlabel('Shift Time (ms)')

% % motor curves- each row is freeload speed in rpm, torque in n*m
% motor_curves = [    06380,  4.69;   % falcon 500
%                     05330,  2.41;   % CIM motor
%                     05840,  1.41;   % mini CIM motor
%                     13180,  0.43;   % BAG motor
%                     18730,  0.71;   % 775 pro
%                     05880,  3.36;   % neo brushless
%                     14270,  0.36;   % andymark 9015
%                     05480,  0.17;   % andymark neverest
%                     05800,  0.28;   % andymark rs775-125
%                     13050,  0.72;   % banebots rs-775 18V
%                     19000,  0.38;   % banebots rs-550
%                     ];
motor_curves = [    05880,  3.36;   % neo brushless
                    05840,  1.41;   % mini CIM motor
                    13180,  0.43;   % BAG motor
                    05480,  0.17;   % andymark neverest
                    ];                

% plot motor curves 
for n = 1 : size(motor_curves, 1)
    y = [0, motor_curves(n, 1)*pi/30];
    x = [motor_curves(n, 2), 0];
    a = (0 : 100) * motor_curves(n, 2) / 100;
    b = interp1(x, y, a) .* a;
    c = interp1(power_vector, time_vector, b);
    plot3(a, b, c, 'LineWidth', 2.0)
end

% references
power_for_10ms = shift_dist * shift_torque * 1000 / 10;
power_for_20ms = shift_dist * shift_torque * 1000 / 20;
power_for_50ms = shift_dist * shift_torque * 1000 / 50 + 5;
width = [0, max_torque];
plot3(width, [power_for_50ms, power_for_50ms], [50, 50], 'LineWidth', 2.0);
plot3(width, [power_for_20ms, power_for_20ms], [20, 20], 'LineWidth', 2.0);
plot3(width, [power_for_10ms, power_for_10ms], [10, 10], 'LineWidth', 2.0);

legend('Shift Time', 'Neo Brushless', 'MiniCIM', 'BAG Motor', 'Neverest', '50ms Shift', '20ms Shift', '10ms Shift')
