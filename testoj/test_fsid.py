
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
  # fs id de Ludwik Łazarz Zamenhof
  fsid='2HMS-88F'

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
      gedcomx.maljsonigi(arbo, jsonDat)
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
    fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  r = fs_sesio.get_url(url
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "fr"} )
  f = open(dosiero,'wb')
  f.write(r.content)
  f.close()
  if r and r.status_code == 200:
    gedcomx.maljsonigi(arbo,r.json())
  else:
    print("url "+url+" ne trovita.")

def akiri_personon(fsid):
    akiri_url_aux_dos("/platform/tree/persons/"+fsid,'rezultoj/person.'+fsid+'.fs.json')

def akiri_gepatroj(arbo,fsid):
  persono = gedcomx.Person._indekso[fsid]
  rels = set()
  for paro in persono._gepatroj :
    rels |= {paro.person1.resourceId , paro.person2.resourceId }
  for cp in persono._gepatrojCP :
    if cp.parent1:
      rels |= {cp.parent1.resourceId }
    if cp.parent2:
      rels |= {cp.parent2.resourceId }
  rels.difference_update({fsid})
  for fsid in rels:
    akiri_personon(fsid)

akiri_personon(fsid)

akiri_gepatroj(arbo,fsid)

for fsPersono in arbo.persons :
  # notoj
  akiri_url_aux_dos("/platform/tree/persons/%s/notes" % fsPersono.id
            ,'rezultoj/person_notes.'+fsPersono.id+'.fs.json')
  # fontoj
  akiri_url_aux_dos("/platform/tree/persons/%s/sources" % fsPersono.id
            ,'rezultoj/person_sources.'+fsPersono.id+'.fs.json')
  # memories
  akiri_url_aux_dos("/platform/tree/persons/%s/memories" % fsPersono.id
            ,'rezultoj/person_memories.'+fsPersono.id+'.fs.json')

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
