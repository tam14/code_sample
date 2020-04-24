function [displacement] = kalman_3d(expected_dist, deg_sweep, arm_length, time, noise)

% laser measurement
measurement1 = expected_dist ./ sind(deg_sweep./2)./2 - arm_length + (noise).*randn(1, 10);
measurement2 = expected_dist ./ sind(deg_sweep./2)./2 - arm_length + (noise).*randn(1, 10);

rate = 800;
idx_end = round(time * rate);
idx = 0 : idx_end;
t = idx ./ (time * rate);

% true rotation data
z_deg = deg_sweep * t;
z_rvel = [deg_sweep./time, diff(z_deg) ./ diff(t)];

% true pos and accel
x_pos = arm_length * cosd(z_deg);
y_pos = arm_length * sind(z_deg);
x_vel = [0, diff(x_pos) ./ diff(t)];
y_vel = [deg_sweep * pi ./ 180, diff(y_pos) ./ diff(t)];
x_accel = [0, diff(x_vel) ./ diff(t)];
y_accel = [0, diff(y_vel) ./ diff(t)];

laser_pointx = x_pos(1) + measurement1 * cosd(z_deg(1));
laser_pointy = y_pos(1) + measurement1 * sind(z_deg(1));

for n = 1:idx_end+1
    x_saccel(n) = x_accel(n).*cosd(z_deg(n)) + y_accel(n)*sind(z_deg(n));
    y_saccel(n) = -x_accel(n).*sind(z_deg(n)) + y_accel(n)*cosd(z_deg(n));
end

delta_t = t(2) - t(1);
% linear kalman
F = [1 delta_t ((delta_t).^2)/2 0 0 0; 0 1 delta_t 0 0 0; 0 0 1 0 0 0; 0 0 0 1 delta_t ((delta_t).^2)/2; 0 0 0 0 1 delta_t; 0 0 0 0 0 1];
H = [0; 0; 1; 0; 0; 1];
P = [1 0 0 0 0 0; 0 1 0 0 0 0; 0 0 1 0 0 0; 0 0 0 1 0 0; 0 0 0 0 1 0; 0 0 0 0 0 1];
Q = [0 0 0 0 0 0; 0 0 0 0 0 0; 0 0 0 0 0 1; 0 0 0 0 0 0; 0 0 0 0 0 0; 0 0 0 0 0 1];
R = 1;
select = [
    0, 0, 0, 0, 0, 0;
    0, 0, 0, 0, 0, 0;
    0, 0, 1, 0, 0, 0;
    0, 0, 0, 0, 0, 0;
    0, 0, 0, 0, 0, 0;
    0, 0, 0, 0, 0, 1
    ];
% rot kalman
A = [1 delta_t; 0 1];
E = [0 1];
B = [1 0; 0 1];
C = [0 0; 0 1];
D = 1;

z = 10;
deg = zeros(z, idx_end);

x_list = zeros(z, idx_end);
y_list = zeros(z, idx_end);

for m = 1 : z
    x_sig = x_saccel + 2*.0132*randn(size(x_saccel));
    y_sig = y_saccel + 2*.0132*randn(size(y_saccel));
    deg_sig = z_rvel + .0132*randn(size(z_rvel));
    
    v_prev = [1; x_vel(1); -deg_sweep*pi./(180*time); 0; y_vel(1); 0];
    w_prev = [z_deg(1); z_rvel(1)];
    meas_x = x_sig(1);
    meas_y = y_sig(1);
    meas_deg = deg_sig(1);

    x_filt = [];
    y_filt = [];
    deg_filt = [];
    for n = 2:size(deg_sig, 2)
        B = A*B*A' + C;
        L = B*E'/(E*B*E' + D);mea
        w_curr = A*w_prev;
        
        w_curr = w_curr + L*(meas_deg - E*w_curr);
        B = (eye(2) - L*E)*B;
        
        %predict
        P = F*P*F' + Q;
        K = P*H/(H'*P*H + R);
        v_curr = F*v_prev;
        real_x = meas_x*cosd(w_curr(1, 1)) - meas_y*sind(w_curr(1, 1));
        real_y = meas_x*sind(w_curr(1, 1)) + meas_y*cosd(w_curr(1, 1));
        temp = select * v_curr;
        v_curr = v_curr + K.*(([0; 0; real_x; 0; 0; real_y] - temp));
        P = (eye(6) - K*H')*P;

        deg_filt = [deg_filt, w_curr];
        x_filt = [x_filt, v_curr(1:3, 1)];
        y_filt = [y_filt, v_curr(4:6, 1)];
        meas_x = x_sig(n);
        meas_y = y_sig(n);
        meas_deg = deg_sig(n);
        
        v_prev = v_curr;
        w_prev = w_curr;
    end

    x_list(m, 1:idx_end) = x_filt(1, 1:idx_end);
    y_list(m, 1:idx_end) = y_filt(1, 1:idx_end);
    deg(m, 1:idx_end) = deg_filt(1, 1:idx_end);
end

% figure(2)
% hold on
% plot(x_pos, y_pos)
% for o = 1:z
%     plot(x_list(o, :), y_list(o, :))
% end
% 
% x_final = x_list(:, end);
% y_final = y_list(:, end);

% figure(3)
% hold on 
% plot(x_pos(end), y_pos(end), 'x')
% plot(x_final, y_final, 'x')
% 
% figure(4)
% hold on
% for o = 1:z
%     plot(t(2:end), z_deg(2:end) - deg(o, :))
% end

laser_pointx_list = x_list(:, end) + measurement2 * cosd(deg(end));
laser_pointy_list = y_list(:, end) + measurement2 * sind(deg(end));

displacement = [];
for n = 1 : size(x_list, 1)
    displacement(n) = sqrt((laser_pointx_list(n) - laser_pointx(n)).^2 + (laser_pointy_list(n) - laser_pointy(n)).^2);
end