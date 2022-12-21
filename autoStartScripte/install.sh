cp mqtt-bridge.service /lib/systemd/system
cp cmulti-bridge.service /lib/systemd/system
cp mqtt2FileBridge.service /lib/systemd/system
cp mqttFritzboxBridge.service /lib/systemd/system

systemctl daemon-reload
systemctl enable mqtt-bridge.service
systemctl enable cmulti-bridge.service
systemctl enable mqtt2FileBridge.service
systemctl enable mqttFritzboxBridge.service

cp ll /home/pi/.local/bin
cp la /home/pi/.local/bin

chmod 775 /home/pi/.local/bin/ll
chmod 775 /home/pi/.local/bin/la

cp ./serial-symlinks.rules /etc/udev/rules.d
