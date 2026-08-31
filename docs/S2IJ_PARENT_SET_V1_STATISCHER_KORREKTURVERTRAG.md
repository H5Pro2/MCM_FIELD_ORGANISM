# S2-IJ ParentSetV1 statischer Korrekturvertrag

## Status und Grenze

Status: `S2IJ_PARENT_SET_V1_CONTRACT_BOUND`

S2-IJ bindet ausschliesslich die kompakte Elternbelegprojektion der privaten
S2-IG-Laufhuelle. Es wurden keine Projektmodule importiert, keine Tests oder
Laufpfade ausgefuehrt und keine Implementierungsdateien geaendert. S2-IH und
der reale Fuenf-Status-Funktionslauf bleiben gesperrt.

## Vorbedingung: validierter Elternbeleg

Ein Elternartefakt darf erst in `ParentSetV1` eingehen, nachdem der
Offline-Verifikator beziehungsweise der Recorder folgende vorhandenen
Bindungen vollstaendig geprueft hat:

1. kanonisch lesbare, vorhandene Artefaktdatei;
2. Artefaktdigest ueber die vollstaendige gespeicherte Huelle;
3. Operations-ID, Operationsklasse und Receiptrolle gemaess Registry;
4. Owner-ID und Reservierungsdigest gemaess Ausfuehrungsplan;
5. START-/RESULT- und Elterndigestverkettung des Elternartefakts;
6. vorhandene History-, Case-, Fallplan-, Quellen- und Zustandsbindungen der
   jeweiligen Receiptrolle.

Der Parent-Set-Digest ersetzt keine dieser Pruefungen und keine Artefaktdatei.
Ein nur als Digest behaupteter, aber fehlender oder unvalidierter Elternbeleg
ist unzulaessig.

## Kanonische Datenform

`ParentSetEntryV1` besitzt exakt diese Felder:

```text
parent_role             Registry-Receiptrolle des Elternartefakts
parent_operation_id     kanonische ie-op-NNN-ID
parent_artifact_digest  SHA-256 der vollstaendigen kanonischen Artefakthuelle
```

`ParentSetV1` besitzt exakt diese Felder:

```text
schema                  s2ij.parent-set.v1
registry_bundle_digest  Digest der vollstaendig validierten Registry
reservation_digest      Reservierung des aktuellen einmaligen Laufs
child_operation_id      Operation, deren START-Ereignis die Eltern bindet
parent_count            Anzahl der ParentSetEntryV1-Eintraege
parents                 kanonisch sortiertes Tupel der Eintraege
```

Der `parent_set_digest` ist SHA-256 ueber die kompakte kanonische
ASCII-JSON-Form von `ParentSetV1` ohne Zeilenabschluss. Fuer die
Groessenpruefung wird derselbe Inhalt mit genau einem kanonischen
Zeilenabschluss gezaehlt.

Die vollstaendige `ParentSetV1`-Form wird nur zur Digestbildung im Speicher
materialisiert. Im START-Ereignis werden ausschliesslich gespeichert:

```text
internal_parent_projection_schema = s2ij.parent-set.v1
internal_parent_count
internal_parent_set_digest
```

## Sortierung und Eindeutigkeit

Die Elternmenge muss exakt der internen Elternmenge der Registryzeile des
Kindes entsprechen. Die kanonische Reihenfolge ist aufsteigend nach dem
Registry-Operationsindex; wegen der festen dreistelligen IDs entspricht dies
der ASCII-Sortierung nach `parent_operation_id`.

Fail-closed abzuweisen sind:

- doppelte Operations-IDs oder doppelte Artefaktdigests;
- fehlende Registryeltern oder zusaetzliche fremde Eltern;
- eine falsche Receiptrolle;
- ein nicht vorhandenes, nicht kanonisches oder digestabweichendes Artefakt;
- Owner- oder Reservierungsabweichung;
- Eltern mit Index groesser oder gleich dem Kindindex;
- Eltern aus einem anderen History-, Case-, Fallplan- oder Quellenzusammenhang;
- eine andere Reihenfolge, Anzahl, Projektion oder ein anderer Set-Digest.

Die Pruefreihenfolge ist: Registry und Kind, Artefaktvorhandensein, kanonischer
Artefaktdigest, Rollen- und Provenienzvalidierung, Eindeutigkeit und
Topologie, kanonische Sortierung, Set-Digest, START-Ereignis.

## Projektionsregel

- Null oder ein interner Elternbeleg: bestehende
  `internal_parent_result_digests`-Form unveraendert.
- Mindestens zwei interne Elternbelege: ausschliesslich die neue
  `ParentSetV1`-Projektion.
- Beide Darstellungen gleichzeitig oder die falsche Darstellung fuer die
  Registryanzahl: `IG-E002`.
- Ueberschreitung einer gebundenen Groessengrenze: `IG-E008`.
- Der externe Evaluationsplandigest von `ie-op-172` bleibt separat und wird
  weiterhin nach der bestehenden `IG-E004`-Regel geprueft.

Es gibt 76 kompakt projizierte START-Operationen mit insgesamt 188 internen
Elternreferenzen. Die weiteren 107 START-Operationen besitzen null oder einen
internen Elternbeleg. Insgesamt bleiben 294 interne und eine externe
Elternreferenz gebunden.

Die groesste kanonische `ParentSetV1`-Digestvorlage entsteht bei
`ie-op-171`. Sie belegt mit den 14 konkreten Registryrollen und maximalen
Digests 2.645 Byte. Der statische In-Memory-Grenzwert wird auf 2.816 Byte
gebunden. Dieser Wert ist keine neue Datei- oder Ereignisgrenze.

## Offline-Rekonstruktion

Der Offline-Verifikator darf den Set-Digest ausschliesslich so rekonstruieren:

1. Registryzeile des Kindes laden und validieren;
2. alle dort benannten, bereits aufgezeichneten Elternartefakte laden;
3. jedes Elternartefakt vollstaendig rollen- und provenancebezogen validieren;
4. den Digest jeder vollstaendigen kanonischen Artefakthuelle berechnen;
5. exakt die `ParentSetEntryV1`-Eintraege erzeugen;
6. nach Registryindex sortieren und `ParentSetV1` bilden;
7. Anzahl und Set-Digest mit dem START-Ereignis vergleichen.

Fehlt ein Elternartefakt, endet die Verifikation `NOT_EVALUABLE`. Der
gespeicherte Set-Digest darf weder eine Ersatzkopie noch einen fehlenden
Elternnachweis legitimieren.

## Azyklischer Digestgraph

```text
Registry + Reservierung
-> vollstaendige fruehere Elternartefakte
-> validierte ParentSetEntryV1-Eintraege
-> ParentSetV1-Digest
-> START-Ereignis des Kindes
-> Kindartefakt
-> RESULT-Ereignis des Kindes
-> spaetere Nachfolger
```

Kein Elternartefakt darf den Kind-START-, Kindartefakt- oder
Kind-RESULT-Digest enthalten. Nachfolger verwenden weiterhin ausschliesslich
den Digest des vollstaendigen Kindartefakts. Damit entstehen keine
Rueckkanten.

## Groessennachweis `ie-op-171` bis `ie-op-183`

Die START-Werte verwenden die exakte S2-IJ-Feldform und eine maximal gueltige
96-Zeichen-Owner-ID. Artefakt- und RESULT-Werte bleiben gegenueber S2-II
unveraendert.

| Operation | START S2-IJ | Artefakt | Artefaktgrenze | RESULT |
|---|---:|---:|---:|---:|
| `171` | 814 | 1.692 | 3.072 | 668 |
| `172` | 955 | 708 | 1.024 | 663 |
| `173-180` | je 880 | je 709 | je 1.536 | je 657 |
| `181` | 794 | 1.064 | 1.280 | 665 |
| `182` | 790 | 630 | 1.024 | 660 |
| `183` | 798 | 578 | 1.024 | 669 |

Der ehemalige S2-IH-Qualifikationsfall fuer `ie-op-171` sinkt mit seiner
konkreten Owner-ID von 1.550 auf 757 Byte. Alle START- und RESULT-Ereignisse
bleiben unter 1.536 Byte; alle Artefakte bleiben unter ihren bestehenden
Grenzen.

## Ledger und Budgets

- Operationen und Ereignisse bleiben `183/366`.
- Parent-Referenzen bleiben 294 intern und eine extern.
- Neu explizit gebunden werden 76 Parent-Set-Digestoperationen.
- Artefaktgrenzen gesamt bleiben `475.290` Byte.
- Maximaler Erfolgspfad bleibt `1.037.466` Byte.
- Maximaler einzelner Fehlerpfad bleibt `1.044.634` Byte.
- `MAX_EVENT_BYTES` bleibt 1.536; die globale Artefaktgrenze bleibt 4.095.
- Funktionale Eingabe-, Speicher-, Probe- und Vergleichsbudgets bleiben
  unveraendert.

## Implementierungsgrenze

Nach S2-IJ darf ausschliesslich die beschriebene konditionale
Parent-Set-Projektion in Registryvertrag, Recorder und Offline-Verifikator
implementiert werden. Runner-Funktionslogik, Fixtures, Memory-Zustaende,
Statusregeln, API und Feldpfad bleiben unveraendert. Danach ist eine neue
gemeinsame Qualifikation unter eigener ID erforderlich.
