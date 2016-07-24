__all__ = ('discover_item',)

def discover_item(title='Link Bridge'):
    return dict(title=title, action='discover.py', actionReturnsItems=True)

def item_for_description(desc):
    device_info = desc['device']
    return dict(
        action='connect.py',
        actionArgument=desc['URLBase'] + '#' + device_info['serialNumber'],
        title='Link to ' + device_info['friendlyName'],
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
            xml = ElementTree.fromstring(requests.get(url, timeout=1).text)
            description = etree_to_dict(xml)['root']
            items.append(item_for_description(description))
    except requests.exceptions.RequestException:
        return []

    return items

def ssdp_discover():
    # yuck; alternative would be to mock netdis and scan SSDP directly
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
    import os.path
    activate_this = os.path.join(os.path.dirname(__file__),
                                 'bin/activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    import json

    items = nupnp_discover()

    if not items:
        items = ssdp_discover()

    if not items:
        items = discover_item('No bridges found. Rescan for bridges?')

    print json.dumps(items)
