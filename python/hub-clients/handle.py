from lamps import SolarParam
from random import randint, random
from twisted.internet.task import LoopingCall


class Handle(object):
    def __init__(self):
        self.body = {}

    def _clean_body(self, empty=False):
        self.body = {
            "action": "",
            "code": 0,
            "data": {}
        }
        if not empty:
            self.body["data"] = {
                "hub": {},
                "lamps": {}
            }

    def register(self, hub):
        self._clean_body()
        self.body["action"] = "register"
        self.body["data"] = {
            "default_group": {},
            "hub": hub.serializer_data,
            "lamps": {}
        }
        for lamp in hub.lamps:
            self.body["data"]["lamps"][lamp.sn] = lamp.serializer_data
        return self.body

    def report_status(self, hub):
        self._clean_body()
        self.body["action"] = "report_status"
        self.body["data"]["hub"][hub.hid] = {
            "A_voltage": 0,
            "A_current": 0,
            "A_consumption": 0,
            "B_voltage": 0,
            "B_current": 0,
            "B_consumption": 0,
            "C_voltage": 0,
            "C_current": 0,
            "C_consumption": 0,
            "consumption": 0
        }
        for lamp in hub.lamps:
            self.body["data"]["lamps"][lamp.sn] = {
                "brightness": [randint(0, 255), randint(0, 255)],
                "solar_status": SolarParam.get_status()
            }

        print(f"上报全量数据: {self.body}")
        return self.body

    def report_weather_data(self):
        self._clean_body(empty=True)
        self.body["action"] = "report_weather_data"
        self.body["data"] = {
            "temperature": round(random() * 20, 2),
            "humidity": round(random() * 20, 2),
            "noise": round(random() * 20, 2),
            "pm2_5": round(random() * 20, 2),
            "pm10": round(random() * 20, 2),
            "air_pressure": round(random() * 20, 2),
            "illuminance": randint(200, 1000)
        }
        return self.body


class ProtocolTaskMixin(object):
    __tasks = {
        "report_status": 20,
        "report_weather_data": 10,
        "send_heartbeat": 5
    }

    def get_tasks(self):
        return self.__tasks


class IntervalMixin(object):
    def start_interval_tasks(self):
        tasks = self.p.get_tasks()
        for name in tasks.keys():
            if hasattr(self.p, name):
                t = LoopingCall(getattr(self.p, name))
                t.start(tasks[name], now=False)
