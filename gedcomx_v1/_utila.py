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

from collections import ChainMap

try:
    from annotationlib import get_annotations
except ImportError:
    from inspect import get_annotations


def all_annotations(klaso) -> ChainMap:
    """Return annotations defined by the class and its base classes."""
    annotations = []
    for base_class in klaso.__mro__:
        try:
            class_annotations = get_annotations(base_class, eval_str=True)
        except (NameError, TypeError, AttributeError):
            class_annotations = {}
        if class_annotations:
            annotations.append(class_annotations)
    return ChainMap(*annotations)


def klaso_ini(obj):
  for atr,k2 in all_annotations(obj.__class__).items() :
     if k2 == set or k2 == dict :
       setattr(obj,atr,k2())
     elif str(k2)[:4] == 'set[' :
       setattr(obj,atr,set())
     elif str(k2)[:5] == 'dict[' :
       setattr(obj,atr,dict())
     else :
       setattr(obj,atr,None)


