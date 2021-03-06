__all__ = ('lights', 'light', 'item_for_light', 'toggle_item_for_light',
           'group', 'item_for_group', 'scenes_item_for_group',
           'scenes', 'scene', 'item_for_scene_name',
           'connected')

HUE_PRODUCTS = dict(
    LLC014='aura',
    HBL001='beyond_ceiling_pendant_table',
    HBL002='beyond_ceiling_pendant_table',
    HBL003='beyond_ceiling_pendant_table',
    LLC005='bloom',
    LLC011='bloom',
    LLC012='bloom',
    LLC007='bloom',
    LCT002='br30',
    LCT011='br30',
    LTW011='br30',
    LWB005='br30',
    LWB011='br30',
    HEL001='entity',
    HEL002='entity',
    LLC020='go',
    LCT003='gu10_par16',
    HIL001='impulse',
    HIL002='impulse',
    LLC006='iris',
    LLC010='iris',
    LST001='lightstrip',
    LST002='lightstrip',
    HML001='phoenix_ceiling_pendant_table_wall',
    HML002='phoenix_ceiling_pendant_table_wall',
    HML003='phoenix_ceiling_pendant_table_wall',
    HML004='phoenix_ceiling_pendant_table_wall',
    HML005='phoenix_ceiling_pendant_table_wall',
    HML006='phoenix_ceiling_pendant_table_wall',
    HML007='phoenix_recessed_spot',
    LLC013='storylight',
    LCT001='white_and_color_e27_b22',
    LCT007='white_and_color_e27_b22',
    LCT010='white_and_color_e27_b22',
    LWT010='white_and_color_e27_b22',
    LWB004='white_and_color_e27_b22',
    LWB006='white_and_color_e27_b22',
    LWB010='white_e27_b22',
    LWB014='white_e27_b22')

HUE_ROOMS=['bathroom', 'bedroom', 'carport', 'dining', 'driveway', 'frontdoor',
           'garage', 'garden', 'gym', 'hallway', 'kids_bedroom', 'kitchen',
           'living', 'nursery', 'office', 'recreation', 'terrace', 'toilet']

import collections, urllib
import bridges

bridge = bridges.current()

def connected():
    return bool(bridge)

def lights():
    lights = dict((light_info['name'], (int(light_id), light_info))
                  for (light_id, light_info) in bridge.lights().iteritems()
                  if light_info['state']['reachable'])
    return collections.OrderedDict(sorted(lights.items()))

def light(light_id):
    return bridge.lights[light_id]

def item_for_light(light_id, light_info):
    icon = 'font-awesome:fa-lightbulb-o'
    if light_info['manufacturername'] == 'Philips':
        icon = HUE_PRODUCTS.get(light_info['modelid'], icon)
    return dict(
        title=light_info['name'],
        icon=icon,
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
        url=action_url('light', id=light_id, on=want_on))
    if on:
        item['badge'] = 'ON'
    return item

def scenes():
    def lights_as_set(lights):
        return frozenset(map(int, lights))
    lights_groups = dict(
        (lights_as_set(group_info['lights']),
         (int(group_id), group_info))
        for (group_id, group_info) in bridge.groups().iteritems()
        if len(group_info['lights']))
    scenes_by_group = {}
    for (scene_id, scene_info) in bridge.scenes().iteritems():
        if scene_info['recycle']: # temporary, ignore
            continue
        lights_set = lights_as_set(scene_info['lights'])
        group_id, group_info = lights_groups.get(lights_set, (None, None))
        if group_id is None:
            continue
        group_name = group_info['name']
        scenes_by_group.setdefault(
            (group_name, group_id), (group_info, []))[1].append(
                (scene_info['name'], scene_id))
    scenes_by_group = collections.OrderedDict(
        sorted((_, (group_info, sorted(scenes)))
               for (_, (group_info, scenes)) in scenes_by_group.iteritems()))
    scenes_by_group[(None, 0)] = ({}, [])
    return scenes_by_group

def group(group_id):
    return bridge.groups[group_id]

def item_for_group(group_id, group_info):
    if group_id is 0:
        return dict(title='All', icon='font-awesome:cubes')

    group_name = group_info['name']
    lower_name = group_name.lower()
    for room in HUE_ROOMS:
        if room in lower_name:
            icon = room
            break
    else:
        icon = 'other'
    item = dict(title=group_name, icon=icon, iconIsTemplate=True)
    state = group_info['state']
    if bool(state['all_on']):
        item['badge'] = 'ALL ON'
    elif bool(state['any_on']):
        item['badge'] = 'ON'
    return item

def scenes_item_for_group((group_name, group_id), (group_info, group_scenes)):
    item = item_for_group(group_id, group_info)
    item.update(
        children=[set_item_for_scene(group_id, scene)
                  for scene in group_scenes] + [
                          dict(title='All On',
                               icon='font-awesome:toggle-on',
                               action='action.py',
                               url=action_url('group', id=group_id, on=1)),
                          dict(title='All Off',
                               icon='font-awesome:toggle-off',
                               action='action.py',
                               url=action_url('group', id=group_id, on=0))])
    return item

def scene(scene_id):
    return bridge.scenes[scene_id]

def item_for_scene_name(scene_name):
    return dict(
        title=scene_name,
        icon='font-awesome:picture-o')

def set_item_for_scene(group_id, (scene_name, scene_id)):
    item = item_for_scene_name(scene_name)
    item.update(
        action='action.py',
        url=action_url('group', id=group_id, scene=scene_id))
    return item
