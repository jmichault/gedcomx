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

# https://github.com/FamilySearch/gedcomx/blob/master/specifications/json-format-specification.md
# https://github.com/FamilySearch/gedcomx/blob/master/specifications/conceptual-model-specification.md
# https://www.familysearch.org/developers/docs/api/gx_json
# https://www.familysearch.org/developers/docs/api/fs_json
 
from collections import ChainMap

from .dateformal import DateFormal
from ._utila import all_annotations, klaso_ini

# gedcomx klasoj
class ExtensibleData:
  _indekso = None
  id: str
  def __init__(self,id=None,tree=None):
    klaso_ini(self)
    if id and cls._indekso:
      self.__class__._indekso[id]=self
  def __new__(cls,id=None,tree=None):
    if id and cls._indekso and id in cls._indekso:
      return cls._indekso[id]
    else:
      return super(ExtensibleData, cls).__new__(cls)

class HasText:
  text: str
  def __init__(self):
    klaso_ini(self)

class Link:
  href: str
  template: str
  title: str
  type: str
  accept: str
  allow: str
  hreflang: str
  count: int
  offset: int
  results: int
  def __init__(self):
    klaso_ini(self)

class Qualifier:
  name: str
  value: str
  def __init__(self):
    klaso_ini(self)

class HypermediaEnabledData(ExtensibleData):
  links: dict[str,Link]

class ResourceReference:
  resourceId: str
  resource: str
  def __init__(self):
    klaso_ini(self)

class Attribution(ExtensibleData):
  contributor: ResourceReference
  modified: int
  changeMessage: str
  changeMessageResource: str
  creator: 	ResourceReference
  created: int

class Tag:
  resource: str

class OnlineAccount(ExtensibleData):
  serviceHomepage: ResourceReference
  accountName: str

class TextValue:
  lang: str
  value: str
  def __init__(self):
    klaso_ini(self)
  def iseq(self,other):
    if isinstance(other,TextValue):
      return (self.lang == other.lang and self.value == other.value)
    return False

# https://www.familysearch.org/developers/docs/api/types/json_Agent
class Agent(HypermediaEnabledData):
  identifiers: dict[str]
  names: set[TextValue]
  homepage: ResourceReference
  openid: ResourceReference
  accounts: set[OnlineAccount]
  emails: set [ResourceReference]
  phones: set [ResourceReference]
  addresses: set [ResourceReference]
  person: ResourceReference

class SourceReference(HypermediaEnabledData):
  _indekso: dict = dict()
  description: str
  descriptionId: str
  attribution: Attribution
  qualifiers: set[Qualifier]
  # fs :
  tags: set[Tag]

class ReferencesSources:
  sources: set[SourceReference]
  def __init__(self):
    klaso_ini(self)

class VocabElement:
  id: str
  uri: str
  subclass: str
  type: str
  sortName: str
  labels: set[TextValue]
  descriptions: set[TextValue]
  sublist: str
  position: int
  def __init__(self):
    klaso_ini(self)

class VocabElementList:
  id: str
  title: str
  description: str
  uri: str
  elements: set[VocabElement]
  def __init__(self):
    klaso_ini(self)

class FamilyView(HypermediaEnabledData):
  parent1: ResourceReference
  parent2: ResourceReference
  children: set[ResourceReference]
  def __init__(self):
    klaso_ini(self)

class Date(ExtensibleData):
  """
  " original: str
  " formal: DateFormal
  """
  original: str
  formal: DateFormal
  normalized: set[TextValue]
  confidence: str

  def __str__(self):
   if self.formal :
      return str(self.formal)
   elif self.original :
      return self.original
   else : return ''
    
class DisplayProperties(ExtensibleData):
  name: str
  gender: str
  lifespan: str
  birthDate: str
  birthPlace: str
  deathDate: str
  deathPlace: str
  marriageDate: str
  marriagePlace: str
  ascendancyNumber: str
  descendancyNumber: str
  relationshipDescription: str
  familiesAsParent: set[FamilyView]
  familiesAsChild: set[FamilyView]
  role: str

class Note(HypermediaEnabledData):
  subject: str
  text: str
  attribution: Attribution
  lang: str

class HasNotes:
  notes: set[Note]
  def __init__(self):
    klaso_ini(self)

class Conclusion(HypermediaEnabledData):
  attribution: Attribution
  sources: set[SourceReference]
  analysis: ResourceReference
  notes: set[Note]
  lang: str
  confidence: str
  sortKey: str

class CitationField:
  # FARINDAĴO : ne dokumenta klaso ???
  def __init__(self):
    klaso_ini(self)

class SourceCitation(TextValue,HypermediaEnabledData):
  citationTemplate: ResourceReference
  fields: set[CitationField]

class PlaceReference(ExtensibleData):
  original: str
  normalized: set[TextValue]
  description: str
  confidence: str
  latitude: float # family search !
  longitude: float # family search !
  names: set[TextValue] # family search !

class HasDateAndPlace:
  date: Date
  place: PlaceReference
  def __init__(self):
    klaso_ini(self)

class Fact(Conclusion):
  _indekso: dict = dict()
  date: Date
  place: PlaceReference
  value: str
  qualifiers: set[Qualifier]
  type: str

class HasFacts:
  facts: set[Fact]
  def __init__(self):
    klaso_ini(self)

class Qualifier:
  name: str
  value: str
  def __init__(self):
    klaso_ini(self)

class NamePart(ExtensibleData):
  type: str
  value: str
  qualifiers: set[Qualifier]

class NameForm(ExtensibleData):
  lang: str
  parts: set[NamePart]
  fullText: str
  nameFormInfo: str  # family search !
  def iseq(self,other):
    if isinstance(other,NameForm):
      return (self.lang == other.lang and self.fullText == other.fullText)
    return False

class Name(Conclusion):
  preferred: bool
  date: Date
  nameForms: set[NameForm]
  type: str
  #def postmaljsonigi(self,d):
  #  """ forigi duplikatajn nomformojn
  #  """
  #  nfs=set()
  #  for nf in self.nameForms:
  #    trov = False
  #    for nf2 in nfs:
  #      #if nf.lang == nf2.lang and nf.fullText==nf2.fullText:
  #      if nf.lang == nf2.lang and nf.fullText==nf2.fullText:
  #        trov=True
  #        break
  #    if not trov:
  #      nfs.add(nf)
  #  self.nameForms = nfs
  def akSurname(self):
    """ akiri familian nomon
    """
    for nf in self.nameForms:
      for p in nf.parts :
        if p.type == 'http://gedcomx.org/Surname':
          return p.value
    return ''
  def akGiven(self):
    """ akiri la antaŭnomon
    """
    for nf in self.nameForms:
      for p in nf.parts :
        if p.type == 'http://gedcomx.org/Given':
          return p.value
    return ''

class EvidenceReference(HypermediaEnabledData):
  _indekso: dict = dict()
  resource: str
  resourceId: str
  attribution: Attribution

class Subject(Conclusion):
  evidence: set[EvidenceReference]
  media: set[SourceReference]
  identifiers: dict[str,set]
  extracted: bool

class Gender(Conclusion):
  type: str

class PersonInfo:
  canUserEdit: bool
  privateSpaceRestricted: bool
  readOnly: bool
  visibleToAll: bool
  def __init__(self):
    klaso_ini(self)

class Relationship(Subject):
  _indekso: dict = dict()
  person1: ResourceReference
  person2: ResourceReference
  facts: set[Fact]
  type: str
  def postmaljsonigi(self,d):
  #  """ 
  #  """
    if self.type == 'http://gedcomx.org/ParentChild' :
      if self.person2 and self.person2.resourceId in Person._indekso :
        child = Person._indekso[self.person2.resourceId]
        child._gepatroj.add(self)
      if self.person1 and self.person1.resourceId in Person._indekso :
        parent = Person._indekso[self.person1.resourceId]
        parent._infanoj.add(self)
    if self.type == 'http://gedcomx.org/Couple' :
      if self.person1 and self.person1.resourceId in Person._indekso :
        edzo = Person._indekso[self.person1.resourceId]
        edzo._paroj.add(self)
      if self.person2 and self.person2.resourceId in Person._indekso :
        edzo = Person._indekso[self.person2.resourceId]
        edzo._paroj.add(self)

class ChildAndParentsRelationship(Subject):
  _indekso: dict = dict()
  # https://www.familysearch.org/developers/docs/api/types/json_ChildAndParentsRelationship
  parent1: ResourceReference
  parent2: ResourceReference
  child: ResourceReference
  parent1Facts: set[Fact]
  parent2Facts: set[Fact]
  def postmaljsonigi(self,d):
   if self.child and self.child.resourceId in Person._indekso :
     child = Person._indekso[self.child.resourceId]
     child._gepatrojCP.add(self)
   if self.parent1 and self.parent1.resourceId in Person._indekso :
     parent = Person._indekso[self.parent1.resourceId]
     parent._infanojCP.add(self)
   if self.parent2 and self.parent2.resourceId in Person._indekso :
     parent = Person._indekso[self.parent2.resourceId]
     parent._infanojCP.add(self)

class Person(Subject):
  _indekso: dict = dict()
  private: bool
  living: bool
  gender: Gender
  names: set[Name]
  facts: set[Fact]
  display: DisplayProperties
  personInfo: set[PersonInfo]  # family search !
  _gepatroj: set[Relationship]
  _infanoj: set[Relationship]
  _paroj: set[Relationship]
  _infanojCP: set[ChildAndParentsRelationship]
  _gepatrojCP: set[ChildAndParentsRelationship]
  def akPrefNomo(self):
    """ akiri preferatan nomon
    """
    for n in self.names:
      if n.preferred: return n
    if len(self.names): return next(iter(self.names))
    return Name()

class Coverage(HypermediaEnabledData):
  spatial: PlaceReference
  temporal: Date

# familySearch extension
# https://www.familysearch.org/developers/docs/api/types/json_ArtifactMetadata
class artifactMetadata:
  filename: str
  qualifiers: set[Qualifier]
  width: int
  height: int
  size: int
  screeningState: str
  displayState: str
  editable: bool

class SourceDescription(Conclusion):
  _indekso: dict = dict()
  citations: set[SourceCitation]
  mediator: ResourceReference
  publisher: ResourceReference
  authors: set[str]
  componentOf: SourceReference
  titles: set[TextValue]
  identifiers: dict[str,set]
  rights: set[str]
  replacedBy: str
  replaces: set[str]
  statuses: set[str]
  about: str
  version: str
  resourceType: str
  mediaType: str
  coverage: set[Coverage]
  descriptions: set[TextValue]
  created: int
  modified: int
  published: int
  repository: Agent
  ### familySearch extension
  artifactMetadata: set[artifactMetadata]
  #def postmaljsonigi(self,d):
  #  """ forigi duplikatajn «citations»
  #  """
  #  cs=set()
  #  for c in self.citations:
  #    trov = False
  #    for c2 in cs:
  #      if c.lang == c2.lang and c.value==c2.value:
  #        trov=True
  #        break
  #    if not trov:
  #      cs.add(c)
  #  self.citations = cs

class Address(ExtensibleData):
  city: str
  country: str
  postalCode: str
  stateOrProvince: str
  street: str
  street2: str
  street3: str
  street4: str
  street5: str
  street6: str
  value: str

class EventRole(Conclusion):
  person: str
  type: str

class Event(Subject):
  type: str
  date: Date
  place: PlaceReference
  roles: set[EventRole]

class Document(Conclusion):
  type: str
  extracted: bool
  textType: str
  text: str
  attribution: Attribution

class GroupRole(Conclusion):
  person: str
  type: str
  date: Date
  details: str

class Group(Subject):
  names: set[TextValue]
  date: Date
  place: PlaceReference
  roles: GroupRole

class PlaceDisplayProperties(ExtensibleData):
  name: str
  fullName: str
  type: str

class PlaceDescription(Subject):
  _indekso: dict = dict()
  names: set[TextValue]
  temporalDescription: Date
  latitude: float
  longitude: float
  spatialDescription: ResourceReference
  place: ResourceReference
  jurisdiction: ResourceReference
  display: PlaceDisplayProperties
  type: str

class Gender(Conclusion):
  _indekso: dict = dict()
  type: str

class Gedcomx(HypermediaEnabledData):
  # de https://github.com/FamilySearch/gedcomx/blob/master/specifications/xml-format-specification.md#gedcomx-type
  attribution: Attribution
  persons: set[Person]
  relationships: set[Relationship]
  sourceDescriptions: set[SourceDescription]
  agents: set[Agent]
  events: set[Event]
  places: set[PlaceDescription]
  documents: set[Document]
  groups: set[Group]
  lang: str
  description: str  # URI must resolve to SourceDescription
  # ne en specifo
  notes: Note
  childAndParentsRelationships: set[ChildAndParentsRelationship]
  sourceReferences: set[SourceReference]
  genders: set[Gender]
  names: set[Name]
  facts: set[Fact]

