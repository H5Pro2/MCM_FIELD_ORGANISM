# Z1: Implementierung des gemeinsamen Observer-Supports

Stand: 2026-08-06

## Status

Die einzige im
[Lauf-196-Korrekturvertrag](Z1_KORREKTURVERTRAG_GEMEINSAMER_OBSERVER_SUPPORT_LAUF_196.md)
zugelassene Messkorrektur wurde implementiert und synthetisch geprueft. Die
reale F3/B3-Vollmatrix ist inzwischen genau einmal als
[Lauf 196](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md)
ausgefuehrt.

## Getrennte Datenrollen

`mcm_field_organism/mcm_f3_z1_completion_support.py` veraendert weder Quelle
noch Felddynamik. Es trennt nach einer vollstaendigen technischen
Aufzeichnung:

```text
Volltrajektorie:
alle technischen Integrationsabschluesse
-> Reproduktion, Diagnose und finale Kontrollen

Entscheidungstrajektorie:
neutraler Start + echte Rezeptorabschlussgruppen
-> unveraenderte Z1-Sachpfadmetrik
```

Die Auswahl verwendet ausschliesslich die vorab feststehenden
Abschlussgruppen der gebundenen Rezeptorsequenzen. Zustandswerte,
Pfaddistanzen und Ergebnisse beeinflussen die Auswahl nicht.

## Supportinventar

| Arm | Vollsamples | Entscheidungssamples | Aenderung |
| --- | ---: | ---: | --- |
| `A.reference` | 92 | 92 | keine |
| `A.partitioned` | 183 | 92 | 91 leere Zwischenabschluesse entfernt |
| `A.stretched` | 92 | 92 | keine |
| `A.compressed` | 92 | 92 | keine |
| `A.reversed` | 92 | 92 | keine |
| `A.permuted` | 92 | 92 | keine |
| `B.independent` | 92 | 92 | keine |

Referenz und partitionierter Arm besitzen bitgleich dasselbe Inventar aus
Starttick und 91 echten Abschlussgruppenticks.

## Kontrollen

Die Projektion prueft fest:

```text
source_contracts_match
all_required_ticks_present
reference_partition_support_equal
nonpartition_support_unchanged
partition_empty_support_removed
```

Ein fehlender erforderlicher Tick bricht die Projektion ab. Es wird weder
interpoliert noch ein naechster technischer Tick ersatzweise verwendet.

## Historische Trennung

Der bestehende Lauf-195-Einstieg bleibt unveraendert und wuerde weiterhin die
vollstaendigen Observertrajektorien direkt auswerten. Fuer Lauf 196 muss ein
eigener Einstieg die vollstaendige technische Matrix zuerst durch die neue
Supportprojektion fuehren und erst danach die unveraenderte Z1-Auswertung
aufrufen.

## Technische Pruefung

Synthetisch bestaetigt sind:

- Abschlussgruppenticks stammen exakt aus den festen Quellen;
- nur `A.partitioned` verliert leere Zwischenstuetzpunkte;
- Referenz und Partition besitzen je 92 identische Entscheidungsticks;
- alle anderen Arme bleiben vollstaendig unveraendert;
- alle fuenf Supportkontrollen bestehen;
- die unveraenderte Auswertung verarbeitet das korrigierte Paket;
- keine reale F3/B3-Vollmatrix wurde aufgerufen.

Zusammen mit den bestehenden Z1/F3-Tests bestehen 50 fokussierte Tests.

## Aussagegrenze

Die bestandene Supportprojektion ist nur eine technische Messkorrektur. Sie
belegt keine Teilungsinvarianz, Zeitkovarianz, Weltzeitbindung,
Ordnungssensitivitaet, relative Feldzeit, Memory, Organisation, Topologie,
Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Der separate
[one-shot Lauf-196-Einstieg](Z1_LAUF196_EINSTIEG_UND_AUSFUEHRUNGSSPERRE.md)
ist inzwischen implementiert und synthetisch geprueft. Als Naechstes darf er
genau einmal real ausgefuehrt werden.
