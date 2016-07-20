#!/Users/nicholas/Documents/Development/Hue/bin/python

__all__ = ('lights', 'light', 'item_for_light', 'toggle_item_for_light',
           'group', 'scenes_item_for_group',
           'scenes', 'scene', 'item_for_scene_name')

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

def scenes():
    def lights_as_set(lights):
        return frozenset(map(int, lights))
    lights_groups = dict((lights_as_set(group_info['lights']), (int(group_id), group_info['name']))
                         for (group_id, group_info) in bridge.groups().iteritems()
                         if len(group_info['lights']))
    scenes_by_group = {}
    for (scene_id, scene_info) in bridge.scenes().iteritems():
        if scene_info['recycle']:
            # temporary, ignore? But may refer to all lights, so...
            continue
        lights_set = lights_as_set(scene_info['lights'])
        # XXX verify that scenes that don't match a group actually
        # refer to all lights
        group_id, group_name = lights_groups.get(lights_set, (0, 'All Lights'))
        scenes_by_group.setdefault((group_name, group_id), []).append(
            (scene_info['name'], scene_id))
    return collections.OrderedDict(
        sorted((_, sorted(scenes))
               for (_, scenes) in scenes_by_group.iteritems()))

def group(group_id):
    return bridge.groups[group_id]

def scenes_item_for_group((group_name, group_id), scenes_by_group):
    return dict(
        title=group_name,
        icon='font-awesome:cube',
        children=[set_item_for_scene(group_id, scene)
                  for scene in scenes_by_group])

def scene(scene_id):
    return bridge.scenes[scene_id]

def item_for_scene_name(scene_name):
    return dict(
        title=scene_name,
        icon='font-awesome:picture-o',
        iconIsTemplate=True)

def set_item_for_scene(group_id, (scene_name, scene_id)):
    item = item_for_scene_name(scene_name)
    item.update(
        action='action.py',
        actionReturnsItems=True,
        url=action_url('group', id=group_id, scene=scene_id))
    return item
