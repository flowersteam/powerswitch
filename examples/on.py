import sys
import powerswitch

powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6').set_on(int(sys.argv[1]))
