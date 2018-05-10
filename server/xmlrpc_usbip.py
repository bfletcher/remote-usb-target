import subprocess
import re

def usbip_init():
  subprocess.check_output(['usbipd', '-D'])


def usbip_fastboot_bind():
  match = 0
  # search for the fastboot device busid and share it
  # only 1 will be connected because we only have one power switch for the whole usb
  # look for busid x-x.x (18d1:d00d)
  regex = "\s-\sbusid\s(?P<busid>.....)\s\(18d1:d00d\)"

  usblist = subprocess.check_output(['usbip', 'list', '-l']) 
  usbbylines = usblist.splitlines() 

  for line in usbbylines:
    m = re.match(regex, line)

    if m:
      fastboot_dev = m.group('busid')
      match = 1

  if not match:
    print usblist
    print "Fastboot device not found"

  else:
    bindresult = subprocess.check_output(['usbip', '--debug', 'bind', '-b', fastboot_dev])
    print bindresult

