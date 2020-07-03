import lib.shyonvif as shyonvif
import sys

login = str(sys.argv[1])
password = str(sys.argv[2])
port = str(sys.argv[3])
old_ip = str(sys.argv[4])
new_ip = str(sys.argv[5])

mycam = shyonvif.onvif(addr=old_ip, port=port, usr=login, pwd=password, debug=False, basicauth=False)
mycam.setIP(new_ip)

