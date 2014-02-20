import sys
import powerswitch

powerswitch.Eps4m(ip_address="193.50.110.135").set_on(int(sys.argv[1]))
