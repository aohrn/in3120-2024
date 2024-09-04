# Uke 2
Denne uka har vi tatt for oss parsing av tekst, skip-pekere og hvordan bruke obligtestene.
## Begreper for parsing av tekst
- Tokenization: Dele opp en sammenhengende sekvensav tekst til tokens  
«En gul bil» → «En», «gul», «bil»
- Normalization: "Normalisere" variasjoner av ord til samme format  
«U.S.A» og «USA» skal ideelt matche
- Lemmatization: Redusere variasjoner av ord til basisform  
am, are, is → be
- Stemming: Redusere et ord til "stammen" av ordet  
Automates, automatic  → automat

## Skip-pekere
Referanser i postinglister som "hopper over" noen postinger. Med skip-pekere trenger man potensielt færre sammenligninger når man merger postinglister.  
Det er et tradeoff å ta hensyn til: Jo flere skips man har, jo mer sannsynlig er det å følge pekeren, men det krever også mange sammenligninger. Har man færre skips vil det være mindre å sammenligne, men også mindre sannsynlig å følge pekeren.  En god strategi er for en postingliste med lengde L, er å fordele pekere på hver $\sqrt{L}$ posting.
