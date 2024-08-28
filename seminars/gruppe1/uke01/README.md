# Uke 1

Her kommer en kort oppsummering av de viktigste delene fra gruppetimen 28. august.

## Viktige begreper

- Ordbok: En datastruktur som mapper termer til sin tilhørende postingliste. Brukes til effektivt oppslag av termer.
- Postingliste: En liste som holder på alle postingene til en gitt term.
- Posting: Metadata om forholdet mellom term og et dokument. Kan inneholde forskjellige ting som dokument-ID, antall forekomster av termen i dokumentet eller posisjon.

## Operasjoner på postinglister
Assignment A handler blant annet om operasjoner på postinglister. Dette er en kort forklaring på hvordan hver av de fungerer.
### Union
Alle postinger som er i A eller B. Det har ingenting å si om postingen er i bare en eller i begge av postinglistene.  
(1, 2, 3) $\cup$ (2, 3, 4, 5) = (1, 2, 3, 4, 5)

### Snitt (intersection)
Alle postinger som forekommer i både A og B. Dette betyr at postinger som kun er i en av postinglistene ikke er en del av resultatet.  
(1, 2 ,3) $\cap$ (2, 3, 4, 5) = (2, 3)

### Difference
Alle postinger som er i A, men som ikke er i B. Bare postingene i A som ikke finnes i B er en del av resultatet. Ingenting fra B er en del av resultatet. Difference kan skrives både *A\B* og *A-B*.  
(1, 2, 3)\\(2, 3, 4) = (1)
