# Uke 7

Vi har sett på måter ulike søkemotorer fungerer: hvordan de tilrettelegger for raske oppslag, hvordan de bruker minne effektivt, hvordan de scorer og rangerer dokumenter, og så videre. Til tross for dette, har vi fortsatt ingen _fasit_ for hvordan en søkemotor skal være! For eksempel vil Google, Bing, og DuckDuckGo sannsynligvis gi (overraskende) ulike svar, gitt nøyaktig samme spørring.

Noen ting man kan se på er

- Hvor fort indekserer den?
- Hvor fort søker den?
- Klarer den å anbefale relevant stoff?
- Er brukerne fornøyde?

Det er ikke alltid så enkelt å vite om brukerne er fornøyde eller ikke. En god indikasjon på at en bruker er fornøyd med søkemotoren er hvis

- Brukeren bruker penger etter et søk
  - Eksempel: En bruker søker etter støvsuger, og kjøper en av dem hen fikk anbefalt
- Brukeren fortsetter å bruke søkemotoren
  - Moteksempel: En bruker som prøver søkemotoren 1 gang og aldri igjen, var antakeligvis ikke veldig fornøyd
- Brukeren får relevante dokumenter

  - Eksempel: Brukeren trykker på resultatene hen får (istedenfor å justere spørringen sin mange ganger først). **NB!** Brukeren kan også bli lurt av clickbaits. Her kan man kanskje se på _hvor mange_ av resultatene hen får som blir trykket på. Hvis brukeren trykker på alle, var kanskje ingen av dem særlig bra likevel.

### Hvordan kan søkemotoren forbedres?

Spørringer må testes! Det viktigste er at brukeren får dokumenter som oppfyller hens behov, ikke bare de som inneholder termer fra spørringen. Her er faktisk et alternativ å ha _mennesker_ for å teste spørringer opp mot resultater. Enten kan man sjekke ekte brukeres søkelogg, eller finne på spørringer der og da.

## Har vi noen objektive mål for hvor resultater søkemotoren vår gir oss?

Ja! Her har vi faktisk en del:

### Precision & Recall

Våre venner fra uke 1! Dette er såkalt "binær evaluering": resultatet er enten "bra" eller "dårlig". Her jobber vi med fire typer resultater:

| type           | betydning                               |
| -------------- | --------------------------------------- |
| True positive  | Relevant dokument som ble hentet        |
| False positive | Irrelevant dokument som ble hentet      |
| True negative  | Irrelevant dokument som ikke ble hentet |
| False negative | Relevant dokument som ikke ble hentet   |

**Precision** er fraksjonen av hentede dokumenter som er relevante for brukeren. Formelen er

> True positives / (True positives + False positives)

Høy presisjon er foretrukket f.eks. når vi skal se en youtube-video til maten. Det er ikke så farlig at vi ikke fikk _alle_ de relevante videoene, siden vi bare rekker et par uansett.

For å øke presisjon kan man legge til termer i spørringen. For eksempel får unngår man flere bil-videoer av spørringen `jaguar AND animal` enn bare `jaguar`.

**Recall** er fraksjonen av relevante dokumenter i korpuset som ble hentet og vist til brukeren. Formelen er

> True positives / (True positives + False negatives)

Høy recall er foretrukket f.eks. når vi skal gjøre forskning til PhDen vår. Vi ønsker _alle_ de relevante artiklene, og leser heller en ekstra irrelevant artikkel enn å risikere å glippe en veldig relevant en.

For å øke recall kan man blant annet lemmatisere dokumentene og spørringen (f.eks. konvertere `cars` til `car` og sånt).

### Precision@K

Si at vi får 5 resultater, i rekkefølgen 1, 2, 3, 4, 5.

Vi vet på forhånd hvilke av dem som er relevante. Da kan vi si _hvilken presisjon resultatet har på indeks K_.

Si at dokument 1, 3 og 5 er relevant for brukerens spørring, mens dokument 2 og 4 er irrelevant. Da har vi følgende precision@k:

- Precision@1: 1/1
  - Fordi vi har 1 relevant dokument blant de 1 første resultatene
- Precision@2: 1/2
  - Fordi vi har 1 relevant dokument blant de 2 første resultatene
- Precision@3: 2/3
  - Fordi vi har 2 relevant dokument blant de 3 første resultatene
- Precision@4: 2/4
  - Fordi vi har 2 relevant dokument blant de 4 første resultatene
- Precision@5: 3/5
  - Fordi vi har 3 relevant dokument blant de 5 første resultatene

Vi har også noe tilsvarende ala recall@k, men det er utenfor skopet til dette kurset :)

### Mean Average Precision

I seg selv virker kanskje precision@k litt unyttig. Men det kan anvendes videre i MAP, som handler om å finne gjennomsnitt!

Først beregner vi **average** av et resultat gjennom p@k. Vi tar p@k-verdien til alle relevante dokumenter, delt på antalle relevante dokumenter. Fra eksemplet over får vi

- 1/1 = 1.0
- 2/3 = 0.67
- 3/5 = 0.6

Summen av disse (`2.27`) delt på antallet (`3`) gir oss `2.27 / 3 = 0.76`.

Så gjør vi dette på tvers av resultater. Et annet tilfelle kan være 1/1, 2/3, 3/4 og 4/5. Dette gir oss `(1.0 + 0.67 + 0.75 + 0.8) / 4`, som igjen gir oss `0.8`.

MAP er gjennomsnittet av gjennomsnitt, så MAP av våre to resulteter gir oss `(0.76 + 0.8) / 2 = 0.78`.

MAP sier noe om hvor bra søkemotoren er på tvers av søk, som er fint og bra!


### Kendall tau-distanse

Gitt 4 dokumenter: dok 1, dok 2, dok 3, og dok 4

Her jobber vi med fire variabler:

- P: Hvor bra hvert dokument er i forhold til hverandre
  - F.eks. [1, 2, 3, 4]. Dette betyr at 1 er bedre enn 2, 3 og 4, at 2 er bedre enn 3 og 4, og at 3 er bedre enn 4.
- A: Rekkefølgen søkemotoren vår gir oss
  - F.eks. [1, 3, 2, 4]
- X: Hvor mange enigheter de har
  - I eksemplet over er det 5 enigheter (1 > 2, 1 > 3, 1 > 4, 3 > 4, og 2 > 4)
- Y: Hvor mange uenigheter de har
  - I eksemplet over er de uenige om rekkefølgen på 2 og 3 (P sier at 2 > 3, mens A sier at 3 > 2).

Kendall tau-distansen mellom A og P er (X-Y)/(X+Y). Fra eksemplet over får vi

- X = 5 Y = 1
- (5-1)/(5+1) = 4/6 = 2/3
- = 0.667


### Normalised Discounted Cumulative Gain

Her er tanken at de beste dokumentene alltid bør vises først. Mange gode dokumenter er jo ikke noe godt resultat hvis de kommer helt sist!

For å forstå NDCG hjelper det å bryte opp hver del av begrepet.

- **Gain** er et tall på hvor bra dokumentet er
  - For eksempel kan vi ha verdiene [0, 1, 2], der 0 betyr "irrelevant" og 2 betyr "veldig relevant". Deretter gir vi disse verdiene til resultatene fra søket vårt.
- **Cumulative Gain** er summen av disse tallene.
  - Hvis G = `2, 0, 1`, så er CG = `(2 + 0 + 1) = 3`
- **Discounted Cumulative Gain** handler om å redusere verdien på Gains etter hvor langt bak de havner.
  - Dette gjøres gjerne gjennom å dele på log av posisjon, fra og med posisjon 2. Eksemplet over vil gi oss DCG = `2 + 0/log(2) + 1/log(3) = 2,63`
- **Normalised Discounted Cumulative Gain** handler om å dele DCG-verdien på "ground truth", altså den beste mulige rekkefølgen (nemlig 2, 1, 0). Da får vi `2,63 / (2 + 1/log(2) + 0/log(3) = 3) = 0,876`.
