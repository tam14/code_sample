import os
import matplotlib.pyplot as plt
import statistics as statty
import shutil
import re
from math import *

q = .05
r = 10

# a = k, p, q, r
a = [1, 1, q, r]
b = [1, 1, q, r]
c = [1, 1, q, r]

data_90_deg = "90deg_data"
pics_90_deg = "90deg_results"

data_stationary = "stationary_data"
pics_stationary = "stationary_results"

data_quick = "quick_data"
pics_quick = "quick_results"


def q_mult(a, b, result):
    result[0] = a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3]
    result[1] = a[1] * b[0] + a[0] * b[1] - a[3] * b[2] + a[2] * b[3]
    result[2] = a[2] * b[0] + a[3] * b[1] + a[0] * b[2] - a[1] * b[3]
    result[3] = a[3] * b[0] - a[2] * b[1] + a[1] * b[2] + a[0] * b[3]


def rotate_vector(angles, p):
    rot_x = [cos(-angles[0]), sin(-angles[0]), 0, 0]
    inv_x = [cos(angles[0]), sin(angles[0]), 0, 0]
    rot_y = [cos(-angles[1]), 0, sin(-angles[1]), 0]
    inv_y = [cos(angles[1]), 0, sin(angles[1]), 0]
    rot_z = [cos(-angles[2]), 0, 0, sin(-angles[2])]
    inv_z = [cos(angles[2]), 0, 0, sin(angles[2])]
    temp1 = [0, 0, 0, 0]
    temp2 = [0, p[0], p[1], p[2]]

    q_mult(rot_x, temp2, temp1)
    q_mult(temp1, inv_x, temp2)
    q_mult(rot_y, temp2, temp1)
    q_mult(temp1, inv_y, temp2)
    q_mult(rot_z, temp2, temp1)
    q_mult(temp1, inv_z, temp2)

    return temp2

def simple_kalman(param_list, vmeas, vprev):
    p = param_list[1]
    q = param_list[2]
    r = param_list[3]

    p += q
    k = p / (p + r)
    vcurr = vprev + k * (vmeas - vprev)
    p = (1 - k) * p

    param_list[0] = k
    param_list[1] = p

    return param_list, vcurr


def get_data(filename):
    data_list = [[], [], []]
    with open(filename, 'r') as fp:
        for line in fp:
            line = line[:-1]
            data_point = line.split(',')
            for i in range(3):
                data_list[i].append(float(data_point[i]))

    return data_list


def plot_smoothed_data(x, y, z, filename, result_directory):

    data_list = get_data(filename)

    axis1 = data_list[0]
    smooth1 = []
    axis2 = data_list[1]
    smooth2 = []
    axis3 = data_list[2]
    smooth3 = []

    prev = axis1[0]
    for point in axis1:
        x, prev = simple_kalman(x, point, prev)
        smooth1.append(prev)

    prev = axis2[0]
    for point in axis2:
        y, prev = simple_kalman(y, point, prev)
        smooth2.append(prev)

    prev = axis3[0]
    for point in axis3:
        z, prev = simple_kalman(z, point, prev)
        smooth3.append(prev)

    index = [float(x) for x in range(len(axis1))]

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(index, axis1)
    plt.plot(index, smooth1)
    plt.subplot(3, 1, 2)
    plt.plot(index, axis2)
    plt.plot(index, smooth2)
    plt.subplot(3, 1, 3)
    plt.plot(index, axis3)
    plt.plot(index, smooth3)

    figname = filename.replace("TXT", "png")
    plt.savefig(fname=figname)
    plt.close()

    figpath = os.path.abspath(figname)
    savepath = os.path.abspath(result_directory)
    shutil.move(figpath, savepath)

    print(statty.stdev(smooth1) / statty.stdev(axis1))
    print(statty.stdev(smooth2) / statty.stdev(axis2))
    print(statty.stdev(smooth3) / statty.stdev(axis3))


def plot_gyro_data(x, y, z, filename, result_directory):

    data_list = get_data(filename)

    axis1 = data_list[0]
    smooth1 = []
    cumsum1 = []
    rawsum1 = []
    axis2 = data_list[1]
    smooth2 = []
    cumsum2 = []
    rawsum2 = []
    axis3 = data_list[2]
    smooth3 = []
    cumsum3 = []
    rawsum3 = []

    prev = axis1[0]
    angle = 0
    rangle = 0
    for point in axis1:
        x, prev = simple_kalman(x, point, prev)
        angle += prev * .005
        rangle += point * .005
        smooth1.append(prev)
        cumsum1.append(angle)
        rawsum1.append(rangle)

    prev = axis2[0]
    angle = 0
    rangle = 0
    for point in axis2:
        y, prev = simple_kalman(y, point, prev)
        angle += prev * .005
        rangle += point * .005
        smooth2.append(prev)
        cumsum2.append(angle)
        rawsum2.append(rangle)

    prev = axis3[0]
    angle = 0
    rangle = 0
    for point in axis3:
        z, prev = simple_kalman(z, point, prev)
        angle += prev * .005
        rangle += point * .005
        smooth3.append(prev)
        cumsum3.append(angle)
        rawsum3.append(rangle)

    index = [float(x) for x in range(len(axis1))]

    plt.figure()
    plt.subplot(3, 2, 1)
    plt.plot(index, axis1)
    plt.plot(index, smooth1)
    plt.subplot(3, 2, 3)
    plt.plot(index, axis2)
    plt.plot(index, smooth2)
    plt.subplot(3, 2, 5)
    plt.plot(index, axis3)
    plt.plot(index, smooth3)

    # plot integral
    plt.subplot(3, 2, 2)
    plt.plot(index, rawsum1)
    plt.plot(index, cumsum1)
    plt.subplot(3, 2, 4)
    plt.yticks([x for x in range(0, 100, 10)])
    plt.plot(index, rawsum2)
    plt.plot(index, cumsum2)
    plt.subplot(3, 2, 6)
    plt.plot(index, rawsum3)
    plt.plot(index, cumsum3)

    figname = filename.replace("TXT", "png")
    plt.savefig(fname=figname)
    plt.close()

    figpath = os.path.abspath(figname)
    savepath = os.path.abspath(result_directory)
    shutil.move(figpath, savepath)


if __name__=="__main__":
    plt.close('all')

    data_folder = data_quick
    pics_folder = pics_quick

    datapath = os.path.join(os.getcwd(), data_folder)
    picspath = os.path.join(os.getcwd(), pics_folder)
    try:
        if os.path.exists(picspath):
            shutil.rmtree(pics_folder)
            os.mkdir(picspath)
    except FileNotFoundError:
        print("Directory doesn't exist")
        os.mkdir(picspath)
    except NotADirectoryError:
        print("Result path not a directory")
        os.remove(pics_folder)
        os.mkdir(picspath)

    files = os.listdir(datapath)
    gyro_files = [x for x in files if re.search(r"_G\d.", x) is not None]

    for file in gyro_files:
        print("generating figure for \"" + file + "\" in \"" + data_folder + "\"")
        file = os.path.join(datapath, file)
        #plot_smoothed_data(a, b, c, file, pics_folder)
        plot_gyro_data(a, b, c, file, pics_folder)
        a = [1, 1, q, r]
        b = [1, 1, q, r]
        c = [1, 1, q, r]
