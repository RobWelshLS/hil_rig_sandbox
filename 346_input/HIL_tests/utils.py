from types import SimpleNamespace
import glob
import lscpgen
from ls_346 import dut

lscp_files = glob.glob('./*.lscp') + glob.glob('../*.lscp') + glob.glob('../../*.lscp')
lscp_enums = SimpleNamespace(**lscpgen.get_enums(*lscp_files))


def build_input_setup_settings(sensor_type=lscp_enums.SensorType.DIODE,
                               autorange=True,
                               range=0,  # diode range 2.5V
                               compensation=True,  # reversal
                               vi_toggle=True):  # broken lead checks
    return {
        'Sensor': sensor_type,
        'Autorange': autorange,
        'Range': range,
        'Compensation': compensation,
        'VI_toggle': vi_toggle
    }


def get_list_of_input_designators():
    list = []
    for x in lscp_enums.InputDes:
        list.append(x.name)
    list.pop()  # we don't want "LAST" enum member

    return list


def get_int_list_of_diode_ranges():
    list = []
    for p in lscp_enums.DiodeRange:
        list.append(p.value)

    list.pop()  # we don't want "LAST" enum member

    return list


def get_int_list_of_ptc_ranges():
    list = []
    for p in lscp_enums.PTCRange:
        list.append(p.value)

    list.pop()  # we don't want "LAST" enum member

    return list


def get_int_list_of_ntc_ranges():
    list = []
    for p in lscp_enums.NTCRange:
        list.append(p.value)

    list.pop()  # we don't want "LAST" enum member

    return list

def set_all_input_settings_to_default():
    inputSetup = build_input_setup_settings()
    list = get_list_of_input_designators()

    for inputDes in list:
        input_name = 'Input' + inputDes
        dut.issue_setting(input_name, inputSetup)


fake_input_settings = build_input_setup_settings(sensor_type=lscp_enums.SensorType.NTC_RTD,
                                                 autorange=False,
                                                 range=6,  # 6 = 100k
                                                 compensation=False,
                                                 vi_toggle=False)
