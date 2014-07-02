try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504: error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
    import _ssl
    _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
except:
    pass

import cookielib
import json
import logging
import urllib
import urllib2
import time

log = logging.getLogger(__name__)

class APIError(Exception):
    pass

class Controller:
    """Interact with a UniFi controller.

    Uses the JSON interface on port 8443 (HTTPS) to communicate with a UniFi
    controller. Operations will raise unifi.controller.APIError on obvious
    problems (such as login failure), but many errors (such as disconnecting a
    nonexistant client) will go unreported.

    >>> from unifi.controller import Controller
    >>> c = Controller('192.168.1.99', 'admin', 'p4ssw0rd')
    >>> for ap in c.get_aps():
    ...     print 'AP named %s with MAC %s' % (ap['name'], ap['mac'])
    ...
    AP named Study with MAC dc:9f:db:1a:59:07
    AP named Living Room with MAC dc:9f:db:1a:59:08
    AP named Garage with MAC dc:9f:db:1a:59:0b

    """

    def __init__(self, host, username, password, version='v2', site_id='default'):
        """Create a Controller object.

        Arguments:
            host     -- the address of the controller host; IP or name
            username -- the username to log in with
            password -- the password to log in with
            version  -- the base version of the controller API [v2|v3]
            site_id  -- the site ID to connect to (UniFi >= 3.x)

        """

        self.host = host
        self.username = username
        self.password = password
        self.site_id = site_id
        self.url = 'https://' + host + ':8443/'
        self.api_url = self.url + self._construct_api_path(version)

        log.debug('Controller for %s', self.url)

        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        self._login()

    def _jsondec(self, data):
        obj = json.loads(data)
        if 'meta' in obj:
            if obj['meta']['rc'] != 'ok':
                raise APIError(obj['meta']['msg'])
        if 'data' in obj:
            return obj['data']
        return obj

    def _read(self, url, params=None):
        res = self.opener.open(url, params)
        return self._jsondec(res.read())

    def _construct_api_path(self, version):
        """Returns valid base API path based on version given

           The base API path for the URL is different depending on UniFi server version.
           Default returns correct path for latest known stable working versions.

        """

        V2_PATH = 'api/'
        V3_PATH = 'api/s/' + self.site_id + '/'

        if(version == 'v2'):
            return V2_PATH
        if(version == 'v3'):
            return V3_PATH
        else:
            return V2_PATH

    def _login(self):
        log.debug('login() as %s', self.username)
        params = urllib.urlencode({'login': 'login',
            'username': self.username, 'password': self.password})
        self.opener.open(self.url + 'login', params).read()

    def get_alerts(self):
        """Return a list of all Alerts."""

        return self._read(self.api_url + 'list/alarm')
        
    def get_alerts_unarchived(self):
        """Return a list of Alerts unarchived."""

        js = json.dumps({'_sort': '-time', 'archived':False})
        params = urllib.urlencode({'json': js})
        return self._read(self.api_url + 'list/alarm', params)

    def get_statistics_last_24h(self):
        """Returns statistical data of the last 24h"""

        return self.get_statistics_24h(time.time())
        
    def get_statistics_24h(self, endtime):
        """Return statistical data last 24h from time"""
        
        js = json.dumps({'attrs':["bytes","num_sta","time"], 'start':int(endtime-86400)*1000, 'end':int(endtime-3600)*1000})
        params = urllib.urlencode({'json': js})
        return self._read(self.api_url + 'stat/report/hourly.system', params)
        
    def get_events(self):
        """Return a list of all Events."""

        return self._read(self.api_url + 'stat/event')

    def get_aps(self):
        """Return a list of all AP:s, with significant information about each."""

        js = json.dumps({'_depth': 2, 'test': None})
        params = urllib.urlencode({'json': js})
        return self._read(self.api_url + 'stat/device', params)

    def get_clients(self):
        """Return a list of all active clients, with significant information about each."""

        return self._read(self.api_url + 'stat/sta')

    def get_users(self):
        """Return a list of all known clients, with significant information about each."""

        return self._read(self.api_url + 'list/user')

    def get_user_groups(self):
        """Return a list of user groups with its rate limiting settings."""

        return self._read(self.api_url + 'list/usergroup')

    def get_wlan_conf(self):
        """Return a list of configured WLANs with their configuration parameters."""

        return self._read(self.api_url + 'list/wlanconf')

    def _mac_cmd(self, target_mac, command, mgr='stamgr'):
        log.debug('_mac_cmd(%s, %s)', target_mac, command)
        params = urllib.urlencode({'json': json.dumps({'mac': target_mac, 'cmd': command})})
        self._read(self.api_url + 'cmd/' + mgr, params)

    def block_client(self, mac):
        """Add a client to the block list.

        Arguments:
            mac -- the MAC address of the client to block.

        """

        self._mac_cmd(mac, 'block-sta')

    def unblock_client(self, mac):
        """Remove a client from the block list.

        Arguments:
            mac -- the MAC address of the client to unblock.

        """

        self._mac_cmd(mac, 'unblock-sta')

    def disconnect_client(self, mac):
        """Disconnect a client.

        Disconnects a client, forcing them to reassociate. Useful when the
        connection is of bad quality to force a rescan.

        Arguments:
            mac -- the MAC address of the client to disconnect.

        """

        self._mac_cmd(mac, 'kick-sta')

    def restart_ap(self, mac):
        """Restart an access point (by MAC).

        Arguments:
            mac -- the MAC address of the AP to restart.

        """

        self._mac_cmd(mac, 'restart', 'devmgr')

    def restart_ap_name(self, name):
        """Restart an access point (by name).

        Arguments:
            name -- the name address of the AP to restart.

        """

        if not name:
            raise APIError('%s is not a valid name' % str(name))
        for ap in self.get_aps():
            if ap.get('state', 0) == 1 and ap.get('name', None) == name:
                self.restart_ap(ap['mac'])

    def archive_all_alerts(self):
        """Archive all Alerts
        """
        js = json.dumps({'cmd': 'archive-all-alarms'})
        params = urllib.urlencode({'json': js})
        answer = self._read(self.api_url + 'cmd/evtmgr', params)
        
    def create_backup(self):
        """Ask controller to create a backup archive file, response contains the path to the backup file.

        Warning: This process puts significant load on the controller may
                 render it partially unresponsive for other requests.
        """

        js = json.dumps({'cmd': 'backup'})
        params = urllib.urlencode({'json': js})
        answer = self._read(self.api_url + 'cmd/system', params)

        return answer[0].get('url')

    def get_backup(self, target_file='unifi-backup.unf'):
        """Get a backup archive from a controller.

        Arguments:
            target_file -- Filename or full path to download the backup archive to, should have .unf extension for restore.

        """
        download_path = self.create_backup()

        opener = self.opener.open(self.url + download_path)
        unifi_archive = opener.read()

        backupfile = open(target_file, 'w')
        backupfile.write(unifi_archive)
        backupfile.close()
