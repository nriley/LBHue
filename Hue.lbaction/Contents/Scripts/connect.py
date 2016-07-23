import json, sys
import bridges

url_bridgeid = sys.argv[1]
if '#' in url_bridgeid:
    url, bridgeid = url_bridgeid.split('#', 1)
else:
    url = None
    bridgeid = url_bridgeid

bridge = bridges.get(bridgeid, url)

if not url and not bridge.linked:
    bridge.link()

if bridge.linked:
    bridge.make_current()
    item = dict(title='Linked to ' + bridge.name,
                icon=bridge.icon,
                iconIsTemplate=True)
else:
    item = dict(title='Press button on %s' % bridge.name,
                subtitle='then Return within 30s',
                action='connect.py',
                actionArgument=bridgeid,
                icon=bridge.icon,
                iconIsTemplate=True)

print json.dumps(item)
