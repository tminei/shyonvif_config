import datetime
import base64
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
        self.connection = http.client.HTTPConnection(addr, port=port)

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

    def sendSoapMsg(self, bmsg):
        print(bmsg)
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
            self.connection = http.client.HTTPConnection(self.address)

        try:
            self.connection.request("POST", self.path, soapmsg, headers=hdrs)
        except ConnectionRefusedError:
            print("cannot connect")
            return None
        resp = self.connection.getresponse()
        print(resp.read())
        if resp.status != 200:
            print(resp.status, resp.reason)
        else:
            return resp.read()

    def setIP(self, new_ip):
        old_ip = "{}:{}".format(self.addr, self.port)
        try:
            session = requests.session()
            session.auth = HTTPBasicAuth(self.login, self.password)
        except:
            return 1
        url = "http://{}/onvif/device_service".format(old_ip)
        try:
            session.post(url,"""<soap-env:Envelope xmlns:soap-env="http://www.w3.org/2003/05/soap-envelope"><soap-env:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsse:UsernameToken><wsse:Username>admin</wsse:Username><wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">CzpsHdK4C3CKxehbfk2x1XJIxMs=</wsse:Password><wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">tI9OGF5NaBjX7mahNpvwvg==</wsse:Nonce><wsu:Created xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">2020-07-03T08:43:25+00:00</wsu:Created></wsse:UsernameToken></wsse:Security></soap-env:Header><soap-env:Body><ns0:SetNetworkInterfaces xmlns:ns0="http://www.onvif.org/ver10/device/wsdl"><ns0:InterfaceToken>eth0</ns0:InterfaceToken><ns0:NetworkInterface><ns1:IPv4 xmlns:ns1="http://www.onvif.org/ver10/schema"><ns1:Enabled>true</ns1:Enabled><ns1:Manual><ns1:Address>{}</ns1:Address><ns1:PrefixLength>24</ns1:PrefixLength></ns1:Manual><ns1:DHCP>false</ns1:DHCP></ns1:IPv4></ns0:NetworkInterface></ns0:SetNetworkInterfaces></soap-env:Body></soap-env:Envelope>""".format(str(new_ip)), timeout=3)
        except:
            session.close()
            return 0
        return 2

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
