# global imports
import sys
import time

import requests
import urllib

STATO_INIT = 0
STATO_LOGIN = 1
STATO_KONEKTITA = 2
STATO_PASVORTA_ERARO = -1
STATO_ERARO = -2

vorteco=1
#import pdb; pdb.set_trace()

class FsSession:
    """Create a FamilySearch session
    :param username and password: valid FamilySearch credentials
    :param verbose: True to active verbose mode
    :param logfile: a file object or similar
    :param timeout: time before retry a request
    :param lingvo:
    :param client_id: FamilySearch client_id
    """

    def __init__(self, username=None, password=None, verbose=False, logfile=False, timeout=60, lingvo=None, client_id=None):
        self.username = username
        self.password = password
        self.verbose = verbose
        self.logfile = logfile
        self.timeout = timeout
        self.fid = self.display_name = None
        self.counter = 0
        self.lingvo = lingvo
        self.stato = STATO_INIT
        self.session = requests.session()
        self.logged = False
        self.client_id = client_id
        self.ip_address = None
        self.redirect_uri = None
        self.state = None
        self.private = None

    def write_log(self, text):
        """write text in the log file"""
        log = "[%s]: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text)
        if self.verbose or vorteco>0 :
            sys.stderr.write(log)
        if self.logfile:
            self.logfile.write(log)


    def login_credentials(self) :
        print("!!!Désolé, l'authentification de type «client_credentials» n'a pas été testée")
        self.logged = False
        self.stato = STATO_LOGIN
        if not self.client_id :
          print("vous avez besoin d'un client_id pour une authentification de type «client_credentials»")
          self.stato = STATO_ERARO
          return False
        if not self.private :
          print("vous avez besoin d'une clé privée pour une authentification de type «client_credentials»")
          self.stato = STATO_ERARO
          return False
        timestamp = format(time.time(),'.3f').encode('utf8')
        import rsa,base64
        secret = base64.b64encode(rsa.sign(timestamp,self.private,'SHA-512'))
        data = {
                   "grant_type": 'client_credentials',
                   "client_id": self.client_id,
                   "client_secret": secret,
                 }
        url = 'https://ident.familysearch.org/cis-web/oauth2/v3/token'
        r = self.post_url(url,data)
        if vorteco :
          print(" étape client_credentials, r="+str(r))
          print("        , r.text="+r.text)
        json = r.json()
        if json and json.get('access_token') :
          self.access_token = r.json()['access_token']
          print("FamilySearch-ĵetono akirita")
          self.logged = True
          self.stato = STATO_KONEKTITA
          return True
        else:
          print(" échec de connexion")
          return False


    def login_password(self):
        self.logged = False
        self.stato = STATO_LOGIN
        if not self.client_id :
          print("vous avez besoin d'un client_id pour une authentification de type «password»")
          self.stato = STATO_ERARO
          return False
        data = {
                   "grant_type": 'password',
                   "client_id": self.client_id,
                   "username": self.username,
                   "password": self.password,
                 }
        url = 'https://ident.familysearch.org/cis-web/oauth2/v3/token'
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
        r = self.post_url(url,data,headers)
        if vorteco :
          print(" étape anon, r="+str(r))
          print("        , r.text="+r.text)
        json = r.json()
        if json and json.get('access_token') :
          self.access_token = r.json()['access_token']
          print("FamilySearch-ĵetono akirita")
          self.logged = True
          self.stato = STATO_KONEKTITA
          return True

    def login(self):
        """retrieve FamilySearch session ID
        (https://www.familysearch.org/developers/docs/guides/oauth2)
        """
        self.logged = False
        self.stato = STATO_LOGIN
        # étape 1 : on appelle login, pour récupérer XSRF-TOKEN et client_id
        url = "https://www.familysearch.org/auth/familysearch/login"
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
        r = self.session.get(url, headers=headers)
        self.xsrf = self.session.cookies["XSRF-TOKEN"]
        # étape 2 : on appelle /login
        url = "https://ident.familysearch.org/login"
        data = {
                "_csrf": self.xsrf,
                "username": self.username,
                "password": self.password,
               }
        r = self.session.post(url,data)
        # étape 3 : on suit redirectUrl pour valider
        try:
          data = r.json()
        except ValueError:
          self.write_log("Invalid auth request")
          return
        if "loginError" in data:
          self.write_log(data["loginError"])
          return
        if "redirectUrl" not in data:
          self.write_log(res.text)
          return
        url = data["redirectUrl"]
        try :
          r = self.session.get(url, headers=headers)
        except TooManyRedirects :
          pass
        self.logged = True
        self.stato = STATO_KONEKTITA


    def post_url(self, url, datumoj, headers=None):
        if not self.logged and self.stato==STATO_INIT:
          self.login()
        if headers is None:
          headers = {"Accept": "application/x-gedcomx-v1+json","Content-Type": "application/x-gedcomx-v1+json"}
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        cookies = None
        if hasattr(self,'access_token') :
          headers ["Authorization"] = 'Bearer '+self.access_token
        if url[0:4] != 'http' :
          url="https://api.familysearch.org" + url
        nbtry = 1
        while True:
            try:
                if nbtry > 3 :
                  self.stato = STATO_ERARO
                  self.logged = False
                  return None
                nbtry = nbtry + 1
                self.write_log("Downloading :" + url)
                r = self.session.post(
                    url,
                    timeout=self.timeout,
                    headers=headers,
                    cookies=cookies,
                    data=datumoj,
                    allow_redirects=False
                )
            except requests.exceptions.ReadTimeout:
                self.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            self.write_log("Status code: %s" % r.status_code)
            if r.status_code == 204:
                self.write_log("headers="+str(r.headers))
                return r
            if r.status_code == 401:
                self.login()
                continue
            if r.status_code == 400:
                self.write_log("WARNING 400: " + url)
                return None
            if r.status_code in { 404, 405, 406, 410, 500}:
                self.write_log("WARNING: " + url)
                self.write_log(r)
                return r
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                self.write_log("HTTPError")
                if r.status_code == 403:
                    if (
                        "message" in r.json()["errors"][0]
                        and r.json()["errors"][0]["message"]
                        == "Unable to get ordinances."
                    ):
                        self.write_log(
                            "Unable to get ordinances. "
                            "Try with an LDS account or without option -c."
                        )
                        return "error"
                    self.write_log(
                        "WARNING: code 403 from %s %s"
                        % (url, r.json()["errors"][0]["message"] or "")
                    )
                    return r
                time.sleep(self.timeout)
                continue
            try:
                return r
            except Exception as e:
                self.write_log("WARNING: corrupted file from %s, error: %s" % (url, e))
                return None

    def put_url(self, url, datumoj, headers=None):
        if not self.logged and self.stato==STATO_INIT:
          self.login()
        if headers is None:
          headers = {"Accept": "application/x-gedcomx-v1+json","Content-Type": "application/x-gedcomx-v1+json"}
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        cookies = None
        if hasattr(self,'access_token') :
          headers ["Authorization"] = 'Bearer '+self.access_token
        if url[0:4] != 'http' :
          url="https://api.familysearch.org" + url
        nbtry = 1
        while True:
            try:
                if nbtry > 3 :
                  self.stato = STATO_ERARO
                  self.logged = False
                  return None
                nbtry = nbtry + 1
                self.write_log("Downloading :" + url)
                r = self.session.put(
                    url,
                    timeout=self.timeout,
                    headers=headers,
                    #cookies=cookies,
                    data=datumoj,
                    allow_redirects=False
                )
            except requests.exceptions.ReadTimeout:
                self.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            self.write_log("Status code: %s" % r.status_code)
            if r.status_code == 204:
                self.write_log("headers="+str(r.headers))
                return r
            if r.status_code == 401:
                self.login()
                continue
            if r.status_code == 400:
                self.write_log("WARNING 400: " + url)
                return None
            if r.status_code in { 404, 405, 406, 410, 500}:
                self.write_log("WARNING: " + url)
                self.write_log(r)
                return r
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                self.write_log("HTTPError")
                if r.status_code == 403:
                    if (
                        "message" in r.json()["errors"][0]
                        and r.json()["errors"][0]["message"]
                        == "Unable to get ordinances."
                    ):
                        self.write_log(
                            "Unable to get ordinances. "
                            "Try with an LDS account or without option -c."
                        )
                        return "error"
                    self.write_log(
                        "WARNING: code 403 from %s %s"
                        % (url, r.json()["errors"][0]["message"] or "")
                    )
                    return r
                time.sleep(self.timeout)
                continue
            try:
                return r
            except Exception as e:
                self.write_log("WARNING: corrupted file from %s, error: %s" % (url, e))
                return None

    def head_url(self, url, headers=None):
        if not self.logged :
          self.login()
        self.counter += 1
        if headers is None:
            headers = {"Accept": "application/x-gedcomx-v1+json"}
        if "Accept-Language" not in headers and self.lingvo :
            headers ["Accept-Language"] = self.lingvo
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        cookies = None
        if hasattr(self,'access_token') :
          headers ["Authorization"] = 'Bearer '+self.access_token
        nbtry = 1
        while True:
            try:
                if nbtry > 3 :
                  self.stato = STATO_ERARO
                  self.logged = False
                  return None
                nbtry = nbtry + 1
                self.write_log("Downloading :" + url)
                r = self.session.head(
                    "https://www.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
                    cookies=cookies,
                )
            except requests.exceptions.ReadTimeout:
                self.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            if r.status_code == 401:
                self.login()
                continue
            return r

    def get_url(self, url, headers=None):
        if not self.logged :
          self.login()
        self.counter += 1
        if headers is None:
            headers = {"Accept": "application/x-gedcomx-v1+json"}
        if "Accept-Language" not in headers and self.lingvo:
            headers ["Accept-Language"] = self.lingvo
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        cookies = None
        if hasattr(self,'access_token') :
          headers ["Authorization"] = 'Bearer '+self.access_token
        nbtry = 0
        while True:
            nbtry = nbtry + 1
            if nbtry > 3 :
              self.stato = STATO_ERARO
              self.logged = False
              return None
            try:
                self.write_log("Downloading :" + url)
                r = self.session.get(
                    "https://www.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
                    cookies=cookies,
                    allow_redirects=False
                )
            except requests.exceptions.ReadTimeout:
                self.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            if r.status_code == 204 or r.status_code == 301:
                self.write_log("Status code: %s" % r.status_code)
                print("headers="+str(r.headers))
                return r
            if r.status_code == 401:
                return r
                self.login()
                continue
            if r.status_code == 400:
                self.write_log("WARNING 400: " + url)
                return None
            if r.status_code in { 404, 405, 406, 410, 500}:
                self.write_log("WARNING: " + url)
                self.write_log(r.text)
                return None
            #else:
            #    self.write_log("WARNING: " + url)
            #    self.write_log(r.json())
            #    return None
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                self.write_log("HTTPError")
                if r.status_code == 403:
                    if (
                        "message" in r.json()["errors"][0]
                        and r.json()["errors"][0]["message"]
                        == "Unable to get ordinances."
                    ):
                        self.write_log(
                            "Unable to get ordinances. "
                            "Try with an LDS account or without option -c."
                        )
                        return "error"
                    self.write_log(
                        "WARNING: code 403 from %s %s"
                        % (url, r.json()["errors"][0]["message"] or "")
                    )
                    return None
                time.sleep(self.timeout)
                continue
            return r

    def get_jsonurl(self, url, headers=None):
        """retrieve JSON structure from a FamilySearch URL"""
        r = self.get_url(url,headers)
        if r:
          try:
            return r.json()
          except Exception as e:
            self.write_log("WARNING:  corrupted file from %s, error: %s" % (url, e))
            print(r.content)
            return None

    def set_current(self):
        """retrieve FamilySearch current user ID, name and language"""
        url = "/platform/users/current"
        data = self.get_jsonurl(url)
        if data:
            self.fid = data["users"][0]["personId"]
            if not self.lingvo :
              self.lingvo = data["users"][0]["preferredLanguage"]
            self.display_name = data["users"][0]["displayName"]

    def _(self, string):
        """translate a string into user's language
        TODO replace translation file for gettext format
        """
        if string in translations and self.lingvo in translations[string]:
            return translations[string][self.lingvo]
        return string
