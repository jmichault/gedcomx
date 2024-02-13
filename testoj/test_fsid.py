
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx_v1


# fs id de Ludwik Łazarz Zamenhof
fsid='2HMS-88F'
if len(sys.argv) >=3 :
  fs_uzanto=sys.argv[1]
  fs_pasvorto=sys.argv[2]
else :
  fs_uzanto=None
  fs_pasvorto=None
if len(sys.argv) >=4 :
  fsid=sys.argv[3]

fs_sesio = None

# krei genealogian arbon
arbo=gedcomx_v1.Gedcomx()

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
      gedcomx_v1.maljsonigi(arbo, jsonDat)
    except:
      print("ne validan json-datumojn.")
    return
  print("legas url "+url+".")
  global fs_sesio
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
    global fs_uzanto
    global fs_pasvorto
    if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
    if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
    fs_sesio = gedcomx_v1.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  if not fs_sesio.logged :
    fs_sesio.login()
  r = fs_sesio.get_url(url
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "fr"} )
  f = open(dosiero,'wb')
  f.write(r.content)
  f.close()
  #print(r.headers)
  if r and r.status_code == 200:
    gedcomx_v1.maljsonigi(arbo,r.json())
  else:
    print("url "+url+" ne trovita.")

def akiri_personon(fsid):
    akiri_url_aux_dos("/platform/tree/persons/"+fsid,'rezultoj/person.'+fsid+'.fs.json')

akiri_personon(fsid)

rezulto = gedcomx_v1.jsonigi(arbo)
f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx_v1.xmligi(arbo)
ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

