import krpc
import json
import time
from collections import OrderedDict, defaultdict

import threading

class TelemetryController(threading.Thread):
    def __init__(self, a_ship, a_graphite, in_telems, interval=1):
    	super(TelemetryController,self).__init__(group=None, target=None, name=None, args=(), kwargs={})
        self.vessel = a_ship
        self.g = a_graphite
        self.telemetries = in_telems
        self.interval = interval
        print("created a telemetry controller")

    def run(self):
    	print("started thread")
    	while True:
    		self.read_and_forward()
    		time.sleep(self.interval)

    def read_and_forward(self):
        #cur_game_time = self.vessel.met*1000
    	for one_telem_name, one_telem_callback in self.telemetries:
    		self.g.send(one_telem_name,one_telem_callback(self.vessel))
        print "forwarded"

import graphitesend
if __name__ == "__main__":
    #GRAPHITE
    g = graphitesend.init(graphite_server="192.168.254.100",system_name="active_vessel",prefix="ksp")

    #KRPC
    conn = krpc.connect(address="localhost",name="telemetry_monitor")

    list_o_telems = [
        ("resource.ElectricCharge",lambda x: x.resources.amount("ElectricCharge")),
        ("resource.LiquidFuel",lambda x: x.resources.amount("LiquidFuel")),
        ("resource.Oxidizer",lambda x:x.resources.amount("Oxidizer")),
        ("resource.Monopropellant",lambda x:x.resources.amount("Monopropellant")),
        ("resource.Ablator",lambda x:x.resources.amount("Ablator")),
        ("resource.Ore",lambda x:x.resources.amount("Ore")),
        ("physics.thrust",lambda x:x.thrust)
    ]

    t_control = TelemetryController(conn.space_center.active_vessel,g, list_o_telems)
    t_control.start()

    #conn.close()
