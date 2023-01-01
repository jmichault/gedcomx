import argparse
import getpass
import json
import re
import sys
import xml.etree.ElementTree as ET
from os.path import exists

import gedcomx

fs_sesio = None
fs_uzanto = None
fs_pasvorto = None
arbo=gedcomx.Gedcomx()

def akiri_url(url):
  global arbo
  global fs_sesio
  print("legas url "+url+".")
  # ensaluti al FamilySearch se necese
  if fs_sesio is None:
    global fs_uzanto
    global fs_pasvorto
    if not fs_uzanto : fs_uzanto = input("Enigu FamilySearch uzantnomon:")
    if not fs_pasvorto : fs_pasvorto = input("Enigu FamilySearch pasvorton:")
    fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
  r = fs_sesio.get_url(url
            ,{"Accept": "application/x-fs-v1+json", "Accept-Language": "fr"} )
  if r and r.status_code == 200:
    gedcomx.maljsonigi(arbo,r.json())
  else:
    print("url "+url+" ne trovita.")

def akiri_personon(fsid):
  if fsid in gedcomx.Person._indekso.keys():
    persono = gedcomx.Person._indekso[fsid]
    if not persono.sortKey is None :
      return
  print (" akiri "+fsid)
  akiri_url("/platform/tree/persons/"+fsid)

def akiri_gepatrojn(arbo,fsid):
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

def akiri_infanojn(arbo):
  for cpr in arbo.childAndParentsRelationships.copy() :
    akiri_personon(cpr.child.resourceId)

def akiri_edzojn(arbo):
  for cpr in arbo.childAndParentsRelationships.copy() :
    if cpr.parent1 and cpr.parent1.resourceId :
      akiri_personon(cpr.parent1.resourceId)
    if cpr.parent2 and cpr.parent2.resourceId :
      akiri_personon(cpr.parent2.resourceId)

def main():
    parser = argparse.ArgumentParser(
        description="Retrieve GEDCOM data from FamilySearch Tree (4 Jul 2016)",
        add_help=False,
        usage="getmyancestors -u uzanto -p pasvorto [options]",
    )
    parser.add_argument(
        "-u", "--uzanto", metavar="<STR>", type=str, help="FamilySearch uzanto"
    )
    parser.add_argument(
        "-p", "--pasvorto", metavar="<STR>", type=str, help="FamilySearch pasvorto"
    )
    parser.add_argument(
        "-i",
        "--individuals",
        metavar="<STR>",
        nargs="+",
        type=str,
        help="List of individual FamilySearch IDs for whom to retrieve ancestors",
    )
    parser.add_argument(
        "-a",
        "--ascend",
        metavar="<INT>",
        type=int,
        default=1,
        help="Number of generations to ascend [4]",
    )
    parser.add_argument(
        "-d",
        "--descend",
        metavar="<INT>",
        type=int,
        default=1,
        help="Number of generations to descend [0]",
    )
    parser.add_argument(
        "-e",
        "--edzoj",
        action="store_true",
        default=False,
        help="Add spouses and couples information [False]",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        metavar="<FILE>",
        type=argparse.FileType("w", encoding="UTF-8"),
        default='arbo.json',
        help="output GEDCOM file ['arbo.json']",
    )

    # extract arguments from the command line
    try:
        parser.error = parser.exit
        args = parser.parse_args()
    except SystemExit:
        parser.print_help(file=sys.stderr)
        sys.exit(2)
    if args.individuals:
        for fid in args.individuals:
            if not re.match(r"[A-Z0-9]{4}-[A-Z0-9]{3}", fid):
                sys.exit("Invalid FamilySearch ID: " + fid)

    args.uzanto = (
        args.uzanto if args.uzanto else input("Enter FamilySearch uzanto: ")
    )
    global fs_uzanto
    fs_uzanto = args.uzanto
    args.pasvorto = (
        args.pasvorto
        if args.pasvorto
        else getpass.getpass("Enter FamilySearch pasvorto: ")
    )
    global fs_pasvorto
    fs_pasvorto = args.pasvorto
    global fs_sesio
    fs_sesio = gedcomx.FsSession(fs_uzanto,fs_pasvorto, True, False, 2)
    # add list of starting individuals to the family tree
    x = args.individuals if args.individuals else [fs_sesio.fid]
    for fsid in x :
      akiri_personon(fsid)
    
    # download ancestors
    for i in range(args.ascend):
      for fsPersono in arbo.persons.copy() :
        akiri_gepatrojn(arbo,fsPersono.id)

    # download descendants
    for i in range(args.descend):
      akiri_infanojn(arbo)

    # download spouses
    if args.edzoj:
      akiri_edzojn(arbo)

    rezulto = gedcomx.jsonigi(arbo)
    f = open(args.outfile.name,'w')
    json.dump(rezulto,f,indent=2)
    f.close()

main()
