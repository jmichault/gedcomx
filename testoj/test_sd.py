
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx_v1


if len(sys.argv) >=4 :
  fs_uzanto=sys.argv[1]
  fs_pasvorto=sys.argv[2]
  fsid=sys.argv[3]
else :
  fs_uzanto=None
  fs_pasvorto=None
  # fs id de Ferdinand Michault
  fsid='3HB2-CPT'

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
    gedcomx_v1.malxmligi(arbo, datumoj)
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
  #import pdb; pdb.set_trace()
  r = fs_sesio.get_url(url
            ,{"Accept": "application/xml", "Accept-Language": "fr,en,de,es"} )
  f = open(dosiero,'wb')
  f.write(r.content)
  f.close()
  if r and r.status_code == 200:
    gedcomx_v1.malxmligi(arbo,r.content)
  else:
    print("url "+url+" ne trovita.")

#akiri_url_aux_dos("/platform/sources/descriptions/%s" % fsid
akiri_url_aux_dos("/service/tree/links/sources/%s" % fsid
            ,'rezultoj/sd.description.'+fsid+'.fs.xml')

# 
rezulto = gedcomx_v1.jsonigi(arbo)
f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx_v1.xmligi(arbo)
ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

