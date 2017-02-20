import krpc
import json
import time
from collections import OrderedDict, defaultdict

import threading

class TelemJSONifiable(object):
	def __init__(self,name,ident,children_name=None,other_params=None):
		self.name = name
		self.id = ident
		self.other_params = other_params
		self.children_name = children_name
		self.children = list()
		self.children_dict = OrderedDict()
		self.vessel = None
		self.parent = None

	def set_vessel(self, in_vess):
		self.vessel = in_vess
		for i in self.children_dict.values():
			i.set_vessel(in_vess)

	def add_child(self, in_child):
		self.children.append(in_child)
		self.children_dict[in_child.id] = in_child
		in_child.set_vessel(self.vessel)
		in_child.parent = self

	def get_json(self,running_identifier=None):

		if running_identifier is None:
			running_identifier = self.id
		else:
			running_identifier = running_identifier + "." + self.id



		return_dictionary = OrderedDict([("name",self.name),("identifier",running_identifier)])
		if self.other_params is not None:
			return_dictionary.update(self.other_params)
		if self.children_name is not None:
			return_dictionary[self.children_name] = [i.get_json(running_identifier=running_identifier) for i in self.children_dict.values()]
		return return_dictionary

class TelemetryMeasurement(TelemJSONifiable):
	def __init__(self,name,identifier,units,in_d_type,the_function):
		super(TelemetryMeasurement,self).__init__(name,identifier,other_params=[("units",units),("type",in_d_type)])
		self.units = units
		self.d_type = in_d_type
		self.mfunc = the_function

	def get_value(self):
		return self.mfunc(self.vessel)

class TelemetrySubsystem(TelemJSONifiable):
	def __init__(self,in_name,in_identifier):
		super(TelemetrySubsystem,self).__init__(in_name,in_identifier,children_name="measurements")
		#self.name = in_name
		#self.id = in_identifier


class TelemetryShip(TelemJSONifiable):
	def __init__(self, the_conn, the_vessel):
		super(TelemetryShip,self).__init__("Example Spacecraft","sc",children_name="subsystems")
		self.conn = the_conn
		self.vessel = the_vessel

	def get_value(self,ident):
		ship_id,subsys_id,measure_id = ident.split(".")
		return self.children_dict[subsys_id].children_dict[measure_id].get_value()

	def get_json_str(self):
		return json.dumps(self.get_json(),indent=5)


class TelemetryShipFactory(object):
	def __init__(self):
		self.name = "blah"

	def create_ship(self, a_connection):
		new_ship = TelemetryShip(a_connection, a_connection.space_center.active_vessel)

		#resources
		r_systems = TelemetrySubsystem("Resources","resou")
		total_e = TelemetryMeasurement("ElectricCharge","echarge","kwh","float",lambda x: x.resources.amount("ElectricCharge"))
		r_systems.add_child(total_e)

		total_f = TelemetryMeasurement("Fuel","fuel","liters","float",lambda x: x.resources.amount("LiquidFuel"))
		r_systems.add_child(total_f)

		total_ox = TelemetryMeasurement("Oxidizer","oxy","liters","float",lambda x:x.resources.amount("Oxidizer"))
		r_systems.add_child(total_ox)

		total_mono = TelemetryMeasurement("Monopropellant","mono","liters","float",lambda x:x.resources.amount("Monopropellant"))
		r_systems.add_child(total_mono)

		total_ore = TelemetryMeasurement("Ore","ore","kilograms","float",lambda x:x.resources.amount("Ore"))
		r_systems.add_child(total_ore)

		new_ship.add_child(r_systems)



		return new_ship

class TelemetryController(threading.Thread):
	def __init__(self, a_ship, interval=1):
		super(TelemetryController,self).__init__(group=None, target=None, name=None, args=(), kwargs={})
		self.a_ship = a_ship
		self.interval=interval
		self.listeners = list()
		self.history = defaultdict(list)
		self.record_all_in_history()
		print("created a telemetry controller")

	def run(self):
		print("started thread")
		while True:
			self.record_all_in_history()
			self.notify_listeners()
			time.sleep(self.interval)

	def record_all_in_history(self):
		for subsys in self.a_ship.children_dict.values():
			for one_measurement in subsys.children_dict.values():
				measurement_name = ".".join([self.a_ship.id,subsys.id,one_measurement.id])
				self.history[measurement_name].append((self.a_ship.vessel.met*1000, one_measurement.get_value()))

	def add_listener(self,other):
		if not other in self.listeners:
			self.listeners.append(other)

	def remove_listener(self,other):
		if other in self.listeners:
			self.listeners.remove(other)

	def notify_listeners(self):
		for i in self.listeners:
			i.new_telemetry()


if __name__ == "__main__":
	conn = krpc.connect(address="localhost",name="telemetry_monitor")

	a_telem_fact = TelemetryShipFactory()
	a_ship = a_telem_fact.create_ship(conn)


	print json.dumps(a_ship.get_json(),indent=5)

	t_control = TelemetryController(a_ship)
	t_control.start()

	#conn.close()
