

import sys
import json
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx

dosiero=sys.argv[1]

# krei genealogian arbon
arbo=gedcomx.Gedcomx()

# legi dosiero
f = open(dosiero,'rb')
datumoj = f.read()
f.close()
gedcomx.maljsonigi(arbo, json.loads(datumoj))

# skribi json
rezulto = gedcomx.jsonigi(arbo)
f = open('rezultoj/arbo.out.json','w')
json.dump(rezulto,f,indent=2)
f.close()

# skribi xml
xml = gedcomx.xmligi(arbo)
ET.indent(xml)
xml.write('rezultoj/arbo.out.xml',encoding='UTF-8'
    ,xml_declaration='version="1.0" standalone="yes"'
    )

