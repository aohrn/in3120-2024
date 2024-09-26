# Uke 5


## Jaccard-koeffisient

Vi er nødt til å "måle" overlappen på et vis. Etter å ha delt de to termene inn i n-grammer, kan vi legge dem i to mengder: X og Y. Jaccard-koeffisienten blir lengden av snittet av X og Y delt på lengden av unionen av X og Y.

{emb, mbe, ber} / {nov, ove, vem, emb, mbe, ber, des, ese, sem} \
3 / 9 = 0.333...

Vi bestemmer selv hva som er høyt nok for å være en match, men spennet er [0, 1].

## Sort-based index construciton

En potensiell løsning! I forelesningen så vi på to varianter: Blocked sort-based indexing (BSBI) og Single-pass in-memory indexing (SPIMI).

### Blocked sort-based indexing

Vi bryter korpuset opp i blokker, som er såpass store at vi har plass til én blokk i hovedminnet om gangen.

Den grunnleggende idéen er:

1. Vi leser én blokk (med dokumenter) fra disken
2. Tokeniser dokumentene
3. Opprett postinger på formen (term, dokument ID)
4. Skriv dem tilbake til disken
5. Gjenta steg 1 til vi har gjort dette med alle blokkene

Når vi har gjort dette med alle blokkene, kan vi bruke en flette sammen postinger fra ulike blokker, og få en invertert indeks.

> Repetisjon: en **posting** sier noe om forholdet mellom en term og dokumentet det forekommer i. Det kan være så enkelt som IDen til dokumentet termen forekommer i, men også mer avansert, om vi ønsker det.

Eksemplet fra forelesningen viser hva som skjer når alle blokkene er skrevet tilbake, og vi merger postings:

Den mest effektive måten å flette sammen postingene på er egentlig ikke en binær merge som vist over, men en såkalt _multi-way merge_, der vi merger fra alle blokkene (i hovedminnet) om gangen! Nøyaktig _hvordan_ dette foregår, er utenfor pensum :)

### Single-pass in-memory indexing

SPIMI fungerer veldig likt:

1. Bryt opp korpuset til blokker
2. Vi leser én blokk (med dokumenter) fra disken
3. Tokeniser dokumentene
4. Lag en invertert indeks for dokumentene i blokken (uten å sortere postinglistene)
5. Gjenta steg 2 til minnet er fullt
6. Skriv alt tilbake til disk, og fortsett til vi har prosessert alle blokkene.

Til slutt kan vi merge sammen de inverterte indeksene til én fullstendig en, og på et magisk vis vil postinglistene være sortert :)

## Så hvilken er best?

- **BSBI** hvis du har begrenset med minne (fordi vi leser en forutsigbar mengde data i hver iterasjon), eller når du avhenger av at termene prosesseres i sortert rekkefølge
- **SPIMI** hvis du har mye minne, og ønsker færre disk-operasjoner (fordi vi bare skriver tilbake til disken når vi _må_)

## Distribuert indexing

Vi bør ikke overlate all jobben til én maskin, da den når som helst kan bli ødelagt. Istedenfor bør vi _distribuere_ jobben på flere maskiner.

> NB! Vi er fortsatt avhengige av én "hovedmaskin", men dens jobb er bare å dirigere oppgaver til andre maskiner.

Et klassisk rammeverk for distribuert indeksing heter **MapReduce**:

Vi deler opp korpuset i blokker, men her velger vi å kalle dem _splits_. Deretter deler vi opp jobben på to grupper: **parsers** og **inverters**.

Hver parser gjør følgende (Map-fasen):

- Blir tildelt en split av hovedmaskinen
- Leser et dokument av gangen fra spliten
  - Lager (term, docID)-par
- Skriver parene til en partisjon\*

Hver inverter gjør følgende (Reduce-fasen):

- Samler par fra én partisjon
- Sorterer parene og skriver dem til postinglister

> \*i forelesningen så vi 3 partisjoner: a-f, g-p og q-z. Par blir lagt i partisjonen tilsvarende termens første bokstav. (informatikk, 1) og (gøy, 1) havner i g-p, mens (er, 1) havner i a-f.

Eksemplet fra forelesningen viser dette fint, men kan være litt overveldende. For å forstå det bedre, kan det være en idé å tegne opp hver del, for å forstå flyten.

## Index compression

Vi ønsker å gjøre den inverterte indeksen vår så liten som mulig! Vi kan _komprimere_ både ordboka og postingene.

> Repetisjon: **ordboka** er bare masse termer. Hver term _mapper_ til en liste bestående av **postinger** (aka en postingliste). En posting består av metadata som er relevant til termen og dokumentene i korpuset, f.eks. hvor mange dokumenter det forekommer i, IDen på dokumentene det forekommer i, hvor det forekommer i hvert dokument osv.

### Hvorfor komprimere i utgangspunktet?

Å komprimere betyr å gjøre noe mindre. Vi skiller forresten på lossless og lossy kompresjon:

- Lossless betyr at all informasjon blir bevart (vanligst)
- Lossy betyr at vi forkaster noe informasjon (tenk f.eks. stemming)

Fordelene med kompresjon er blant annet

- vi bruker mindre plass på disken, og sparer penger
- vi kan beholde mer ting i hovedminnet, og får raskere operasjoner

For maskinvaren går det kjappere å lese komprimert data enn det er å lese ukomprimert data. Om vi har gode dekomprimeringsalgoritmer, er det bedre å dekomprimere dataen når vi har den i hovedminnet (og trenger den).

### I konteksten av inverterte indekser

Vi ønsker at ordboka er såpass liten at vi får plass til hele i hovedminnet, samt noen postinglister.

Vi får ikke plass til alle postinglistene i hovedminnet, så en del av dem vil ligge på disken. Om de er små vil de bruke mindre plass, og vi bruker mindre tid på å lese dem.

## Heaps' law

En måte å regne ut _vokabularet_ til et korpus, altså hvor mange distinkte ord som finnes.

Regnestykket er følgende:

> $M = kT^b$

**M** er størrelsen på vokabularet. \
**T** er antall tokens i hele korpuset. \
**k** og **b** konstanter som velges basert på hva slags kolleksjon det er (språk, størrelse osv.). Vi kan slå oss til ro med at 30 ≤ **k** ≤ 100, og **b** ≈ 0.5.

> Sidenote: Hvorfor i all verden er "M" symbolet for størrelsen på vokabularet? Svaret er at "M" ofte brukes for å betegne **m**ålbare kvantiteter, så det har ingenting direkte med vokabularstørrelse å gjøre :)

Jo mer vi vet om størrelsen på vokabularet, desto enklere er det å velge riktig form for komprimering av ordboka!

## Zipf's law

Det kan også være interessant å se på ordenes frekvens: Hvor ofte forekommer de enkelte ordene i hvert korpus? Zipf's lov forteller oss at ordet som forekommer flest ganger, også forekommer dobbelt så ofte som ordet som forekommer nest flest ganger.

Altså, hvis ordet "er" forekommer oftest, og forekommer 10 ganger, vil ordet som forekommer nest flest ganger forekomme 5 ganger.

I slidene og i boka ser vi denne formelen:

> $cf_i ∝ 1/i = K/i$

Men dere kan se på den som en black box. "∝" betyr "proposjonalt med". Så man kan lese formelen over som

> $cf_i$ er proposjonal med $1/i = K/i$

Men i bunn og grunn betyr det bare

> Det nest vanligste ordet i korpuset, forekommer halvparten så ofte som det vanligste ordet i korpuset

og

> Det tredje vanligste ordet i korpuset, forekommer 1/3 så ofte som det vanligste ordet i korpuset

osv., i det mønsteret.

## Ordbok-komprimering

Ettersom søket starter i ordboka, ønsker vi å beholde den i hovedminnet. Om vi ikke får plass i hovedminnet, ønsker vi uansett at den er såpass liten at det går fort å hente den fram.

### Alternativ 1: La ordboka være én streng

Så har vi en ordbok med pekere på siden, som peker til starten på hver term. Dermed har vi også implisitt en peker til slutten av en term. Noe ala:

```python
ordbokstreng = "jeggledermegtilåhørehvaukasboker"

ordbok = [
    { frekvens, postingliste_peker, term_peker },
    { frekvens, postingliste_peker, term_peker },
    { frekvens, postingliste_peker, term_peker },
    ...
]
```

### Alternativ 1.2: Blocking

Istedenfor å ha pekere i alle oppføringene i ordboka, kan vi prefikse alle ordene med lengden deres. Så kan vi ha pekere til f.eks. hvert tredje ord istedenfor!

```python
ordbokstreng = "3jeg6gleder3meg3til1å4høre3hva4ukas3bok2er"

ordbok = [
    { frekvens, postingliste_peker, term_peker },
    { frekvens, postingliste_peker },
    { frekvens, postingliste_peker },
    { frekvens, postingliste_peker, term_peker },
    { frekvens, postingliste_peker },
    ...
]
```

Ordbokstrengen blir lengre, men en `peker` tar mer plass enn en `char`, så i lengden sparer vi plass! Om vi har et enda større intervall sparer vi enda mer plass, men da tar det igjen lengre tid å lete etter ordene.

Ettersom vi ikke har en peker til hvert ord, må vi gå til den nærmeste pekeren, også søke lineært frem til neste peker for å finne ordet vårt.

### Alternativ 2: Front coding

I en alfabetisk sortert ordbok vil vi fort se at mange ord deler prefiks. Vi kaster bort mye plass ved å kjøre

```python
ordbokstreng = "8automata8automate9automatic10automation"
```

Istedenfor kan vi lagre prefiksen, og slenge på bare endringene!

Istedenfor kan vi slenge på noen symboler, som gjør at vi sparer _mye_ plass:

```python
ordbokstreng = "8automat*a1◊e2◊ic3◊ion"
```

- `8automat*` betyr at vi har en prefiks på 8 bokstaver: "automat". `*` betyr at prefiksen er slutt, og det som kommer etter er suffikser
- `a` er den første suffiksen
- `1◊e` kan se noe forvirrende ut, men `1◊` betyr at "nå kommer det en suffiks på 1 char". Vi trengte ikke `◊` for den første suffiksen (a), fordi vi avsluttet `8automat` med en `*`, som betyr "nå kommer det en eller flere suffikser"
- `2◊ic` følger mønsteret over, der `2◊` sier "nå kommer en suffiks på 2 chars" og `ic`, som er suffiksen på 2 chars
- `3◊ion` følger også mønsteret over, der `3◊` sier "nå kommer en suffiks på 3 chars" og `ion`, som er suffiksen på 3 chars

Hvis vi ikke ser en `◊` etter et tall, vet vi at vi er ferdige med den forrige prefiksen! Her er et eksempel med _to_ strenger:

```python
ordbok_med_to_strenger = "8automat*a1◊e2◊ic3◊ion3int*er2◊el5◊ernet"
```

Ingen mellomrom som skiller `8automat*a1◊e2◊ic3◊ion` og `3int*er2◊el5◊ernet`, men heller mangelen på et `◊`-symbol!

## Posting-komprimering

Her begrenser vi postinger til å være dokument-IDer, for enkelthetens skyld.

### Alternativ 1: Lagre mellomromet istedenfor IDen

Akkurat nå vil vi lagre postinglister som dette:

```python
computer: 33, 47, 154, 159, 202
```

Men her bruker vi plass på å lagre den nøyaktige IDen til hvert dokument. Et altnernativ er å heller lagre _mellomrommet_! Altså, hvor mange dokumenter er det mellom postingene?

```python
computer: 33, 14, 107, 5, 43
```

Her ser vi at det første dokumentet har ID 33, mens det neste har (33+14), før det neste igjen har (33+14+107) osv. Beregningen er uansett lynrask, så vi prioriterer å spare plass!

for ord som `the` kan vi spare _veldig_ mye plass:

```python
the: ..., 283042, 283043, 283044, 283045, ...
```

kan bli til

```python
the: ..., 1, 1, 1, 1, ...
```

### Alternativ 2: Variable Byte (VB) codes

Her ønsker vi å bruke så få bits som mulig. Tanken er følgende:

### Encoding

1. Konverter dokument-IDen fra desimal til binær
2. Del tallet opp i deler på maks 7 bits (fra høyre til venstre)
3. Hvis den til venstre er under 7 bits, legg til nuller
4. Legg til `1` på den helt til høyre, og `0` på de resterende

La oss bruke `300` som eksempel

1. 30 = 100101100
2. 10, 0101100
3. 0000010, 0101100
4. 00000010, 10101100

### Decoding

1. Les bytene fra venstre til høyre, helt til vi møter en byte som starter på `1`
2. Fjern alle ledende nuller

Med samme eksempel, starter vi på `00000010, 10101100`

1. Vi leser `00000010`, og siden det starter på `0`, fortsetter vi. Så leser vi `10101100`, og siden det starter på `1`, leser vi ikke flere bytes i denne omgang. Da har vi lest `00000010` `10101100`.
2. Fjern den første biten fra sekvensene vi har lest.
3. Vi gjør `0000010` `0101100` om til `100101100`, som igjen kan konverteres til desimaltallet `300`

### Alternativ 3: Gamma encoding

#### Encoding

1. Konverter dokument-IDen fra desimal til binær, men fjern prefiksen, siden alle binærtall uansett starter på `1`
2. Ta vare på lengden til binærtallet i unær, og legg på en null
3. Konkatener steg 2 med steg 3

La oss bruke `13` som eksempel

1. 13 = 1101. Vi fjerner prefiksen, som gir oss `101`
2. Lengden på 101 er 3, som gir oss 111 i unær. Vi legger på en null og får `1110`.
3. `1110` + `101` = `1110101`

### Decoding

1. Les antall bytes frem til vi treffer `0`. Da har vi lest N enere
2. Les de neste N bitsene, og sett på en `1`

Med samme eksempel, leser vi `1110101`

1. Vi leser `111` før vi treffer `0`, som betyr at vi skal lese 3 bits til
2. Vi leser `101`, og slenger på en `1`: `1101`

Dette funker fint for små tall, men er for treigt når de blir større

### Alternativ 4: Delta encoding

Dette er omtrent det samme som Gamma encoding, men vi kjører også en gamma encoding på lengden, istedenfor å bare ha den unær! Så istedenfor å ha `1110101`, så har vi `110101`, også plusser vi bare på en til lengden senere.

### Alternativ 5: Rice coding

Her behandler vi en hel postingliste, og nærmere bestemt en som anvender Alternativ 1, beskrevet lenger opp. Vi bruker følgende eksempel:

```python
term: 34, 178, 291, 453
```

1. Konverter IDene til mellomrommene: [34, 178, 291, 453] -> [34, 144, 113, 162]
2. Finn gjennomsnittet: (34+144+113+162) / 4 = 113
3. Rund gjennomsnittet ned til nærmeste "power of two". 2^7 = 128 er større enn 113, mens 2^6 = 64 er mindre, så den "vinner". Vi sier at `b=64`
4. For hver `x` i lista skal vi nå finne to ting:
   1. (`x`-1) / `b` (i unær. hvis resultatet ikke er 0, legg på en ekstra 0 på slutten)
   2. (`x`-1) % `b` (i binær)
   - Dette gir oss [0 100001, 110 001111, 10 110000, 110 100001]

En av de største fordelene med Rice coding, er at den er såpass enkel å implementere!

### Alternativ 6: Golomb coding

Golomb coding er akkurat som Rice coding, men at `b` er gjennomsnittet \* 0.69. Nice

### Alternativ 7: Simple9

Simple9 benytter en 32-bit `word`. De 4 første bitsene ("selector value") sier noe om hvordan tall er distribuert i de resterende 28 bitsene.

Hvis selector value er 0000, betyr det at de resterende 28 bitsene inneholder én integer på 28 bits.

#### Eksempel 1

Desimaltallet `134217726` kan skrives om til binærtallet `11111111111111111111111110`, som tar 28 bits. Da kan en simple9-enkoding være følgende: `0000 11111111111111111111111110`.

Hvis selector value er 0100, betyr det at de resterende 28 bitsene inneholder 14 tall på 2 bits hver.

#### Eksempel 2

Desimaltallene `1`, `2`, `2`, `3`, `0`, `1`, `2`, `2`, `3`, `0`, `1`, `2`, `2`, og `3` kan skrives om til til `01`, `11` osv., som alle tar 2 bits. Da kan en simple9-enkoding være følgende: `0111 01101010001100101000110011`.

Algoritmen for Simple9 coding er omtrent slik:

```python
if <the next 28 numbers fit into one bit each>:
    <use that case>
elif <the next 14 numbers fit into 2 bits each>:
    <use that case>
elif <the next 9 numbers fit into 3 bits each>:
    <use that case>
elif ...
```
