import lib.shyonvif as shyonvif
import json
import sys

login = str(sys.argv[1])
password = str(sys.argv[2])
port = str(sys.argv[3])
ip = str(sys.argv[4])

mycam = shyonvif.onvif(addr=ip, port=port, usr=login, pwd=password, debug=False, basicauth=False)
print(json.dumps(mycam.getRTSP()))
