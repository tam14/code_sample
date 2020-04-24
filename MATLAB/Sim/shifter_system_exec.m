% moment of inertia of the rotor (kg*m^2)
J = .00082;
%J = 0.00039;  % kg*m^2 | GM9213-2-SP 
%J = 0.00013; % kg*m^2 | GM8212-21-SP
%J = 0.00023; % kg*m^2 | GM8224S020-sp

% motor viscous friction constant (N*m*s)
b = .05;
%b = 0.02; %oz*in/krpm


% electromotive force constant (V/rad/sec)
Ke = 2.47;
%Ke = 2.29; %V/krpm, need V/rad/sec
% = .0395


% motor torque constant (N*m/Amp)
Kt = 3.34;
%Kt = 5.6; % N*m/Amp | GM9213-2-SP
%Kt = 3.06; % N*m/Amp | GM8212-21-SP
%Kt = 3.09; % N*m/Amp | GM8224S020-SP


% electric (terminal) resistance (Ohms)
R = 1.17;
%R = 8.33; % Ohms | GM9213-2-SP
%R = 10.8; % Ohms | GM8212-21-SP
%R = 4.33; % Ohms | GM8224S020-SP


% electric inductance (H)
L = 1;
%L = 6.2; % H | GM9213-2-SP
%L = 5.4; % H | GM8212-21-SP
%L = 2.3; % H | GM8224S020-SP

sim('shifter_system_sim_new')