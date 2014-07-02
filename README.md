unifi-api
=========

A rewrite of https://github.com/unifi-hackers/unifi-lab in cleaner Python.

Install
-------

    sudo pip install -U unifi

Utilities
---------

The following small utilities are bundled with the API:

### unifi-ls-clients

Lists the currently active clients on the networks. Takes parameters for
controller, username, password, controller version and site ID (UniFi >= 3.x)

```
jb@unifi:~ % unifi-ls-clients -c localhost -u admin -p p4ssw0rd -v v3 -s default
NAME                             MAC  AP            CHAN  RSSI   RX   TX
client-kitchen     00:24:36:9a:0d:ab  Study          100    51  300  216
jborg-mbp          28:cf:da:d6:46:20  Study          100    45  300  300
jb-iphone          48:60:bc:44:36:a4  Living Room      1    45   65   65
jb-ipad            1c:ab:a7:af:05:65  Living Room      1    22   52   65
```

### unifi-low-snr-reconnect

Periodically checks all clients for low SNR values, and disconnects those who
fall below the limit. The point being that these clients will then try to
reassociate, hopefully finding a closer AP. Take the same parameters as above,
plus settings for intervals and SNR threshold. Use `unifi-low-snr-reconnect -h`
for an option summary.

A good source of understanding for RSSI/SNR values is [this
article](http://www.wireless-nets.com/resources/tutorials/define_SNR_values.html).
According to that, an SNR of 15 dB seems like a good cutoff, and that's also
the default value in the script. You can set a higher value for testing:

```
jb@unifi:~ % unifi-low-snr-reconnect -c localhost -u admin -p p4ssw0rd -v v3 -s default --minsnr 30
2012-11-15 11:23:01 INFO unifi-low-snr-reconnect: Disconnecting jb-ipad/1c:ab:a7:af:05:65@Study (SNR 22 dB < 30 dB)
2012-11-15 11:23:01 INFO unifi-low-snr-reconnect: Disconnecting Annas-Iphone/74:e2:f5:97:da:7e@Living Room (SNR 29 dB < 30 dB)
```

For production use, launching the script into the background is recommended...

### unifi-save-statistics

Get a csv file with statistics

```
unifi-save-statistics -c localhost -u admin -p p4ssw0rd -v v3 -s default -f filename.csv
```

API Example
-----------

```python
from unifi.controller import Controller
c = Controller('192.168.1.99', 'admin', 'p4ssw0rd')
for ap in c.get_aps():
	print 'AP named %s with MAC %s' % (ap['name'], ap['mac'])
```

See also the scripts `unifi-ls-clients` and `unifi-low-rssi-reconnect` for more
examples of how to use the API.

UniFi v3 Compatibility and Migration
------------------------------------
With the release of v3, UniFi gained multisite support which requires some
changes on how to interract with the API . Currently we assume v2 to be the
default, thus: Updating the API WON'T BREAK existing code using this API.

Though, for continued v2 usage we **recommend** you start explicitely
instanciating your controller in v2 mode for the day the default assumption
starts to be v3 or newer:

```python
c = Controller('192.168.1.99', 'admin', 'p4ssw0rd', 'v2')
```

With UniFi v3, connecting to the first (`default`) site, is as easy as
instanciating a controller in v3 mode:

```python
c = Controller('192.168.1.99', 'admin', 'p4ssw0rd', 'v3')
```

Connecting to a site other than `default` requires indication of both version
and the site ID:

```python
c = Controller('192.168.1.99', 'admin', 'p4ssw0rd', 'v3', 'myothersite')
```

You can find about the site ID by selecting the site in the UniFi web interface,
i.e. "My other site". Then you can find ia its URL (`https://localhost:8443/manage/s/foobar`)
that the site ID is `myothersite`.

API
---

### `class Controller`

Interact with a UniFi controller.
 
Uses the JSON interface on port 8443 (HTTPS) to communicate with a UniFi
controller. Operations will raise unifi.controller.APIError on obvious
problems (such as login failure), but many errors (such as disconnecting a
nonexistant client) will go unreported.

### `__init__(self, host, username, password)`

Create a Controller object.
     
 - `host` -- the address of the controller host; IP or name
 - `username` -- the username to log in with
 - `password` -- the password to log in with
 
### `block_client(self, mac)`

Add a client to the block list.

 - `mac` -- the MAC address of the client to block.
 
### `disconnect_client(self, mac)`

Disconnects a client, forcing them to reassociate. Useful when the
connection is of bad quality to force a rescan.

 - `mac` -- the MAC address of the client to disconnect.

### `get_alerts(self)`

Return a list of Alerts.

### `get_alerts_unarchived(self)`

Return a list of unarchived Alerts.
 
### `get_events(self)`

Return a list of Events.

### `get_aps(self)`

Return a list of all AP:s, with significant information about each.
 
### `get_clients(self)`

Return a list of all active clients, with significant information about each.

### `get_statistics_last_24h(self)`

Return statistical data of the last 24h

### `get_statistics_24h(self, endtime)`

Return statistical data last 24h from endtime

 - `endtime` -- the last time of statistics.
        
### `get_users(self)`

Return a list of all known clients, with significant information about each.

### `get_user_groups(self)`

Return a list of user groups with its rate limiting settings.

### `get_wlan_conf(self)`

Return a list of configured WLANs with their configuration parameters.
 
### `restart_ap(self, mac)`

Restart an access point (by MAC).

 - `mac` -- the MAC address of the AP to restart.
 
### `restart_ap_name(self, name)`

Restart an access point (by name).

 - `name` -- the name address of the AP to restart.
 
### `unblock_client(self, mac)`

Remove a client from the block list.

 - `mac` -- the MAC address of the client to unblock.

### `archive_all_alerts(self)`

Archive all alerts of site.

### `create_backup(self)`

Tells the controller to create a backup archive that can be downloaded with download_backup() and
then  be used to restore a controller on another machine.

Remember that this puts significant load on a controller for some time (depending on the amount of users and managed APs).

### `get_backup(self, targetfile)`

Tells the controller to create a backup archive and downloads it to a file. It should have a .unf extension for later restore.

 - `targetfile` -- the target file name, you can also use a full path. Default creates unifi-backup.unf in the current directoy.

License
-------

MIT

