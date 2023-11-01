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

from .dateformal import DateFormal
from ._utila import all_annotations

def jsonigi(obj):
  """Liveras jsonigita version de obj.
  """
  if hasattr(obj, "jsonigi"):
    return obj.jsonigi()
  ko = obj.__class__.__name__
  if ( ko == 'bool' or ko == 'str' or ko == 'int' or ko == 'float') :
    return obj
  if ( ko == 'set' or ko == 'list'):
    if len(obj) == 0: return
    return [ jsonigi(o) for o in obj ]
  if ko == 'dict' :
    if len(obj) == 0: return
    x = dict()
    for k,v in obj.items() :
      json_k=jsonigi(k)
      json_v=jsonigi(v)
      if json_v:
        x[json_k] = json_v
    return x
  ser = dict()
  for a in dir(obj):
    if not a.startswith('_') and not callable(getattr(obj, a)) :
      attr = getattr(obj,a)
      a = a.replace('_','-')
      ka = attr.__class__.__name__
      if ka == 'NoneType' : continue
      if (ka == 'set' or ka == 'list' or ka == 'str' or ka == 'dict') and len(attr)==0 : continue
      ser[a] = jsonigi(attr)
  return ser

def _aldKlaso(kl2,x,parent):
  havasId = all_annotations(kl2).get("id")
  havasIndekso = all_annotations(kl2).get("_indekso")
  if kl2.__name__ == "str":
    return str(x)
  elif  ( havasId and not havasIndekso ) :
    obj = None
    if kl2.__name__ == 'SourceReference' :
      setName = 'sources'
    else:
      setName = kl2.__name__.lower()+'s'
    if (hasattr(parent, setName) and x.get("id")) :
      id = x.get("id")
      for f in getattr(parent,setName) :
        if f.id == id :
          obj = f
          break
    if not obj :
      obj = kl2()
  elif ( havasId and havasIndekso
      and x.get("id") in kl2._indekso ) :
    obj=kl2._indekso[x.get("id")]
  elif ( havasId and havasIndekso
      and x.get("id") ) :
    obj = kl2(id=x.get("id"))
  else :
    obj = kl2()
  maljsonigi(obj,x)
  if ( havasId and havasIndekso):
    if( x.get("id") ) :
      kl2._indekso[x["id"]] = obj
  return obj

def maljsonigi(obj,d, nepre=False):
  if not nepre and hasattr(obj, "maljsonigi"):
    obj.maljsonigi(d)
    return
  if not d: return
  if obj.__class__.__name__ == 'str' :
    obj=d
    return
  if obj.__class__.__name__ == 'set' :
    for v in d :
      obj.add(v)
    obj = obj.union()
    return
  for k in d :
    # serĉi ĉiu ero en la komentarioj de «obj»
    if ( k[:38] == '{http://www.w3.org/XML/1998/namespace}'):
      attrnomo = k[38:].replace('-','_')
    else:
      attrnomo = k.replace('-','_')
    ann = all_annotations(obj.__class__).get(attrnomo)
    kn = str(ann)
    if (  kn == "<class 'bool'>" ) :
      if d[k]=='true' : setattr(obj,attrnomo, True)
      elif d[k]=='false' : setattr(obj,attrnomo, False)
      else : setattr(obj,attrnomo, d[k])
    elif (  kn == "<class 'bool'>" or kn == "<class 'str'>" or kn == "<class 'int'>" or kn == "<class 'float'>" or kn == "<class 'None'>") :
      setattr(obj,attrnomo, d[k])
    elif kn == "<class 'set'>":
      attr = getattr(obj,attrnomo, None) or set()
      #attr.update(d[k])
      attr = attr.union(d[k])
      setattr(obj,attrnomo, attr)
    elif kn == "<class 'list'>":
      attr = getattr(obj,attrnomo, None) or list()
      attr.update(d[k])
      setattr(obj,attrnomo, attr)
    elif kn == "<class 'dict'>":
      attr = getattr(obj,attrnomo, None) or dict()
      attr.update(d[k])
      setattr(obj,attrnomo, attr)
    elif kn[:8] == "<class '" :
      kl2 = ann
      nova = _aldKlaso(kl2,d[k],obj)
      if nova: 
        setattr(obj,attrnomo, nova)
      else:
        print("maljsonigi:eraro : k="+k+"; d[k]="+str(d[k]))
    elif kn[:4] == 'set[' :
      kn2 = kn[4:len(kn)-1]
      if (  kn2 == 'bool' or kn2 == 'str' or kn2 == 'int' or kn2 == 'float' or kn2 == 'None') :
        attr = getattr(obj,attrnomo, None) or set()
        #attr.update(d[k])
        attr = attr.union(d[k])
        setattr(obj,attrnomo, attr)
      else :
        attr = getattr(obj,attrnomo, None) or set()
        kl2 = ann.__args__[0]
        for x in d[k] :
          nova = _aldKlaso(kl2,x, obj)
          if nova :
            trov = False
            if hasattr(kl2,"iseq"):
              for x in attr :
                if x.iseq(nova):
                  trov = True
                  break
            if not trov:
              attr.add(nova)
          else:
            print("maljsonigi:eraro :  k="+k+"; x="+str(x))
        attr = attr.union()
        setattr(obj,attrnomo, attr)
    elif kn[:9] == 'dict[str,' : # speciala kazo : dict[str,Link]
      kl2 = ann.__args__[1]
      attr = getattr(obj,attrnomo, None) or dict()
      for k2,v in d[k].items() :
        nova = _aldKlaso(kl2,v, obj)
        if nova : attr[k2] =nova
        else:
          print("maljsonigi:eraro :   k="+k+";k2="+str(k2)+"; v="+str(v)+"; kl2="+str(kl2))
      setattr(obj,attrnomo, attr)
    else:
      print("maljsonigi:nekonata ero: "+obj.__class__.__name__+":"+k)
      #from objbrowser import browse ;browse(locals())
  if not nepre and hasattr(obj, "postmaljsonigi"):
    obj.postmaljsonigi(d)

