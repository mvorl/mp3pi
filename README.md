# mp3pi

## Requirements on Ubuntu:

apt-get install libbluetooth-dev bc pulseaudio

pip install pyalsaaudio pybluez python-networkmanager pygments

## Requirements on Raspberry Pi:

(from https://kivy.org/docs/installation/installation-rpi.html)

```
apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev cython

apt-get install python-pip libjpeg-dev python-dbus pulseaudio-utils pulseaudio \
   mtdev-tools libbluetooth-dev bc network-manager

apt-get install xclip xsel

#pip install --upgrade Cython==0.23
pip install --upgrade Cython
pip install git+https://github.com/kivy/kivy.git@master
```

## Turn auto exit in pulseaudio off
```
echo "exit-idle-time = -1" >> /etc/pulse/daemon.conf
```

Install recent version of mpg123:
```
apt-get install libpulse-dev
wget https://www.mpg123.de/download/mpg123-1.25.0.tar.bz2
tar xvjf mpg123-1.25.0.tar.bz2
cd mpg123...
./configure --with-audio=pulse
make -j4
make install
echo "/usr/local/lib" > /etc/ld.so.conf.d/locallib.conf
ldconfig
```

Install pulseaudio-ctl
```
git clone https://github.com/graysky2/pulseaudio-ctl
cd pulseaudio-ctl
make
make install
```

If you want to use ALSA instead of pulseaudio:
```
apt-get install python-alsaaudio
```

Modifications on ~/.kivy/config.ini
```
[input]
mouse = mouse
%(name)s = probesysfs,provider=hidinput
mtdev_%(name)s = probesysfs,provider=mtdev
hid_%(name)s = probesysfs,provider=hidinput
```

Install as a system service
```
systemctl set-default multi-user.target

cp systemd/mp3pi.service /etc/systemd/system
cp systemd/pulseaudio.service /etc/systemd/system
systemctl enable mp3pi
systemctl enable pulseaudio
```

?? gir1.2-networkmanager-1.0 gir1.2-nmgtk-1.0 libnm-dev libnm-glib-dev libnm-glib-vpn-dev libnm-gtk-dev
  libnm-util-dev libnmap-parser-perl libnmz7 libnmz7-dev network-manager-dev ??

## Disable WLAN power management:
```
echo 'KERNEL=="wlan*", ACTION=="add", RUN+="/sbin/iwconfig wlan0 power off"' > /etc/udev/rules.d/10-wlan-powersavings-off.rules
```

## Screen is turned upside down:
  add "lcd_rotate=2" to /boot/config.txt

## Undervolt symbol in upper right is bugging you:
  add "avoid_warnings=1" to /boot/config.txt

## Add Splash Screen:
```
  apt-get install plymouth
  plymouth-set-default-theme tribar
```

  Add "quiet splash" to the kernel cmdline /boot/cmdline.txt

## Turn off console screensaver (1 hour by default)
  add "consoleblank=0" /boot/cmdline.txt

## Wifi list networks:
```
nmcli device wifi list
```

## Wifi connect to AP:
```
nmcli device wifi connect "SSID" password "WLANPSK"
```

## Optional Stuff
Change Hostname
```
echo "raspiradio" > /etc/hostname
sed -i "s/127.0.1.1.*raspberrypi/127.0.1.1\traspiradio/g" /etc/hosts
```

## Play with custom Playlists
```
curl -A "User-Agent: XBMC Addon Radio" 'http://radio.de/info/menu/broadcastsofcategory?category=_top' | jq "." > radio.de.json

jq '[.[]|select(.name=="NDR 2" or .name=="RADIO BOB!")]' < radio.de.json
```

## Screenshots
![alt text](screenshots/screenshot.png "Description goes here")

## Work in progress (i.e. does not work fully yet)
- draggable station list slider (stuck in a loop occasionally)
- favorites station list
- image viewer: on activation, 1st image not shown

## Ideas
- move listview+draggable slider into a class
- move ALSA+pulse into an AudioInterface class
- How to activate "add/remove favorite"?
- How to select favorites?
