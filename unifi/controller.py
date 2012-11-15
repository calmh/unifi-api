import cookielib
import json
import logging
import urllib
import urllib2

log = logging.getLogger(__name__)

class APIError(Exception):
    pass

class Controller:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.url = 'https://' + host + ':8443/'
        log.debug('Controller for %s', self.url)

        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

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

    def login(self):
        log.debug('login() as %s', self.username)
        params = urllib.urlencode({'login': 'login',
            'username': self.username, 'password': self.password})
        self.opener.open(self.url + 'login', params).read()

    def get_aps(self):
        js = json.dumps({'_depth': 2, 'test': None})
        params = urllib.urlencode({'json': js})
        return self._read(self.url + 'api/stat/device', params)

    def get_clients(self):
        return self._read(self.url + 'api/stat/sta')

    def get_wlan_conf(self):
        return self._read(self.url + 'api/list/wlanconf')

    def _mac_cmd(self, target_mac, command, mgr='stamgr'):
        log.debug('_mac_cmd(%s, %s)', target_mac, command)
        params = urllib.urlencode({'json':
            {'mac': target_mac, 'cmd': command}})
        self._read(self.url + 'api/cmd/' + mgr, params)

    def block_client(self, mac):
        self._mac_cmd(mac, 'block-sta')

    def unblock_client(self, mac):
        self._mac_cmd(mac, 'unblock-sta')

    def reconnect_client(self, mac):
        self._mac_cmd(mac, 'kick-sta')

    def restart_ap(self, mac):
        self._mac_cmd(mac, 'restart', 'devmgr')

    def restart_ap_name(self, apnamefilter=''):
        aplist = self.get_aps()
        for ap in aplist:
            if ap.get('state', 0) == 1:
                if 'name' in ap and ap['name'].startswith(apnamefilter):
                    self.reboot_ap(ap['mac'])

