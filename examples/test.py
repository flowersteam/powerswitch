import powerswitch
import time

ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6')
#ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6', load_config=True)

ps.print_status()

while True:
    ps.print_status()
    time.sleep(1)
