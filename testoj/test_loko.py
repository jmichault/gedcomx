
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx


if len(sys.argv) >=4 :
  fs_uzanto=sys.argv[1]
  fs_pasvorto=sys.argv[2]
  fsid=sys.argv[3]
else :
  fs_uzanto=None
  fs_pasvorto=None
  # fs id de Paris 9
  fsid='11928800'

fs_sesio = None

# krei genealogian arbon
arbo=gedcomx.Gedcomx()

def akiri_url_aux_dos(url,dosiero):
  global arbo
  if exists(dosiero):
    print("legas dosieron "+dosiero+".")
    f = open(dosiero,'rb')
    datumoj = f.read()
    f.close()
    if not datumoj or datumoj == "":
      print("ne datumojn.")
      return
    try:
      jsonDat = json.loads(datumoj)
    except:
      print("ne validan json-datumojn.")
    gedcomx.maljsonigi(arbo, jsonDat)
    return
  print("legas url "+url+".")
  global fs_sesio
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
    global fs_uzanto
    global fs_pasvorto
    if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
    if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
    fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  if not fs_sesio.logged :
    fs_sesio.login()
  r = fs_sesio.get_url(url
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "fr,en,de,es"} )
  f = open(dosiero,'wb')
  f.write(r.content)
  f.close()
  if r and r.status_code == 200:
    gedcomx.maljsonigi(arbo,r.json())
  else:
    print("url "+url+" ne trovita.")

akiri_url_aux_dos("/platform/places/description/%s" % fsid
            ,'rezultoj/loko.description.'+fsid+'.fs.json')

# 
rezulto = gedcomx.jsonigi(arbo)
f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx.xmligi(arbo)
ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

