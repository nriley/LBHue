__all__ = ('current', 'get')

import os.path
activate_this = os.path.join(os.path.dirname(__file__), 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import json, os, requests, sys
from urlparse import urljoin

bridges_path = os.path.join(os.getenv('LB_SUPPORT_PATH'), 'bridges.json')

bridges = None
try:
    if os.path.exists(bridges_path):
        bridges = json.load(file(bridges_path))
except Exception, e:
    print >> sys.stderr, 'Error restoring bridges:', e

if not bridges:
    bridges = dict(all={})

# XXX automatically handle bridge changed IP address?

class HueException(Exception):
    LINK_BUTTON_NOT_PRESSED = 101

    def has_type(self, type_id):
        type_id = int(type_id)
        return any(error for error in self.args
                   if int(error['type']) == type_id)

    def __str__(self):
        return '\n'.join(error['description'] for error in self.args)

class HueAPI(object):
    __slots__ = ('url', 'bridge')

    def __init__(self, bridge, url):
        self.bridge = bridge
        self.url = url

    def _make_request(self, method=None, *args, **kw):
        url = self.url
        if self.bridge is not self:
            url = urljoin(self.bridge.url, url)
        if args:
            url = urljoin(url, '/'.join(map(str, args)))
        # print url

        if method is None:
            method = 'PUT' if kw else 'GET'

        try:
            if kw:
                response = requests.request(method, url, json=kw, timeout=2)
            else:
                response = requests.request(method, url, timeout=2)
        except requests.ConnectionError, e:
            print >> sys.stderr, e
            exit_with_connection_error()

        response.raise_for_status()

        response_json = response.json()
        # print response_json

        if type(response_json) is list:
            errors = [r['error'] for r in response_json
                      if type(r) is dict and 'error' in r]
            if errors:
                raise HueException(*errors)

        return response_json

    def __call__(self, **kw):
        return self._make_request(**kw)

    def __delattr__(self, attr):
        return self._make_request('DELETE', attr)

    __delitem__ = __delattr__

    def __getattr__(self, attr):
        url = str(attr) + '/'
        if self.bridge is not self:
            url = urljoin(self.url, url)

        return HueAPI(self.bridge, url)

    __getitem__ = __getattr__

    def __repr__(self):
        if self.bridge is self:
            return '<%s: %s>' % (self.__class__.__name__, self.url)
        return '<%s: %s | %s>' % (self.__class__.__name__,
                                self.bridge.url, self.url)

    __str__ = __repr__

class HueBridge(HueAPI):
    __slots__ = ('serial', 'info',)

    def __init__(self, serial, info):
        self.serial = serial
        self.info = info
        self.bridge = self
        self._update_url()

    @property
    def modelid(self): return self.info['modelid']

    @property
    def name(self): return self.info['name']

    @property
    def icon(self):
        version = '1' if self.modelid == '929000226503' else '2'
        return ('bridge_v' + version if self.linked
                else 'pushlink_bridgev' + version) + '.pdf'

    @property
    def linked(self):
        if 'username' not in self.info:
            return False

        if 'whitelist' not in self.config():
            del self.info['username']
            save()
            return False

        return True

    def link(self):
        import subprocess
        computer_name = subprocess.check_output(
            ['/usr/sbin/scutil', '--get', 'ComputerName']).rstrip()[:19]
        try:
            user = self._make_request(method='POST',
                                      devicetype='LBHue#' + computer_name)
        except HueException, e:
            if e.has_type(HueException.LINK_BUTTON_NOT_PRESSED):
                return False

        self.info['username'] = user[0]['success']['username']
        save()

        self._update_url()

        return True

    def make_current(self):
        bridges['current'] = self.serial
        save()

    def _update_url(self):
        username = self.info.get('username')
        if username:
            self.url = urljoin(self.info['url'], '/api/%s/' % username)
        else:
            self.url = urljoin(self.info['url'], '/api/')

class NoBridge(object):
    def __call__(self, **kw):
        return {}

    def __nonzero__(self):
        return False

    def __getattr__(self, attr): return self
    __getitem__ = __getattr__

# Serial numbers (from description.xml) are 12 hex digits.
# Bridge IDs (in Hue or N-UPnP API) are 16 hex digits, consisting of:
# (first 6 digits of serial number) + fffe + (last 6 digits of serial number)
# This is not documented anywhere, but be careful not to confuse the two.

def get(serial, url=None):
    serial = serial.upper()
    assert len(serial) == 12

    bridge_info = bridges['all'].get(serial, {})
    if url:
        bridge_info.update(url=url)
        bridges['all'][serial] = bridge_info
    elif not bridge_info:
        return

    bridge = HueBridge(serial, bridge_info)

    if url: # update configuration
        config = bridge.config()
        bridge_info.update(modelid=config['modelid'], name=config['name'])
        save()

    return bridge

# unique HueBridges?
def current():
    current_serial = bridges.get('current')

    if current_serial:
        return get(current_serial)

    return NoBridge()

def save():
    json.dump(bridges, file(bridges_path, 'w'))

# If we get a connection error, offer to relink a bridge
def exit_with_connection_error():
    import discover
    item = discover.discover_item('Unable to connect. Relink bridge?')

    print json.dumps(item)
    sys.exit(0)
