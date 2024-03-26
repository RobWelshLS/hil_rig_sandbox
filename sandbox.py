from time import sleep
from enum import IntEnum
from hil_test_rig import HILTestRig, HILTestCase

rig = HILTestRig()


standard_settle_time = 1
voltage_gain_error_spec = 0.03
voltage_offset_spec = 0.05  # V
resistance_gain_error_spec = 0.03
resistance_offset_spec = 5  # Ω


def tearDownModule():
    # Runs after all tests in the module
    print('\nRunning tearDownModule...')
    rig.crossbar.clear()
    rig.shorts.clear()
    rig.load_bank.clear()
    rig.voltage_source.clear()


# Use IntEnum to connect DMM to DUT 1
class dmm_connection(IntEnum):
    front_in = 1


class TestSwitches(HILTestCase):
    def setUp(self):
        # Runs before each test in the class
        print('\nRunning setUp...')
        rig.crossbar.clear()
        rig.shorts.clear()
        rig.load_bank.clear()
        rig.voltage_source.clear()

    def test_crossbar_continuity(self):
        test_voltage = 1
        rig.voltage_source.apply_dc(test_voltage)

        for dut_port in range(1, 13):
            for other_row in range(1, 4):
                nets = [[]] * 4
                nets[0] = [dut_port, rig.voltage_source]
                nets[other_row] = [dut_port, rig.voltage_input[0]]
                rig.crossbar.connect(*nets)
                sleep(standard_settle_time)

                measured_voltage = rig.voltage_input[0].measure_dc()

                self.assertWithinSpec(measured_voltage, test_voltage,
                                      gain_spec=voltage_gain_error_spec,
                                      offset_spec=voltage_offset_spec)

    def test_shorts(self):
        for dut_port in range(1, 13):
            rig.shorts.clear()
            rig.crossbar.connect([dut_port, rig.current_source, rig.voltage_input[0]])
            rig.shorts.close(dut_port)
            sleep(standard_settle_time)

            measured_resistance = rig.measure_resistance(excitation_current=0.01)

            self.assertWithinSpec(measured_resistance, 0, gain_spec=0, offset_spec=resistance_offset_spec)


# #  board_loads = [0, 1, 3.01, 10, 30.1, 100, 301, 1E3, 3.01E3, 10E3, 30.1E3, 100E3]
#
# def simple_resistor_test():
#     """Test the selected resistor with a DMM connected to DUT 1"""
#     rig.crossbar.connect([1, rig.load_bank])
#     load = 100E3  # Select resistor to measure
#     rig.load_bank.apply(load)
#     sleep(10)




