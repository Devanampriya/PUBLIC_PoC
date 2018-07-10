from netmiko import ConnectHandler
from napalm import get_network_driver

####### Connection to the device
get_network_driver('ios')
driver = get_network_driver('ios')
# enable secret need to be preconfigured
device = driver('172.16.1.128', 'cisco', 'cisco123', optional_args = {"secret":"cisco123"})
device.open()

###### Getting information from device
print(device.get_facts())
print(device.get_interfaces())
print(device.get_environment())
print(device.get_users())