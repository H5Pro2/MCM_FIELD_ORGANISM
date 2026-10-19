# REV1: Diagnose der gespeicherten Entscheidungen Q129–160

2026-10-16. Ausschließlich bestehende REV1-Archive; keine Quellen, Policy-Ausführung, Alternativausgaben, Bootstrapziehungen oder Signifikanztests. Das Forschungsurteil INCONCLUSIVE bleibt unverändert.

## Vollständige Rückführung der Summen

Alle 1024 Primärziele sind genau einem gespeicherten U-Entscheidungsgrund zugeordnet. Die Gründe wurden zusätzlich anhand der eingefrorenen berechtigten Hypothesen geprüft. 418 unterschiedliche U/R-Ausgaben ergeben 222 bessere und 196 schlechtere Ziele; 606 Ziele bleiben gleich. Gewinn 75,75, Schaden 61,75, Nettogewinn 14. Keine Zielposition wurde entfernt.

| Entscheidungsgrund | Ziele | Verschiedene Ausgaben | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kein berechtigter Kontext | 40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 |
| Ausschließlich kalte Hypothesen | 66 | 66 | 26 | 40 | 0 | 13/2 | 10 | -7/2 |
| Keine negative warme Bewertung | 220 | 220 | 115 | 105 | 0 | 115/4 | 105/4 | 5/2 |
| Gleichstand beim besten negativen Wert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Eindeutige Kontextwahl | 698 | 132 | 81 | 51 | 566 | 81/2 | 51/2 | 15 |

Die vollständigen eigenen Summen für die 418 verschiedenen Ausgaben stehen zusätzlich unter reasons[].different in result.json. Da an diesen binären Primärzielen verschiedene Ausgaben verschiedene Fehler ergeben, sind dort genau 222 Verbesserungen und 196 Verschlechterungen, keine gleich guten verschiedenen Ausgaben.
Deskriptive Einordnung: Eindeutige Kontextwahl trägt netto +15 bei, Enthaltung ohne negative warme Bewertung +2,5, ausschließlich kalte Hypothesen −3,5. Die beiden Enthaltungsgründe zusammen ergeben −1; zusammen mit +15 aus unterschiedlichen Kontextwahlen entstehen die bekannten +14. Ein negativer Bestwert-Gleichstand tritt überhaupt nicht auf. Diese Aufteilung ist keine neue Signifikanz- oder Kausalaussage.

## Getrennte Warm- und Bestandsklassen

Jede der folgenden Partitionen deckt für sich dieselben 1024 Ziele ab. Tabellen nicht miteinander aufsummieren. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. Zusätzliche Kreuztabellen Entscheidungsgrund × Warmklasse bzw. × Bestandsklasse stehen in result.json.

| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| warm | none | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| warm | cold | 66 | 26 | 40 | 0 | 13/2 | 10 | -7/2 |
| warm | mixed | 135 | 66 | 69 | 0 | 33/2 | 69/4 | -3/4 |
| warm | warm | 783 | 130 | 87 | 566 | 211/4 | 69/2 | 73/4 |
| eligible | 0 | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| eligible | 1 | 646 | 66 | 66 | 514 | 33/2 | 33/2 | 0 |
| eligible | 2 | 338 | 156 | 130 | 52 | 237/4 | 181/4 | 14 |
| choice | both_persistence | 40 | 0 | 0 | 40 | 0 | 0 | 0 |
| choice | mixed | 286 | 141 | 145 | 0 | 141/4 | 145/4 | -1 |
| choice | same_context | 566 | 0 | 0 | 566 | 0 | 0 | 0 |
| choice | different_context | 132 | 81 | 51 | 0 | 81/2 | 51/2 | 15 |

## Herkunft und Rückmeldungen kalter Hypothesen

201 kalte Hypothesenauftritte an 201 Primärzielen, verteilt auf 201 Originalidentitäten einschließlich Offset. Rollen: {'1': 201} (0=retained, 1=candidate). 0 Auftritte haben eine frühere gespeicherte Rückmeldung für dieselbe Originalidentität und denselben Offset; davon 0 mit gültiger lebender Zelle. Bei 0 Auftritten ist zuvor eine gültige Fehlerzelle im gespeicherten Zustandsverlauf sichtbar.
Für alle 201 Auftritte sind Aufnahmezustand und internes close_segment-/Promotion-Ereignis belegt. 7 Auftritte stammen aus spätestens Frame 512 aufgenommenen Originalen, 194 aus später aufgenommenen. Abstände zwischen Aufnahme und Vorhersageframe (Frames: Häufigkeit): {'10': 19, '14': 5, '18': 6, '2': 127, '22': 2, '6': 42}.

cold-index.json verknüpft jeden kalten Auftritt mit seiner Originalfolge, Rolle/Generation, Offset, erster Aufnahme und Belegposition. In case-NN.json enthalten histories die gespeicherten berechtigten Vorkommen, Rückmeldungen und Zustandsübergänge einschließlich Zellanlage, Rollenwechsel oder Entfernung. Maßgeblich sind Originalordinalfolge und Offset; eine Promotion wird nicht als neue unabhängige Erfahrung gezählt. Die Originalbeobachtung selbst ist keine frühere Bewertung dieser später abrufbaren Hypothese.

Zeitgrenze: feedback:after mit accepted=f gehört zum Ziel f+1. Für eine Vorhersage auf t werden deshalb nur Ereignisse mit effektivem Frame <t als Vorgeschichte gezählt. Die beim aktuellen Ziel entstehende Zelle zählt nicht rückwirkend als warm. Bei der Entwicklung wurde diese Zählermehrdeutigkeit anhand des ersten Archivfalls erkannt und ausschließlich aus den bereits extrahierten Zuständen berichtigt; clock-boundary-audit.json dokumentiert die Korrekturen. Ergebnisrichtungen und Gewinn-/Schadenssummen waren nicht betroffen.

Belegt sind gespeicherte Zustandsfolgen und Entscheidungswege. Nicht belegt ist, ob eine andere Auswahl- oder Initialisierungsregel die Fehler reduziert hätte. Nicht gespeicherte lokale Zwischenvariablen und kontrafaktische Verläufe werden nicht ergänzt. Keine verbleibende Informationslücke bei Zuordnung und Summen; die kausale Wirkung möglicher Regeländerungen bleibt ungeprüft.

## Feste Beispiele

Auswahl vor der Auswertung festgelegt: erste Archivposition nach aufsteigender Geschichte und Zielordinal, getrennt je Entscheidungsgrund und Ergebnisrichtung. Positionen sind nullbasiert innerhalb /U/forecasts; vollständige eingefrorene Hypothesen, Originalverweise, Fehler und Record-SHA stehen in examples.json und case-NN.json. Fehlende Kombinationen sind ausdrücklich ausgewiesen. Angezeigt ist jeweils die erste Vektorkomponente; es werden ausschließlich gespeicherte Ausgaben dargestellt.

| Grund | Richtung | Geschichte/Ziel | Forecastposition | U/R-Ausgabe | U/R-Fehler |
|---|---|---|---:|---|---|
| Kein berechtigter Kontext | better | nicht vorhanden | — | — | — |
| Kein berechtigter Kontext | worse | nicht vorhanden | — | — | — |
| Kein berechtigter Kontext | equal | 2/599 | 298 | 0.5/0.5 | 0.25/0.25 |
| Ausschließlich kalte Hypothesen | better | 1/519 | 258 | 0.5/0.75 | 0.25/0.5 |
| Ausschließlich kalte Hypothesen | worse | 1/539 | 268 | 0.5/0.75 | 0.25/0.0 |
| Ausschließlich kalte Hypothesen | equal | nicht vorhanden | — | — | — |
| Keine negative warme Bewertung | better | 1/563 | 280 | 0.5/0.75 | 0.25/0.5 |
| Keine negative warme Bewertung | worse | 1/551 | 274 | 0.5/0.75 | 0.25/0.0 |
| Keine negative warme Bewertung | equal | nicht vorhanden | — | — | — |
| Gleichstand beim besten negativen Wert | better | nicht vorhanden | — | — | — |
| Gleichstand beim besten negativen Wert | worse | nicht vorhanden | — | — | — |
| Gleichstand beim besten negativen Wert | equal | nicht vorhanden | — | — | — |
| Eindeutige Kontextwahl | better | 2/575 | 286 | 0.25/0.75 | 0.0/0.5 |
| Eindeutige Kontextwahl | worse | 1/515 | 256 | 0.25/0.75 | 0.5/0.0 |
| Eindeutige Kontextwahl | equal | 1/523 | 260 | 0.75/0.75 | 0.0/0.0 |

## Reproduktion, Bindungen und Ressourcen

Skript: tools/s2uc_ura1_rev1_diagnosis.py; Abschluss und unabhängige Prüfung der Beispielwahl: tools/s2uc_ura1_rev1_diagnosis_finalize.py. Beide lesen ausschließlich vorhandene Archive bzw. deren kompakte Auszüge. Beispielaufruf mit neuem exklusivem Diagnoseziel (keine Anweisung zu einem weiteren Lauf):

```powershell
& 'C:\Python314\python.exe' -m tools.s2uc_ura1_rev1_diagnosis --output reports/s2uc/ura1-rev1-diagnosis-reproduction
& 'C:\Python314\python.exe' -m tools.s2uc_ura1_rev1_diagnosis_finalize reports/s2uc/ura1-rev1-diagnosis-reproduction
```

bindings.json bindet alle 106 ursprünglichen Lieferdateien, deren Abschluss und die Auswertungsskripte. Pro Archiv wurden U/R-Forecasts und Rückmeldungen sowie U-Außen- und interne Lebenszyklusereignisse vollständig gegen ihre Erfassungs-Hashes geprüft. Die Gleichheit der U/R-Zustandsfolgen wird aus den unveränderten ursprünglichen Prüfbelegen übernommen. Dekodiert wird immer nur ein Archiv gleichzeitig; kein vollständiger Roharchivexport. Die Decodergrenzen für gzip, Encoded-Daten, Records und Referenztabellen bleiben erhalten.

resources.json und final-resources.json enthalten Laufzeiten und harte Job-Speichergrenzen; diagnosis-closure.json bindet die finale Lieferung. Höchstens 512 MiB Job, zwei Prozesse zulässig, tatsächlich ein Auswertungsprozess; Workerfrist 54000 s, Gesamtobergrenze 57600 s. Administrative Ausgabe unter 2 MiB und damit unter 64 MiB Gesamtexport. Historische Quellen, Archive und das Urteil INCONCLUSIVE unverändert.

## Höchstens eine Anschlussfrage

Lässt sich der beobachtete Nachteil ausschließlich kalter Kandidaten durch einen getrennt vorregistrierten Umgang mit ihrer ersten berechtigten Nutzung verringern, während die warme Fehlerauswahl unverändert bleibt? Begründung ist der isolierte Nettobeitrag −3,5 dieser Klasse gegenüber +15 aus eindeutiger Kontextwahl; fehlende Erstbewertung ist für alle kalten Auftritte belegt. Dies ist eine Anschlussfrage an den Projektleiter, keine Implementierungs- oder Versuchserlaubnis.
