import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
import logging
import subprocess
import time

import xmlrpc_usbip
import xmlrpc_pwm

#
# xmlrpc server for LAVA target control, to 
# share a fastboot device over usbip connected to the USB 
# control 12v and USB power switching via PWM HAT
#

otg_state = "unknown"
pwr_state = "unknown"



# System functions
def init():
 xmlrpc_usbip.usbip_init()
 xmlrpc_pwm.pwm_init()

# API functions
def server_conn():
 # Debug 
 # Check for server connection (Boolean)
 return 0

def status():
 # Debug 
 # Return status info (String/Binary)
 returnstring = 'Controller Status:\n' + \
 subprocess.check_output(['uname', '-a']) + '\n' + \
 subprocess.check_output(['hub-ctrl']) + '\n' + \
 subprocess.check_output(['usbip', 'list', '-l']) 
 return xmlrpclib.Binary(returnstring)
 return 0

def get_otg():
 # Debug 
 # Query OTG power state (String/Binary)
 global otg_state
 return xmlrpclib.Binary(otg_state)

def set_otg(state):
 # Set OTG power state
 global otg_state
 if (state):
  # power on the USB
  subprocess.call(['hub-ctrl', '-h', '0', '-P', '2', '-p', '1']) 
  otg_state = "on"
  # wait for the connected USB device to initialise
  # call the usbip functionality to start sharing it
  time.sleep(20)
  xmlrpc_usbip.usbip_fastboot_bind()
 else:
  # power off the USB
  # note: kills the usbip sharing
  subprocess.call(['hub-ctrl', '-h', '0', '-P', '2', '-p', '0']) 
  otg_state = "off"
 return 0

def get_pwr():
 # Debug 
 # Query 12V power state (String/Binary)
 global pwr_state
 return xmlrpclib.Binary(pwr_state)

def set_pwr(state):
 # Set 12V power state
 global pwr_state
 if (state):
  pwr_state = "on"
  # power on the 12V
  xmlrpc_pwm.pwm_set(1)
  # wait for the connected USB device to initialise
  # call the usbip functionality to start sharing it
  time.sleep(20)
  xmlrpc_usbip.usbip_fastboot_bind()
 else:
  # power off the 12V
  # note: kills the usbip sharing
  pwr_state = "off"
  xmlrpc_pwm.pwm_set(0)
 return 0

init()

server = SimpleXMLRPCServer(('0.0.0.0', 9000))
print "Listening on port 9000..."

server.register_function(server_conn, "server_conn")
server.register_function(status, "status")
server.register_function(get_otg, "get_otg")
server.register_function(set_otg, "set_otg")
server.register_function(get_pwr, "get_pwr")
server.register_function(set_pwr, "set_pwr")

server.serve_forever()
