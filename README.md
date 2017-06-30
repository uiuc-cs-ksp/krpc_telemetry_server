This project now contains multiple krpc-based telemetry servers in varying states of working. (Underlying technologies change.)

Dashboards themselves are absolutely beyond the scope of this project. (But see our other projects!)

openmct
_______
	[openmct](http://github.com/nasa/openmct)
	This project provides a telemetry server that connects a KSP game running kRPC to a NASA openmct console. It works by replecating the protocol used by the telemetry tutorial.

graphite
________
	[graphite](https://graphiteapp.org)
	This will be more about getting telemetry data into time-series databases, beginning with Graphite [link](https://graphiteapp.org).
	With good software engineering, we may be able to create some resusable components that support multiple such databases in a pluggable manner.
	
	Graphite : Very easy to setup/use. (But to be useful for KSP, you probably need to configure it for 1 second or lower time resolution, which is not the default.)
	Elasticsearch : Very flexable.
	OpenTSDB : Very fine grained.
