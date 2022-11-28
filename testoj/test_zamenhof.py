
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx


if len(sys.argv) >=3 :
  fs_uzanto=sys.argv[1]
  fs_pasvorto=sys.argv[2]
else :
  fs_uzanto=None
  fs_pasvorto=None

# fs id de Ludwik Łazarz Zamenhof
fsid='2HMS-88F'
# fs id de Adam Zamenhof
fsid2='2HMS-8MZ'


fs_sesio = None

# krei genealogian arbon
arbo=gedcomx.Gedcomx()

def akiri_persono_de_url(fsid):
  global fs_sesio
  global fs_uzanto
  global fs_pasvorto
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
    if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
    if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
    fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  
  datumoj = fs_sesio.get_url("/platform/tree/persons/"+fsid
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "eo"} )
  gedcomx.maljsonigi(arbo,datumoj.json())
  # 
  f = open('rezultoj/person.'+fsid+'.fs.json','wb')
  f.write(datumoj.content)
  f.close()

def akiri_persono_de_dosiero(fsid):
  f = open('rezultoj/person.'+fsid+'.fs.json','rb')
  datumoj = f.read()
  f.close()
  gedcomx.maljsonigi(arbo, json.loads(datumoj))

if exists('rezultoj/person.'+fsid+'.fs.json'):
  akiri_persono_de_dosiero(fsid)
else:
  akiri_persono_de_url(fsid)

rezulto = gedcomx.jsonigi(arbo)

f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx.xmligi(arbo)

ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

if exists('rezultoj/person.'+fsid2+'.fs.json'):
  akiri_persono_de_dosiero(fsid2)
else:
  akiri_persono_de_url(fsid2)

rezulto = gedcomx.jsonigi(arbo)

f = open('rezultoj/arbo2.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx.xmligi(arbo)

ET.indent(xml)
xml.write('rezultoj/arbo2.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

