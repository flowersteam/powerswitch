powerswitch
===========

Python library for controlling ePowerSwitch 4M+.

    import powerswitch
    import time
    ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6')
    while True:
      ps.print_status()
      time.sleep(1)
