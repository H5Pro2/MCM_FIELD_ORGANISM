# S2-KZ - Neutrale Qualifikation des auditiven Teilhinweisabrufs

## Ergebnis

```text
S2KZ_PRIVATE_AUDITORY_PARTIAL_CUE_RETRIEVAL_VALID
```

Der einzige Testaufruf bestand mit `16/16`, Exit-Code `0` und `OK`.
Produkt- und Testquellhashes waren vor und nach dem Lauf identisch.

## Qualifizierter Umfang

- `MaskedAuditoryCue48V1` enthaelt nur 24 beobachtete Rezeptorwerte;
- `AuditoryBandPlan48V1` bindet `0..23` als beobachtet und `24..47` als
  maskiert;
- B4, Fast und auditive Slow-Bank werden vollstaendig als `9/3/8` gescannt;
- positive Distanzen werden mit `distance <= threshold` bewertet;
- B4/Fast-Kandidaten werden erst danach ueber alle 48 Werte exakt auf
  Gleichheit oder Konflikt geprueft;
- B4 und Fast bleiben intern `A_RECENT`, auditive Slow-Treffer erscheinen nur
  als `B_STABLE_AUDITORY`;
- hoechstens eine getrennte Hypothese mit 24 maskierten Werten entsteht;
- Funktion und unabhaengige Direktbaseline stimmen in allen gueltigen Faellen
  ueberein;
- native Audiouhr, spaeteres Audiofenster und getrennte visuelle Uhr sind
  qualifiziert;
- Quellen-, Zeit-, Bandplan-, Dimensions-, Digest- und Zustandsfehler stoppen
  fail-closed.

Ein Testcue wurde direkt aus dem unveraenderten S2-KY-Maschinenbeleg mit
realen PCM- und Rezeptordigests sowie den tatsaechlich erzeugten 48
Rezeptorwerten gebunden. Der Audiorezeptor wurde in S2-KZ nicht erneut
ausgefuehrt.

## Ressourcen

```text
Slotbestand                         9 + 3 + 8 = 20
beobachtete Distanzterme            20 x 24 = 480
B4/Fast-Vollwertvergleich           48
maximale Wertvergleiche je Arm      528
maximale Hypothesenwerte            24
groesste neutrale Ausgabe           17.334 Byte
gebundene Ausgabegrenze             32.768 Byte
```

Vor- und Nachzustandsdigests waren in Funktion und Baseline identisch. Es
gab keine reale Memorygeschichte, keine Kontextverwendung und keinen
Feldzugriff.

## Aussagegrenze

S2-KZ qualifiziert die private Slotscan- und Enthaltungslogik technisch. Es
ist noch kein realer auditiver Teilhinweisabruf aus frisch gebildeten
Memoryzustaenden. Als naechster Schritt duerfen wenige reale PCM-basierte
Memorygeschichten fuer einen getrennt freizugebenden Hauptlauf konstruiert
werden.
