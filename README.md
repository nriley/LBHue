# LBHue
A LaunchBar action for controlling Philips hue lights.

Please note that this isn't ready for general distribution yet, but if
you stumble on this repository and want to try it out, you will need
to build a virtualenv and edit the bridge IP address and username in
`hue.py`.  The final version will have bridge discovery built-in.

Building the virtualenv will also be automated for packaging
eventually, but for the moment:

```
cd Hue.lbaction/Contents/Scripts
virtualenv --system-site-packages .
virtualenv --relocatable .
source bin/activate
pip install qhue
```

The `qhue` dependency will be removed at some point.
