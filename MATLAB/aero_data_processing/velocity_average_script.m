close all
clear

% change this variable when you figure out good angle for cornering
cornering_angle = 10;
% ^^^

%% load file(s)

% % load single file
% % uncomment to choose file (comment multiple file block)
% file = uigetfile('*.csv');
% files = [file];


% load multiple files
files = dir('*.csv');

%% start summary cell array
% initialize summary cell array, populate first column
summary = cell(7, length(files) + 1);
summary{2, 1} = '''Straightline median';
summary{3, 1} = '''Straightline average';
summary{4, 1} = '''Straightline stddev';
summary{5, 1} = '''Cornering median';
summary{6, 1} = '''Cornering average';
summary{7, 1} = '''Cornering stddev';

for x = 1:length(files)
    %% stuff
    
    table = csvread(files(x).name);
    
    % pull relevant data and smooth (because it's kinda shit)
    fleft = smoothdata(table(:, 4), 'gaussian', 10);
    steering_mag = abs(table(:, 5) - 14);

    % calculate parameters for cornering data
    c_median = median(fleft(steering_mag >= cornering_angle));
    c_mean = mean(fleft(steering_mag >= cornering_angle));
    c_std = std(fleft(steering_mag >= cornering_angle));

    % calculate parameters for straight data
    s_median = median(fleft(steering_mag < cornering_angle));
    s_mean = mean(fleft(steering_mag < cornering_angle));
    s_std = std(fleft(steering_mag < cornering_angle));

    % % plot histograms: uncomment to plot histograms. only recommend doing
    % % this on one file at a time
    % figure(1)
    % c_hist = histogram(fleft(steering_mag >= cornering_angle));
    % 
    % figure(2)
    % s_hist = histogram(fleft(steering_mag < cornering_angle));

    %% output results

    % pull info from file title
    driver = regexp(files(x).name, "^([a-z]+)_", "tokens");
    run = regexp(files(x).name, "([1-2])", "tokens");

    % print individual to command window
    fprintf("%s's Autocross Stats (Run %d)\n", string(driver{1}), str2double(string(run{1})))
    fprintf("Median straight speed: %f\n", s_median)
    fprintf("Average straight speed: %f\n", s_mean)
    fprintf("Standard Deviation: %f\n", s_std)
    fprintf("Median cornering speed: %f\n", c_median)
    fprintf("Average cornering speed: %f\n", c_mean)
    fprintf("Standard Deviation: %f\n\n", c_std)
    
    % save stats to cell
    summary{1, x + 1} = char(strcat(string(driver{1}), string(run{1})));
    summary{2, x + 1} = s_median;
    summary{3, x + 1} = s_mean;
    summary{4, x + 1} = s_std;
    summary{5, x + 1} = c_median;
    summary{6, x + 1} = c_mean;
    summary{7, x + 1} = c_std;
end

xlswrite('autoX_summary.xlsx', summary);