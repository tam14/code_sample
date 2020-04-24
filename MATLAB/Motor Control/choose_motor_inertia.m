mass_factor = (.5 : .025 : 1);
mass = mass_factor * .76 ./ 2.2;
inertia = .5 * mass * (.037 .^ 2);

gear_factor = (.7 : .025 : 1);
gear_ratio = gear_factor * 3600;

a = 1 ./ (gear_factor' * mass_factor);

figure(1)
[x, y] = meshgrid(mass_factor, gear_factor);
surf(x, y, a)