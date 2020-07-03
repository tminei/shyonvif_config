# Using this library [shyonvif](https://github.com/tminei/shyonvif/)

# How to use:

### shyonvif_get_cams_as_json.py 
**Params:** without any params

**Ex.:**

```
python3 shyonvif_get_cams_as_json.py
```

**Ex. output:**

```
[{"ip": "192.168.1.12", "port": "80", "manufacturer": "IPC", "serial": "2D24OMM01Z0201090001"}]
```

### shyonvif_set_ip.py
**Params:** login password port old_ip new_ip 
**Ex.:** 

```
python3 shyonvif_set_ip.py admin 12345 80 192.168.1.13 192.168.1.12
```

**Ex. output:** without output

### shyonvif_get_links.py
**Params:** login password port old_ip new_ip 

**Ex.:** 

```
python3 shyonvif_get_links.py admin 12345 80 192.168.1.12
```

**Ex. output:** 

```
{"low": "rtsp://192.168.1.12:554/live/sub", "high": "rtsp://192.168.1.12:554/live/main"}
```

**Keep in mind,** if the program fails to get a low link, the output will be about this:

```
{"low": "", "high": "rtsp://192.168.1.12:554/live/main"}
```
