# S1-OT G2/D3 drei O3-Checkpoints: Funktions- und Falsifikationsvertrag

## Status

S1-OT bindet ausschliesslich Funktion, kausale Messpunkte,
Gegenbaselinegrenze und Falsifikationsbedingungen fuer drei read-only
O3-Checkpoints an der akzeptierten S1-OS-Zweischrittkomposition. Der Schritt
bindet noch kein neues Schema, keine Implementierung, keinen Testlauf und
keine Feldrueckwirkung.

Entscheidung:

```text
G2_D3_TWO_STEP_THREE_POST_VALIDATION_O3_CHECKPOINTS_FUNCTION_AND_FALSIFICATION_BOUND
```

## Technische Frage

S1-OT prueft spaeter nur:

```text
Traegt dieselbe vollstaendig validierte D3-Zustandsfolge C0 -> Mixed -> Second
an drei getrennten read-only O3-Checkpoints exakt die vorab berechenbare
Zulassungsfolge 0.5 -> 0.25 -> 0.125?
```

O3 bezeichnet weiterhin nur
`local_admissible_engagement = max(0.0, free - bound_configured)`. Der Wert
ist eine statische obere Zulassungsgrenze. Er ist keine Transferbuchung,
keine Feldantwort und keine ausgefuehrte Aufnahme.

## Drei gebundene Checkpoints

### CP0: Initialzustand

CP0 liest ausschliesslich das validierte initiale C0 vor der ersten
Projektion:

```text
free = 0.5
bound_configured = 0.0
O3_CP0 = 0.5

D3 input digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7

anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f
```

### CP1: Erster Commitzustand

CP1 ist erst zulaessig, nachdem der erste Schritt vollstaendig
`PROJECTED_COMMITTED` geliefert und das S1-OS-Zwischenidentitaetsgate Mixed
bestaetigt hat:

```text
free = 0.5
bound_configured = 0.25
O3_CP1 = 0.25

D3 input digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c
```

Ein Projektionspreview oder ein fehlgeschlagener erster Commit ist kein CP1.

### CP2: Finaler Commitzustand

CP2 ist erst zulaessig, nachdem der zweite Schritt vollstaendig
`PROJECTED_COMMITTED` geliefert und das finale S1-OS-Identitaetsgate Second
bestaetigt hat:

```text
free = 0.5
bound_configured = 0.375
O3_CP2 = 0.125

D3 input digest
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab

anatomy_record_digest
= efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681
```

## Gerichtete technische Komponenten

Ohne Toleranz, Fit oder Rundung werden vorab gebunden:

```text
Delta_CP1_CP0 = O3_CP1 - O3_CP0 = -0.25
Delta_CP2_CP1 = O3_CP2 - O3_CP1 = -0.125
Delta_CP2_CP0 = O3_CP2 - O3_CP0 = -0.375

O3_CP1 = O3_CP0 / 2
O3_CP2 = O3_CP1 / 2
```

Diese Werte folgen konstruktiv aus dem akzeptierten O3-Operator und den
konservativen D3-Unterteilungen. Sie sind eine technische
Checkpointprognose, kein empirisch offener Effekt.

## X/Y-Symmetrie

`OP_CHAIN_XXX` und `OP_CHAIN_YYY` muessen an jedem korrespondierenden
Checkpoint bitidentische D3-Bytes und deshalb bitidentische O3-Belege
erzeugen:

```text
XXX_CP0 = YYY_CP0 = 0.5
XXX_CP1 = YYY_CP1 = 0.25
XXX_CP2 = YYY_CP2 = 0.125
```

Orientierung, Chainrolle, Kontakt- und Grenzdigests duerfen den O3-Sachwert
nicht erreichen.

## Keine Belegkette als Eingang

Der akzeptierte S1-OS-Sequenzbeleg bleibt passive Dokumentation. Ein
spaeterer O3-Checkpointpfad darf ihn weder entgegennehmen noch daraus Mixed
oder Second rekonstruieren.

Ebenfalls verboten sind:

- Nachladen von Mixed oder Second aus einer Fixturetabelle;
- Ableiten eines Checkpointwerts aus Chainrolle, Schrittnummer oder
  erwartetem Ergebnis;
- Weiterreichen eines Projektions-, Commit- oder O3-Belegs als fachliche
  Folgeeingabe;
- erneute Bildung einer parallelen Zweischrittlogik nur fuer die Messung.

## Gemeinsame private Ausfuehrungsgrenze

Die spaetere Architektur muss genau einen privaten, reinen
Zweischrittexecutor besitzen. Er darf innerhalb eines Aufrufs transient
halten:

```text
validated initial C0 bytes
first committed Mixed bytes
second committed Second bytes
zugehoerige passive interne Belege
```

Die bestehende oeffentliche Funktion
`compose_g2_d3_two_step_continuation` muss diesen Executor verwenden und
weiterhin bitidentisch nur Finalbytes plus den unveraenderten S1-OQ-Beleg
ausgeben.

Ein spaeterer separater O3-Checkpointoperator darf denselben privaten
Executor genau einmal aufrufen und die drei transienten D3-Bytes danach
read-only an den bereits akzeptierten O3-Operator uebergeben. Die private
Trace darf weder oeffentlich zurueckgegeben noch gespeichert werden.

Da O3 rein und zustandslos ist, duerfen die drei Werte nach Abschluss der
atomaren Zweischrittfolge aus den innerhalb desselben Aufrufs getragenen
Checkpointbytes ausgewertet werden. Die logische Checkpointrolle wird durch
den jeweiligen vollstaendigen Commitzustand gebunden, nicht durch
eine externe Uhr.

## Vorgesehene reine Oberflaeche

Eine spaetere API darf inhaltlich hoechstens bereitstellen:

```text
evaluate_g2_d3_two_step_o3_checkpoints(
    first_boundary_raw_bytes,
    second_boundary_raw_bytes,
    initial_d3_raw_bytes,
    formation_enabled,
    checkpoint_registry,
    sequence_registry,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TwoStepO3CheckpointResult
```

Sie nimmt weder Sequenzbeleg noch Zwischen- oder Finalbytes entgegen. S1-OT
implementiert diese API nicht.

## Messreihenfolge und Atomaritaet

Verbindlich gilt:

```text
1. alle Eingaben und Registries fail-closed pruefen
2. C0 validieren und als CP0 binden
3. ersten Projektions-/Commitschritt vollstaendig abschliessen
4. Mixed-Identitaet bestaetigen und als CP1 binden
5. zweite Grenze, Quelle und Kontaktlink pruefen
6. zweiten Projektions-/Commitschritt vollstaendig abschliessen
7. Second-Identitaet bestaetigen und als CP2 binden
8. O3 je einmal auf CP0, CP1 und CP2 auswerten
9. Werte, gerichtete Komponenten und passive Belegdigestrollen bilden
10. alle privaten Checkpointbytes und internen Belege verwerfen
```

Scheitert die Sequenz vor CP2, gibt der Checkpointoperator kein partielles
Messresultat aus. CP0 oder CP1 werden dann nicht einzeln publiziert.

## Angepasste Gegenbaseline

Die Folge `0.5 -> 0.25 -> 0.125` ist vollstaendig durch die vorab gesetzte
Halbierungsregel und den bekannten O3-Operator bestimmt. Ein fairer
zustandsbehafteter Adapter kann dieselbe Folge tragen.

Deshalb ist unzulaessig:

```text
G2/D3-Zustandsfolge gegen eine unveraenderte konstante Baseline vergleichen
und die Differenz als eigene Substratfunktion werten.
```

Eine spaetere Gegenbaseline muss dieselbe X/X/X- oder Y/Y/Y-Exposition sehen,
ihren eigenen Zustand ueber beide Schritte tragen duerfen und auf dieselben
drei logischen Checkpoints gelesen werden. S1-OT waehlt oder implementiert
diese Baseline noch nicht.

## Falsifikationsbedingungen

Der Checkpointpfad wird gestoppt, wenn:

- ein Checkpoint vor vollstaendiger D3-Validierung oder vor seinem Commit
  gelesen wird;
- CP1 nicht exakt Mixed oder CP2 nicht exakt Second ist;
- ein Sequenzbeleg, Fixturelookup oder Schrittnummer den Sachwert bestimmt;
- XXX und YYY an korrespondierenden Checkpoints verschiedene O3-Werte oder
  O3-Belege liefern;
- ein O3-Beleg D3, Sequenz, O3-Folgeaufruf oder Feldzustand beeinflusst;
- der bestehende S1-OS-Kompositionsoutput durch die private
  Executorrefaktorierung veraendert wird;
- mehr als eine Zweischrittausfuehrung pro Checkpointaufruf erforderlich ist;
- bei Sequenzfehler ein partieller Checkpointvektor sichtbar wird;
- O3 einen Transfer bucht, Checkpointbytes mutiert oder einen Feldschritt
  ausfuehrt;
- eine konstante, nicht zustandstragende Baseline als ausreichende
  Funktionsabgrenzung verwendet wird.

## Aussagegrenze

S1-OT bindet nur eine konstruktiv erwartete read-only Zulassungsfolge auf
drei validierten D3-Zustaenden. Es gibt noch keinen Checkpointoperator und
keinen neuen Lauf. Die Folge belegt keine tatsaechliche Aufnahme, keine
Feldrueckwirkung, keine Abschwaechungsfunktion gegen angepasste Baselines und
keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OU darf ausschliesslich den gemeinsamen privaten Executorvertrag, die
unveraenderte bestehende Kompositionsoberflaeche, Checkpoint-API, Registry,
Vertragsdigests, Phasen, Einzelcodes und passive Belegrollen statisch binden.

S1-OU darf keine Produktions- oder Testimplementierung, keinen Testlauf,
keine Runtimepublikation und keinen Feld-, Transfer-, Runner- oder
Medienpfad ausfuehren.
