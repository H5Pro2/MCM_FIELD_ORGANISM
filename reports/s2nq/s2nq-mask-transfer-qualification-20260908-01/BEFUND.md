# S2-NQ: private Masken-/Laufanbindung, neutrale Qualifikation

2026-09-08, Ausgangscommit `eecb081`. Genau ein Qualifikationsaufruf unter
`s2nq-mask-transfer-qualification-20260908-01`, kein Retry:

```powershell
python -m reports.s2nq.qualify_once
```

Arbeitsverzeichnis `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Ein untergeordneter Aufruf von
`python -m unittest tests.test_s2nq_private_transfer -v -f`.
**24/24 bestanden, Exit-Code 0**, Testdauer laut Protokoll 13.633 Sekunden.
Resultatstatus `S2NQ_NEUTRAL_QUALIFIED`. Alle vorab gebundenen Datei-SHA-256
blieben gleich. Kein Code wurde nach der Qualifikation korrigiert.

## Implementierter Umfang

Sechs kleine private Module, eine Testdatei und eine begrenzte
Qualifikations-Aufrufbindung; keine neue Recorder-/Runtimeplattform:

- `_s2nq_private_mask_scan.py`: zwei exakte versionierte Bandplaene, 24
  indexgebundene Cuewerte, unveraenderte ALL-BANDS-A-/Mittelwert-Slow-Regeln,
  vollstaendige 9/3/8-Scans, A-interne und oeffentliche Aufloesung.
- `_s2nq_private_direct.py`: eigene Scans und eigene Entscheidungstabelle;
  keine produktiven Scan-/Entscheidungshelfer. Gemeinsame technische
  Eingabetypen und Validierungen, getrennte Numerik.
- `_s2nq_private_sources.py`: literale 36-Ereignis-Folge und eigene
  Quellen-/Zeitbindung an vorhandene reine Generatoren und NJ. Historische
  NP-Wurzeln bleiben historische Identitaeten; neue Ereigniszeiten werden
  nicht in alte Materialisate geschrieben.
- `_s2nq_private_run.py`: geschlossener `run_main_once`, drei frische
  Bildungsgeschichten plus Nullzustand, atomarer Gesamtbeleg ueber den
  vorhandenen NE-Dateiweg. Fehlerabschluss ohne fachliche Teilauswertung.
- `_s2nq_private_verification.py`: offline Quellen-, Zustands-, Receipt-,
  Fast-Rang-, PPB-Zuordnungs-/Update- und vollstaendige Scanpruefung.
  Zusaetzliche Verifikationsarbeit separat begrenzt und ausgewiesen.
- `_s2nq_private_evaluation.py`: Herkunft aus den tatsaechlichen
  Formationsketten, getrennte Beziehungs-/oeffentliche N/D/R/L, Verluste,
  Fehlzulassungen und Zielentfernung. Siehe offene Variationsgrenze unten.

Historische KZ-/NE-/NL-Module und Validatoren bleiben unveraendert.
Keine Vollvektorumordnung oder globale Maskenaenderung. Eine Hypothese
enthaelt nur die 24 Kandidatenwerte im jeweiligen Komplement und bleibt
unangewandt. Erhaltung vergleicht Bereich und Herkunft, nicht identische
Ausgabezahlen zwischen den Sichten. Die zusammenhaengende Sicht wurde an
vier neutralen Zustaenden gegen den bestehenden Halbprofil-ALL-BANDS-Abruf
geprueft: gleiche Entscheidungen, Treffer, Statistiken und Hypothesenwerte.

## Beobachtete neutrale Arbeit

| Messung/Zaehlung | Wert |
| --- | --- |
| Neue neutrale Scanaufrufe, beide Implementierungen | 81 |
| Zugehoerige beobachtete Differenzen plus Kandidatengleichheit | 17.304 |
| Zusaetzliche Verifikationsvergleiche | 18.264 |
| Historische Referenzscanaufrufe, separat | 4 |
| Reale neutrale atomare Formationen | 4 |
| NJ-Projektionen synthetischer Rohzustandsfixtures | 6 |
| Rezeptoranalysen / NP-Payloads / NQ-Hauptgeschichten | 0 / 0 / 0 |
| Groesster gepruefter Einzelabrufbeleg | 18.481 Byte |
| Konkrete volle neutrale Serialisierung | 2.665.108 Byte |
| Gespeicherter neutraler Gesamtbeleg | 191.217 Byte |
| Gespeicherter neutraler Pruefbeleg | 6.378 Byte |

Die kleinen neutralen Quellen sind synthetische, gueltige AuditoryState-
und visuelle Kontaktfixtures. Keine Behauptung eines neuen Rezeptorbefunds.
Die sechs Ereignisse enthalten vier Formationen und zwei read-only Cues;
der eingeschobene Cue setzt den Zustand nicht zurueck. Die realen neutralen
PPB-Uebergaenge lauten in beiden Modalitaeten NO_UPDATE, CREATED, MATCHED,
MATCHED; Endsupport 3. Der letzte Cue enthaelt sich wegen Mehrdeutigkeit und
bleibt technisch verifizierbar. Der getrennte Auswerter akzeptiert diesen
gueltigen negativen Fall, ohne eine richtige Hypothese zu erfinden.

Der synthetische Serialisierungsfall erzeugt nur JSON mit voller Belegform,
keine 36-Ereignis-Ausfuehrung. Er ersetzt weder einen realen Groessenbefund
noch einen Prozesspeaknachweis. Einzel- und Gesamtlimits bleiben im Code
hart: 32.768 bzw. 4.194.304 Byte; keine Grenzerhoehung.

## Getrennte Offline-Pruefung

Die Vorbindung nennt die spaeteren Abruf- und Verifikationsbudgets separat.
Im gespeicherten neutralen Gesamtpruefbeleg stehen unter anderem:

| Zusaetzliche Arbeit dieses Gesamtpruefbelegs | Belastung |
| --- | --- |
| Armpruefungen / Slotinspektionen | 8 / 160 |
| Banddifferenzen / Kandidatengleichheit | 768 / 192 |
| Formationspruefungen / Fast-Rangterme | 4 / 1.008 |
| PPB-Zuordnungsterme | 672 |
| Konservativ berechnete Updatekomponenten | 2.688 |
| Zustandsdekodierungen / Validierungspassagen | 5 / 17 |
| Konservativer Zustandswert-Formpruefdeckel | 94.656 |
| Quellenbindungen / Eingabewertpositionen | 6 / 1.440 |

Diese Zahlen sind nicht die Summe aller manipulativen Testunterfaelle und
werden nicht als Teil der 17.304 Ausfuehrungsvergleiche versteckt.
Die obigen 18.264 zaehlen die zusaetzlichen Scanvergleiche im gesamten
neutralen Aufruf. Keine zweite Formation oder Rezeptoranalyse zur Pruefung.

Die Offline-Pruefung validiert vorhandene NJ-Quellen-/Projektionsbindungen
und gerundete Werte. Ohne Rohspektren rekonstruiert sie keine Halbierung.
Der native TSPM-Resultatdigest wird als Herkunftsbindung mitgefuehrt, nicht
als unabhaengig rekonstruierter nativer Receipt ausgegeben. Fast-Slotwahl,
PPB-Slotwahl, Support, Updates und Zustandsketten werden separat nachgerechnet.
Die S2-NM-Gleichheitsgrenze des Halbprofils bleibt bestehen.

## Offene statische Auswertungsgrenze

Beim abschliessenden Lesen der neuen Auswertung faellt eine eng begrenzte,
von den 24 Testkoerpern nicht geschlossene Bedeutungsfrage auf:
`actual_variation` wird derzeit aus Cue-/Zielslot-Termdifferenzen gebildet.
Das ist eine **Abweichung vom gespeicherten Kandidaten**, nicht notwendig
eine Rezeptorvariation gegenueber der urspruenglichen Ziel-Formation.
Bei einem PPB-Prototyp kann bereits dessen Binary64-Update-Rundung diesen
Wert setzen, obwohl die Exaktkontrolle die urspruenglichen Rezeptorwerte
unveraendert reproduziert. Exakt-/Pegel-/Frequenz-/Spektral-Quellenrollen
bleiben zwar separat erhalten; diese Flagge darf aber nicht als unabhaengiger
Variationsnachweis ausgegeben werden.

Die neutrale Qualifikation bleibt bestanden; sie belegt keine richtige
Variationsklassifikation fuer diesen Rundungsfall. Keine nachtraegliche
Produkt-/Testkorrektur und kein weiterer Aufruf in diesem Auftrag.
Vor einer Hauptfreigabe sollte der Analyst die kleine Trennung entscheiden:
rezeptorseitige Cuevariation gegen die gebundene urspruengliche Formation
einerseits und Cue-/Slotabweichung inklusive PPB-Rundung andererseits.
Keine neue Distanzregel, Maske oder Quellenanpassung ist dafuer erforderlich.

## Dauerhafte Bindungen

Resultatdigest:
`004701c74b857aef8ad3137893deb858f51a39dd9f6fb4e654b8657a25aa6ec5`.
Stdout-SHA-256:
`d9a47dec488c86a6ffb7cfbba9a2e176114dbabdcdee56e944b23597090911ca`.
Stderr-SHA-256:
`a762792df897ee3f30a987ca1a697248d848eee37377ea7e0563f48f7ca608e0`.

| Eigene qualifizierte Datei | SHA-256 vor und nach Aufruf |
| --- | --- |
| tools/_s2nq_private_mask_scan.py | d4fa6d257a267e0f63fb89ba5e743f9b534afde4efb861da097266dae605f0be |
| tools/_s2nq_private_direct.py | d460d72db142e99491f4a360c884afe60c533a1f09c05504fe753b24a92af2c3 |
| tools/_s2nq_private_sources.py | 5e457d81f51ffc28c6a4d3e312e3026b3bb11bed0b910013eb52bcf6de60ff5e |
| tools/_s2nq_private_run.py | d6f64da5c2a79ad199b83e4db0502d4ba54d4f39b65beb5492b80c45b0b8a2ce |
| tools/_s2nq_private_verification.py | 0d7165b5b95c3680f248d4c0e14b8307e3e4a49d8cc789e0563ae202438ab684 |
| tools/_s2nq_private_evaluation.py | 449ecbf0c2ac222320dd252b776ddb091f8230f1b024ffff10e430850411aec2 |
| tests/test_s2nq_private_transfer.py | 8cea21e8d5f3d809e32a4cfde05d499897e970e159c5f21ab305d23595b41c2a |
| reports/s2nq/qualify_once.py | 0611b82073d445e0b3439ef323d033d89f1673eecaffe938805c90185aaf6af4 |

Alle weiteren Dokument-/Historien-/Komponentenbindungen stehen vollstaendig
in preregistration.json und result.json. NP-Materialisat und Historien wurden
nur gehasht, weder geparst noch verglichen. Kein Gate geoeffnet; keine
Memorykerne, Rezeptoren, Defaultadapter, historischen Belege, fremden Dateien
oder Bootstrap geaendert. Der reale NQ-Transfer bleibt separat gesperrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung der 24/24-
Qualifikation und der eng benannten Variationsklassifikation vor einer
Freigabe des realen Transferlaufs weiter.
