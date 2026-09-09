# S2-NW: einmalige rezeptorfreie Vorversiegelung

## Abschluss und Umfang

Lauf-ID `s2nw-source-preseal-20260909-01`.
Nach bestandener [20/20-Quellenqualifikation](../s2nw-source-binding-qualification-20260909-01/BEFUND.md)
genau ein Aufruf `C:/Python314/python.exe -m reports.s2nw.preseal_once`
aus workspace. Dieser erzeugte einmal die Quellen und fuehrte danach genau
eine unabhaengige read-only Bindungspruefung durch. Exit-Code `0`, kein Retry.

Status: `S2NW_SOURCES_PRESEALED` und `S2NW_PRESEAL_VERIFIED`.
26/26 getrennte PCM-Fenster, 124.800 Samples, insgesamt 499.200 erzeugte
PCM-Bytes. Hoechstens ein vollstaendiger 19.200-Byte-Payload gleichzeitig;
nach Hashbildung freigegeben, keine Rohpayloadablage. Keine Deduplizierung.

Die literal gebundene Reihenfolge bleibt l01 w00..w05, danach s01..s04
je w00..w04. Native Uhr `audio.sample`, Fenster je 4.800 Samples,
Snapshotindex aus exakt teilbarem Fensterstart. Keine Quellenanpassung,
Normalisierung, Ersatzquelle oder vorweggenommene Rezeptorgueltigkeit.

## Lern- und Pruefbindungen, noch nicht ausgefuehrt

- Ausfuehrungswurzel: sechs Lernfenster, vier Stellen t01..t04 mit Update
  erst nach den beobachteten Zielen l01 w02..w05.
- Einfriergrenze nach t04 und vor Erzeugung von `nw-s01-w00` im spaeteren
  Funktionslauf. Ein unveraenderter Freeze fuer alle zwoelf Pruefstellen;
  frisches Praefix je Strom, keine Testupdates oder stromuebergreifende Historie.
- Drei vorab feste Arme LEARNED_DELTA, LINEAR und PERSIST. Rechnung und
  Fehlerformeln sind ausschliesslich literale Metadaten; kein Lerner ausgefuehrt.
- Initialzustand mit n=0 und positiven Nullwerten; kein erwarteter
  Lernkoeffizient aus Rezepten (`expected_learned_coefficient=null`).
- Evaluationswurzel separat: sechs strikte Fortsetzungsbedingungen gegen
  beide Baselines, drei getrennte Wechselverlustbedingungen, je Baseline
  eigene WIN/TIE/LOSS-Befunde. Trainingsbefunde ersetzen keine Transferpruefung.

Die jetzige rezeptorfreie Payloadversiegelung ist **nicht** die spaetere
prospektive Zielverarbeitung. Dort muessen Prognosen vor jeder Zielerzeugung
gebunden, Updates erst nach Zielbeobachtung zugelassen und der Lernzustand
vor allen Prueffenstern eingefroren werden. Diese funktionale Aufrufgrenze
ist bislang nur geplant, nicht durch die Quellenqualifikation nachgewiesen.

## Bytegleichheiten bei getrennten Quellen

Die vollstaendigen Payloadhashes stehen in `seal.json` und jeder Quellenzeile.
Es wurden genau diese vier Kollisionsgruppen erfasst; keine wurde beseitigt:

| Bytegleiche Quellen | Einordnung der Rezepte, keine Rezeptorauswertung |
| --- | --- |
| nw-s01-w00, nw-s02-w00, nw-s03-w00, nw-s04-w00 | gemeinsames erstes Praefixfenster |
| nw-s01-w01, nw-s02-w01, nw-s02-w03, nw-s03-w01, nw-s04-w01 | zweites Praefix und spaetere Pegelrueckkehr |
| nw-s01-w02, nw-s02-w02, nw-s03-w02, nw-s03-w03, nw-s03-w04, nw-s04-w02 | drittes Praefix und unveraendertes Fortbestehen |
| nw-s04-w03, nw-s04-w04 | wiederholtes Fenster der zweiten Pruefgruppe |

Alle 26 Quellen behalten eigene IDs, Ordinalzahlen, Zeitfenster und
Quelldigests. Bytegleichheit wird nicht als unabhaengige Replikation oder
als vorab gepruefte Gleichheit spaeterer Rezeptorwerte ausgegeben.

## Bindungen und lesende Pruefgrenze

CPython 3.14.4, 64 Bit; `C:/Python314/python.exe` und Python-DLLs gehasht.
`math` ist nach `__spec__.origin` und Built-in-Mitgliedschaft als eingebaut
gebunden, ohne erfundene Moduldatei. NumPy 2.4.4 ist ueber Paket-/Dateimetadaten
gebunden, nicht importiert. Unveraenderte reine NU-Synthesehelfer sowie
NW-Renderanschluss sind durch Datei- und Funktions-AST-Digests gebunden.
Keine historischen Haupt-/Versiegelungseinstiege wurden ausgefuehrt.

| Bindung | Digest |
| --- | --- |
| NW-Planfile SHA-256 | `246f43d3f713aa638b586a0deee04c18066077db77115639c3a8c6e977887b98` |
| Ausfuehrungswurzel | `96b902af68ffb2662aaa6995756b1ca6c435b157012b17cb1065b18c7d5a4a7c` |
| Evaluationswurzel | `28d5af12ba9c3be0a101017f003593a37f7fa81648033d9ff6fd7f82a4cd79d3` |
| Siegel | `9df2bc5147c6e85f51eb1a628bf2f0fffcf851e6037c74f52cfc2b5ef4fe4a65` |
| Verifikation | `5707a3147139c291fe4fb9816e718d47710288d9a07d52c225db9fc21a95075b` |
| Rohprofil | `5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7` |
| Halbprofil | `4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f` |

Dateigroessen: Ausfuehrungsplan 40.972, Evaluationsplan 2.428,
Vorbindung 37.371 und Siegel 4.415 Byte, jeweils unter 65.536 Byte;
Verifikation 2.245 Byte unter 262.144 Byte.
Quellhashes und Umgebung vor/nach Versiegelung stimmen ueberein.
Alle drei geprueften Dateien sind vor/nach Verifikation bytegleich gehasht.

Die unabhaengige Pruefung rekonstruiert die literal erwarteten Quellen-,
Zeit-, Stellen-, Freeze- und Bewertungsmetadaten und prueft Digests,
Zaehler, Qualifikation, Umwelt und Kollisionsliste. Sie erzeugt **keine**
PCM-Payloads erneut und beweist deshalb nicht unabhaengig deren numerische
Synthese. Diese Bindung beruht auf dem qualifizierten Generator und den
einmal gemessenen Payloadhashes. Kein Prognose-/Lernzeitablauf wird bewiesen.

Rezeptor-, NJ-, Koeffizienten-/Lern-, Prognose-, Fehler-, Memory-, Feld-,
Kontext- und Runtimeaufrufe jeweils `0`. Gates bleiben `False`; ME/MI
gesperrt. Historische Belege, fremde Aenderungen und Bootstrap unveraendert.

Noch kein Rezeptor-, Lern- oder Transferbefund. Ein spaeterer Erfolg waere
ein aus Erfahrung geschaetzter Vorhersageparameter mit begrenztem
Transfernutzen, keine Quellenidentitaet, Objektbindung oder allgemeines
Sequenzlernen. Der reale Lern-/Transferlauf bleibt separat gesperrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Quellen-,
Lernstellen- und Freeze-Bindungen vor Freigabe eines Prognoseanschlusses weiter.
