import hue, json, sys, urlparse

input = sys.argv[1]
if input[0] == '{':
    input = json.loads(input)['url']

url = urlparse.urlparse(input)
kind = url.path.split('/')[-1]
query = dict((k, v[0]) for k, v in urlparse.parse_qs(url.query).iteritems()
             if len(v) == 1)

on = query.get('on')
if on is not None:
    on = bool(int(query['on']))
    on_or_off = 'on' if on else 'off'

if kind == 'light':
    light_id = int(query['id'])

    light = hue.light(light_id)
    light.state(on=on)

    item = hue.item_for_light(light_id, light())
    item['title'] = '%s is now %s' % (item['title'], on_or_off)

elif kind == 'group':
    group_id = int(query['id'])

    group = hue.group(group_id)

    scene_id = query.get('scene')
    if scene_id is not None:
        group.action(scene=scene_id)
        item = hue.item_for_scene_name(hue.scene(scene_id)()['name'])
        item['title'] = '%s set' % item['title']

    if on is not None:
        group.action(on=on)
        item = hue.item_for_group(group_id, group())
        item['title'] = '%s lights are now %s' % (item['title'], on_or_off)

print json.dumps(item)
