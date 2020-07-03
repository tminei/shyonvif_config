import lib.shyonvif as shyonvif
import subprocess
import sys
import json

goodPorts = ["80", "8899"]
passList = ["admin1234", "", "12345"]

def net_scan():
    output = subprocess.check_output("nmap 192.168.1.*", shell=True).decode().splitlines()
    iList = []
    adrList = []
    goodList = []
    for i in range(0, len(output) - 1):
        if "Nmap scan report for" in output[i]:
            if ")" not in output[i]:
                adrList.append(output[i][output[i].find("192"):])
            else:
                adrList.append(output[i][output[i].find("192"):-1])
            iList.append(i)
    iList.append(len(output))
    for j in range(0, len(iList) - 1):
        for k in range(iList[j], iList[j + 1]):
            if "554" in output[k]:
                if ")" not in output[iList[j]]:
                    goodList.append(output[iList[j]][output[iList[j]].find("192"):])
                else:
                    goodList.append(output[iList[j]][output[iList[j]].find("192"):-1])
    return goodList


def check_info(ipList):
    infoList = []
    for i in ipList:
        for j in goodPorts:
            for k in passList:
                try:
                    mycam = shyonvif.onvif(addr=i, port=j, usr='admin', pwd=k)
                    raw = mycam.execute("GET_DEVICE_INFO").decode()
                    if not "The requested URL was not found on this server" in raw:
                        infoList.append([i, j, str(raw[raw.find("Manufacturer") + 13:raw.find("</tds:Manufacturer>")]),
                                         str(raw[raw.find("SerialNumber") + 13:raw.find("</tds:SerialNumber>")])])
                except:
                    pass
                break
    return infoList

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


print(json.dumps(get_manufactured(check_info(net_scan()))))