from lamps import Lamp
from tools import cached_property


class HubParam(object):
    def __init__(self, hid):
        self.params = {
            "sn": hid,
            "status": 1,
            "rf_band": 427,
            "rf_addr": 0,
            "address": "浦东新区",
            "longitude": 119,
            "latitude": 22,
            "unit": "",
            "memo": "备注",
            "registered_time": "2019-05-15"
        }


class BaseHub(object):
    def __init__(self, hid, lamp_ids):
        self.hid = hid
        self.lamp_ids = lamp_ids

    @cached_property
    def lamps(self):
        _lamps = []
        for lamp_id, seq in self.lamp_ids.items():
            _lamps.append(Lamp(lamp_id, seq))
        return _lamps

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.hid == other.hid
        return False

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return "<Hub: %s>" % self.hid


class Hub(BaseHub):
    @property
    def serializer_data(self):
        _data = HubParam(self.hid).params
        _data["version"] = "7.0-748"
        return _data
