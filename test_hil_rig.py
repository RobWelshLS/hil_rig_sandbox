from time import sleep
from enum import IntEnum
import pytest
from hil_test_rig import HILTestRig, HILTestCase

rig = HILTestRig()


@pytest.fixture()
def clear_rig():
    rig.load_bank.clear()
    rig.shorts.clear()
    rig.crossbar.clear()
    rig.voltage_source.clear()
    yield
    rig.load_bank.clear()
    rig.shorts.clear()
    rig.crossbar.clear()
    rig.voltage_source.clear()


# Set test variables
standard_settle_time = 1
voltage_gain_error_spec = 0.03  # %
voltage_offset_spec = 0.05  # V
resistance_gain_error_spec = 0.03  # v
resistance_offset_spec = 5  # Ω


# Use IntEnum to connect DMM to dut 10
class dmm_connection(IntEnum):
    front_in = 10


@pytest.mark.usefixtures("clear_rig")
class TestHilRig(HILTestCase):
    def test_voltage_loop_back(self):
        """Test both voltage inputs over a range of voltages on Row B"""
        test_voltages = [-10, -5, 0, 5, 10]
        for channel in range(2):
            for voltage in test_voltages:
                # Connect the DMM, voltage source, and voltage input to Row B
                rig.crossbar.connect([], [dmm_connection.front_in, rig.voltage_source,
                                          rig.voltage_input[channel]])
                rig.voltage_source.apply_dc(voltage)
                sleep(standard_settle_time)
                measured_voltage = rig.voltage_input[channel].measure_dc()
                self.assertWithinSpec(measured_voltage, voltage,
                                      gain_spec=voltage_offset_spec, offset_spec=voltage_offset_spec)

    def test_1K_resistor(self):
        """Test the 1K resistor measurement"""
        # Connect the DMM, resistor load bank, voltage source, and voltage input to Row D
        rig.crossbar.connect([], [], [], [dmm_connection.front_in, rig.load_bank, rig.current_source,
                                          rig.voltage_input[0]])
        load = 1E3
        rig.load_bank.apply(load)
        excitation_current = 0.005
        sleep(standard_settle_time)
        measured_resistance = rig.measure_resistance(excitation_current=excitation_current,
                                                     settle_time=standard_settle_time)
        self.assertWithinSpec(measured_resistance, load, gain_spec=resistance_gain_error_spec,
                              offset_spec=resistance_offset_spec)

    def test_short(self):
        """Short the dut port the dmm is connected to and measure resistance. Use Row A"""
        rig.crossbar.connect([dmm_connection.front_in, rig.current_source, rig.voltage_input[0]])
        rig.shorts.close(dmm_connection.front_in)
        sleep(standard_settle_time)
        measured_resistance = rig.measure_resistance(excitation_current=0.010, settle_time=standard_settle_time)
        self.assertWithinSpec(measured_resistance, 0, gain_spec=0,
                              offset_spec=resistance_offset_spec)
