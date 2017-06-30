###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
#
#File originally from https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo
#


import sys

import json

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource

import krpc
from watch_spacecraft import *

import threading
import time


from collections import OrderedDict, defaultdict

class TelemetryServerFactory(WebSocketServerFactory):

    def __init__(self, uri, krpc_conn, krpc_ship):
        WebSocketServerFactory.__init__(self, uri)
        self.krpc_conn = krpc_conn
        self.krpc_ship = krpc_ship
        self.t_control = TelemetryController(krpc_ship)
        self.t_control.start()

class TelemetryServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        super(TelemetryServerProtocol,self).__init__()
        self.subscriptions = list()

    def onConnect(self, request):
        self.factory.t_control.add_listener(self)
        print("WebSocket connection request: {}".format(request))

    def onMessage(self, payload, isBinary):
        #TODO: dispatch to appropriate handler
        s = payload.decode('utf8')
        contents = s.split(" ")
        print("got a message", contents)
        if contents[0] == "dictionary":
            self.sendMessage(bytes("""{ "type":"dictionary", "value":%s}"""%(self.factory.krpc_ship.get_json_str())),False)
            return
        elif contents[0] == "subscribe":
            if not contents[1] in self.subscriptions:
                self.subscriptions.append(contents[1])
            return
        elif contents[0] == "unsubscribe":
            if contents[1] in self.subscriptions:
                self.subscriptions.remove(contents[1])
            return
        elif contents[0] == "history":
            the_hist = self.factory.t_control.history[contents[1]]
            history_json_obj = OrderedDict([("type","history"),("id",contents[1]),("value",[{"timestamp":int(i),"value":j} for i,j in the_hist])])
            history_json_str = json.dumps(history_json_obj)
            print("returning",history_json_str)
            self.sendMessage(bytes(history_json_str),False)
            return
        else:
            print("there was a problem")
            return
        return

    def new_telemetry(self):
        print("got new telemetry")
        for i in self.subscriptions:
            last_value = self.factory.t_control.history[i][-1]
            value_json_obj = OrderedDict(
                [("type","data"),("id",i),("value",{"timestamp":int(last_value[0]),"value":last_value[1]})]
                )
            value_json_str = json.dumps(value_json_obj)
            print("the teleme", value_json_str)
            self.sendMessage(bytes(value_json_str),False)


if __name__ == '__main__':
    conn = krpc.connect(address="localhost",name="telemetry_monitor")
    a_telem_fact = TelemetryShipFactory()
    a_ship = a_telem_fact.create_ship(conn)

    #print json.dumps(a_ship.get_json(),indent=5)

    log.startLogging(sys.stdout)

    factory = TelemetryServerFactory(u"ws://127.0.0.1:8081",conn,a_ship)
    factory.protocol = TelemetryServerProtocol

    resource = WebSocketResource(factory)

    # we server static files under "/" ..
    #root = File("./")

    # and our WebSocket server under "/ws" (note that Twisted uses
    # bytes for URIs)
    #root.putChild(b"ws", resource)

    # both under one Twisted Web Site
    #site = Site(root)
    site = Site(resource)
    reactor.listenTCP(8081, site)

    reactor.run()
