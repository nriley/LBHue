# LBHue
A LaunchBar action for controlling Philips hue lights.

Please note that this isn't ready for general distribution yet, but if
you stumble on this repository and want to try it out, you will need
to build a virtualenv manually.  Building the virtualenv will also be
automated for packaging eventually, but for the moment:

```
cd Hue.lbaction/Contents/Scripts
virtualenv --system-site-packages .
virtualenv --relocatable .
source bin/activate
pip install netdisco
```

You should then be able to open Hue.lbaction and add it to LaunchBar.
