#!/Users/nicholas/Documents/Development/Hue/bin/python

import hue, json

lights = hue.lights()

items = [dict(title='Rooms & Scenes',
              icon='font-awesome:picture-o',
              iconIsTemplate=True,
              actionReturnsItems=True,
              action='scenes.py')]

for (light_name, (light_id, light_info)) in lights.iteritems():
    items.append(hue.toggle_item_for_light(light_id, light_info))

print json.dumps(items)
