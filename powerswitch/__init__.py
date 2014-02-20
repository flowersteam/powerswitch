"""
Typical usage:
    import powerswitch
    ps = powerswitch.Eps4m(mac_address='00:13:f6:01:52:d6', ip_address='193.50.110.135')
    ps.set_all_on()
"""
from .powerswitch import Eps4m
