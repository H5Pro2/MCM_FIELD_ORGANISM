# S2-FR: Atomarer privater B4-/TSPM-1-Verbund

## Auftrag und Status

S2-FR bindet ausschliesslich die Architektur und Falsifikation eines privaten
Koordinators fuer die bereits vorhandenen Speicherbausteine B4 und TSPM-1.
Der Vertrag fuehrt keine neue Speichermechanik ein und verschmilzt keine
Zustaende. Er ordnet zwei technisch gepruefte Funktionen unter einer
gemeinsamen atomaren Fortschreibung:

- B4 traegt die juengsten perzeptiven Zustaende und ihre tatsaechlichen
  Bildungsindizes;
- TSPM-1 Fast traegt kurzlebige audiovisuelle Inhaltsspuren;
- TSPM-1 Slow traegt durch Wiederholung stabilisierte auditive und visuelle
  PPB-1-Prototypen.

Es wurden fuer S2-FR keine Projektmodule importiert, keine Zustands- oder
Probefunktion aufgerufen, keine Tests ausgefuehrt und kein Code geaendert.
Oeffentliche API, Snapshot, Feldpfad, Produktion und Ausfuehrung bleiben
gesperrt.

## Technische Grundlage

Der Vertrag ist an den versionierten Stand
`12f7fab784c9e03e88d3d2f51185f996aff8652f` gebunden:

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| B4-FIFO-Zustand und Operator | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| TSPM-1 Fast/Slow und atomare Konsolidierung | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| Getrennte read-only Auswertung | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| Gebundene Schwellen und Geschichten | `tools/_retention_capacity_fixtures.py` | `a81a6878c2b807d9217c756ee7f6b76026352738b6b96e211e666ebc0edd4adb` |
| Gepruefter gemeinsamer Rezeptorpfad | `tools/_retention_capacity_runner.py` | `28b1d662d04d8d2a76352e35168a5e49b8aa10f5c24e8afff2e342f00d06d42f` |

Der [Erhaltungsbefund](../reports/tspm1_functional/retention-capacity-main-20260829-01-evaluation/BEFUND.md)
belegt die Rollen getrennt. Er ist keine Abnahme des hier erst beschriebenen
Verbundkoordinators.

## Architekturentscheid

B4 und TSPM-1 bleiben zwei getrennte Zustaende. Der Verbund besitzt weder
einen dritten Speicherbestand noch einen gemeinsamen Prototypraum:

```text
ein validierter perzeptiver Eingang
        |                         |
        v                         v
   B4-FIFO-Schritt          TSPM-1-Schritt
        |                         |
        +---- atomare Abnahme ----+
                     |
          privater Verbundzustand
```

Die Verbindung besteht ausschliesslich aus gemeinsamer Quellenbindung,
atomarer Abnahme und einem gemeinsamen Ressourcenbeleg. Inhalte duerfen nicht
zwischen B4 und TSPM-1 kopiert, uminterpretiert oder als Steuerbefehle
verwendet werden.

## Vorgesehene private Rollen

Eine spaetere Implementierung darf nur folgende neue Verbundrollen anlegen:

1. `B4TSPM1CoordinatorConfig`: Digests der unveraenderten B4- und TSPM-1-
   Konfigurationen, Dimensionsbindung und vollstaendiger Ressourcenplan.
2. `B4TSPM1CompositeState`: genau ein B4-Zustand, genau ein TSPM-1-
   Composite-Zustand, Verbundgeneration, Vorzustandsdigest und eigener
   Composite-Digest.
3. `B4TSPM1BoundInput`: genau eine validierte Rezeptorhuelle, deren auditive
   und visuelle Frames sowie daraus abgeleitete 26 AV-Werte beide Arme binden.
4. `B4TSPM1CoordinatorOwner`: private Einmaligkeitsrolle mit
   `AUTHORIZED`, `CONSUMED` oder `FAILED`.
5. `B4TSPM1StepReceipt`: Quellen-, Vorzustands-, Kandidaten-, Ressourcen-,
   Owner- und Nachzustandsdigests sowie beide unveraenderten Teilreceipts.
6. `B4TSPM1StepResult`: genau ein vollstaendiger Composite-Nachzustand und
   genau ein dazu passendes Receipt.
7. `B4TSPM1ReadOnlyFinding`: drei getrennte Befundrollen `B4_RECENT`,
   `TSPM_FAST` und `TSPM_SLOW`, ohne Gesamtauswahl und ohne Nachzustand.

Alle Rollen bleiben privat, unveraenderlich und kanonisch digestgebunden. Sie
werden nicht aus Paketroot, API oder Feldsnapshot exportiert.

## Gemeinsame Eingangsbindung

Beide Arme erhalten dieselbe bereits validierte auditive und visuelle
Rezeptorexposition. Verbindlich gilt:

- B4 erhaelt ausschliesslich die kanonische Konkatenation der acht auditiven
  und 18 visuellen Werte aus dieser einen Huelle;
- TSPM-1 erhaelt ausschliesslich die beiden unveraenderten Timed Frames aus
  derselben Huelle;
- B4-`formation_index` ist immer `b4_prestate.accepted_count + 1` und darf
  nicht von aussen geliefert werden;
- beide Projektionen muessen vor dem ersten Zustandsaufruf gegen Quell-,
  Werte-, Geometrie-, Zeit- und Huelldigests uebereinstimmen;
- ein zweiter Rezeptoraufruf, eine Ersatzkopie oder getrennt erzeugte
  Eingaben fuer die Arme ist unzulaessig.

Labels, Geschichtenrollen, Sollwerte, Wiederholungszaehler, erwartete
Ereignisse und Recorderinformationen duerfen nur ausserhalb des Operators
zur spaeteren Auswertung existieren. B4 darf keine TSPM-Konsolidierung
ausloesen. TSPM-1 darf keinen B4-Index oder FIFO-Ersatz bestimmen.

## Zustandsinvarianten

Jeder gueltige Verbundvor- und -nachzustand erfuellt:

```text
verbund.generation
= b4.accepted_count
= tspm.fast_state.accepted_exposure_count
```

Zusaetzlich gelten:

- B4 besitzt weiterhin exakt neun FIFO-Slots und das vollstaendige aktuelle
  `formation_index`-Fenster;
- TSPM-1 behaelt seine unveraenderte Fast-Kapazitaet, Ablauf-, Match-, LRU-
  und Konsolidierungsregeln;
- auditive und visuelle PPB-1-Bank bleiben getrennt und duerfen weniger
  akzeptierte Schritte als die Verbundgeneration besitzen;
- kein B4-Digest darf Bestandteil einer TSPM-Distanz oder eines PPB-
  Prototyps sein;
- kein TSPM-Support, Slot- oder Kontextbefund darf einen B4-Eintrag bilden;
- ein Verbunddigest dient nur Identitaet und Provenienz, nie Match oder
  funktionaler Auswahl.

## Atomare Fortschreibung

Die spaetere Fortschreibung muss in dieser festen Reihenfolge erfolgen:

1. exakte private Typen, Konfigurationen und Vertragsdigests pruefen;
2. Owner, Einmaligkeit und unverbrauchten Composite-Vorzustand pruefen;
3. gemeinsame Rezeptorhuelle, Frames, AV-Projektion, Zeit und Geometrie
   pruefen;
4. alle Zustandsinvarianten des Vorzustands pruefen;
5. den B4-Nachzustandskandidaten rein und noch unveroeffentlicht berechnen;
6. den TSPM-1-Nachzustandskandidaten mit einem privaten, nur diesem Schritt
   gehoerenden TSPM-Owner berechnen;
7. beide Kandidaten, Teilreceipts, Generationsgleichheit und Ressourcenbeleg
   vollstaendig pruefen;
8. genau einen Composite-Nachzustand und ein Verbundreceipt veroeffentlichen;
9. den Verbundowner terminal `CONSUMED` setzen.

Schlaegt ein Schritt fehl, entsteht kein `B4TSPM1StepResult`. Beide vom
Aufrufer gehaltenen Vorzustaende bleiben unveraendert und der Verbundowner
wird terminal `FAILED`. Ein lokaler, noch nicht veroeffentlichter Kandidat ist
kein Teilcommit. Retry, Fortsetzung und Wiederverwendung desselben Owners sind
untersagt.

Die Atomaritaet ist die eigene vertraglich zu pruefende technische Garantie
des Koordinators: Ein unabhaengig sequenzieller Controller kann nach einem
erfolgreichen ersten Arm und einem Fehler des zweiten Arms einen sichtbaren
Teilzustand hinterlassen; der gebundene Verbund darf dies nicht. Ein
einfacherer, ebenfalls vollstaendig transaktionaler Wrapper waere eine
gueltige Reduktionsbaseline und keine neue Speicherursache.

## Getrennter read-only Abruf

Eine spaetere Verbundprobe bindet genau eine kausal spaetere Rezeptorprobe an
den unveraenderten Composite-Zustand. Sie ruft die bestehenden read-only
B4- und TSPM-1-Pfade hoechstens einmal auf und liefert:

- `B4_RECENT`: B4-Inhaltstreffer mit `formation_index`; eine Folgenpruefung
  ist nur aus aktuell belegten B4-Slots zulaessig;
- `TSPM_FAST`: vollstaendiger gemeinsamer Fast-Treffer oder kein Treffer;
- `TSPM_SLOW`: auditive und visuelle Slow-Befunde mit Support, Stabilitaet
  und Quelle, weiterhin getrennt;
- gemeinsame Quell-, Vor- und Nachzustandsdigests sowie Kosten.

Es gibt kein Feld `BEST_MEMORY`, `SELECTED_MEMORY` oder eine automatische
Prioritaet zwischen den drei Sichten. Insbesondere darf die bestehende interne
TSPM-Kontextquellenentscheidung nicht als Verbundentscheidung ausgegeben
werden. Ein spaeterer innerer Kontext waere ein eigener Verbraucher dieser
Befunde und gehoert nicht zu S2-FR.

Folgenordnung stammt ausschliesslich aus B4. TSPM-1 erhaelt keine
Reihenfolgekoordinate, keine Uebergangsliste und keinen Zugriff auf
Versuchsplan oder Recorderhistorie.

## Gespeicherter Umfang

Zulaessig bleiben ausschliesslich:

- reduzierte auditive und visuelle Rezeptorwerte;
- feste Slotidentitaeten und B4-Bildungsindizes;
- Fast-Support, letzter Auswahlschritt und Konsolidierungszahl;
- PPB-1-Prototypwerte, Support und letzter Auswahlschritt;
- Quellen-, Zustands-, Receipt- und Konfigurationsdigests.

Ausgeschlossen sind Rohbilder, Rohvideo, Roh-Audio, Datei- oder Replayhistorie,
Woerter, Objekt-IDs, semantische Labels, Sollklassen und Feldsnapshotwerte.

## Ressourcenvertrag

Die Kombination ist kein kostenloser Funktionsgewinn. Jeder spaetere Schritt
muss ein gemeinsames zaehlbares Ledger besitzen:

```text
Gesamtkosten
= B4-Validierung und B4-Operator
+ TSPM-Validierung, Fast-Operator und eventuelle PPB-1-Schritte
+ Verbundvalidierung, Owner, Receipt und Composite-Bindung
```

Die gemeinsame Rezeptorprojektion darf genau einmal gezaehlt und von beiden
Armen read-only wiederverwendet werden. Alle armspezifischen Distanzen,
Schreibwoerter, Slotpruefungen, PPB-1-Aufrufe und Digestvalidierungen werden
dagegen vollstaendig addiert.

Aus dem bestehenden Funktionsversuch gelten pro Exposition weiterhin die
konservativen Armobergrenzen von je 293 Schreibwoertern und 234
Distanztermen. Eine spaetere Implementierungsfreigabe muss zusaetzlich den
exakten Koordinatoraufwand binden. `586` Schreibwoerter und `468`
Distanzterme sind daher nur die Summe der beiden bisherigen Armobergrenzen,
nicht das vollstaendige Verbundbudget.

Read-only Proben schreiben null Speicherwoerter. B4- und TSPM-Distanzen sowie
Verbundvalidierung werden getrennt gezaehlt. Eine B4-Folgenpruefung darf ihre
bestehenden 416 Terme verwenden; TSPM-1 erzeugt dabei keine Folgenkosten und
keinen Folgenbefund.

Fehlt ein vollstaendiges Ledger oder wird eine Teilfunktion nicht gezaehlt,
ist ein spaeterer Lauf methodisch ungueltig.

## Funktionale Gegenprognose

Ein spaeterer begrenzter Funktionsversuch muss dieselbe gebundene
Eingabegeschichte an beide Arme geben und drei Zeitpunkte trennen:

1. **Frueher Folgencheckpoint:** Vier unterscheidbare Zustaende liegen noch
   vollstaendig in B4. `B4_RECENT` muss Inhalt und Reihenfolge liefern.
2. **Nach B4- und Fast-Verlust:** Ein Zielzustand wurde insgesamt viermal,
   ein zweiter Zielzustand nur zweimal exponiert. Danach folgen mindestens
   so viele fremde akzeptierte Expositionen, dass beide Ziele aus B4
   verdraengt und ihre TSPM-Fast-Slots abgelaufen sind.
3. **Spaeter read-only Abruf:** Der viermal exponierte Zielzustand muss nur in
   `TSPM_SLOW` mit stabilem Support abrufbar sein. Der zweimal exponierte
   Zielzustand darf weder in `B4_RECENT`, `TSPM_FAST` noch als stabiler
   `TSPM_SLOW`-Treffer erscheinen.

Alle visuellen Inhalte muessen unter `44/765` vorab unterscheidbar sein. Die
spaeteren visuellen Fuellzustaende duerfen keinen Zielzustand innerhalb der
Schwelle reproduzieren. Beide Arme erhalten identische Expositionen, Ticks
und Proben.

Der Versuch prueft damit gleichzeitig:

```text
kurze Folge                    -> B4_RECENT
ausreichend wiederholt         -> TSPM_SLOW nach B4/Fast-Verlust
nicht ausreichend wiederholt  -> vollstaendig vergessen
```

Das ist keine neue Speicherphysik. Es ist die kontrollierte Zusammensetzung
der bereits einzeln belegten Funktionen.

## Baselines und Falsifikation

Mindestens folgende Kontrollen sind spaeter erforderlich:

- B4 allein: Folgenordnung und FIFO-Verlust ohne Slow-Erhaltung;
- TSPM-1 allein: Fast-/Slow-Inhalt ohne vollstaendige Folgenordnung;
- unabhaengig sequenzieller Doppelaufruf: gleiche Erfolgszustaende, aber
  keine garantierte atomare Fehlergrenze;
- read-only Inhaltskontrolle ohne B4-Indizes: keine Folgenrekonstruktion;
- niedrige Wiederholung: kein stabiler Slow-Treffer nach Fast-Verlust.

Der Verbund ist fuer den gebundenen Zweck falsifiziert oder die Untersuchung
ist zu stoppen, wenn mindestens einer dieser Faelle eintritt:

1. B4 und TSPM-1 erhalten nicht dieselbe kausale Rezeptorquelle.
2. Nach Fehler eines Arms wird ein Teilnachzustand oder Teilreceipt sichtbar.
3. Generation, B4-Zahl und TSPM-Fast-Zahl laufen auseinander.
4. B4 steuert Konsolidierung oder TSPM-1 steuert FIFO beziehungsweise
   Folgenordnung.
5. Der viermal exponierte Zustand ist nach belegtem B4-/Fast-Verlust nicht
   stabil aus Slow abrufbar.
6. Der nur zweimal exponierte Zustand wird ohne passende Baselineerklaerung
   als stabiler Slow-Inhalt erkannt.
7. Eine Reihenfolge wird TSPM-1, Labels oder externer Historie entnommen.
8. Eine read-only Probe veraendert einen Teil- oder Composite-Zustand.
9. Ressourcen, PPB-1-Aufrufe oder Koordinatorarbeit sind unvollstaendig
   gezaehlt.
10. Eine einfachere Architektur liefert bei gleicher Atomaritaetsgarantie,
    gleicher Funktion und geringerem Ressourcenverbrauch denselben Befund.

Ein fachlich falscher Abruf ist ein Ergebnis und kein technischer Abbruch.
Fremde Quelle, Teilcommit, Digestbruch oder unvollstaendige Aufzeichnung macht
den Versuch dagegen `NOT_EVALUABLE`. Eine Wiederholung benoetigt eine neue
ausdrueckliche Freigabe.

## Claim- und Integrationsgrenze

Ein spaeterer Erfolg darf nur lauten:

`ATOMIC_PRIVATE_DUAL_VIEW_PERCEPTUAL_MEMORY_FUNCTION_CONFIRMED`

Dies bezeichnet einen technischen Verbund aus FIFO-Folgensicht und
wiederholungsabhaengiger Zwei-Zeitskalen-Inhaltssicht. Nicht zulaessig sind
Aussagen ueber allgemeine oder langfristige MCM-Memory, Semantik,
Objektverstaendnis, Episodenlernen, Bewusstsein oder MCM-Feldwirkung.

## Entscheidung und naechster Schritt

`PASS_S2FR_STATIC_B4_TSPM1_ARCHITECTURE_AND_FALSIFICATION_CONTRACT_BOUND`

Der Architekturentscheid ist statisch vollstaendig: getrennte Zustaende,
gemeinsame Quelle, atomare Fortschreibung, getrennte read-only Befunde,
vollstaendiges Ressourcenprinzip und eindeutige Falsifikation sind gebunden.

Noch nicht freigegeben sind Implementierung, Tests, Runner, Fixtures,
Ausfuehrung, API, Snapshot oder Feldintegration. Der naechste konkrete Schritt
waere nach neuer Freigabe eine kleine private Koordinatorimplementierung mit
neutralen synthetischen Atomaritaets- und Quellbindungstests. Vor einem
Funktionslauf muss diese Implementierung den exakten Koordinatoranteil des
Ressourcenledgers materialisieren. Eine weitere allgemeine Vertragsauditkette
ist nicht erforderlich.

## S2-FS: private Koordinatorimplementierung

Die spaeter erteilte S2-FS-Freigabe wurde eng umgesetzt. Hinzugekommen sind
genau ein privates Koordinatormodul und eine fokussierte Testdatei. Der
Koordinator bindet eine gemeinsame Rezeptorquelle vollstaendig vor dem ersten
Armaufruf, haelt beide Kandidatennachzustaende lokal und gibt nur einen
vollstaendig validierten Composite-Nachzustand zurueck. Ein Fehler des zweiten
Arms nach berechnetem B4-Kandidaten laesst keinen B4-Teilzustand sichtbar
werden.

Der read-only Abruf gibt ausschliesslich die drei getrennten Rollen
`B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW` zurueck. Es gibt keine Gesamtwahl und
keinen zusaetzlichen Speicherbestand. Das Ressourcenledger zaehlt die
gemeinsame Projektion einmal sowie B4-, TSPM- und Koordinatorarbeit getrennt.
Seine gebundene Formation umfasst 617 funktionale Schreibwoerter, 468
Distanzterme und 54 Kontrollterme; die frueheren Armwerte `586/468` sind damit
nicht als Gesamtbudget ausgegeben.

Nach bestandener statischer Syntax-, Quellen-, Hash- und Exportpruefung wurde
die eine neutrale Suite genau einmal ausgefuehrt:

```text
python -m unittest -v tests.test_s2fs_private_b4_tspm1_coordinator
Ran 12 tests in 0.095s
OK
Exit-Code 0
```

Die ausgefuehrten Quellen sind digestgebunden:

```text
95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0  tools/_s2fs_b4_tspm1_private_coordinator.py
446fca812490688f8a47f01217f745cd8eeb2fbe1bc8add0ba33c035a5eae4ad  tests/test_s2fs_private_b4_tspm1_coordinator.py
```

Die Tests decken Initialinvarianten, gemeinsame Quelle, atomaren Doppelschritt,
Generationsgleichheit, Vorabbruch, beide Armfehler, veraltete Quelle,
Receiptmanipulation, Owner-Einmaligkeit, getrennten read-only Abruf,
Ressourcenledger und private Exportgrenze ab. Die bestehenden B4-, TSPM-1-,
PPB-1- und Adapterquellen blieben unveraendert.

`PRIVATE_ATOMIC_COORDINATOR_CONTRACT_VALID`

Dieser Befund qualifiziert ausschliesslich die private atomare
Koordinatorgrenze. Er ist noch kein funktionaler Nachweis des kombinierten
Memory-Verbunds, keine Feldintegration und keine automatische Auswahl eines
Abrufbefunds. Der naechste fachliche Schritt benoetigt eine eigene Freigabe fuer
einen kleinen Funktionsnachweis derselben gebundenen Geschichte ueber die drei
getrennten Sichten.
