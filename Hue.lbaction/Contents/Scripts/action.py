#!/Users/nicholas/Documents/Development/Hue/bin/python

import hue, json, sys, urlparse

input = sys.argv[1]
if input[0] == '{':
    input = json.loads(input)['url']

url = urlparse.urlparse(input)
kind = url.path.split('/')[-1]
query = dict((k, v[0]) for k, v in urlparse.parse_qs(url.query).iteritems() if len(v) == 1)

if kind == 'light':
    light_id = int(query['id'])
    on = bool(int(query['on']))

    light = hue.light(light_id)
    light.state(on=on)

    item = hue.item_for_light(light_id, light())
    item['title'] = '%s is now %s' % (item['title'], 'on' if on else 'off')

elif kind == 'group':
    group_id = int(query['id'])
    scene_id = query['scene']

    group = hue.group(group_id)
    group.action(scene=scene_id)

    item = hue.item_for_scene_name(hue.scene(scene_id)()['name'])
    item['title'] = '%s set' % item['title']

print json.dumps(item)
