# Uke 4
Denne timen har vi bare gjennomgått stringfinder fra oblig b-1. Slidene dekker hva algortimen gjør, og hvorfor scanningen blir riktig.

## 3 ting å sjekke for hver term
1. Consume fra roten. Hvis det ikke blir None, kan vi legge til i oversikten over aktive states.
2. Consume fra alle tidligere aktive states. Hvis noen returnerer None, kan vi slette de (vi trenger ikke bry oss om disse statene).
3. Yielde alle states som er en final node.