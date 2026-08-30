# S2-GD: Statischer Zwei-Bereich-Vertrag

## Auftrag und Status

S2-GD bindet ausschliesslich die statische Abbildung des bestaetigten
Drei-Rollen-Bestands auf die logischen Memory-Bereiche `A_RECENT` und
`B_STABLE`. Der Vertrag definiert eine moegliche Migration und ihre
Falsifikationsgrenzen. Er implementiert, migriert oder fuehrt nichts aus.

Der bestehende technische Bestand bleibt unveraendert:

```text
B4_RECENT | TSPM_FAST | TSPM_SLOW
```

Das gebundene Zielbild lautet:

```text
A_RECENT
- juengster Inhalt
- kurze Reihenfolge
- interne Fast-Spur

B_STABLE
- auditive und visuelle stabilisierte Prototypen
- keine Reihenfolge
```

Die zwei Bereiche sind eine logische Produkt- und Verbrauchersicht. Sie sind
keine nachtraegliche Behauptung ueber eine bereits vorhandene physische
Zwei-Bereich-Implementierung.

## Gebundene Grundlage

S2-GD ist an den technischen Ausgangsstand
`14defb0a7cc1c29d49ca6041adf9a986fba54e37` und folgende Quellen gebunden:

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Zwei-Bereich-Leitlinie | `docs/ANALYSTISCHE_LEITLINIE_MCM_MEMORY_ZWEI_BEREICHE.md` | `e6312fb2ad59845514fe33a5f755e61f672d0ea6131721cae4f6fc45ddeb94d9` |
| Qualifizierte Drei-Rollen-Projektion | `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| Atomarer B4-/TSPM-Koordinator | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| TSPM-Fast-/Slow-Kern und Receipt | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| S2-FZ-Funktionsbefund | `docs/S2FZ_UNABHAENGIGER_18_SCHRITT_BESTAETIGUNGSLAUF.md` | `443aae2ac3a7215f304487c2ec27da6bf3286f3e845cd4fd3e173f9f8258295f` |
| S2-GC-Qualifikation | `docs/S2GC_EINMALIGE_BUNDLE_WIEDERHOLUNGSQUALIFIKATION.md` | `2b94ba7f830588202aeea6c815b1f8d7fc73eada5ca2500b944ee287f2b435b8` |

Die analytische Leitlinie wird als fachliche Orientierung uebernommen. Sie
ersetzt keinen Befund und erteilt keine Code- oder Ausfuehrungsfreigabe.

## Funktionsprognose

Eine spaetere reine Zwei-Bereich-Projektion muss bei demselben validierten
Drei-Rollen-Bundle deterministisch genau zwei logische Bereichsbefunde
erzeugen und dabei jede fuer S2-FZ und S2-GC relevante Information erhalten:

1. `A_RECENT` enthaelt B4-Inhalt und B4-Kurzfolge als getrennte Teilbefunde.
2. Eine vorhandene TSPM-Fast-Spur bleibt in A als interner technischer
   Teilbefund mit Quelle, Support, Zeit- und Ablaufbindung erhalten.
3. Fast erscheint nicht als dritter oeffentlicher Memory-Bereich.
4. `B_STABLE` enthaelt nur stabilisierte auditive und visuelle
   TSPM-Slow-Prototypen.
5. Auditive und visuelle B-Komponenten bleiben getrennt, solange keine
   gespeicherte audiovisuelle Relationsidentitaet vorliegt.
6. Bereich B enthaelt keine Reihenfolge, Bildungsfolge oder B4-Indizes.
7. Instabile Slow-Spuren bleiben als interner Stabilitaets- und
   Falsifikationsbeleg sichtbar, werden aber nicht als `B_STABLE`-Kandidat
   ausgegeben.
8. Gueltige Abwesenheit bleibt von beschaedigter Evidenz getrennt.
9. Es entsteht weder eine Rangfolge zwischen A und B noch eine automatische
   Kontextauswahl.

Die Gegenprognose gegen eine blosse Umbenennung lautet: Wenn B4, Fast und
Slow nur unter zwei neuen Schluesseln abgelegt werden, ohne interne Rollen,
Quellen, Supports, Abwesenheiten und Zeitbindungen zu erhalten, ist die
Abbildung nicht verlustfrei und damit unzulaessig.

## Verlustfreie Abbildung

| Bestehende Rolle | Zielbereich | Erhaltene Funktion | Verbotene Umdeutung |
| --- | --- | --- | --- |
| `B4_RECENT` Inhalt | `A_RECENT.recent_content` | aktuell belegter B4-Inhalt, Distanz, Slot- und Bildungsindex | kein stabiler Prototyp |
| B4-Kurzfolge | `A_RECENT.short_sequence` | aufsteigende tatsaechliche Bildungsreihenfolge | keine TSPM-Folge und keine Episode |
| `TSPM_FAST` | `A_RECENT.fast_internal` | kurzlebige Inhaltsspur, Support, letzter Auswahlschritt, Ablauf- und Quellbeleg | kein dritter oeffentlicher Bereich und keine B4-Reihenfolge |
| stabiler auditiver `TSPM_SLOW`-Befund | `B_STABLE.auditory` | Prototyp, Support, Stabilitaet, Distanz, Bank- und Slotbeleg | keine audiovisuelle Gesamtidentitaet |
| stabiler visueller `TSPM_SLOW`-Befund | `B_STABLE.visual` | Prototyp, Support, Stabilitaet, Distanz, Bank- und Slotbeleg | keine Reihenfolge |
| instabiler Slow-Befund | `B_STABLE.stabilization_evidence` intern | Support und begruendete Nichtaufnahme in B | kein stabiler B-Kandidat |

`A_RECENT.fast_internal` darf fuer technische Validierung, Ressourcenbilanz
und den spaeteren A-nach-B-Nachweis erhalten bleiben. Ein oeffentlicher
Verbraucher erhaelt trotzdem nur die zwei Bereichsrollen `A_RECENT` und
`B_STABLE`. Das Ausblenden von Fast aus der oeffentlichen Rollenmenge darf
nicht mit seiner physischen Entfernung oder funktionalen Gleichheit zu B4
verwechselt werden.

Gleiche Inhalte in B4 und Fast bleiben zwei quellverschiedene interne
Teilbefunde in A. Sie werden nicht gemittelt, dedupliziert oder zu einem neuen
Speicherzustand verschmolzen.

## Vollstaendige S2-FZ-Reproduktion

Eine spaetere A/B-Projektion muss den bestaetigten S2-FZ-Befund ohne neue
Speicher- oder Probeoperation vollstaendig reproduzieren:

| S2-FZ-Befund | A/B-Projektion |
| --- | --- |
| B4 rekonstruiert nach Schritt 4 `P1, P2, P3, P4` | `A_RECENT.short_sequence` liefert dieselben vier B4-Referenzen in derselben Bildungsreihenfolge |
| P1 fehlt final aus B4 | kein P1 in `A_RECENT.recent_content` |
| P1 fehlt final aus TSPM-Fast | kein P1 in `A_RECENT.fast_internal` |
| P1 besitzt auditiv und visuell Slow-Support `3` | P1 erscheint getrennt in `B_STABLE.auditory` und `B_STABLE.visual`, jeweils stabil und quellgebunden |
| P2 fehlt final aus B4 und Fast | kein P2-Kandidat in A |
| P2 besitzt Slow-Support `1` und ist instabil | kein P2-Kandidat in B; Support `1` bleibt als interner Stabilitaetsbeleg erhalten |
| alle Probezugriffe sind read-only | identische Vor- und Nachzustandsdigests auch fuer die A/B-Projektion |
| keine automatische Auswahl | kein `BEST_MEMORY`, kein Gesamtmatch und keine Prioritaet zwischen A und B |

Fehlt auch nur einer dieser Befunde oder muss er aus Fixture-Labels,
Solltabellen oder Recorderhistorie rekonstruiert werden, ist die Migration
nicht materialisierbar.

## Gegenbaseline

Die staerkste Gegenbaseline ist das unveraenderte qualifizierte
`PerceptualContextBundle` mit drei Rollen. Es bleibt technische Referenz und
darf nicht durch die Zielarchitektur ersetzt oder umgedeutet werden.

Eine Zwei-Bereich-Projektion ist nur dann zulaessig, wenn sie:

- dieselben Kandidatenwerte, Quellen, Distanzen, Supports und Zeitbindungen
  reproduziert;
- dieselben gueltigen Abwesenheiten und Fail-Closed-Entscheidungen erzeugt;
- keine hoehere Kandidaten-, Werte- oder Operationsgrenze benoetigt;
- keine zusaetzliche Speicherfunktion einfuehrt;
- jeden A/B-Befund auf genau einen bestehenden Drei-Rollen-Befund
  zurueckfuehren kann.

Die Zwei-Bereich-Sicht besitzt gegen diese Baseline keinen behaupteten
Memory-Funktionsvorteil. Ihr zulaessiger Engineeringnutzen ist eine klarere
Verbrauchergrenze mit zwei logischen Bereichen.

## Echte quellgebundene A-nach-B-Bindung

Der bestehende TSPM-Kern besitzt bereits eine engere technische Kette:

```text
passende aktuelle Originalexposition
-> FAST_UPDATED und konsolidierungsberechtigt
-> atomare auditive und visuelle PPB-1-Aktualisierung
-> gemeinsamer TSPM-Receipt und Composite-Nachzustand
```

Der vorhandene `TSPM1TransitionReceipt` bindet unter anderem:

- Konfiguration, Owner-Vorzustand und aktuelle `exposure_digest`;
- Fast-Kandidat, Ereignis, ausgewaehlten Slot und
  Konsolidierungsentscheidung;
- auditive und visuelle PPB-1-Readouts und Stabilitaetsbefunde;
- Fast-, beide PPB- und Composite-Nachzustandsdigests.

Das ist eine technisch plausible Grundlage fuer eine
`A_FAST_GATED_SOURCE_BOUND_B_UPDATE`. Es ist jedoch keine Uebertragung eines
B4-Zustands und keine Kopie der Fast-Werte nach B. Die B-Aktualisierung nutzt
die aktuelle, quellgebundene Originalexposition. Deshalb sind folgende
Formulierungen gesperrt:

- "B4 wandert nach B";
- "der gesamte A-Zustand wird konsolidiert";
- "Fast wird nach B kopiert";
- "A und B bilden bereits eine bestaetigte physische Speicheranatomie".

Fuer einen spaeteren ausdruecklichen A-nach-B-Uebergangsbeleg sind mindestens
folgende Bindungen erforderlich:

1. ein gemeinsamer, vor dem Schritt validierter Wahrnehmungsquelldigest fuer
   B4- und TSPM-Arm;
2. A-Vorzustandsdigest mit getrenntem B4- und Fast-Anteil;
3. Fast-Kandidat, Supportuebergang und eindeutige
   Konsolidierungsberechtigung;
4. dieselbe aktuelle Originalexposition fuer beide PPB-1-Modalitaeten;
5. getrennte auditive und visuelle PPB-Vor-/Nachzustands- und Readoutbelege;
6. ein atomarer Composite-Receipt ohne sichtbaren Teilcommit;
7. A- und B-Nachzustandsdigests sowie vollstaendiges Ressourcenledger;
8. Ausschluss von Replay, Labels, Sollwerten und externen
   Wiederholungsbefehlen;
9. ein eigener Status `A_FAST_GATED_SOURCE_BOUND_B_UPDATE`, der keine
   physische Zustandsuebertragung behauptet.

Diese Bindungen koennen voraussichtlich aus vorhandenen privaten Receipts und
Zustaenden projiziert werden. Das ist noch nicht implementiert oder durch
einen eigenen A/B-Beleg qualifiziert. Reicht der vorhandene Receiptbestand
nicht aus, darf kein neuer Wirkungsclaim durch Interpretation ergaenzt
werden.

## Memory-Atomaritaet und Feldgrenze

Die spaetere A/B-Atomaritaet gilt nur innerhalb des privaten Memory-Schritts:

- A- und B-Kandidaten bleiben lokal, bis beide relational validiert sind;
- bei Memoryfehler wird kein A- oder B-Teilzustand veroeffentlicht;
- ein bereits entstandener MCM-Feldzustand wird weder geloescht, widerrufen
  noch rueckwirkend geaendert;
- der Feldzustand ist kein Rollback-Teilnehmer des Memory-Koordinators;
- die A/B-Projektion liest keine Feldwerte und erzeugt keinen MCM-Drive;
- normaler Ablauf oder Kapazitaetsdruck ist ein Memoryereignis und kein
  Feldfehler.

Eine spaetere Kontext- oder Feldwirkung benoetigt einen eigenen Vertrag und
darf nicht in die Migrationsimplementierung aufgenommen werden.

## Vorgesehene statische Datenrollen

Eine spaetere private Schattenprojektion darf hoechstens folgende neue
unveraenderliche Rollen materialisieren:

1. `TwoAreaProjectionBinding`: Drei-Rollen-Bundle-, Quell-, Probe-, Zustands-
   und Vertragsbindung;
2. `AreaARecentFinding`: B4-Inhalt, B4-Kurzfolge und getrennte interne
   Fast-Evidenz;
3. `AreaBStableFinding`: getrennte stabile auditive und visuelle Prototypen
   sowie interne Instabilitaetsbelege;
4. `TwoAreaTransitionEvidence`: optionaler, rein belegender
   Fast-ausgeloester und quellgebundener B-Aktualisierungsbefund;
5. `TwoAreaContextBundle`: genau die zwei oeffentlichen Rollen `A_RECENT` und
   `B_STABLE`, keine Gesamtauswahl;
6. `TwoAreaResourceLedger`: vollstaendige Validierungs-, Projektions-,
   Digest- und Ausgabekosten.

`TwoAreaTransitionEvidence` darf nicht aus einem read-only Abruf erfunden
werden. Ohne einen passenden Formationsreceipt lautet sein Status
`TRANSITION_NOT_OBSERVED`, nicht `A_TO_B_CONFIRMED`.

## Migration in begrenzten Stufen

1. Drei-Rollen-Code, Tests, Befunde und Bundle bleiben unveraendert.
2. Eine spaetere private read-only Schattenprojektion bildet genau ein
   validiertes Drei-Rollen-Bundle auf A und B ab.
3. Neutrale Tests pruefen Verlustfreiheit, Abwesenheit, Trennung, Digests,
   Grenzen und das Fehlen einer Auswahl.
4. Der S2-FZ-Beleg wird anschliessend rein aus vorhandenen gespeicherten
   Belegen in beiden Darstellungen verglichen; keine neue Hauptausfuehrung.
5. Erst bei Gleichheit darf der spaetere Kontextvergleich die zwei
   Verbraucherrollen verwenden.
6. Eine physische Zusammenlegung oder Entfernung von Fast bleibt eine eigene
   spaetere Architekturentscheidung und ist durch S2-GD nicht freigegeben.

## Falsifikations- und Stoppregeln

Die Zwei-Bereich-Implementierung ist zu stoppen, wenn:

1. B4-Inhalt, B4-Reihenfolge oder Fast-Lebenszyklus nicht getrennt in A
   erhalten bleiben;
2. eine instabile Slow-Spur verloren geht oder als stabiler B-Kandidat
   erscheint;
3. auditive und visuelle Slow-Prototypen ohne Relationsbeleg verschmolzen
   werden;
4. Bereich B eine Reihenfolge oder B4 einen Slow-Support erhaelt;
5. Fast nur durch physische Entfernung, verdeckte Fusion oder unbelegte
   Gleichsetzung mit B4 aus der dritten oeffentlichen Rolle entfernt werden
   kann;
6. ein A-nach-B-Uebergang ohne aktuelle Originalquelle, Fast-Berechtigung,
   beide PPB-Belege und atomaren Receipt behauptet wird;
7. die S2-FZ-Befunde nicht vollstaendig reproduzierbar sind;
8. die A/B-Projektion mehr als zwei oeffentliche Memory-Bereiche,
   automatische Auswahl oder Ranking erzeugt;
9. Memoryfehler einen Feldzustand veraendern oder widerrufen;
10. gleiche Eingaben verschiedene A/B-Payloads oder Digests erzeugen;
11. die Ressourcenbilanz unvollstaendig ist;
12. die Migration Labels, Semantik, Rohdaten oder Recorderhistorie benoetigt.

Wenn nur eine unbelegte Umdeutung des bestehenden Mechanismus als A-nach-B
moeglich ist, bleibt die Drei-Rollen-Referenz aktiv und es erfolgt keine
Zwei-Bereich-Implementierung.

## Entscheidung

Der statische Abgleich ergibt:

- Die Zwei-Bereich-Projektion ist verlustfrei darstellbar, wenn B4 und Fast
  als getrennte interne A-Teilrollen erhalten bleiben.
- `TSPM_SLOW` ist ohne Reihenfolge auf `B_STABLE` abbildbar; instabile
  Supports muessen als interne Falsifikationsevidenz erhalten bleiben.
- S2-FZ ist im A/B-Modell vollstaendig reproduzierbar, ohne neue
  Speicherfunktion.
- Der vorhandene TSPM-Receipt traegt eine Fast-ausgeloeste,
  originalquellgebundene B-Aktualisierung. Er belegt keine physische
  Uebertragung des gesamten A- oder B4-Zustands.
- Eine spaetere Implementierung darf deshalb nur als private read-only
  Schattenprojektion beginnen. Physische Migration, Kontextverwendung und
  Feldwirkung bleiben gesperrt.

S2-GD-Abschluss:

`PASS_S2GD_STATIC_TWO_AREA_MAPPING_MIGRATION_AND_FALSIFICATION_CONTRACT_BOUND`

Der spaetere Funktionsvergleich darf nach qualifizierter A/B-Projektion nur
noch lauten:

```text
CURRENT_PERCEPTION_ONLY
gegen
CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT
```

S2-GD selbst erlaubt weder diese Funktionspruefung noch Code, Tests,
Zustandsaufrufe oder Feldintegration.
