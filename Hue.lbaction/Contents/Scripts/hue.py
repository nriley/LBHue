#!/Users/nicholas/Documents/Development/Hue/bin/python

__all__ = ('lights', 'light', 'item_for_light', 'toggle_item_for_light')

# XXX replace this with either nothing or something that isn't GPLv2
import collections, qhue, urllib

bridge = qhue.Bridge('192.168.0.14', 'USERNAME')

def lights():
    lights = dict((light_info['name'], (int(light_id), light_info))
                  for (light_id, light_info) in bridge.lights().iteritems()
                  if light_info['state']['reachable'])
    return collections.OrderedDict(sorted(lights.items()))

def light(light_id):
    return bridge.lights[light_id]

def item_for_light(light_id, light_info):
    return dict(
        title=light_info['name'],
        icon='font-awesome:fa-lightbulb-o',
        iconIsTemplate=True)

def action_url(kind, **params):
    return 'x-launchbar:action/net.sabi.LaunchBar.action.Hue/%s?%s' % (
        kind, urllib.urlencode(params))

def toggle_item_for_light(light_id, light_info):
    item = item_for_light(light_id, light_info)
    on = bool(light_info['state']['on'])
    want_on = 0 if on else 1
    item.update(
        action='action.py',
        actionReturnsItems=True,
        url=action_url('light', id=light_id, on=want_on))
    if on:
        item['badge'] = 'ON'
    return item
