from time import sleep
from enum import IntEnum
from hil_test_rig import HILTestRig, HILTestCase

#  Modified self_test to add additional test setup, test all switches except for UR13-UR16 (which are not
#  used), and all resistors.

rig = HILTestRig()


standard_settle_time = 1
voltage_gain_error_spec = 0.03
voltage_offset_spec = 0.05  # V
resistance_gain_error_spec = 0.03
resistance_offset_spec = 5  # Ω


class ohmmeter_connection(IntEnum):
    ohmmeter = 1


def setUpModule():
    rig.voltage_source.clear()
    rig.crossbar.clear()
    rig.shorts.clear()
    rig.load_bank.clear()


def tearDownModule():
    rig.voltage_source.clear()
    rig.crossbar.clear()
    rig.shorts.clear()
    rig.load_bank.clear()


class TestVoltageLoopBack(HILTestCase):
    def test_voltage_loop_back(self):
        """Tests a range of voltages output from the voltage source and measured on both voltage inputs.
        Tests repeated on all rows. Switches tested: A13-A15, B13-B15, C13-C15, D13-D15"""
        for channel in range(2):
            for row in range(4):
                nets = [[]] * 4
                nets[row] = [rig.voltage_source, rig.voltage_input[channel]]
                for test_voltage in [-10, -1, 0, 1, 10]:
                    rig.crossbar.connect(*nets)
                    rig.voltage_source.apply_dc(test_voltage)
                    sleep(standard_settle_time)

                    measured_voltage = rig.voltage_input[channel].measure_dc()

                    self.assertWithinSpec(measured_voltage, test_voltage,
                                          gain_spec=voltage_gain_error_spec,
                                          offset_spec=voltage_offset_spec)


class TestLoads(HILTestCase):
    def test_low_resistance_loads(self):
        """Measure test loads less than 10 KOhm using the onboard resistance measure function. Tests repeated
        on all rows. Switches tested: A13, A16, A17, B13, B16, B17, C13, C16, C17, D13, D16, D17, UR1-UR9"""
        for row in range(4):
            nets = [[]] * 4
            nets[row] = [rig.load_bank, rig.current_source, rig.voltage_input[0]]
            rig.crossbar.connect(*nets)

            for load in rig.load_bank.available_loads:
                if load < 10000:  # Higher resistances cannot reliably be measured
                    rig.load_bank.apply(load)

                    excitation_current = min(0.01, 5 / (load + 1))  # Compute a reasonable excitation current for this load

                    measured_resistance = rig.measure_resistance(excitation_current=excitation_current, settle_time=standard_settle_time)

                    self.assertWithinSpec(measured_resistance, load,
                                          gain_spec=resistance_gain_error_spec,
                                          offset_spec=resistance_offset_spec)

    def test_high_resistance_loads(self):
        """Measure test loads 10 KOhm and up using an external ohmmeter. This is a manual test that requires the
         operator to enter the resistance value. Switches tested: A1, A17, UR10-UR12"""

        input('\n\nAttach an ohmmeter to DUT 1 then press Enter... ')
        rig.crossbar.connect([ohmmeter_connection.ohmmeter, rig.load_bank])

        for load in rig.load_bank.available_loads:
            if load >= 10000:
                rig.load_bank.apply(load)

                measured_resistance = float(input('\nEnter the measured resistance value: '))

                self.assertWithinSpec(measured_resistance, load,
                                      gain_spec=resistance_gain_error_spec,
                                      offset_spec=resistance_offset_spec)

        input('\nDisconnect the ohmmeter from DUT 1 then press Enter... ')


class TestSwitches(HILTestCase):
    def test_crossbar_continuity(self):
        """For each row on page 1 of the schematics, connect the voltage source to Row A and measure the test voltage
        on Rows B-D. Repeat for each column. Switches tested: UA1-UA12, UB1-UB12, UC1-UC12, UD1-UD12, UA13, UA15,
        UB13, UC13, UD13"""
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
        """Connect Row A, Switch 1 and DUT 1 short to the current source and voltage input. Verify short switch.
        Repeat for each column. Switches tested: UA1-UA12, U101-U112, UA13, UA16"""
        for dut_port in range(1, 13):
            rig.shorts.clear()
            rig.crossbar.connect([dut_port, rig.current_source, rig.voltage_input[0]])
            rig.shorts.close(dut_port)
            sleep(standard_settle_time)

            measured_resistance = rig.measure_resistance(excitation_current=0.01)

            self.assertWithinSpec(measured_resistance, 0, gain_spec=0, offset_spec=resistance_offset_spec)
