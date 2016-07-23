import os.path
activate_this = os.path.join(os.path.dirname(__file__), 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import json

def item_for_description(description):
    device_info = description['device']
    return dict(
        action='connect.py',
        actionArgument=description['URLBase'],
        title='Connect to ' + device_info['friendlyName'],
        icon='bridge_v1.pdf' if device_info['modelNumber'] == '929000226503'
        else 'bridge_v2.pdf',
        iconIsTemplate=True,
        actionReturnsItems=True)

def nupnp_discover():
    import requests
    from netdisco.util import etree_to_dict
    from xml.etree import ElementTree

    items = []
    try:
        response = requests.get('https://www.meethue.com/api/nupnp', timeout=8)
        bridges = response.json()
        for bridge in bridges:
            url = 'http://%s/description.xml' % bridge['internalipaddress']
            xml = ElementTree.fromstring(requests.get(url).text)
            description = etree_to_dict(xml)['root']
            items.append(item_for_description(description))
    except requests.exceptions.RequestException:
        return []

    return items

def ssdp_discover():
    # yuck; another alternative would be to mock up netdis and scan SSDP
    # directly
    import netdisco.ssdp
    original_scan = netdisco.ssdp.scan
    def scan(st=None, timeout=2, max_entries=None):
        return original_scan(st, timeout, max_entries)
    netdisco.ssdp.scan = scan
    from netdisco.discovery import NetworkDiscovery

    discovery = NetworkDiscovery(limit_discovery=['philips_hue'])

    # again yuck, but limit_discovery doesn't work backwards
    discovery.is_discovering = True
    discovery.ssdp.scan()
    discovery.is_discovering = False

    return [item_for_description(entry.description)
            for entry in discovery.get_entries('philips_hue')
            if entry.st == 'upnp:rootdevice']

if __name__ == '__main__':
    items = nupnp_discover()

    if not items:
        items = ssdp_discover()

    print json.dumps(items)
