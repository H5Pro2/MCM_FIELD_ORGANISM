# S2-JI - End-to-End-Kontextzulassungs- und Verbrauchsvertrag

## Status und Auftrag

`STATIC_END_TO_END_CONTROLLED_CONTEXT_USE_CONTRACT_BOUND`

S2-JI bindet den letzten begrenzten Funktionsschritt des privaten
Kontextzweigs:

```text
CURRENT_PERCEPTION_ONLY
gegen
CURRENT_PERCEPTION_PLUS_ADMITTED_CONTEXT
```

Geprueft wird genau eine spaetere maskierte visuelle Wahrnehmung. Ein bereits
gebildeter A/B-Memoryzustand wird read-only beurteilt, die qualifizierte
S2-JH-Zulassung wird angewendet und nur zugelassener Kontext darf maskierte
Werte ergaenzen.

S2-JI ist ausschliesslich statisch. Nicht freigegeben sind Implementierung,
Tests, Runner, Ausfuehrung, Feldzugriff, API, Snapshot, Lernoperation oder eine
weitere Kontextinfrastruktur.

## Gebundener Bestand

Technischer Ausgangsstand:

`e158a90b29190572cd5da5687bcc32b6e3bf206e`

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| S2-JG-Architekturvertrag | `docs/S2JG_ARCHITEKTUR_UND_KONTEXTZULASSUNGSVERTRAG.md` | `5bde38988b0203cbcf1173e14620ea9bdf372e7f22c7a0f3f682946d0ad426af` |
| Qualifizierte Zulassungsfunktion | `tools/_s2jh_private_controlled_context_admission.py` | `191c9216703885c24397fabd13dd15d359531445b0b9d4dce70cfda2126258bc` |
| Unabhaengige Zulassungsbaseline | `tools/_s2jh_private_direct_admission_baseline.py` | `e151b195d7aa7bda1e4edeee44eb25e83a273f615244409779e5fe525911e340` |
| S2-JH-Qualifikationsbefund | `docs/S2JH_PRIVATE_KONTEXTZULASSUNG_IMPLEMENTIERUNG_UND_QUALIFIKATION.md` | `42970562c54a4f6a5c52d1dfb4a70aaeccc5802c5b703ac99d3cba75f6190d0d` |
| Rollenadressierter Kontextverbraucher | `tools/_s2hq_private_role_addressed_context_consumer.py` | `cb9b3ecea1bfd0090d379bdbd46c317565ea58d664d2b3f66a64f33008960e57` |
| Unabhaengige rollenadressierte Fuellbaseline | `tools/_s2hq_private_direct_role_addressed_mask_fill_baseline.py` | `e42ed48b7c06baf5939654be0e470e8d39e8e98e837680c6128c92ac46c12254` |
| Reiner bestehender Funktionsauswerter | `tools/_s2gk_private_masked_visual_completion_evaluator.py` | `ac33ed97b670681250cb709b40332024ab107365836cd5641d27e34ee85e5cf5` |

Die bestehenden Memory-, Projektions-, Signal-, Aggregat-, Zulassungs- und
Verbrauchsfunktionen bleiben unveraendert. Historische Ergebnisdateien duerfen
nur als Methodenbeleg gelesen werden; sie sind kein Eingang eines spaeteren
S2-JI-Laufs.

## Funktionskette

Der spaetere Versuch muss fuer jeden Fall aus frischen Anfangszustaenden genau
folgende Richtung materialisieren:

```text
reale gebundene Wahrnehmungsgeschichte
-> atomarer A_RECENT-/B_STABLE-Zustand
-> read-only A/B-Projektion
-> rezeptorgetreues Fuenf-Status-Signal
-> qualifizierte S2-JH-Zulassung
-> read-only Folgewahrnehmung
   +-> CURRENT_PERCEPTION_ONLY
   \-> CURRENT_PERCEPTION_PLUS_ADMITTED_CONTEXT
-> getrennte reine Auswertung
```

Memory, A/B-Projektion, Signal und Zulassung muessen vor und nach jedem
Probezugriff identische Zustands- und Belegdigestwerte besitzen. Der
Folgewahrnehmungspfad darf keine Formation, Konsolidierung, Verdrangung,
Rezeptoranpassung oder Feldoperation ausloesen.

## Eingaben und Rollen

Beide Funktionsarme erhalten dieselbe validierte maskierte Probe mit 18
visuellen Positionen, davon neun sichtbar und neun maskiert. Zielwerte liegen
ausschliesslich in einer getrennten Auswerterfixture.

Der Plus-Arm erhaelt zusaetzlich genau ein vollstaendig validiertes
`ControlledPerceptualContextAdmission` samt den bereits gebundenen
S2-IC-Anwendbarkeitsbefunden. Er darf keine Wunschrolle, Fallkennung,
Sollentscheidung, Belohnung oder Zielwerte erhalten.

Die Zulassungsentscheidung wird nicht neu berechnet. Status, zugelassene
Rolle, ungeordneter A/B-Aequivalenzset-Digest und gemeinsamer
Ergaenzungsdigest muessen exakt dem qualifizierten S2-JH-Ergebnis entsprechen.

## Verbindliche Verbrauchsregeln

### `SINGLE_SOURCE`

`ALLOW_CONTEXT` muss genau eine `admitted_role` enthalten. Der Plus-Arm darf
den vorhandenen qualifizierten S2-HQ-Rollenverbraucher genau fuer diese Rolle
aufrufen. Der andere Bereich darf Ergebnis, Status, Ledger oder Herkunft nicht
beeinflussen.

### `CONSISTENT`

`ALLOW_CONTEXT` darf keine Einzelrolle enthalten. Beide bereits validierten
Anwendbarkeitsbefunde muessen denselben `common_supplement_digest` tragen.
Der Plus-Arm darf ausschliesslich die positionsweise identische gemeinsame
Neun-Werte-Ergaenzung verwenden.

Die gemeinsame Ergaenzung ist kein Mittelwert, keine Verschmelzung und keine
Auswahl der ersten Listenposition. Ihre Bindung muss aus dem ungeordneten
A/B-Aequivalenzset und dem gemeinsamen Ergaenzungsdigest entstehen. Jede
Abweichung zwischen A und B stoppt vor einer Fuellung fail-closed.

### Enthaltung

Fuer `CONFLICT`, `NO_CONTEXT` und `NO_APPLICABLE_CONTEXT` muss die S2-JH-
Entscheidung `PROCEED_WITHOUT_CONTEXT` lauten. Der Plus-Arm darf dann keinen
Kontextverbraucher aufrufen und gibt exakt die unveraenderte maskierte
Wahrnehmung des Current-only-Arms aus.

Es gibt keinen Fallback, keine Teilfuellung und keine Abschwaechung eines
Konflikts.

## Zwei Funktionsarme

### `CURRENT_PERCEPTION_ONLY`

Der Arm validiert die Probe, erhaelt keinen Kontext und muss ausgeben:

```text
completed_positions = ()
completed_value_count = 0
output_values = unveraenderte Probe einschliesslich Maskenmarkern
```

### `CURRENT_PERCEPTION_PLUS_ADMITTED_CONTEXT`

Der Arm validiert dieselbe Probe und die S2-JH-Zulassung.

- Bei `SINGLE_SOURCE` werden genau die neun maskierten Werte der zugelassenen
  Rolle ergaenzt.
- Bei `CONSISTENT` werden genau die neun gemeinsam identischen Werte ergaenzt.
- Bei den drei Enthaltungsstatus wird kein Wert ergaenzt.
- Alle neun sichtbaren Werte bleiben in jedem Fall bitgleich.
- Herkunft, Zulassungsstatus, Ergaenzungsdigest und Ergebnis bleiben
  transparent gebunden.

Das Ergebnis besitzt kein Feld fuer Gewinner, Rang, Score, beste Erinnerung,
gemischten Kontext oder Feldwirkung.

## Pflichtbaseline

Die staerkste Engineeringbaseline ist die unabhaengige Komposition aus:

1. direkter S2-JH-Entscheidungstabelle;
2. direkter rollenadressierter Maskenfuellung bei `SINGLE_SOURCE`;
3. direktem Gleichheitsnachweis und direkter gemeinsamer Fuellung bei
   `CONSISTENT`;
4. unveraenderter Probe bei allen Enthaltungsstatus.

Die Baseline erhaelt dieselben Signal-, Zulassungs-, Probe- und
Kontextbelege sowie identische funktionale Budgets. Sie darf weder die
End-to-End-Funktion noch deren Zwischen- oder Endergebnis aufrufen. Umgekehrt
darf der End-to-End-Pfad kein Baselineergebnis verwenden.

Vollstaendige Gleichheit mit dieser Baseline ist der erwartete
Engineeringbefund und schliesst jeden Claim auf neue MCM-Physik aus.

## Endliche Fallmatrix

Ein spaeterer einmaliger Funktionslauf muss die bereits materialisierten
S2-IE-Faelle aus neuen Zustaenden und ohne Wiederverwendung alter
Ergebnisdateien erzeugen:

| Fall | Status | Zulassung | Plus-Arm |
| --- | --- | --- | --- |
| `c01` | `CONSISTENT` | gemeinsamer Kontext | neun gemeinsame P1-Maskenwerte |
| `c02` | `CONFLICT` | Enthaltung | Probe unveraendert |
| `c03` | `CONFLICT`, gespiegelt | Enthaltung | Probe unveraendert |
| `c04` | `SINGLE_SOURCE` aus A | `A_RECENT` | neun P11-Maskenwerte aus A |
| `c05` | `SINGLE_SOURCE` aus B | `B_STABLE` | neun P1-Maskenwerte aus B |
| `c06` | `NO_CONTEXT` | Enthaltung | Probe unveraendert |
| `c07` | `NO_APPLICABLE_CONTEXT` | Enthaltung | Probe unveraendert |
| `c08` | `NO_APPLICABLE_CONTEXT`, gespiegelt | Enthaltung | Probe unveraendert |

Die sechs gebundenen Geschichten und 38 Formationen aus S2-IE bleiben
unveraendert. Die drei Funktionsarme Current-only, Plus-admitted und direkte
Baseline erhalten pro Fall dieselbe Probe und dieselben fertig gebildeten
read-only Memorybelege. Eine zweite Bildung fuer einen Arm ist unzulaessig.

## Funktionale und technische Budgets

Pro Fall gelten hoechstens:

```text
maskierte Probe                         = 1
validiertes A/B-Bundle                  = 1
validiertes Fuenf-Status-Signal         = 1
validierte S2-JH-Zulassung              = 1
Current-only-Ausgabe                    = 1
Plus-admitted-Ausgabe                   = 1
direkte Baselineausgabe                 = 1
sichtbare Positionspruefungen je Fuellarm <= 9
maskierte Kopien je Fuellarm            = 0 oder 9
neue Memory-/Rezeptor-/Feldoperationen  = 0
```

Die spaetere Implementierung muss Validierung, Digests, Owner und
Tabellenentscheidung vollstaendig zaehlen. Der Plus-Arm und die Baseline
erhalten identische Obergrenzen. Native Laufzeit und Prozessspeicher werden
getrennt berichtet und sind keine kostenlose Funktionsressource.

Eine private Implementierung darf hoechstens einen reinen End-to-End-Adapter,
eine unabhaengige Baselinekomposition und fokussierte neutrale Tests anfuegen.
Neue Recorder-, Registry-, Runner- oder Plattformmodule sind durch S2-JI
nicht begruendet.

## Auswertung

Der reine Auswerter erhaelt Zielwerte erst nach Abschluss beider Arme und
berichtet je Fall getrennt:

- erhaltene sichtbare Werte;
- Anzahl und Herkunft ergaenzter Maskenwerte;
- Fehler nur auf maskierten Positionen;
- Gleichheit von Plus-Arm und Direktbaseline;
- unveraenderte Memory-, Signal-, Zulassungs- und Bundlebelege;
- funktionale Kosten beider Arme.

Ein begrenzter Nutzen liegt nur vor, wenn `c01`, `c04` und `c05` gegenueber
Current-only genau die vorab gebundenen fehlenden Werte bereitstellen und
`c02`, `c03`, `c06`, `c07` sowie `c08` unveraendert ohne Kontext fortfahren.

## Falsifikation und `NOT_EVALUABLE`

Bei vollstaendig gueltiger Beweiskette ist die Funktion falsifiziert, wenn
mindestens eines gilt:

- ein zugelassener Fall liefert nicht die gebundene Ergaenzung;
- ein Enthaltungsfall veraendert einen sichtbaren oder maskierten Wert;
- `CONSISTENT` bevorzugt A oder B, mittelt oder verschmilzt Werte;
- der nicht zugelassene Bereich beeinflusst `SINGLE_SOURCE`;
- Plus-Arm und unabhaengige Direktbaseline weichen bei identischen Eingaben
  funktional voneinander ab;
- ein read-only Vor-/Nachzustand aendert sich.

`NOT_EVALUABLE` gilt bei fehlender, fremder, widerspruechlicher oder
unvollstaendiger Quellen-, Probe-, Status-, Zulassungs-, Owner-, Digest-,
Zustands- oder Ledgerbindung. Ein solcher technischer Befund ist keine
Funktionsfalsifikation und darf nicht nachtraeglich als Erfolg ausgewertet
werden.

## Erfolgsstatus und Abschlussgrenze

Bei vollstaendigem Erfolg lautet der eng begrenzte Befund:

`S2JI_CONTROLLED_CONTEXT_USE_VALID_DIRECT_TABLE_AND_FILL_EXPLAIN`

Er bestaetigt nur, dass ein bereits zugelassener innerer Wahrnehmungskontext
eine spaetere maskierte Wahrnehmung kontrolliert ergaenzen kann und dass bei
Konflikt oder Abwesenheit sicher ohne Kontext fortgefahren wird. Die direkte
Baseline erklaert die Funktion vollstaendig.

Nach einem gueltigen einmaligen Funktionsbefund wird dieser Kontextzweig
geschlossen. Nicht nachgewiesen sind automatische Kontextwahl, Semantik,
fortlaufende Episodenbildung, Lernen, Feldrueckwirkung oder MCM-spezifische
Physik.

Der danach getrennt zu bindende Wahrnehmungsgrenzvertrag muss Browser,
Desktop, Video, Simulation und Kamera als austauschbare reine Pixelquellen
sowie kontrollierte Audioquellen behandeln. DOM, URL, Seitentext,
Objektmetadaten und sonstige Quellsemantik duerfen weder Rezeptor-, Memory-
noch Kontextinput werden. Diese offene Grenze blockiert S2-JI nicht und wird
durch S2-JI nicht vorweggenommen.
