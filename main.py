import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from services.c3100 import C3100Device
from utils.utils import add_timestamp


instr = C3100Device()
instr.open()
time0 = time.time()
fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

xar1, yar1 = [], []

color1, color2 = 'blue', 'red'


def read_data(i, xar1, yar1):
    data = instr.get_data()
    if data:
        measure_time = time.time() - time0
        if len(data) == 2:
            print('{:5.3f},{},{}'.format(measure_time, *data))
            yar1.append(data[0])
            xar1.append(measure_time)
            with open(filename, 'a') as f:
                print('{:5.3f},{},{}'.format(measure_time, *data), file=f)

        elif len(data) == 4:
                print('{:5.3f},{},{},{},{}'.format(measure_time, *data))
                yar1.append(data[0])
                xar1.append(measure_time)
                # yar2.append(data[2])
                # xar2.append(measure_time)
                with open(filename, 'a') as f:
                    print('{:5.3f},{},{},{},{}'.format(measure_time, *data), file=f)

        ax1.plot(xar1, yar1, color=color1)


def read_data_test(i, xar1, yar1, xar2, yar2):
    option = np.random.randint(0, 2)
    measure_time = time.time() - time0
    if option == 0:
        value = np.random.random() * 10
        yar1.append(value)
        xar1.append(measure_time)
        print(value, measure_time)
    elif option == 1:
        value1 = np.random.random() * 10
        value2 = np.random.random() * 10
        yar1.append(value1)
        xar1.append(measure_time)
        yar2.append(value2)
        xar2.append(measure_time)
        print(value1, value2, measure_time)

    ax1.plot(xar1, yar1, color=color1)
    ax1.plot(xar2, yar2, color=color2)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = add_timestamp('c3100')

    time0 = time.time()
    ani = animation.FuncAnimation(fig, read_data, fargs=(xar1, yar1), interval=300)
    plt.show()

