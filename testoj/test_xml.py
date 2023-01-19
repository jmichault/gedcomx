
import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx

fs_sesio = None

# krei genealogian arbon
arbo=gedcomx.xmlGedcomx()

import re

def akiri_dos(dosiero):
  global arbo
  if exists(dosiero):
    print("legas dosieron "+dosiero+".")
    f = open(dosiero,'rb')
    datumoj = f.read()
    f.close()
    # !!! FamilySearch ne respektas xml-specifojn, kaj enmetas novliniojn kaj pluraj malplenaj en valorojn.
    # Do ni anstataŭigas la linirompojn por ke la analizilo rekonu ilin.
    # Ĉi tio ne solvas la problemon, ke pluraj malplenaj estas anstataŭigitaj per unu !
    datumoj = re.sub(rb'([^>])\n',rb'\1<br/>',datumoj)
    f = open('xmlre.xml','wb')
    f.write(datumoj)
    f.close()
    if not datumoj or datumoj == "":
      print("ne datumojn.")
      return
    gedcomx.malxmligi(arbo, datumoj)
    return
  print("dosiero ne trovita "+dosiero+".")

arbo=gedcomx.xmlGedcomx()
akiri_dos('rezultoj/arbo.out.xml')
rezulto = gedcomx.jsonigi(arbo)
f = open('rezultoj/arboxml.out2.json','w')
json.dump(rezulto,f,indent=2)
f.close()

