% this script should calculate the angular position of one arm of a 4R
% linkage given the angular position of the other. this script is in
% context to the shifter linkage between the shifter motor and the engine,
% but can be applied to similar problems

clear
clc
close all

% linkage lengths
% these lengths g and h are dependent on the position of the motor relative
% to the engine and will need to be updated from year to year. 
a = 2.54;       % motor arm
b = 4;          % shifter arm
g = 10.112;     % distance between motor and shifter axes
h = 10;         % connector

% angles
d_theta = .5;                   % increment angle calculations by .5 deg
theta = 0 : d_theta : 360;      % input angle (angle of arm a)
psi = zeros(size(theta));      % output angle (angle of arm b)

A = 0;
B = 0;
C = 0;

% mechanical advantage calc
t_co = zeros(size(theta));      % torque ratio

for n = 1 : size(theta, 2)
    % calculate output angle
    A = 2*a*b*cosd(theta(n)) - 2*g*b;
    B = 2*a*b*sind(theta(n));
    C = (g.^2) + (b.^2) + (a.^2) - (h.^2) - 2*a*g*cosd(theta(n));
    psi(n) = (atand(B / A) + acosd(-C / sqrt((A .^ 2) + (B .^ 2))));
    
    % calculate mechanical advantage
    t_co(n) = -(-a*b*cosd(psi(n))*sind(theta(n)) - b*g*sind(psi(n)) + a*b*cosd(theta(n))*sind(psi(n))) / (a*g*sind(theta(n)) + a*b*cosd(psi(n))*sind(theta(n)) - a*b*cosd(theta(n))*sind(psi(n)));
    %fprintf("%.1f deg, %.2f deg, %.3f \n", theta(n), psi(n), t_co(n));
end

% limit domain to positive arc
max_idx = find(psi == max(psi));
min_idx = find(psi == min(psi));

theta = theta(min_idx : max_idx);
psi = psi(min_idx : max_idx);
t_co = t_co(min_idx : max_idx);

% center on the shifter arm range
angle_diff = abs(psi - theta);
center = find(angle_diff == min(angle_diff));
center = psi(center);

min_idx = size(psi, 2);
max_idx = 0;
for n = 1 : size(psi, 2)
    if and((psi(n) >= center - 25), (psi(n) <= center + 25))
        if (n < min_idx)
            min_idx = n;
        end
        
        if (n > max_idx)
            max_idx = n;
        end
    end
end

theta = theta(min_idx : max_idx);
psi = psi(min_idx : max_idx);
t_co = t_co(min_idx : max_idx);

clear angle_diff

% map effect of shifter arm to motor arm
data = csvread('angle_to_force.csv');
sa_angle = data(1, :) + center;     % angle of shifter arm
sa_torque = data(2, :);             % torqe at arm angle

ma_angle = zeros(size(sa_angle));
ma_torque = zeros(size(sa_torque));

for n = 1 : size(sa_angle, 2)
    m = 0;
    while psi(m + 1) < sa_angle(n)
       m = m + 1;
    end
    s = (theta(m + 1) - theta(m)) / (psi(m + 1) - psi(m));
    ma_angle(n) = theta(m) + s * (sa_angle(n) - psi(m));
end

for n = 1 : size(sa_torque, 2)
    m = 0;
    while theta(m+1) < ma_angle(n)
        m = m + 1;
    end
    s = (t_co(m + 1) - t_co(m)) / (theta(m + 1) - theta(m));
    factor = t_co(m) + s * (ma_angle(n) - theta(m));
    ma_torque(n) = sa_torque(n) ./ factor;
end

% display results
figure(1)
subplot(1, 2, 1)
plot(psi, theta)
subplot(1, 2, 2)
plot(theta, t_co)

figure(2)
plot(ma_angle, ma_torque)
hold on
plot(ma_angle, sa_torque)

disp(ma_angle - center)
disp(ma_torque)
