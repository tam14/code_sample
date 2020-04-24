close all
clear

idx = 0 : 10000;
t = idx ./ 100;
% pos = .2 * sin(t);
pos = zeros(size(idx));
% pos = t.*t ./ 360;

% % ramp in middle
% for i = 1:6001
%     if (i <= 1000)
%         pos(i) = 0;
%     elseif (i <= 2000)
%         pos(i) = 1 + sin(pi*.1*(t(i) + 5));
%     else
%         pos(i) = 2;
%     end
%     
%     
% end

init_vel = 0;

vel = [init_vel, diff(pos) ./ diff(t)];
accel = [0, diff(vel) ./ diff(t)];

delta_t = t(2) - t(1);

% x_k = F*x_(k-1) + G*u_(k-1)
F = [1 delta_t ((delta_t).^2)/2; 0 1 delta_t; 0 0 1];
G = [((delta_t).^2)/2; delta_t; 1];

% y_k = H*x_k 
H = [0 0 1];


P = [1, 0 0; 0 1 0; 0 0 1];
Q = [1, 0 0; 0, 1, 0; 0, 0, 1];
R = 1;

z = 50;
position_list = zeros(z, 6000);
accel_list = zeros(z, 6000);

for m = 1 : z
    n_accel_1 = accel + .005*randn(size(accel));
    n_accel_2 = accel + .005*randn(size(accel));
    
    length = 5;
    window = zeros(1, length);
    average = sum(window)./length;
    plotted_average = zeros(1, 1001);
    
    x_prev_1 = [0; init_vel; 0];
    u_prev_1 = n_accel_1(1);
    u_prev_2 = n_accel_2(1);

    filtered_pos = [];
    for n = 2:size(n_accel_1, 2)    
        %predict
        P = F*P*F' + Q;
        K = P*H'/(H*P*H' + R);
        x_curr_1 = F*x_prev_1;
        
        x_curr_1 = x_curr_1 + K*((u_prev_1+u_prev_2)./2 - H * x_curr_1);
        %x_curr_1 = x_curr_1 + K*((average)./2 - H * x_curr_1);
        P = (eye(3) - K*H)*P;

        filtered_pos = [filtered_pos, x_curr_1];

        u_prev_1 = n_accel_1(n);
        u_prev_2 = n_accel_2(n);
        x_prev_1 = x_curr_1;

        window = [window(2:end), u_prev_1];
        average = sum(window) ./ length;
        plotted_average(n) = average;
    end

    position_list(m, 1:6000) = filtered_pos(1, 1:6000);
    accel_list(m, 1:6000) = filtered_pos(3, 1:6000);
end

min_pos = zeros(1, 6000);
max_pos = zeros(1, 6000);
std_pos = zeros(1, 6000);
avg_pos = zeros(1, 6000);
for l = 1 : 6000
    min_pos(l) = min(position_list(:, l));
    max_pos(l) = max(position_list(:, l));
    std_pos(l) = std(position_list(:, l));
    avg_pos(l) = mean(position_list(:, l));
end

end_idx = 6000;

%% plotting results
% position
figure(4)
hold on
plot(t(1:end_idx), min_pos(1:end_idx), 'b')
plot(t(1:end_idx), max_pos(1:end_idx), 'b')
upper_std = avg_pos(1:6000) + std_pos;
lower_std = avg_pos(1:6000) - std_pos;
plot(t(1:end_idx), upper_std(1:end_idx), 'k')
plot(t(1:end_idx), lower_std(1:end_idx), 'k')
plot(t(1:end_idx), avg_pos(1:end_idx), 'g')
plot(t(1:end_idx), pos(1:end_idx), 'r')
xlabel('time')
ylabel('position')

% acceleration
min_accel = zeros(1, 6000);
max_accel = zeros(1, 6000);
std_accel = zeros(1, 6000);
avg_accel = zeros(1, 6000);
for l = 1 : 6000
    min_accel(l) = min(accel_list(:, l));
    max_accel(l) = max(accel_list(:, l));
    std_accel(l) = std(accel_list(:, l));
    avg_accel(l) = mean(accel_list(:, l));
end

figure(5)
hold on 
plot(t(1:end_idx), min_accel(1:end_idx), 'b')
plot(t(1:end_idx), max_accel(1:end_idx), 'b')
upper_accel = avg_accel(1:6000) + std_accel;
lower_accel = avg_accel(1:6000) - std_accel;
plot(t(1:end_idx), upper_accel(1:end_idx), 'k')
plot(t(1:end_idx), lower_accel(1:end_idx), 'k')
plot(t(1:end_idx), avg_accel(1:end_idx), 'g')
plot(t(1:end_idx), accel(1:end_idx), 'r')
xlabel('time')
ylabel('accel')

end_idx = 10000;
figure(2)
subplot(2, 1, 1)
plot(filtered_pos(1, 1:end_idx))
hold on
plot(pos(1, 1:end_idx))
subplot(2, 1, 2)
plot(pos(1, 1:end-1) - filtered_pos(1, 1:end_idx))

figure(3)
hold on
subplot(2, 1, 1)
plot(accel_list(50, :))
subplot(2, 1, 2)
plot(n_accel_1(1:end-1))