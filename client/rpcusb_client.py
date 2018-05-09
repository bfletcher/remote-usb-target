import sys
import xmlrpclib
import time
import subprocess
import re

PROXY_IP = "192.168.2.100"
# PROXY_IP = "192.168.0.26"

proxy = xmlrpclib.ServerProxy("http://" + PROXY_IP + ":9000/")

# command usage:
# rpcusb-client {12v,otg} {0,1,reset}
# rpcusb-client remote-status

def reattach_otg():
        # Find the shared OTG device over usbip
        # attach it locally
        match = 0
        usblist = subprocess.check_output(['usbip', 'list', '-r', PROXY_IP, '-l'])
        regex = "\s*(?P<busid>.....):\sGoogle"
        usbbylines = usblist.splitlines()

        for line in usbbylines:
          m = re.match(regex, line)

          if m:
            fastboot_busid =  m.group('busid')
            match = 1

        if not match:
          print usblist
          print "Remote fastboot device not found"
        else:
          subprocess.check_output(['usbip', 'attach', '-r', PROXY_IP, '-b', fastboot_busid])
          print "Remote fastboot device attached"

if len(sys.argv) < 2 or len(sys.argv) > 3:

        print "usage: rpcusb-client {12v,otg} {0,1,reset}"
        print "usage: rpcusb-client remote-status"

elif sys.argv[1] == 'remote-status':
	# remote-status
	# Check for server connection (Boolean)
	print "server_conn() : %s" % str(proxy.server_conn())

	# Return status info (String/Binary)
	print "status() : %s" % str(proxy.status())

	# Query OTG power state (String/Binary)
	print "get_otg()" 
	print str(proxy.get_otg())

	# Query 12V power state (String/Binary)
	print "get_pwr()" 
	print str(proxy.get_pwr())

elif sys.argv[1] == '12v':
	if len(sys.argv) < 3:
        	print "usage: rpcusb-client {12v,otg} {0,1,reset}"
	elif sys.argv[2] == '0':
		# Clear 12V power state
		print "set_pwr(0)" 
		print str(proxy.set_pwr(0))
        elif sys.argv[2] == '1':
		# Set 12V power state
		print "Set 12V power state - NB wait for fastboot to (re-)attach"
		print "get_pwr()" 
		if str(proxy.get_pwr()) != 'on':
			print "set_pwr(1)" 
			print str(proxy.set_pwr(1))
			time.sleep(5)
			reattach_otg()
		else:
			print "Nothing to do"
			# End set 12V power state
        elif sys.argv[2] == 'reset':
		# Clear 12V power state
		print "set_pwr(0)" 
		print str(proxy.set_pwr(0))
		time.sleep(5)
		# Set 12V power state
		print "Set 12V power state - NB wait for fastboot to (re-)attach"
		print "set_pwr(1)" 
		print str(proxy.set_pwr(1))
		time.sleep(5)
		reattach_otg()
	else: 
		print "usage: rpcusb-client {12v,otg} {0,1,reset}"

elif sys.argv[1] == 'otg':
	if len(sys.argv) < 3:
        	print "usage: rpcusb-client {12v,otg} {0,1,reset}"
	elif sys.argv[2] == '0':
		# Clear OTG power state
		print "set_otg(0)" 
		print str(proxy.set_otg(0))
        elif sys.argv[2] == '1':
		# Set OTG power state
		print "Set OTG power state - NB wait for fastboot to (re-)attach"
		print "get_otg()"
		if str(proxy.get_otg()) != 'on':
			print "set_otg(1)"
			print str(proxy.set_otg(1))
			time.sleep(5)
			reattach_otg()
		else:
			print "Nothing to do"
			# End set OTG power state
else: 
	print "usage: rpcusb-client {12v,otg} {0,1,reset}"
	print "usage: rpcusb-client remote-status"






