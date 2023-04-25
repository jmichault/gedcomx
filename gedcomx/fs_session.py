# global imports
import sys
import time

import requests

STATO_INIT = 0
STATO_KONEKTITA = 1
STATO_PASVORTA_ERARO = -1
STATO_ERARO = -2


class FsSession:
    """Create a FamilySearch session
    :param username and password: valid FamilySearch credentials
    :param verbose: True to active verbose mode
    :param logfile: a file object or similar
    :param timeout: time before retry a request
    """

    def __init__(self, username, password, verbose=False, logfile=False, timeout=60, lingvo=None):
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
        self.logged = self.login()

    def write_log(self, text):
        """write text in the log file"""
        log = "[%s]: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text)
        if self.verbose:
            sys.stderr.write(log)
        if self.logfile:
            self.logfile.write(log)

    def login(self):
        """retrieve FamilySearch session ID
        (https://www.familysearch.org/developers/docs/guides/oauth2)
        """
        nbtry = 1
        while True:
            if nbtry > 3 :
              self.stato = STATO_ERARO
              print("too many errors")
              return False

            try:
                nbtry = nbtry + 1
                url = "https://www.familysearch.org/auth/familysearch/login"
                headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
                #headers ["Accept-Language"] = self.lingvo
                r = self.session.get(url, params={"ldsauth": False}, allow_redirects=False, headers=headers)
                import urllib
                self.client_id = urllib.parse.parse_qs(urllib.parse.urlparse(r.next.url).query)['client_id'][0]
                self.client_secret = urllib.parse.parse_qs(urllib.parse.urlparse(r.next.url).query)['client_secret'][0]
                self.redirect_uri = urllib.parse.parse_qs(urllib.parse.urlparse(r.next.url).query)['redirect_uri'][0]
                r = self.session.send(r.next)
                idx = r.text.index('name="params" value="')
                span = r.text[idx + 21 :].index('"')
                params = r.text[idx + 21 : idx + 21 + span]

                url = "https://ident.familysearch.org/cis-web/oauth2/v3/authorization"
                r = self.session.post(
                    url,
                    data={
                        "params": params,
                        "userName": self.username,
                        "password": self.password,
                        "privateComputer": False
                    },
                    timeout=self.timeout,
                    allow_redirects=False,headers=headers,
                )

                if "The username or password was incorrect" in r.text:
                    self.write_log("The username or password was incorrect")
                    self.stato = STATO_PASVORTA_ERARO
                    return False

                if "Invalid Oauth2 Request" in r.text:
                    self.write_log("Invalid Oauth2 Request")
                    time.sleep(self.timeout)
                    continue

                # get the authorization code from redirect url :
                self.code = urllib.parse.parse_qs(urllib.parse.urlparse(r.next.url).query)['code'][0]
                self.fssessionid = r.next._cookies["familysearch-sessionid"]
                url = 'https://ident.familysearch.org/cis-web/oauth2/v3/token'
                r = self.session.post(
                    url,
                    timeout=self.timeout,
                    headers=headers,
                    data={
                       "code": self.code,
                       "client_id": self.client_id,
                       "client_secret": self.client_secret,
                       "redirect_uri": self.redirect_uri,
                       "grant_type": 'authorization_code',
                      },
                    allow_redirects=False
                )
                self.access_token = r.json()['access_token']
            except requests.exceptions.ReadTimeout:
                self.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            except requests.exceptions.HTTPError:
                self.write_log("HTTPError")
                time.sleep(self.timeout)
                continue
            except KeyError:
                self.write_log("KeyError")
                print(r.content)
                time.sleep(self.timeout)
                continue
            except ValueError:
                self.write_log("ValueError")
                time.sleep(self.timeout)
                continue

            self.stato = STATO_KONEKTITA
            url = "/platform/users/current?access_token="+self.access_token
            r = self.session.get(
                    "https://www.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
                    allow_redirects=False
                )
            if r:
              data=r.json()
              if data:
                self.fid = data["users"][0]["personId"]
                if not self.lingvo :
                  self.lingvo = data["users"][0]["preferredLanguage"]
                self.display_name = data["users"][0]["displayName"]
            return True

    def post_url(self, url, datumoj, headers=None):
        if headers is None:
            headers = {"Accept": "application/x-gedcomx-v1+json","Content-Type": "application/x-gedcomx-v1+json"}
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        headers ["Authorization"] = 'Bearer '+self.access_token
        nbtry = 1
        while True:
            try:
                if nbtry > 3 :
                  self.stato = STATO_ERARO
                  return None
                nbtry = nbtry + 1
                self.write_log("Downloading :" + url)
                r = self.session.post(
                    "https://api.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
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
            if r.status_code in {400, 404, 405, 406, 410, 500}:
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
        self.counter += 1
        if headers is None:
            headers = {"Accept": "application/x-gedcomx-v1+json"}
        if "Accept-Language" not in headers and self.lingvo :
            headers ["Accept-Language"] = self.lingvo
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        headers ["Authorization"] = 'Bearer '+self.access_token
        nbtry = 1
        while True:
            try:
                if nbtry > 3 :
                  self.stato = STATO_ERARO
                  return None
                nbtry = nbtry + 1
                self.write_log("Downloading :" + url)
                r = self.session.head(
                    "https://www.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
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
        self.counter += 1
        if headers is None:
            headers = {"Accept": "application/x-gedcomx-v1+json"}
        if "Accept-Language" not in headers and self.lingvo:
            headers ["Accept-Language"] = self.lingvo
        headers.update( {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        headers ["Authorization"] = 'Bearer '+self.access_token
        nbtry = 0
        while True:
            nbtry = nbtry + 1
            if nbtry > 3 :
              self.stato = STATO_ERARO
              return None
            try:
                self.write_log("Downloading :" + url)
                r = self.session.get(
                    "https://www.familysearch.org" + url,
                    timeout=self.timeout,
                    headers=headers,
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
                print("headers="+str(r.headers))
                return r
            if r.status_code == 401:
                return r
                self.login()
                continue
            if r.status_code in {400, 404, 405, 406, 410, 500}:
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
            self.write_log("WARNING: corrupted file from %s, error: %s" % (url, e))
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
