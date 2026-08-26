# W7-X: Vertrag fuer Siebenpfad-Quellplan und Checkpointkopien

## Entscheidung

`SEVEN_PATH_SOURCE_PLAN_CONTRACT_BOUND`

W7-X bindet statisch die Reihenfolge der in W7-W vollstaendig belegten
Quellen. Der Vertrag erzeugt noch keinen Planadapter, verarbeitet keine
Sequenz und startet weder Modell noch Matrix.

## 1. Bindungen

Ein spaeterer Quellplan muss unveraenderlich an folgende Rollen gebunden
sein:

- W7-M-Matrix- und Regionsdigest;
- vorhandener K2-B-Basisinventardigest;
- W7-W-Symmetrieinventardigest;
- W7-W-Autorisierungsdigest;
- Organismusuhr `organism.mcm_f3_k2b`;
- Tickrate `1_000_000`;
- genau die Pfade `AB`, `AG`, `BA`, `BG`, `UA`, `UB` und `UG`;
- genau die Checkpoints 0 bis 4.

Die Pfadbezeichnungen sind technische Quellenrollen. Sie sind keine Klasse,
Bedeutung, Belohnung oder Zielvorgabe.

## 2. Gemeinsame Zeitordnung

Die Hauptpfade besitzen ausschliesslich folgende kausale Zeitordnung:

| Rolle | Intervall oder Tick |
| --- | --- |
| Praefix A oder B | 0 bis 4 |
| Uniformstart U | Tick 4, ohne Quellsegment |
| Checkpoint 0 | Tick 4 |
| Fortsetzungsschritt 1 | 4 bis 5 |
| Checkpoint 1 | Tick 5 |
| Fortsetzungsschritt 2 | 5 bis 6 |
| Checkpoint 2 | Tick 6 |
| Fortsetzungsschritt 3 | 6 bis 7 |
| Checkpoint 3 | Tick 7 |
| Fortsetzungsschritt 4 | 7 bis 8 |
| Checkpoint 4 | Tick 8 |

Ticks sind hier nur externe Organismusuhrgrenzen. Sie sind keine Feldzeit.

## 3. Vollstaendiger Hauptpfadplan

| Pfad | Start/Praefix 0-4 | Fortsetzung 4-8 |
| --- | --- | --- |
| `AB` | vorhandener kombinierter A-Praefix | vorhandene B-Schritte 0 bis 3 |
| `AG` | vorhandener kombinierter A-Praefix | vorhandene G-Schritte 0 bis 3 |
| `BA` | additiver kombinierter B-Praefix | additive A-Schritte 0 bis 3 |
| `BG` | additiver kombinierter B-Praefix | vorhandene G-Schritte 0 bis 3 |
| `UA` | Uniformstart bei Tick 4 | additive A-Schritte 0 bis 3 |
| `UB` | Uniformstart bei Tick 4 | vorhandene B-Schritte 0 bis 3 |
| `UG` | Uniformstart bei Tick 4 | vorhandene G-Schritte 0 bis 3 |

`G` bezeichnet ausschliesslich die vorhandenen
`interruption_steps`-Quellen. U ist kein Nullkontakt und keine erzeugte
Sequenz, sondern der unveraenderte vorregistrierte Anfangszustand am
Checkpoint 0.

Die vier einzelnen additiven B-Praefixschritte aus W7-W bleiben technische
Support- und Autorisierungsrollen. BA und BG verwenden im Hauptplan genau den
verlustfrei kombinierten B-Praefix. Ein stiller Austausch gegen vier
Einzelschritte oder eine gemischte Segmentierung ist unzulaessig.

## 4. Hauptzustandsketten

Jeder Pfad besitzt fuer jedes ausgefuehrte Modell eine eigene Hauptkette.
Zulaessig sind zwei technisch gleichwertige Aufbauarten:

1. vollstaendig getrennte Berechnung identischer gemeinsamer Praefixe;
2. unveraenderliche Kopie eines vollstaendigen Praefixzustands an der
   vorregistrierten Verzweigungsgrenze.

Die gewaehlte Aufbauart muss vor einer Ausfuehrung im Plandigest gebunden
sein. Nach Tick 4 duerfen Pfade keine veraenderbaren Zustandsobjekte,
Digestketten oder Fortsetzungsbindungen teilen. Insbesondere duerfen A-B-
und B-A-Linien nicht gekreuzt werden.

P0-S/H, gekoppelter Feldzustand, M-Substratzustand und jeder externe
Observerzustand bleiben getrennte Zustandsrollen. Ein Digest einer Rolle
darf keine andere Rolle ersetzen.

## 5. Passive Checkpoints

Checkpoint 0 wird nach abgeschlossenem A-/B-Praefix oder direkt auf dem
Uniformstart bei Tick 4 gebunden. Checkpoint 1 bis 4 werden jeweils nach
genau einem weiteren Fortsetzungsschritt gebunden.

Ein Checkpoint darf nur unveraenderliche Referenzen festhalten:

- Pfad und Checkpointnummer;
- Tick;
- zuletzt abgeschlossenen Hauptsegmentdigest;
- Digest des aktuellen P0-S/H-Zustands;
- getrennte Digests aller vorhandenen Modellzustaende;
- getrennte Digests aller vorhandenen Observerzustaende;
- Vorgaenger-Checkpointdigest;
- kanonischen Checkpointdigest.

Fehlt eine noch nicht implementierte Modellrolle, wird sie nicht durch null,
P0 oder einen Observer ersetzt. Sie bleibt im statischen Plan als noch nicht
ausfuehrbar markiert.

## 6. Probeplan auf Zustandskopien

Jeder Pfad besitzt an jedem Checkpoint genau eine vorhandene Probe:

| Probe | Kopiergrenze | Probeintervall |
| --- | --- | --- |
| P0 | Checkpoint 0, Tick 4 | 4 bis 5 |
| P1 | Checkpoint 1, Tick 5 | 5 bis 6 |
| P2 | Checkpoint 2, Tick 6 | 6 bis 7 |
| P3 | Checkpoint 3, Tick 7 | 7 bis 8 |
| P4 | Checkpoint 4, Tick 8 | 8 bis 9 |

Vor jeder Probe werden alle fuer den untersuchten Arm erforderlichen
Zustandsrollen am Checkpoint unveraendert in einen eigenstaendigen
Probeast kopiert. Die Probe darf ausschliesslich diesen Ast fortsetzen.

P0 bis P3 koennen zeitlich mit dem naechsten Hauptsegment ueberlappen, weil
beide auf getrennten Zustandskopien beginnen. Daraus entsteht keine
Zusammenlegung. Probeendzustand, Probeobserver und Probemessungen duerfen nie
in Hauptpfad, naechsten Checkpoint oder einen anderen Probeast zurueckwirken.

## 7. Segment- und Autorisierungsregeln

Jeder Haupt- oder Probesegmenteintrag bindet mindestens:

- Segmentrolle und Pfad;
- Quellrolle und Quelldigest;
- exaktes Start- und Endtick;
- Digest der tatsaechlich uebergebenen Rezeptorsequenzen;
- Vorgaenger-Zustandsdigest;
- erwartete Fortsetzungsrolle;
- Kennzeichen Hauptpfad oder Probeast.

Vorhandene W7-M-Quellen bleiben nach W7-R direkt gebunden. Additiver
B-Praefix und additive A-Schritte benoetigen zusaetzlich den exakten W7-W-
Autorisierungsvertrag. Pfad- oder Intervallabweichungen muessen vor jeder
Zustandsfortsetzung stoppen.

## 8. Plandigests

Jeder Pfad erhaelt einen kanonischen `path_plan_digest`. Er umfasst nur:

- globale Inventar- und Autorisierungsbindungen;
- gewaehlte Praefixaufbauart;
- geordnete Hauptsegmente;
- Checkpointrollen;
- geordnete Proberollen und ihre Quellendigestbindung.

Der globale `seven_path_plan_digest` bindet die sieben Pfadplandigests in
kanonischer Pfadreihenfolge. Er enthaelt keine Feld-, Modell-, Observer- oder
Messwerte und darf nicht nach einem Ergebnis veraendert werden.

## 9. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- genau sieben eindeutige Pfadplaene;
- exakt die in Abschnitt 2 gebundene Zeitordnung;
- lueckenlose vier Fortsetzungsschritte je Pfad;
- Uniformstart ohne erfundene Quellsequenz;
- kombinierten B-Praefix fuer BA und BG;
- passende W7-W-Autorisierung fuer jede additive Quelle;
- genau fuenf Checkpoints und fuenf Probeaeste je Pfad;
- Probequellen P0 bis P4 mit ihren vorhandenen Digests;
- unveraenderte Hauptzustandsdigests waehrend jeder Probe;
- verschiedene Probeast- und Hauptketten;
- deterministischen Pfad- und Gesamtplandigest;
- unveraenderte W7-M-/W7-W-Inventardigests;
- fehlende Exporte aus `current_api`;
- keine Reports, Runner, Browserstarts oder Laufmarker.

## 10. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein Segment fehlt, ueberlappt, doppelt vorkommt oder zeitlich verschoben
  wird;
- eine additive Quelle ohne passende W7-W-Autorisierung erscheint;
- BA oder BG die B-Praefix-Einzelschritte statt des kombinierten Praefixes
  verwenden;
- U als Nullsequenz, Gap oder kuenstlicher Weltkontakt materialisiert wird;
- ein Probeendzustand in die Hauptkette zurueckkehrt;
- Probeaeste untereinander einen veraenderbaren Zustand teilen;
- ein Checkpoint einen Zustand normalisiert, neutralisiert oder zuruecksetzt;
- A-B-, B-A- oder U-Linien Zustandsketten kreuzen;
- Plandigests Modellresultate oder Messwerte enthalten;
- der statische Plan bereits als Matrix- oder Forschungsbefund ausgegeben
  wird.

## 11. Aussagegrenze

W7-X ist nur ein statischer Quell- und Kopierplanvertrag. Es wurden keine
Sequenzen verarbeitet, keine Zustandsketten fortgesetzt und keine Pfade
verglichen. Daraus folgen keine Feldfunktion, kein Memory, keine Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## 12. Verwendete Quellen

- `docs/W7S_VERTRAG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md`
- `docs/W7T_IMPLEMENTIERUNG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md`
- `docs/W7V_VERTRAG_ADDITIVE_SYMMETRISCHE_QUELLENFAMILIE.md`
- `docs/W7W_IMPLEMENTIERUNG_ADDITIVE_SYMMETRISCHE_QUELLENFAMILIE.md`
- `mcm_field_organism/mcm_f3_k2b_source.py`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`
- `mcm_field_organism/w7t_observer_continuation.py`
- `mcm_field_organism/w7w_symmetric_source_family.py`

## 13. Naechster Schritt

W7-Y darf einen isolierten, nicht ausfuehrenden Siebenpfad-Planadapter und
seine Vertragstests implementieren. Er darf nur Quellreferenzen,
Checkpointrollen, Probeastrollen und Digests materialisieren. Keine
Zustandsfortsetzung, Pfadmatrix, kein Browser, Report oder Forschungslauf.
