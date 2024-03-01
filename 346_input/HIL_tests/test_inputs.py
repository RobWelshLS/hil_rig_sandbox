import msvcrt
import unittest
import logging
from copy import deepcopy

from ls_346 import dut
from utils import build_input_setup_settings, lscp_enums, set_all_input_settings_to_default, fake_input_settings, \
    get_list_of_input_designators, get_int_list_of_diode_ranges, get_int_list_of_ptc_ranges, get_int_list_of_ntc_ranges

from hil_test_rig import HILTestCase
#logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S', level=logging.DEBUG)

#  def setUpModule():
    # dut.issue_command('CalClear')
    # dut.issue_command('RestoreFactorySelfCal')
    # dut.issue_command('Start')

# The following class is simply to verify settings are received and validated properly.
# Separate tests are present to check the settings are applied propertly to the hardware
class TestInputSettings(unittest.TestCase):

    # setUp gets run before each test, that's defined within this class, executes
    # def setUp(self):
        # set_all_input_settings_to_default()

    # simply make sure the ettings response confirmation for each input setup, matches what we send down
    def test_setting_and_response(self):
        #self.assertEqual(1,1)
        list = get_list_of_input_designators()

        for inputDes in list:
            input_name = 'Input' + inputDes
            response = dut.issue_setting(input_name, fake_input_settings)
            self.assertEqual(response, fake_input_settings)

    def test_sensor_type_limit_high(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = 9     # non valid enum for sensor type

        for inputDes in list:
            input_name = 'Input' + inputDes
            response = dut.issue_setting(input_name, test_settings)
            # verify fw didn't accept 9 and kept sensor type at previous value, which is '1' = DIODE
            self.assertEqual(response['Sensor'], lscp_enums.SensorType.DIODE)


    def test_diode_range(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.DIODE
        range_list = get_int_list_of_diode_ranges()

        for inputDes in list:
            input_name = 'Input' + inputDes
            for ranges in range_list:
                test_settings['Range'] = ranges
                response = dut.issue_setting(input_name, test_settings)
                self.assertEqual(response, test_settings)


    def test_diode_range_out_of_bounds(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.DIODE
        test_settings['Range'] = -30

        for inputDes in list:
            input_name = 'Input' + inputDes
            response = dut.issue_setting(input_name, test_settings)
            # -30 is not valid range for diode, verify code kept it at previous value, which is r2pt5
            self.assertEqual(response['Range'], lscp_enums.DiodeRange.r2pt5)


    def test_ptc_ranges(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.PLAT_RTD
        range_list = get_int_list_of_ptc_ranges()

        for inputDes in list:
            input_name = 'Input' + inputDes
            for ranges in range_list:
                test_settings['Range'] = ranges
                response = dut.issue_setting(input_name, test_settings)
                self.assertEqual(response, test_settings)


    def test_ptc_range_out_of_bounds(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.PLAT_RTD
        test_settings['Range'] = 24

        for inputDes in list:
            input_name = 'Input' + inputDes
            response = dut.issue_setting(input_name, test_settings)
            self.assertEqual(response['Range'], lscp_enums.PTCRange.r10)


    def test_ntc_ranges(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.NTC_RTD
        range_list = get_int_list_of_ntc_ranges()

        for inputDes in list:
            input_name = 'Input' + inputDes
            for ranges in range_list:
                test_settings['Range'] = ranges
                response = dut.issue_setting(input_name, test_settings)
                self.assertEqual(response, test_settings)


    def test_ntc_range_out_of_bounds(self):
        list = get_list_of_input_designators()
        test_settings = fake_input_settings.copy()
        test_settings['Sensor'] = lscp_enums.SensorType.NTC_RTD
        test_settings['Range'] = lscp_enums.NTCRange.LAST

        for inputDes in list:
            input_name = 'Input' + inputDes
            response = dut.issue_setting(input_name, test_settings)
            self.assertEqual(response['Range'], lscp_enums.NTCRange.r100)