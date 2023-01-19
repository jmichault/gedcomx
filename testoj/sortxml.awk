BEGIN{ niveau=1; niveaux[1][1]=""; indents[1]=0; nblignes[1]=0;}
{
 indent=0;
 while (substr($0,indent,1) == " ") {indent++;}
 if (niveau == 1 && nblignes[1]==0) indents[1]=indent;
 if (substr($0,indent,1) != "<")
 {
   niveaux[niveau][nblignes[niveau]]= niveaux[niveau][nblignes[niveau]] "\n" $0;
 }
 else if (indent > indents[niveau]) 
 {
    niveau++;
    indents[niveau] = indent;
    nblignes[niveau]=0;
    nblignes[niveau]++;
#    niveaux[niveau][1];
    niveaux[niveau][nblignes[niveau]]=$0;
#    print "niveau ++ " niveau niveaux[niveau][nblignes[niveau]]
 }
 else if (indent == indents[niveau])
 {
    nblignes[niveau]++;
    niveaux[niveau][nblignes[niveau]]=$0;
 }
 else if (indent < indents[niveau])
 {
#   print "tri " niveau
   asort(niveaux[niveau]);
   for ( i= 1 ; i<= nblignes[niveau] ; i++)
   {
     niveaux[niveau-1][nblignes[niveau-1]] = niveaux[niveau-1][nblignes[niveau-1]] "\n" niveaux[niveau][i];
   }
   niveau--;
   niveaux[niveau][nblignes[niveau]]= niveaux[niveau][nblignes[niveau]] "\n" $0;
#   print "niveau -- " niveau niveaux[niveau][nblignes[niveau]]
   while (indents[niveau]>indent) niveau --;
 }
 else
 {
   print("erreur !");
 }
 
}
END { 
 for ( i= 1 ; i<= nblignes[1] ; i++)
    print niveaux[1][i];
}
