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

% BAG motor
max_speed = 13180;
max_torque = .43;

% motor curve
y = [0, max_speed*pi/30];
y_i = [0, max_speed];
x = [max_torque, 0];

torque_range = (0 : 5 : 100) * max_torque / 100;
speed_range = (0 : 5 : 100) * max_speed / 100;

power_mesh = torque_range' * speed_range;
power_line = torque_range .* fliplr(speed_range);
time_mesh = shift_dist * shift_torque * 1000 ./ power_mesh;
time_line = shift_dist * shift_torque * 1000 ./ power_line;

figure(1)
hold on
surfc(torque_range, speed_range, time_mesh, 'FaceAlpha', 0)
plot3(torque_range, fliplr(speed_range), time_line, 'LineWidth', 2.0)
xlabel('Motor Torque (n*m)')
ylabel('Motor Speed (rpm)')
zlabel('Motor Power (W)')
legend('Plot of Motor Torque * Speed (W)', 'Torque-Speed-Power curve through parameter space')

figure(2)
hold on
contour(torque_range, speed_range, time_mesh, [1, 1])
plot(x, y_i)