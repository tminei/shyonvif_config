# pip install WSDiscovery
import requests
import json
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from wsdiscovery.publishing import ThreadedWSPublishing as WSPublishing
from wsdiscovery import QName, Scope
import lib.shyonvif as shyonvif


def get_manufactured(info):
    out_list = []
    for i in info:
        tempDict = {}
        tempDict["ip"] = i[0]
        tempDict["port"] = i[1]
        tempDict["manufacturer"] = i[2]
        try:
            tempDict["serial"] = i[3]
        except:
            pass
        out_list.append(tempDict)
    return out_list


ttype1 = QName("http://www.onvif.org/ver10/device/wsdl", "Device")
scope1 = Scope("onvif://www.onvif.org/Model")
xAddr1 = "localhost:8080/abc"

wsp = WSPublishing()
wsp.start()
wsp.publishService(types=[ttype1], scopes=[scope1], xAddrs=[xAddr1])

wsd = WSDiscovery()
wsd.start()
services = wsd.searchServices()
adrArr = []
for service in services:
    if service.getXAddrs()[0] != xAddr1:
        adr = service.getXAddrs()[0]
        adrArr.append(adr)
wsd.stop()
infoList = []
for i in adrArr:
    try:
        # IPC
        session = requests.session()
        session.auth = HTTPBasicAuth("admin", "")
        # msg = """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetScopes xmlns="http://www.onvif.org/ver10/device/wsdl"/></s:Body></s:Envelope>"""
        msg = """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/></s:Body></s:Envelope>"""
        try:
            req = session.post(i, msg, timeout=7)
            ip = str(i)
            ip = ip[ip.find("//") + 2:]
            port = ip[ip.find(":") + 1:ip.find("/")]
            ip = ip[:ip.find(":")]
            raw = req.text
            infoList.append([ip, port, str(raw[raw.find("Manufacturer") + 13:raw.find("</tds:Manufacturer>")]),
                             str(raw[raw.find("SerialNumber") + 13:raw.find("</tds:SerialNumber>")])])
            session.close()
        except:
            # DAHUA
            ip = str(i)
            ip = ip[ip.find("//") + 2:]
            port = "80"
            ip = ip[:ip.find("/")]
            mycam = shyonvif.onvif(addr=ip, port='80', usr='admin', pwd="admin1234")
            raw = mycam.execute("GET_DEVICE_INFO").decode()
            mycam.close()
            if not "The requested URL was not found on this server" in raw:
                infoList.append([ip, port, str(raw[raw.find("Manufacturer") + 13:raw.find("</tds:Manufacturer>")]),
                                 str(raw[raw.find("SerialNumber") + 13:raw.find("</tds:SerialNumber>")])])
            session.close()
            continue
    except:
        continue
print(json.dumps(get_manufactured(infoList)))
