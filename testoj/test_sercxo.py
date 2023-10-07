import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx


if len(sys.argv) >=2 :
  fs_uzanto=sys.argv[1]
  fs_pasvorto=sys.argv[2]
else :
  fs_uzanto=None
  fs_pasvorto=None

fs_sesio = None

# krei genealogian arbon
arbo=gedcomx.Gedcomx()
dosiero='rezultoj/sercxo.fs.json'

if exists(dosiero):
  print("legas dosieron "+dosiero+".")
  f = open(dosiero,'rb')
  content = f.read()
  datumoj = json.loads(content)
  f.close()
else:
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
      if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
      if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
      fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  r = fs_sesio.get_url(
               "/platform/tree/search?q.surname=Jallobert&q.givenName=Jerome&q.sex=Male&q.birthLikeDate=+1604-12-31&q.deathLikeDate=+1636&q.anyPlace=Saint-Malo&offset=0&count=10"
              ,{"Accept": "application/x-gedcomx-atom+json"} )
  f = open(dosiero,'wb')
  f.write(r.content)
  f.close()
  datumoj=r.json()

for entry in datumoj["entries"] :
  print (entry.get("id")+ ";  score = "+str(entry.get("score")))
  data=entry["content"]["gedcomx"]
  for person in data["persons"]:
    x = gedcomx.Person(person["id"], arbo)
    gedcomx.maljsonigi(x,person)

