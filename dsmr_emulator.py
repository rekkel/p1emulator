import time
from datetime import datetime, timedelta
import struct
import crcmod.predefined
crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')
import socket
import os.path

SOCKET = "dsmr.sock"
if os.path.exists(SOCKET):
    os.remove(SOCKET)

# Do not convert line endings to LF in this file!

class DSMREmulator:

    def __init__(self, name="DSMRGenerator", ):
        self.name = name

    @property
    def _dsmr_version(self):
        return str(int(self.dsmr_version))[0:2]

    @property
    def _timestamp(self):
        if self.timestamp.tzname() == "CET":
            return f"{self.timestamp:%y%m%d%H%M%SW}"
        elif self.timestamp.tzname() == "CEST":
            return f"{self.timestamp:%y%m%d%H%M%SS}"

    @property
    def _identifier(self):
        return str(self.identifier)[:34]

    @property
    def _power_failure_log(self):
        return str(self.num_long_power_failures)[0:74]

    @property
    def _num_voltage_sags_l1(self):
        return f"{self.num_voltage_sags_l1:05d}"

    @property
    def _num_voltage_sags_l2(self):
        return f"{self.num_voltage_sags_l2:05d}"

    @property
    def _num_voltage_sags_l3(self):
        return f"{self.num_voltage_sags_l3:05d}"

    @property
    def _num_voltage_swells_l1(self):
        return f"{self.num_voltage_swells_l1:05d}"

    @property
    def _num_voltage_swells_l2(self):
        return f"{self.num_voltage_swells_l2:05d}"

    @property
    def _num_voltage_swells_l3(self):
        return f"{self.num_voltage_swells_l3:05d}"

    @property
    def _text_message(self):
        return str(self.text_message.encode('ascii').hex())

    @property
    def _mbus_device_type(self):
        return str(self.mbus_device_type)[0:3]

    @property
    def _mbus_equipment_id(self):
        return f"{self.mbus_equipment_id:034d}"

    @property
    def _five_min_gas_reading(self):
        return str(self.five_min_gas_reading)[0:39]

    @property
    def _telegram(self):
        return "\r\n".join([f"/{self.name}",
                            f"",
                            f"1-3:0.2.8({self._dsmr_version})",
                            f"0-0:1.0.0({self._timestamp})",
                            f"0-0:96.1.1({self._identifier})",
                            f"1-0:1.8.1({self.energy_import_t1:010.3f}*kWh)",
                            f"1-0:1.8.2({self.energy_import_t2:010.3f}*kWh)",
                            f"1-0:2.8.1({self.energy_export_t1:010.3f}*kWh)",
                            f"1-0:2.8.2({self.energy_export_t2:010.3f}*kWh)",
                            f"0-0:96.14.0({self.tariff_indicator:04d})",
                            f"1-0:1.7.0({self.power_import:06.3f}*kW)",
                            f"1-0:2.7.0({self.power_export:06.3f}*kW)",
                            f"0-0:96.7.21({self.num_power_failures:05d})",
                            f"0-0:96.7.9({self.num_long_power_failures:05d})",
                            f"1-0:99.97.0({self._power_failure_log})",
                            f"1-0:32.32.0({self._num_voltage_sags_l1})",
                            f"1-0:52.32.0({self._num_voltage_sags_l2})",
                            f"1-0:72.32.0({self._num_voltage_sags_l3})",
                            f"1-0:32.36.0({self._num_voltage_swells_l1})",
                            f"1-0:52.36.0({self._num_voltage_swells_l2})",
                            f"1-0:72.36.0({self._num_voltage_swells_l3})",
                            f"0-0:96.13.0({self._text_message})",
                            f"1-0:32.7.0({self.voltage_l1:05.1f}*V)",
                            f"1-0:52.7.0({self.voltage_l2:05.1f}*V)",
                            f"1-0:72.7.0({self.voltage_l2:05.1f}*V)",
                            f"1-0:31.7.0({self.current_l1:03.0f}*A)",
                            f"1-0:51.7.0({self.current_l2:03.0f}*A)",
                            f"1-0:71.7.0({self.current_l3:03.0f}*A)",
                            f"1-0:21.7.0({self.power_import_l1:06.3f}*kW)",
                            f"1-0:41.7.0({self.power_import_l2:06.3f}*kW)",
                            f"1-0:61.7.0({self.power_import_l3:06.3f}*kW)",
                            f"1-0:22.7.0({self.power_export_l1:06.3f}*kW)",
                            f"1-0:42.7.0({self.power_export_l2:06.3f}*kW)",
                            f"1-0:62.7.0({self.power_export_l3:06.3f}*kW)",
                            f"0-1:24.1.0({self._mbus_device_type})",
                            f"0-1:96.1.0({self._mbus_equipment_id})",
                            f"0-1:24.2.1(181106140010W)({self._five_min_gas_reading}*m3)",
                            "!"]).encode('ascii')

    @property
    def telegram(self):
        """
        Return a complete DSMR telegram.
        """
        t = self._telegram
        print(t)
        crc = struct.pack(">H", crc16(t))
        return t.decode('ascii') + crc.hex().upper() + '\r\n'


def encode_dsmr_timestamp(ts):
    encoded = ts.strftime("%y%m%d%H%M%S")
    if ts.tzname() == "CEST":
        encoded += "S"
    elif ts.tzname() == "CET":
        encoded += "W"
    return encoded


def main():
    d = DSMREmulator()
    message = """{"Header":{"Action":"EBGDirectControl","ValidFrom":"191010120000S","ValidTo":"191010121500S"},"Body":{"Periods":[{"Start":"191010115900S","MxPwr":200},{"Start":"191010120100S","MxPwr":110,"MxPhaseImbal":200,"MxPwrFallbck":600,"SetPointFallbck":80,"RefreshInterv":20},{"Start":"191010120130S","LoadReduct":80},{"Start":"191010120140S","MxPwr":1000,"MxPwrFallbck":800},{"Start":"191010120300S","MxPhaseImbal":400,"MxPwr":150},{"Start":"191010120340S","LoadReduct":99},{"Start":"191010120500S","LoadReduct":100},{"Start":"191010120600S","RefreshInterv":60,"MxPwrFallbck":110}]}}"""
    now = datetime(2019,10,10,11,59,30).astimezone()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(SOCKET)
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            while True:
                now += timedelta(seconds=10)
                d.name = "SLIMMEMETER5.0"
                d.identifier = 123456
                d.dsmr_version = 50
                d.timestamp = now
                d.energy_import_t1 = 0
                d.energy_import_t2 = 0
                d.energy_export_t1 = 0
                d.energy_export_t2 = 0
                d.tariff_indicator = 1
                d.power_import = 0.23
                d.power_export = 0
                d.num_power_failures = 8
                d.num_long_power_failures = 2
                d.power_failure_log = "2"
                d.num_voltage_sags_l1 = 1
                d.num_voltage_sags_l2 = 1
                d.num_voltage_sags_l3 = 2
                d.num_voltage_swells_l1 = 0
                d.num_voltage_swells_l2 = 0
                d.num_voltage_swells_l3 = 0
                d.text_message = message
                d.voltage_l1 = 230.1
                d.voltage_l2 = 229.8
                d.voltage_l3 = 231.3
                d.current_l1 = 12.1
                d.current_l2 = 0.5
                d.current_l3 = 0
                d.power_import_l1 = 0
                d.power_import_l2 = 0
                d.power_import_l3 = 0
                d.power_export_l1 = 0
                d.power_export_l2 = 0
                d.power_export_l3 = 0
                d.mbus_device_type = "003"
                d.mbus_equipment_id = 3232323241424344313233343536373839
                d.five_min_gas_reading = "12785.123"
                print(f"It is now {now}")
                print(d.telegram)
                conn.sendall(d.telegram.encode('ascii'))
                time.sleep(10)


if __name__ == "__main__":
    main()
