import powerswitch
import time

ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6')
#ps = powerswitch.Eps4m(ip_address='193.50.110.135')
#ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6', ip_address='193.50.110.135')
ps.set_all_on()
while True:
    ps.print_status()
    time.sleep(1)
