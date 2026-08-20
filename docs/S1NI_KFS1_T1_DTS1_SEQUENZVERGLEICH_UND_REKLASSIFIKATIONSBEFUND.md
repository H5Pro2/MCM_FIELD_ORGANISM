# S1-NI KFS-1/T1-DTS-1-Sequenzvergleich

## Status

S1-NI implementiert und fuehrt genau einmal den in S1-NH gebundenen,
feldfreien Sequenzvergleich aus. Die T1-Regel, das registrierte DTS-1-Profil
`0.4/0.3/0.2` in `r1/r2/r4/r8` und die DTS-1-Nullratenkontrolle erhalten
dieselbe sieben Ereignisse lange Beteiligungsfolge.

Entscheidung:

```text
T1_DTS1_SWITCHED_VARIANT_ONLY
```

## Implementierter Umfang

Das isolierte Modul
`mcm_field_organism/kfs1_s1ni_sequence_comparison.py`:

- erzeugt den gemeinsamen, geschlossenen Einkantenanfangszustand;
- fuehrt T1 genau einmal je Ereignisgrenze aus;
- fuehrt DTS-1 fuer die vorregistrierten Profile und Refinements aus;
- bildet an allen sieben Grenzen gemeinsame Dreirollenledger und
  Bruttotransfertripel;
- prueft Erhaltung, strukturelle Nullen, numerische Aequivalenz und die
  algebraische Reduzierbarkeit auf eine geschaltete DTS-1-Rollenabbildung;
- erzeugt keine Feld-, Adapter-, H-, Readout- oder Ergebniswerte.

## Einmalige fokussierte Abnahme

```text
python -m unittest tests.test_kfs1_s1ni_sequence_comparison
........
----------------------------------------------------------------------
Ran 8 tests in 0.022s

OK
```

Die Ausfuehrung umfasste:

```text
T1-Uebergaenge:         7
DTS-1-Subschritte:    112
MCM-Feldschritte:       0
```

Alle Ledger blieben innerhalb der vorregistrierten Rundungsgrenze erhalten.
Die sieben T1-Grenzen entsprachen bitgenau der S1-NH-Prognose. Die
Nullratenkontrolle blieb exakt statisch.

## Vergleichsbefund

Keiner der fuenf festen DTS-1-Arme reproduziert alle T1-Grenzledger und
Transfertripel. Dies betrifft sowohl das registrierte Profil in allen vier
Refinements als auch die Nullratenkontrolle.

Die binare T1-Folge ist dennoch vollstaendig durch dieselbe Dreirollenbilanz
darstellbar, wenn DTS-1-Transferanteile ereignisabhaengig geschaltet werden:

```text
p = 1: engagement = free, turnover = 0, recovery = 0
p = 0: engagement = 0, turnover = bound, recovery = blocked
```

Die atomare Nachzustandsbildung ist dann an jeder der sieben Grenzen exakt
identisch zu T1. T1 fuegt in diesem Vergleich daher keine unabhaengige
Ressourcenanatomie und keinen von DTS-1 getrennten Rollenwechsel hinzu. Es ist
eine parameterfreie diskrete Schaltregel ueber der bereits vorhandenen
DTS-1-Dreirollenmechanik.

## Methodische Konsequenz

`KFS1-T1_LOCAL_TARGET_REFRACTORY` wird nicht als unabhaengiger
Substratkandidat und nicht fuer eine Feldrueckwirkung weitergefuehrt. Die
Implementierung bleibt als reproduzierbare diskrete DTS-1-Gegenbaseline und
als Test fuer Ereignisgrenzen erhalten.

Der Befund verwirft nicht das MCM-Wahrnehmungsfeld und nicht die offene
Entwicklungsrichtung einer hypothetischen MCM-Memory. Er zeigt enger, dass
dieser konkrete T1-Regelkandidat keine neue technische Evidenzachse dafuer
bereitstellt.

## Gebundene Dateidigests

```text
mcm_field_organism/kfs1_s1ni_sequence_comparison.py
SHA256 FE826F6A54465DC11D29782AA54EEF3EAB1C7D33C3C7824E6864E78786FBC6C4

tests/test_kfs1_s1ni_sequence_comparison.py
SHA256 368C22FFF1FA6CD1153B372083CD66696600048AE6830551D27044D2F8DC1F8A
```

## Aussagegrenze

S1-NI ist ein lokaler Redundanz- und Reklassifikationsbefund. Er ist kein
Feldlauf, kein Feldfunktionsbefund und kein Nachweis einer Lern- oder
Memory-Funktion.

## Naechster erlaubter Schritt

S1-NJ darf ausschliesslich den statischen Abschluss der T1-Reklassifikation
und die Mindestanforderung an einen spaeteren KFS-1-Regelkandidaten binden.
Der neue Kandidat muss vor Implementierung eine lokale Zustands- oder
Kausalprognose besitzen, die nicht durch feste oder ereignisgeschaltete
DTS-1-Transferanteile auf derselben Dreirollenbilanz darstellbar ist.

S1-NJ waehlt noch keine Gleichung, keinen Kandidaten, keine Parameter und
keine Feldrueckwirkung.
