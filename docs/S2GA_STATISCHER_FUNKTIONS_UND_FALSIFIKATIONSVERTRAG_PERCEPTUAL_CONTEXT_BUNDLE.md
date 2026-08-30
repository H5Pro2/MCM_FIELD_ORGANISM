# S2-GA: Privates PerceptualContextBundle

## Auftrag und Status

S2-GA bindet ausschliesslich den statischen Funktions- und
Falsifikationsvertrag eines privaten, read-only inneren Kontextverbrauchers.
Der Verbraucher legt die bereits getrennt vorliegenden Speicherbefunde
transparent in einem `PerceptualContextBundle` vor. Er trifft keine Auswahl,
veraendert keinen Zustand und fuehrt keine Lern- oder Feldoperation aus.

S2-GA fuehrt keine neue Speichermechanik ein. Grundlage ist der in S2-FZ fuer
eine begrenzte synthetische Geschichte bestaetigte technische
Memory-Grundbaustein:

- `B4_RECENT` fuer juengste Inhalte und Kurzfolge;
- `TSPM_FAST` fuer voruebergehende Inhaltsspuren;
- `TSPM_SLOW` fuer durch Wiederholung stabilisierte Inhalte.

Noch nicht freigegeben sind Implementierung, Tests, Fixtures, Runner,
Zustands- oder Probefunktionen, Feldrueckwirkung, API, Snapshot,
Produktionsintegration oder eine Funktion zur automatischen Kontextwahl.

## Gebundene technische Grundlage

Der Vertrag ist an den versionierten Stand
`3bed9f82b22c2d2ab6f53b656783bcddcfa91dd9` gebunden:

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Atomarer B4-/TSPM-Koordinator und getrennter read-only Befund | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| Bestehende Inhaltsauswertung | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| Bestehende B4-Folgenauswertung | `tools/_visual_sequence_memory_probe.py` | `d5fef4aa9fbbc06502f630e729161274b13c972f9ae2a1f13fb2084bb00593ec` |
| B4-Zustand und FIFO-Regeln | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| TSPM-1 Fast/Slow | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1 Slow-Zustaende | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| Bestaetigter S2-FZ-Funktionsbefund | `reports/tspm1_functional/s2fz-confirmation-20260830-01-evaluation-canonical/functional-evaluation.json` | `2926685d3cc1c3a93aef07e68179c47918e2719603db6561952fe8004bc9cc5a` |

Diese Bindung uebernimmt nur vorhandene technische Rollen. Der S2-FZ-Befund
beweist noch keinen Nutzen eines Kontextbundles bei einer Folgewahrnehmung.

## Funktionsprognose

Bei identischem validiertem Composite-Zustand und identischer gebundener
Probe muss der spaetere Verbraucher deterministisch genau ein
`PerceptualContextBundle` erzeugen, das:

1. hoechstens je einen Kandidaten aus `B4_RECENT`, `TSPM_FAST` und
   `TSPM_SLOW` enthaelt;
2. jede Rolle, Herkunft, zeitliche Bindung, Distanz und vorhandenen Support
   getrennt ausweist;
3. einen gueltigen Nichttreffer als `ABSENT_VALID` darstellt;
4. beschaedigte oder widerspruechliche Evidenz vollstaendig fail-closed
   ablehnt und nicht als Abwesenheit tarnt;
5. B4-Folgeninformation nur in einem gesonderten Kurzzeitbefund bereitstellt;
6. keine Rangfolge, Verschmelzung, Gesamtwertung oder Auswahl erzeugt;
7. vor und nach der Projektion denselben Composite-Zustandsdigest belegt;
8. bei gleichen Eingaben ein bytegleiches kanonisches Ergebnis und denselben
   Bundledigest erzeugt.

Dies ist die eigene Gegenprognose von S2-GA gegen einen ungeprueften
Dictionary- oder Listenexport: Nicht nur Inhalte, sondern Rollen,
Abwesenheiten, Provenienz, Unveraendertheit und Ressourcen muessen
vollstaendig und widerspruchsfrei gebunden sein.

## Vorgesehene private Datenrollen

Eine spaetere Implementierung darf ausschliesslich folgende neue private,
unveraenderliche Datenrollen materialisieren:

### `PerceptualContextComponent`

Ein einzelner Modalitaets- oder gemeinsamer AV-Bestandteil mit:

- `component_role`: `AV_JOINT`, `AUDITORY` oder `VISUAL`;
- reduzierte Werte mit exakt gebundener Dimension;
- Quell-, Slot- beziehungsweise Bank- und Wertedigest;
- native und funktionale Distanz, soweit der bestehende Befund sie liefert;
- Support, Stabilitaet und letzter Auswahlschritt, soweit fuer die Rolle
  vorhanden;
- B4-`formation_index` nur fuer einen B4-Bestandteil;
- keine Labels, Sollwerte oder semantischen Kennungen.

Nicht vorhandene rollenspezifische Felder bleiben `None`. Sie duerfen nicht
durch Schaetzungen oder Standardwerte ersetzt werden.

### `PerceptualContextCandidate`

Ein Kandidat besitzt genau eine der Rollen:

```text
B4_RECENT | TSPM_FAST | TSPM_SLOW
```

Er enthaelt eine feste, rollenabhaengige Komponentenform:

- `B4_RECENT`: genau eine gemeinsam gespeicherte 26-Werte-AV-Komponente und
  ihren tatsaechlichen `formation_index`;
- `TSPM_FAST`: genau eine gemeinsam gespeicherte 26-Werte-AV-Komponente mit
  Fast-Support, letztem Auswahlschritt und Slotdigest;
- `TSPM_SLOW`: eine auditive Acht-Werte- und eine visuelle
  18-Werte-Komponente, jeweils mit eigenem Bank-, Slot-, Distanz-, Support-
  und Stabilitaetsbefund.

Die beiden `TSPM_SLOW`-Komponenten duerfen nicht zu einem neuen 26-Werte-
Gesamtprototyp verschmolzen werden. Der bestehende Slow-Zustand besitzt keine
eigenstaendige gespeicherte audiovisuelle Relations-ID. Das Bundle darf
deshalb nur `CROSS_MODAL_RELATION_NOT_REPRESENTED` ausgeben und keine
gemeinsame gespeicherte Episode behaupten.

### `PerceptualContextRoleFinding`

Fuer jede der drei Rollen existiert genau ein Rollenbefund mit einem der
Zustaende:

```text
AVAILABLE_COMPLETE
AVAILABLE_PARTIAL
ABSENT_VALID
```

- `AVAILABLE_COMPLETE` bedeutet, dass alle fuer diese Rolle notwendigen
  Komponenten nach den bestehenden unveraenderten Regeln vorliegen.
- `AVAILABLE_PARTIAL` ist nur fuer `TSPM_SLOW` zulaessig, wenn genau eine
  Modalitaet einen gueltigen stabilen Treffer liefert. Der fehlende Teil darf
  nicht ergaenzt werden.
- `ABSENT_VALID` bedeutet einen vollstaendig validierten read-only Befund
  ohne zulaessigen Kontextkandidaten.

Zulaessige Abwesenheitsgruende sind ausschliesslich aus dem Befund ableitbare
Codes wie `NO_FUNCTIONAL_MATCH`, `NO_STABLE_SLOW_MATCH` oder
`NO_OCCUPIED_SOURCE`. Ablauf, Verdraengung oder eine andere Ursache darf nur
genannt werden, wenn sie selbst durch den uebergebenen Beleg nachgewiesen ist.

### `B4ShortSequenceFinding`

Der gesonderte Kurzzeitbefund enthaelt hoechstens neun aktuell belegte
B4-Referenzen in aufsteigender tatsaechlicher Bildungsreihenfolge:

- `formation_index`;
- Slotdigest;
- Wertedigest;
- optional den bereits gebundenen read-only Folgenbefund.

Er kopiert keine zweite Historie und enthaelt keine TSPM-Position. Eine
fehlende oder nicht angeforderte Folgenprobe ist ein eigener gueltiger Status
und darf nicht aus Recorder- oder Versuchsmetadaten rekonstruiert werden.

### `PerceptualContextBundle`

Das erste Ausgabeobjekt besitzt mindestens:

- privaten Schema- und Vertragsdigest;
- Composite-Konfigurations-, Composite-Zustands- und Probendigest;
- gemeinsame Quell-, Geometrie-, Clock- und Zeitfensterbindung;
- genau drei `PerceptualContextRoleFinding` in kanonischer Rollenreihenfolge;
- null bis maximal drei darin enthaltene Kontextkandidaten;
- genau einen getrennten `B4ShortSequenceFinding`;
- vollstaendiges Ressourcenledger;
- identische Vor- und Nachzustandsdigests;
- eigenen kanonischen Bundledigest;
- `automatic_selection = None`.

Die kanonische Reihenfolge `B4_RECENT`, `TSPM_FAST`, `TSPM_SLOW` dient nur
der reproduzierbaren Serialisierung. Sie ist keine Prioritaet oder Rangfolge.

## Quellen- und Zustandsbindung

Vor jeder spaeteren Bundlebildung muss gelten:

1. exakte private Typen und unveraenderte Vertragsdigests;
2. ein validierter `B4TSPM1CompositeState`;
3. genau eine kausal spaetere gebundene read-only Probe;
4. genau ein gueltiger `B4TSPM1ReadOnlyFinding` aus diesem Zustand und dieser
   Probe;
5. Rollenmenge exakt `B4_RECENT`, `TSPM_FAST`, `TSPM_SLOW`;
6. identische Composite-, Probe-, Konfigurations- und Quelldigests;
7. identische Vor- und Nachzustandsdigests des Composite und aller
   Teilbefunde;
8. auditive und visuelle Slow-Bank genau einmal und mit korrekter Modalitaet;
9. vollstaendiges read-only Ressourcenledger.

Der Verbraucher darf den bestehenden Composite-Probeweg spaeter hoechstens
einmal aufrufen. Alternativ darf er einen bereits erzeugten, vollstaendig
validierten Findingbeleg verarbeiten. Beides gleichzeitig ist unzulaessig.
Ein zweiter Probeaufruf, ein erneuter Speicherabruf oder eine
Zustandsfortschreibung waehrend der Bundlebildung ist verboten.

## Abwesenheit und Fail-Closed-Grenze

Gueltige Abwesenheit ist ein funktionaler Befund. Sie setzt voraus, dass
Quelle, Zustand, Probe, Rollen, Distanzen, Digests und read-only Grenze
vollstaendig gueltig sind.

Beschaedigte Evidenz erzeugt dagegen kein `PerceptualContextBundle` und auch
keine leere Kandidatenliste. Fail-closed abzulehnen sind insbesondere:

- fremder, veralteter oder unbekannter Composite-Zustand;
- Probe- oder Quelldigest passt nicht zum Finding;
- Vor- und Nachzustandsdigest unterscheiden sich;
- fehlende, doppelte oder vertauschte Rollen beziehungsweise Modalitaeten;
- ungueltige Dimension, nicht endliche Werte oder nicht kanonische Typen;
- Distanz, Support, Stabilitaet und Slotbefund widersprechen einander;
- B4-Index liegt ausserhalb der aktuellen FIFO-Anatomie;
- unvollstaendiges Ledger oder nicht reproduzierbarer Bundledigest;
- irgendein Auswahl-, Score-, Fusions- oder Lernfeld.

Ein Fehler darf weder einen Teilbundle noch bereits materialisierte
Kandidaten veroeffentlichen. Der Aufrufer erhaelt nur einen privaten
terminalen Fehlerbeleg mit Fehlercode und Quelldigest, keinen ersatzweise
leeren Kontext.

## Determinismus und Ressourcen

Der Bundleumfang ist endlich gebunden:

- genau drei Rollenbefunde;
- maximal drei Kandidaten;
- maximal 78 reduzierte Kandidatenwerte: je 26 fuer B4, Fast und die zwei
  getrennten Slow-Komponenten zusammen;
- maximal vier Komponentenobjekte: B4-AV, Fast-AV, Slow-Audio, Slow-Visual;
- maximal neun B4-Folgenreferenzen ohne zweite Wertekopie;
- keine Rohdaten und keine unbeschraenkte Historie.

Das spaetere Ledger muss getrennt zaehlen:

```text
Gesamtkosten
= Eingangs- und Vertragsvalidierung
+ genau ein bestehender read-only Verbundbefund oder dessen Belegvalidierung
+ drei Rollenprojektionen
+ Komponenten-, Abwesenheits- und Folgenvalidierung
+ Ausgabe-, Digest- und Ledgerbildung
```

Bereits im gueltigen Finding vorhandene Distanzen werden uebernommen und
nicht neu optimiert. Eine spaetere Implementierung muss jede tatsaechliche
Distanzneuberechnung separat zaehlen und begruenden. Kandidatenzahl,
Wertezahl, Folgenreferenzen, validierte Digests und ausgegebene Woerter
muessen im Ledger explizit vorkommen.

Bei identischen kanonischen Eingaben muessen Payload, Fehlerstatus,
Ressourcenledger und Bundledigest identisch sein. Zeit, Zufall,
Dictionary-Reihenfolge oder Prozessidentitaet duerfen das Ergebnis nicht
veraendern.

## Ausdruecklich ausgeschlossene Funktionen

S2-GA erlaubt nicht:

- `BEST_MEMORY`, `SELECTED_CONTEXT`, Rang, Score oder Prioritaet;
- Verschmelzung der drei Rollen oder Mittelung ihrer Werte;
- automatische Entscheidung, welcher Kandidat verwendet wird;
- Erzeugung neuer Prototypen, Supports, Bildungsindizes oder Zeitwerte;
- Zustandsfortschreibung, Konsolidierung, Vergessen oder Lernen;
- Labels, Woerter, Objektklassen, Belohnung oder Sollausgaben;
- Rohbild-, Rohvideo-, Roh-Audio- oder Replayablage;
- Feldrueckwirkung, MCM-Drive, API-, Snapshot- oder Produktionsintegration.

Das Bundle ist ein transparenter technischer Bereitstellungsbefund. Es ist
noch kein Nachweis, dass ein Folgeschritt den bereitgestellten Kontext
funktional verwendet.

## Spaetere Funktionspruefung gegen CURRENT_PERCEPTION_ONLY

Eine spaetere, separat zu bindende Kontextverwendungspruefung muss mindestens
zwei budgetgleiche Arme besitzen:

1. `CURRENT_PERCEPTION_ONLY`: nur dieselbe aktuelle reduzierte
   Folgewahrnehmung;
2. `CURRENT_PERCEPTION_PLUS_CONTEXT_BUNDLE`: dieselbe Folgewahrnehmung plus
   das unveraenderte Bundle.

Zusaetzlich ist eine kontextfremde oder zeitlich unpassende Bundlekontrolle
erforderlich. Sie muss dieselben Datenformen und Ressourcenobergrenzen
besitzen und darf nicht ueber eine Lauf- oder Sollkennung erkennbar sein.

Vorab zu binden sind eine einzelne technische Aufgabe, richtige und falsche
Ausgaben, Fehlzuordnungen, Abwesenheitsfaelle, Interferenzfaelle und ein
identisches Operationsbudget. Die Aufgabe darf weder Labels noch den
Versuchsplan als Eingabe verwenden. Erfolg liegt nur vor, wenn der gebundene
Kontextarm bei gleicher Folgewahrnehmung einen vorab gerichteten messbaren
Vorteil gegen `CURRENT_PERCEPTION_ONLY` zeigt und die fremde Kontextkontrolle
diesen Vorteil nicht reproduziert.

Gleichheit beider Arme bedeutet:

`CONTEXT_BUNDLE_AVAILABLE_BUT_FUNCTIONAL_USE_NOT_SHOWN`

Eine Verschlechterung oder kontextfremde Verbesserung falsifiziert die
jeweilige Kontextverwendungsregel. Sie falsifiziert nicht rueckwirkend die in
S2-FZ bestaetigte Speicherfunktion.

## Falsifikations- und Stoppregeln

S2-GA ist als Bundlevertrag zu stoppen oder zu korrigieren, wenn:

1. mehr als drei Kandidaten oder eine vierte Speicherrolle erforderlich
   werden;
2. ein Kandidat ohne vollstaendige Herkunfts- und Zustandsbindung erscheint;
3. gueltige Abwesenheit und beschaedigte Evidenz denselben Status erhalten;
4. auditive und visuelle Slow-Komponenten ohne Relationsbeleg verschmolzen
   werden;
5. TSPM-1 eine Folgenordnung oder B4 einen Slow-Support erhaelt;
6. eine Rangfolge, Gesamtwertung oder automatische Auswahl entsteht;
7. Bundlebildung einen Speicherzustand oder Teilzustand veraendert;
8. gleiche Eingaben verschiedene Payloads oder Digests erzeugen;
9. Ressourcen unvollstaendig gezaehlt oder Obergrenzen ueberschritten werden;
10. Labels, Sollwerte, Recorderhistorie oder Rohdaten in den Verbraucher
    gelangen.

Eine spaetere Kontextverwendung ist separat zu stoppen, wenn kein Vorteil
gegen `CURRENT_PERCEPTION_ONLY` verbleibt oder eine einfachere, gleich
budgetierte Bereitstellung denselben Nutzen liefert. In diesem Fall kann das
Bundle als Diagnoseausgabe bestehen bleiben, aber ein funktionaler Uebergang
zu innerem Kontext ist nicht belegt.

## Claim-Grenze und Entscheidung

Ein spaeter bestandener Implementierungsvertrag darf hoechstens den Status

`PRIVATE_READ_ONLY_PERCEPTUAL_CONTEXT_BUNDLE_VALID`

tragen. Erst eine getrennte faire Folgewahrnehmungspruefung darf gegebenenfalls

`PERCEPTUAL_CONTEXT_USE_FUNCTION_CONFIRMED`

melden. Keiner dieser Status belegt allgemeine Langzeit-Memory, Semantik,
automatische Erinnerungsauswahl oder Feldwirkung.

S2-GA-Abschluss:

`PASS_S2GA_STATIC_PERCEPTUAL_CONTEXT_BUNDLE_FUNCTION_AND_FALSIFICATION_CONTRACT_BOUND`

Der naechste konkrete Schritt waere nach separater Freigabe eine kleine
private Implementierung ausschliesslich der unveraenderlichen Datenrollen und
der reinen, fail-closed Bundleprojektion mit neutralen synthetischen Tests.
Eine Feldintegration oder Kontextverwendungsfunktion gehoert nicht zu diesem
naechsten Implementierungsschritt.
