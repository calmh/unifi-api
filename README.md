unifi-api
=========

A rewrite of https://github.com/unifi-hackers/unifi-lab in cleaner Python.

Example
=======

```python
from unifi.controller import Controller
c = Controller('192.168.1.99', 'admin', 'p4ssw0rd')
for ap in c.get_aps():
	print 'AP named %s with MAC %s' % (ap['name'], ap['mac'])
```

API
===

`class Controller`
------------------

Interact with a UniFi controller.
 
Uses the JSON interface on port 8443 (HTTPS) to communicate with a UniFi
controller. Operations will raise unifi.controller.APIError on obvious
problems (such as login failure), but many errors (such as disconnecting a
nonexistant client) will go unreported.

`__init__(self, host, username, password)`
------------------------------------------

Create a Controller object.
     
### Arguments:

 - `host` -- the address of the controller host; IP or name
 - `username` -- the username to log in with
 - `password` -- the password to log in with
 
`block_client(self, mac)`
-------------------------

Add a client to the block list.

### Arguments:

 - `mac` -- the MAC address of the client to block.
 
`disconnect_client(self, mac)`
------------------------------

Disconnect a client.

Disconnects a client, forcing them to reassociate. Useful when the
connection is of bad quality to force a rescan.

### Arguments:
 
 - `mac` -- the MAC address of the client to disconnect.
 
`get_aps(self)`
---------------

Return a list of all AP:s, with significant information about each.
 
`get_clients(self)`
-------------------

Return a list of all active clients, with significant information about each.
 
`get_wlan_conf(self)`
---------------------

Return a list of configured WLANs with their configuration parameters.
 
`restart_ap(self, mac)`
-----------------------

Restart an access point (by MAC).

### Arguments:

 - `mac` -- the MAC address of the AP to restart.
 
`restart_ap_name(self, name)`
-----------------------------

Restart an access point (by name).

### Arguments:

 - `name` -- the name address of the AP to restart.
 
`unblock_client(self, mac)`
---------------------------

Remove a client from the block list.

### Arguments:

 - `mac` -- the MAC address of the client to unblock.

License
=======

MIT

