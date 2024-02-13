
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx_v1


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
arbo=gedcomx_v1.Gedcomx()

def akiri_persono_de_url(fsid):
  global fs_sesio
  global fs_uzanto
  global fs_pasvorto
  global arbo
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
    if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
    if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
    fs_sesio = gedcomx_v1.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  if not fs_sesio.logged :
    fs_sesio.login()
  
  datumoj = fs_sesio.get_url("/platform/tree/persons/"+fsid
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "fr"} )
  gedcomx_v1.maljsonigi(arbo,datumoj.json())
  # 
  f = open('rezultoj/person.'+fsid+'.fs.json','wb')
  f.write(datumoj.content)
  f.close()

def akiri_persono_de_dosiero(fsid):
  f = open('rezultoj/person.'+fsid+'.fs.json','rb')
  datumoj = f.read()
  f.close()
  gedcomx_v1.maljsonigi(arbo, json.loads(datumoj))

def akiri_gepatroj(arbo,fsid):
  persono = gedcomx_v1.Person._indekso[fsid]
  rels = set()
  for paro in persono._gepatroj :
    rels |= {paro.person1.resourceId , paro.person2.resourceId }
  for cp in persono._gepatrojCP :
    rels |= {cp.parent1.resourceId , cp.parent2.resourceId }
  rels.difference_update({fsid})
  for fsid in rels:
    if exists('rezultoj/person.'+fsid+'.fs.json'):
      akiri_persono_de_dosiero(fsid)
    else:
      akiri_persono_de_url(fsid)

if exists('rezultoj/person.'+fsid+'.fs.json'):
  akiri_persono_de_dosiero(fsid)
else:
  akiri_persono_de_url(fsid)
akiri_gepatroj(arbo,fsid)

rezulto = gedcomx_v1.jsonigi(arbo)

f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx_v1.xmligi(arbo)

ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

if exists('rezultoj/person.'+fsid2+'.fs.json'):
  akiri_persono_de_dosiero(fsid2)
else:
  akiri_persono_de_url(fsid2)

rezulto = gedcomx_v1.jsonigi(arbo)

f = open('rezultoj/arbo2.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

xml = gedcomx_v1.xmligi(arbo)

ET.indent(xml)
xml.write('rezultoj/arbo2.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

