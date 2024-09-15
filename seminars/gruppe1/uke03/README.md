# Uke 3
Vi har repetert fra forelesning og gått gjennom hva som skal gjøres i oblig b-1.
## Suffix array
Suffix array er en datastruktur for å finne tekst-matcher raskt. Hvis vi lagrer (documentID, offset)-par i en liste og sorterer leksikografisk kan vi finne matcher på stringen på logaritmisk tid med binærsøk.  
Offset betyr hvor mange karakterer inn i dokumentet vi skal starte for å lete etter matcher. Det vil være et (docID, offset)-par i suffix arrayet for hver term i hvert dokument.  
Hvis vi har dokumentene:
```  
(0, {"En gul bil"})  
(1, {"Informatikk er gøy"})

```
Vil vi få et suffix array som ser slik ut:  
```
[(0, 7), (0, 0), (1, 12), (0, 3), (1, 15), (1, 0)]
```    
Vi trenger ikke lagre hva teksten er i suffix arrayet. Istedet kan vi bruke en hjelpefunksjon som returnerer teksten etter offset i et dokument. Da trenger kun hvert dokument å lagres en gang, som sparer masse plass!