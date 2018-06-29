
D:
cd d:\stream-media\venv\Scripts
echo activate env...
call activate.bat

ping 127.0.0.1 -n 1 > nul
set CM_MQTT_HOST=47.100.125.222
set CM_MONGO_HOST=47.100.125.222
set CM_FLASK_HOST=127.0.0.1
cd ..\..\cloud-media\media_control_server

echo execute python script...
python %1


