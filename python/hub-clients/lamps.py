from collections import OrderedDict
from random import randint


class LampParam(object):
    def __init__(self, sn, seq):
        self.params = {
            "sn": sn,
            "sequence": seq,
            "status": 1,
            "type": 1,
            "is_repeated": 0,
            "rf_band": 427,
            "rf_addr": 11,
            "address": "上海浦东",
            "longitude": 121.529129,
            "latitude": 31.223868,
            "memo": "",
            "registered_time": "2019-08-26"
        }


class SolarParam(object):
    params = {
            "model": 0,
            "max_power": 7,
            "acc_time": 0,
            "acc_over_discharge_count": 0,
            "time_section1": 48,
            "current1": 7,
            "section2": 0,
            "current2": 1,
            "section3": 0,
            "current3": 0,
            "control": 1,
            "adv_settings": 1,
            "load_control_mode": 2,
            "lux_control_delay": 1,
            "lux_control_voltage": 50,
            "battery_type": 1,
            "supercharge_voltage": 170,
            "overdischarge_voltage": 110,
            "dischargeback_voltage": 130,
            "lift_voltage": 148,
            "float_voltage": 136,
            "power_priority": 0,
            "section4": 0,
            "current4": 0,
            "section5": 0,
            "current5": 0,
            "section6": 0,
            "current6": 0,
            "voltage_level": 1,
            "charge_voltage": 145,
            "charget_current": 100,
            "charge_end_current": 5,
            "protocol_version": 33,
            "charge_hightemp_protection": 100,
            "charge_lowtemp_protection": 0,
            "discharge_hightemp_protection": 100,
            "discharge_lowtemp_protection": 0,
            "sensor_power": 254,
            "sensor_delay_start": 255,
            "sensor_delay_start_time": 0,
            "sensor_delay_end_time": 3
        }

    __status = OrderedDict({
        "lastday_discharge_energy_H": 9,
        "solar_voltage_L": 6,
        "date": "2019-08-26 12:31:58",
        "under_voltage_L": 8,
        "reserved5": 1,
        "acc_discharge_energy_H": 7,
        "reserved2": 9,
        "today_discharge_energy_H": 8,
        "acc_discharge_energy_L": 3,
        "reserved7": 9,
        "today_discharge_energy_L": 2,
        "load_status": 2,
        "over_discharge_H": 5,
        "days_H": 9,
        "reserved6": 7,
        "reserved3": 8,
        "load_voltage_H": 5,
        "solar_status": 10,
        "solar_current_L": 3,
        "battery_voltage_L": 5,
        "today_charge_energy_L": 9,
        "battery_energy_left": 8,
        "battery_energy_L": 1,
        "lastday_charge_energy_H": 7,
        "reserved4": 3,
        "lastday_discharge_energy_L": 5,
        "load_current_H": 2,
        "inner_temperature": 4,
        "solar_voltage_H": 8,
        "days_L": 5,
        "today_charge_energy_H": 1,
        "overdischarge_times": 4,
        "outer_temperature": 2,
        "over_discharge_L": 5,
        "reserved1": 1,
        "load_current_L": 9,
        "battery_state": 4,
        "battery_voltage_H": 9,
        "acc_charge_energy_H": 4,
        "battery_energy_H": 1,
        "acc_under_voltage": 3,
        "reserved8": 3,
        "under_voltage_H": 4,
        "lastday_charge_energy_L": 2,
        "acc_charge_energy_L": 1,
        "solar_current_H": 2,
        "load_voltage_L": 7
    })

    @classmethod
    def get_status(cls):
        data = [randint(1, 10) for _ in range(len(cls.__status.keys()))]
        start_idx = 0
        for k in cls.__status.keys():
            cls.__status[k] = data[start_idx]
            start_idx += 1
        return cls.__status


class BaseLamp(object):
    def __init__(self, sn, seq):
        self.sn = sn
        self.seq = seq

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.sn == other.sn
        return False

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return "<Lamp: %s>" % self.sn


class Lamp(BaseLamp):
    @property
    def serializer_data(self):
        _data = LampParam(sn=self.sn, seq=self.seq).params
        _data.update(SolarParam.params)
        return _data
