import discover, hue, json

items = []

if hue.connected():
    items.append(dict(title='Rooms & Scenes',
                      icon='font-awesome:picture-o',
                      iconIsTemplate=True,
                      actionReturnsItems=True,
                      action='scenes.py'))

lights = hue.lights()

for (light_name, (light_id, light_info)) in lights.iteritems():
    items.append(hue.toggle_item_for_light(light_id, light_info))

items.append(discover.discover_item())

print json.dumps(items)
