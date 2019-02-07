# remote-usb-target
Replicating a USB connection over ethernet including target board 12v power and USB 5v power control.

## About this project
When automating software tests deployed to embedded target devices it's generally necessary to be able to control the target 
power/reset and also any other external interfaces (e.g. USB) that affect the testing. Doing this with commodity scalable
hardware is a well-known problem for building test farms, but even with one or two boards on your desk it can get fiddly
quite quickly. It's also quite cool for being tidy and possibly scable if you can send more functions down the same wire.
This was a proof-of-concept for the [LAVA On Your Desk boF](http://connect.linaro.org/resource/hkg18/hkg18-tr11/) 
session at Linaro Connect HKG18.

## Target device control - quirks of the 96Boards CE Edition
CE Edition 96Boards (e.g. Hikey, DB410C) have USB OTG ports which are used for loading images and firmware. However, when 
powered, the OTG port disables the USB host ports, which it the primary route for connecting ethernet via USB-ethernet adaptors.
You can't run deploy automated Linux-based tests that assume network functionality to these boards without USB OTG power 
switching. 
To work around this behaviour in an automated test setup, the sequence of operations needs to look something like this:
1. Power on the OTG port
2. Power up the board
3. Load the image over OTG
4. Power off the board
5. Power off the OTG port
6. Power on the board
7. Boot the test
8. Test connects to the network

## Hardware
### In principle
1. A Linux PC client running some kind of test framework
2. An embedded server controlling power and USB
3. A target device-under-test (DUT)
### Example
1. PC running Debian and a local instance of LAVA
2. RPi with Motor Hat switching power and USB OTG on the target (BBB should work also)
3. Hikey6220 DUT

## How it works
There's a data connection and a control connection:
1. The data connection is USB-over-IP - replicating a USB connection (in this case fastboot) on a remote device
2. The control connection is XML-RPC to control power and port switching

The RPi runs an XML-RPC server which executes local functions to control:
1. Power switching via 12V tolerant motor H-bridge board (Adafruit)
2. USB on-off for OTG via local RPi root hub control
3. RPi USB (for OTG) shared over IP using usbip
4. The USB binding needs to be actively managed because switching operations break it
5. A client on the PC invokes the XML-RPC calls on the RPi

## Operation
On boot, the RPi server connected to the target finds the USB-connected fastboot (Google) device and shares it over usbip.
For more info, look at the docs for usbip. You need to load a kernel module on both the server and client IIRC.

### Tasks
At start up on the RPi server:
1. load the `usbip-host` module
2. start the `usbipd -D` daemon
3. start the xmlrpc server 

Each time you re-power the OTG port via the xmlrpc call (this is called the ‘pre-power’ command in LAVA-speak)

On the RPi server:
1. power on the port
2. Wait for the Hikey to initialise
3. list the locally connected usb devices
4. find the Google one 
5. bind the Google one to usbip
6. return

On the PC client:
1. call the USB port power-on RPC command & assume we wait for it to return
2. list the remotely connected usb devices (dispatcher context, fortunately) and find the Google one/only shared one
attach it locally

## Implemented RPC API
```
status() - Return status info (String/Binary)
get_otg() - Query OTG power state (String/Binary)
set_otg(state) - Set OTG power state
get_pwr() - Query 12V power state (String/Binary)
set_pwr(state) - Set 12V power state
```

## Dependencies
### usbip
#### References -  
[1 hirofuchi.pdf](https://www.usenix.org/legacy/events/usenix05/tech/freenix/hirofuchi/hirofuchi.pdf)
[2 linux-rpi-and-usb-over-ip](https://3mdeb.com/firmware/linux-rpi-and-usb-over-ip/)

```
pi: $ sudo apt-get install usbip
pi: $ sudo usbip list -l # gives a list of local usb devices
pi: $ sudo modprobe usbip-host
pi: $ sudo usbipd -D
```

### hub-ctl
See [hub-ctrl.c](https://github.com/codazoda/hub-ctrl.c)

### vhci-hcd
```
host: $ sudo modprobe vhci-hcd
```

### 12v switching hardware library
To switch 12v I use the Adafruit MotorHAT. It's a PWM motor control board. Most of the work was to figure out how
to NOT do PWM but just use the bridge transistors to switch DC 12v on/off.
Adafruit_MotorHAT - Adafruit_PWM_Servo_Driver

## Integrated with LAVA

### From the Device Dictionary
```
commands:
    connect: telnet localhost 7002
    hard_reset: python /usr/bin/rpcusb_client.py 12v reset
    soft_reset: fastboot reboot -s 547E6F8B000B090B
    power_off: python /usr/bin/rpcusb_client.py 12v 0
    power_on: python /usr/bin/rpcusb_client.py 12v 1
    pre_power_command: python /usr/bin/rpcusb_client.py otg 1
    pre_os_command: python /usr/bin/rpcusb_client.py otg 0
```    

# Todo
IPs are static at the moment
