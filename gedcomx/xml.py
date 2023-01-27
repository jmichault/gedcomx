#
# Kopirajto © 2022 Jean Michault
# Licenco «GPL-3.0-or-later»
#
# Ĉi tiu programo estas libera programaro; vi povas redistribui ĝin kaj/aŭ modifi
# ĝi laŭ la kondiĉoj de la Ĝenerala Publika Permesilo de GNU kiel eldonita de
# la Free Software Foundation; ĉu versio 3 de la Licenco, aŭ
# (laŭ via elekto) ajna posta versio.
#
# Ĉi tiu programo estas distribuata kun la espero, ke ĝi estos utila,
# sed SEN AJN GARANTIO; sen eĉ la implicita garantio de
# KOMERCEBLECO aŭ TAĜECO POR APARTA CELO. Vidu la
# GNU Ĝenerala Publika Permesilo por pliaj detaloj.
#
# Vi devus esti ricevinta kopion de la Ĝenerala Publika Permesilo de GNU
# kune kun ĉi tiu programo; se ne, skribu al 
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
" NE UZI xmligi ! LABORO EN PROGRESO !!!
"""
import datetime

import xml.etree.ElementTree as ET

import gedcomx.gedcomx

from gedcomx.gedcomx import Gedcomx
from gedcomx.json import maljsonigi, all_annotations, _aldKlaso
from gedcomx.dateformal import SimplaDato

verb=False

class xmlero:
  def __init__(self):
    self._depth=0
    self._obj={ 1:self}
    self._rel={ 1:None}
    self._attr={ 1:None}
    self._eroj={ 1:'gedcomx'}
    self._klaso={ 1:self.__class__.__name__}
    self._isset={ 1:False}
    self._isdict={ 1:False}
  def start(self, tag, attrib):   # Vokita por ĉiu malferma etikedo.
    patro=self._obj.get(self._depth)
    self._depth += 1
    if self._depth == 1:
      maljsonigi(self,attrib)
      return
    if tag[:24] == '{http://gedcomx.org/v1/}':
      attrnomo=tag[24:]
    elif tag[:29] == '{http://familysearch.org/v1/}':
      attrnomo=tag[29:]
    else :
      print("AVERTO: ne konata tag: "+tag)
      return
    attrnomo = attrnomo.replace('-','_')
    if verb: print("  start:"+str(attrnomo)+" ; "+str(attrib))
    if attrnomo == 'br' :
      self._obj[self._depth-1] += "\n"
      return
    if attrnomo == 'space' :
      self._obj[self._depth-1] += " "
      return
    ann = all_annotations(patro.__class__).get(attrnomo)
    kn = str(ann)
    if ann:
      if verb : print("  simple:"+str(ann))
      kl2 = ann
      if kn[:4] == 'set[':
        self._isset[self._depth]=True
        self._isdict[self._depth]=False
        obj = getattr(patro,attrnomo, None) or kl2()
        kn2 = kn[4:len(kn)-1]
        if (  kn2 == 'bool' or kn2 == 'str' or kn2 == 'int' or kn2 == 'float' or kn2 == 'None') :
          attr = getattr(patro,attrnomo, None) or set()
          kl2 = ann.__args__[0]
          obj2 = kl2()
          if verb : print("  simple :attrib="+str(attrib))
          maljsonigi(obj2,attrib)
          attr.add(obj2)
          setattr(patro,attrnomo, attr)
        else :
          attr = getattr(patro,attrnomo, None) or set()
          kl2 = ann.__args__[0]
          obj2 = _aldKlaso(kl2,attrib,patro)
          attr.add(obj2)
          setattr(patro,attrnomo,attr)
          self._eroj[self._depth]=attrnomo
          self._obj[self._depth]=obj2
          self._klaso[self._depth]=kl2
      else: 
        obj = getattr(patro,attrnomo, None) or kl2()
        if not obj:
          obj=kl2()
        if verb : print("  simple:attrib="+str(attrib))
        maljsonigi(obj,attrib)
        setattr(patro,attrnomo,obj)
        self._eroj[self._depth]=attrnomo
        self._obj[self._depth]=obj
        self._klaso[self._depth]=ann
        self._isset[self._depth]=False
        self._isdict[self._depth]=False
      return
    if attrnomo[:6] == 'family' :
      attrnomo='families'+attrnomo[6:]
    elif attrnomo == 'child' :
      attrnomo='children'
    else :
      attrnomo=attrnomo+'s'
    self._eroj[self._depth]=attrnomo
    ann = all_annotations(patro.__class__).get(attrnomo)
    if not ann:
      print("malxmligi-start:AVERTO: depth="+str(self._depth)+" xml-ne konata ero: "+patro.__class__.__name__+"."+tag+"-attrnomo="+attrnomo)
      return
    sann = str(ann)
    self._klaso[self._depth]=ann
    if sann[:4] == 'set[':
      self._isset[self._depth]=True
      kl2 = ann.__args__[0]
      if verb: print("   set[: "+sann+" ; attrib="+str(attrib))
      attr = getattr(patro,attrnomo, None) or set()
      obj = _aldKlaso(kl2,attrib,patro)
      attr.add(obj)
      setattr(patro,attrnomo, attr)
      self._attr[self._depth]=attr
      #from objbrowser import browse ;browse(locals())
    elif sann == 'dict[str, gedcomx.gedcomx.Link]' : # speciala kazo : dict[str, Link]
      self._isdict[self._depth]=True
      kl2 = ann.__args__[1]
      if verb: print("   dict[: "+sann+" ; attrib="+str(attrib))
      attr = getattr(patro,attrnomo, None) or dict()
      rel = attrib.pop('rel')
      obj = _aldKlaso(kl2,attrib,patro)
      #from objbrowser import browse ;browse(locals())
      self._rel[self._depth]=rel
      self._attr[self._depth]=attr
      attr[rel] = obj
      setattr(patro,attrnomo, attr)
    elif sann[:9] == 'dict[str,' : # speciala kazo : dict[str, x]
      self._isdict[self._depth]=True
      kl2 = ann.__args__[1]
      if verb: print("   dict[: "+sann+" ; attrib="+str(attrib))
      attr = getattr(patro,attrnomo, None) or dict()
      rel = attrib.pop('type')
      obj = _aldKlaso(kl2,attrib,patro)
      self._rel[self._depth]=rel
      self._attr[self._depth]=attr
      attr[rel] = obj
      setattr(patro,attrnomo, attr)
    else:
      print("AVERTO: ne konata klaso: "+patro.__class__.__name__+":"+attrnomo+" - "+sann)
    self._obj[self._depth]=obj
  def end(self, tag):             # Vokita por ĉiu ferma etikedo.
    obj = self._obj.get(self._depth)
    kn = self._eroj.get(self._depth)
    isset = self._isset.get(self._depth)
    isdict = self._isdict.get(self._depth)
    self._depth -= 1
    patro = self._obj.get(self._depth)
    if verb: print("  end:"+str(kn)+" ; "+tag)
    if self._depth >= 1:
      if isset:
        pass
      elif isdict:
        pass
      else:
        if obj:
          setattr(patro,kn,obj)
      self._obj[self._depth+1] = None
      self._eroj[self._depth+1] = ''
      self._isset[self._depth+1]=False
      self._isdict[self._depth+1]=False
  def data(self, data):
    if data and not data.isspace() :
      obj = self._obj.get(self._depth)
      kn = self._eroj.get(self._depth)
      klaso = self._klaso.get(self._depth)
      isset = self._isset.get(self._depth)
      isdict = self._isdict.get(self._depth)
      if verb: print("    data:"+str(kn)+" ; "+data)
      if kn == 'modified' :
        sdato= SimplaDato(data)
        data=sdato.int()
      if obj != None and klaso and (klaso.__name__ == 'float'):
        self._obj[self._depth]=float(data)
      elif obj != None and klaso and (klaso.__name__ == 'bool'):
        if data=='true' : self._obj[self._depth]=True
        elif data=='false' : self._obj[self._depth]=False
        else : self._obj[self._depth]=str(data)
      elif obj != None and klaso and klaso.__name__ == 'int' :
        self._obj[self._depth]=int(data)
      elif obj != None and klaso and klaso.__name__ == 'str' :
        self._obj[self._depth] += data
      elif obj != None and klaso and klaso.__name__ == 'DateFormal':
        maljsonigi(obj,data)
      elif obj != None and obj.__class__.__name__ == 'set':
        obj.add(data)
      elif obj != None and klaso and klaso.__name__ == 'set' and obj.__class__.__name__ == 'TextValue':
        obj.value = data
      elif obj != None and str(klaso)[:9] == 'dict[str,':
        #from objbrowser import browse ;browse(locals())
        #obj += data
        attr = self._attr.get(self._depth)
        rel = self._rel.get(self._depth)
        attr[rel] = data
      elif obj != None and klaso and klaso.__name__ == 'set':
        obj.value = data
      elif obj != None and klaso and klaso.__name__ == 'TextValue':
        obj.value = data
      else:
        print("malxmligi:AVERTO:   "+str(self._depth)+"-data: kn="+kn+" ;"+data+";klaso="+str(klaso)+" - "+str(obj))
        if klaso :
          print("                :   klaso.__name__="+klaso.__name__)
  def close(self):    
    pass


def malxmligi(obj,d, nepre=False):
  parser=ET.XMLParser(target=obj)
  parser.feed(d)
  parser.close()


def xmligi(obj):
  r = ET.Element(obj.__class__.__name__.lower())
  r.attrib['xmlns']='http://gedcomx.org/v1/'
  r.attrib['xmlns:fs']='http://familysearch.org/v1/'
  r.attrib['xmlns:atom']='http://www.w3.org/2005/Atom'
  farixml(r,obj)
  return ET.ElementTree(r)

def farixml(r,obj):
  for a in dir(obj):
    if not a.startswith('_') and not callable(getattr(obj, a)) :
      attr = getattr(obj,a)
      if a == 'childAndParentsRelationships' :
        a='fs:childAndParentsRelationships'
      if a == 'child' :
        a='fs:child'
      if a == 'parent1' :
        a='fs:parent1'
      if a == 'parent2' :
        a='fs:parent2'
      if a == 'parent1Facts' :
        a='fs:parent1Facts'
      if a == 'parent2Facts' :
        a='fs:parent2Facts'
      ka = attr.__class__.__name__
      if ka == 'NoneType' : continue
      if (ka == 'set' or ka == 'list' or ka == 'str' or ka == 'dict') and len(attr)==0 : continue
      kn = str(ka)
      #if a == 'identifiers' :
      #  print(" kn="+kn)
      if (kn == 'str') or (kn == 'int') or (kn == 'bool') or (kn == 'float') :
        r.attrib[a]=str(attr)
      elif (kn == 'set'):
        if a[len(a)-1]=='s':
          a = a[:len(a)-1]
        for x in attr:
         sub = ET.SubElement(r,a)
         farixml(sub,x)
      elif (kn == 'dict'):
        if a[len(a)-1]=='s':
          a = a[:len(a)-1]
        for k,v in attr.items():
         sub = ET.SubElement(r,a)
         if a == 'link':
           sub.attrib['rel']=k
         elif a =='identifier' :
           #print("  k="+k)
           #print("  v="+str(v))
           sub.attrib['type']=k
           if v.__class__.__name__ == 'set' :
             unua=True
             sub.text = ''
             for x in v :
               if unua : unua=False
               else : sub.text += ','
               sub.text += x
           else :
             sub.text = v
           #from objbrowser import browse ;browse(locals())
         else:
           sub.attrib['type']=k
           print('nekonata dict: '+a)
         farixml(sub,v)
      else :
        sub = ET.SubElement(r,a)
        farixml(sub,attr)
  

class xmlGedcomx(xmlero,Gedcomx):
  pass
