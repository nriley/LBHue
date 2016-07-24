# LBHue
A LaunchBar action for controlling Philips hue lights.

Please note that this is a beta version (with known bugs), but if you
want to try it out, you are welcome.  If you're interested in
developing it, you'll need to build a
[virtualenv](https://virtualenv.pypa.io/en/stable/) as follows:

```
cd Hue.lbaction/Contents/Scripts
virtualenv --system-site-packages .
virtualenv --relocatable .
source bin/activate
pip install -r ../../../requirements.txt
```

You should then be able to open `Hue.lbaction` and add it to LaunchBar.

To run (most of) the scripts individually, you will need to simulate
the LaunchBar environment as follows (or your shell's equivalent):

```
export LB_SUPPORT_PATH=~/'Library/Application Support/LaunchBar/Action Support/net.sabi.LaunchBar.action.Hue'
```

## Screenshots

### The main list
![](https://github.com/nriley/LBHue/blob/master/Screenshots/main.png)

### Rooms & Scenes
![](https://github.com/nriley/LBHue/blob/master/Screenshots/rooms.png)

### A room
![](https://github.com/nriley/LBHue/blob/master/Screenshots/room.png)
