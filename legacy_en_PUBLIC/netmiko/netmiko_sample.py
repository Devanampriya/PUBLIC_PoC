from netmiko import ConnectHandler
import difflib

#########Connection initiator to the device
net_connect = ConnectHandler(device_type='cisco_ios', ip='172.16.1.128', username='cisco', password='cisco123')
output = net_connect.find_prompt()
print(output)
if '>' in output:
    cmd = "enable"
    output = net_connect.send_command_timing(cmd, strip_command=False, strip_prompt=False)
    print(output)
if ':' in output:
    output = net_connect.send_command_timing("cisco123", strip_command=False, strip_prompt=False)
    print(output)

##########Executing multiple commands and collecting results
#command_list = ["config t", "int lo1", "ip add 1.1.1.1 255.255.255.255", "no shut"]
command_list = ["show version","show ip int br", "show arp", "show ip route"]
for entry in command_list:
    if '#' in output:
        output = net_connect.send_command_timing(entry, strip_command=False, strip_prompt=False)
        print(output)

##########Collect startup and running config and do comparison for the changes needed to be commited
command_list = ["show startup"]
for entry in command_list:
    if '#' in output:
        output = net_connect.send_command_timing(entry, strip_command=False, strip_prompt=False)
startup_config = output.split("\n")
command_list = ["end","show run brief"]
for entry in command_list:
    if '#' in output:
        output = net_connect.send_command_timing(entry, strip_command=False, strip_prompt=False)
run_config = output.split("\n")
for line in difflib.ndiff(startup_config, run_config):
    print(line)

###########Disconnect from the device    
net_connect.disconnect()
