#!/Users/nicholas/Documents/Development/Hue/bin/python

import hue, json

scenes = hue.scenes()

items = []
for (group, scenes) in scenes.iteritems():
    items.append(hue.scenes_item_for_group(group, scenes))

print json.dumps(items)
