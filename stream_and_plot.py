from time import sleep
from enum import IntEnum
from matplotlib import pyplot
from hil_test_rig import HILTestRig, HILTestCase

rig = HILTestRig()


# Use IntEnum to connect DMM to dut 10
class dmm_connection(IntEnum):
    front_in = 10


def plot_sine_wave():
    rig.crossbar.connect([rig.voltage_source, rig.voltage_input[0]])
    rig.voltage_source.apply_sin(frequency=10E3, amplitude=5)  # 10 Khz sine wave at 5V peak
    sleep(1)

    data = rig.voltage_input[0].get_points(500, 1E6)  # 500 points at 1 MSa/s - results in 5 cycles, returned as list.

    pyplot.plot(data)
    pyplot.show()


def clear_rig():
    rig.load_bank.clear()
    rig.shorts.clear()
    rig.crossbar.clear()
    rig.voltage_source.clear()

plot_sine_wave()
clear_rig()
