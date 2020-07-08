import datetime
import base64
import re
from hashlib import sha1
from random import SystemRandom
import string
import http.client
from . import messages, namespace
import requests
from requests.auth import HTTPBasicAuth

SPATH = "/onvif/device_service"
PROF = "prof0"
nsmap = {k: v for k, v in namespace.__dict__.items() if not k.startswith('__')}
pool = string.ascii_letters + string.digits + string.punctuation


class onvif():
    def __init__(self, addr=None, port=80, pth=SPATH, prf=PROF, usr=None, pwd=None, basicauth=False, debug=False):
        self.debug = debug
        self.basicauth = basicauth
        self.addr = addr
        self.login, self.password = usr, pwd
        self.port = port
        self.path = pth
        self.profile = prf
        if not addr:
            if self.debug:
                print("Address is not listed.")
            exit(1)
        if not port:
            if self.debug:
                print("Port is not listed.")
            exit(1)
        if not usr:
            if self.debug:
                print("Username is not listed.")
            exit(1)
        if not pwd:
            if self.debug:
                print("Password is not listed.")
            exit(1)
        self.connection = http.client.HTTPConnection(addr, port=port, timeout=2)

    def execute(self, command, **parms):
        tmpl = getattr(messages, command)
        parms.update(namespace.__dict__)
        try:
            result = tmpl.format(**parms)
        except KeyError as exc:
            if self.debug:
                print("Method is not listed.")
        else:
            response = self.sendSoapMsg(result)
            return response

    def close(self):
        self.connection.close()

    def sendSoapMsg(self, bmsg):
        body = messages._SOAP_BODY.format(content=bmsg, **nsmap)
        hdrs = {}
        if self.login and self.password:
            if self.basicauth:
                auth_plaintext = f"{self.login}:{self.password}".encode("ascii")
                auth_encoded = base64.b64encode(auth_plaintext).decode("ascii")
                hdrs = {"Authorization": "Basic " + auth_encoded}
            else:
                body = self.getAuthHeader() + body
        soapmsg = messages._SOAP_ENV.format(content=body, **nsmap)
        if not self.connection:
            self.connection = http.client.HTTPConnection(self.address, timeout=1)

        try:
            self.connection.request("POST", self.path, soapmsg, headers=hdrs)
        except ConnectionRefusedError:
            if self.debug:
                print("cannot connect")
                self.connection.close()
            return None
        resp = self.connection.getresponse()
        if resp.status != 200:
            print(resp.status, resp.reason)
            self.connection.close()
        else:
            ret = resp.read()
            self.connection.close()
            return ret

    # def getInfo(self, device_url):
    #     try:
    #         session = requests.session()
    #         session.auth = HTTPBasicAuth(self.login, self.password)
    #     except:
    #         return 1
    #     msg = """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetScopes xmlns="http://www.onvif.org/ver10/device/wsdl"/></s:Body></s:Envelope>"""
    #     try:
    #         req = session.post(device_url, msg, timeout=3)
    #         print(req)
    #         session.close()
    #     except:
    #         session.close()
    #         return 0
    #
    #     return 0

    def setIP(self, new_ip):
        old_ip = "{}:{}".format(self.addr, self.port)
        try:
            session = requests.session()
            session.auth = HTTPBasicAuth(self.login, self.password)
        except:
            return 1
        url = "http://{}/onvif/device_service".format(old_ip)
        try:
            session.post(url,
                         """<soap-env:Envelope xmlns:soap-env="http://www.w3.org/2003/05/soap-envelope"><soap-env:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsse:UsernameToken><wsse:Username>admin</wsse:Username><wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">CzpsHdK4C3CKxehbfk2x1XJIxMs=</wsse:Password><wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">tI9OGF5NaBjX7mahNpvwvg==</wsse:Nonce><wsu:Created xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">2020-07-03T08:43:25+00:00</wsu:Created></wsse:UsernameToken></wsse:Security></soap-env:Header><soap-env:Body><ns0:SetNetworkInterfaces xmlns:ns0="http://www.onvif.org/ver10/device/wsdl"><ns0:InterfaceToken>eth0</ns0:InterfaceToken><ns0:NetworkInterface><ns1:IPv4 xmlns:ns1="http://www.onvif.org/ver10/schema"><ns1:Enabled>true</ns1:Enabled><ns1:Manual><ns1:Address>{}</ns1:Address><ns1:PrefixLength>24</ns1:PrefixLength></ns1:Manual><ns1:DHCP>false</ns1:DHCP></ns1:IPv4></ns0:NetworkInterface></ns0:SetNetworkInterfaces></soap-env:Body></soap-env:Envelope>""".format(
                             str(new_ip)), timeout=2)
        except:
            session.close()
            return 0
        return 2

    def getMediaToken(self):
        raw = self.execute("GET_PROFILES").decode()
        if "404 File Not Found" not in raw:
            raw = (raw[raw.find("token=") + 7:])
            token = raw[:raw.find("\"")]
            return token
        else:
            return 1

    def getRTSP(self):
        high = self.getRTSPmain()
        low = self.getRTSPsub(high)
        links = {}
        links["low"] = low
        links["high"] = high
        return links

    def getRTSPmain(self):
        ip = "{}:{}".format(self.addr, self.port)
        try:
            session = requests.session()
            session.auth = HTTPBasicAuth(self.login, self.password)
        except:
            return 1
        url = "http://{}/onvif/media".format(ip)
        token = self.getMediaToken()
        if token != 1:
            try:
                req = session.post(url,
                                   """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Header><Security s:mustUnderstand="1" xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><UsernameToken><Username>admin</Username><Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">4qABGGmCOgjgSFYQLVaPPsujaR8=</Password><Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">EofkvNlWdU269kRk4KO+vEkAAAAAAA==</Nonce><Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">2020-07-03T12:24:54.748Z</Created></UsernameToken></Security></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetStreamUri xmlns="http://www.onvif.org/ver10/media/wsdl"><StreamSetup><Stream xmlns="http://www.onvif.org/ver10/schema">RTP-Unicast</Stream><Transport xmlns="http://www.onvif.org/ver10/schema"><Protocol>RTSP</Protocol></Transport></StreamSetup><ProfileToken>{}</ProfileToken></GetStreamUri></s:Body></s:Envelope>""".format(
                                       str(token)), timeout=3)
                session.close()
                raw = req.text
                raw = (raw[raw.find("<tt:Uri>") + 8:])
                link = raw[:raw.find("</tt:Uri>")]
                return link
            except:
                session.close()

    def getRTSPsub(self, RTSP):
        camType = "NaN"
        link = RTSP
        lowLink = "NaN"
        pattern = 'rtsp:\/\/192\.168\.1\.[0-9]{1,3}:[0-9]{1,3}\/live\/main'
        result = re.match(pattern, link)

        if result:
            camType = "IPC"
        else:
            pattern = 'rtsp:\/\/192\.168\.1\.[0-9]{1,3}:[0-9]{1,3}\/cam'
            result = re.match(pattern, link)
            if result:
                camType = "DAHUA"
        if camType == "IPC":
            lowLink = link[:-4] + "sub"
        elif camType == "DAHUA":
            lowLink = link[:link.find("subtype=") + 8] + "1" + link[link.find("subtype=") + 9:]
        # print(link + "\n" + lowLink)
        return lowLink

    def getAuthHeader(self):
        created = datetime.datetime.now().isoformat().split(".")[0]
        n64 = ''.join(SystemRandom().choice(pool) for _ in range(22))
        nonce = base64.b64encode(n64.encode('ascii')).decode("ascii")
        base = (n64 + created + self.password).encode("ascii")
        pdigest = base64.b64encode(sha1(base).digest()).decode("ascii")
        parms = {}
        parms.update(**nsmap)
        username = self.login
        parms.update(**locals())
        return messages._AUTH_HEADER.format(**parms)
