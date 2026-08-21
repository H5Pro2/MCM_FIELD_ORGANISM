# S1-QT: Statischer M2-Delay-/Replaypuffer-Bestands-, Nichtduplizierungs- und Falsifikationsaudit

## Status und Umfang

S1-QT prueft ausschliesslich den Projektbestand und die technische
Eigenstaendigkeit der in S1-QC und S1-QD gebundenen M2-Familie. M2 bleibt
eine private negative Gegenbaseline. Es ist weder Kandidatenmechanik noch
Funktion des primaeren MCM-Wahrnehmungsfeldes.

Der Audit bindet keine Gleichung, Puffergrenze, Laglaenge, Replaylaenge,
Ausgabewerte, Konfiguration, Implementierung, Fixture oder Ausfuehrung. Es
wurde kein Test und kein Feldlauf ausgefuehrt.

Auditentscheidung:

```text
NO_ADMISSIBLE_COMPLETE_M2_CORE_PRESENT
TYPED_CAUSAL_INPUT_AND_FIELD_COMPOSITION_PRIMITIVES_EXIST
ROLLING_FIXED_LAG_AND_BOUNDED_PREFIX_REPLAY_CAN_REMAIN_DISTINCT
REPLAY_REQUIRES_PREREGISTERED_CAUSAL_START_END_AND_EXHAUSTION_OR_MERGES_INTO_DELAY
M2_IMPLEMENTATION_AND_EXECUTION_REMAIN_UNBOUND
```

## Verbindliche M2-Mindestrolle

M2 prueft, ob ein spaeterer Feldverlauf allein durch eine deterministische,
endliche Wiederverwendung frueherer modellneutraler Eingaben erklaert werden
kann. Fuer alle Arme muessen dieselbe feste Regel, dieselbe endliche Grenze
und ein eigener leerer Frischzustand gelten.

Der private Zustand darf nur Records enthalten, die M2 in derselben
kausalen Geschichte bereits erhalten hat. Arm-, Familien-, Gap-, Probe- und
Ergebnislabels, Kandidatenzustand, Observerresultate, Zukunftszugriff,
globale Caches und Pufferuebertrag zwischen Armen bleiben verboten.

## Bestandsinventar

| Bestand | Tatsaechliche Rolle | M2-Einordnung |
|---|---|---|
| `auditory_field_function_probe.py` | boolescher Ein-Schritt-Vergleich | kein privater Delayzustand, kein Feldpfad |
| `history_sensitive_reentry_probe.py` | konkatenierter Observervektor zweier Kontakte | kein Puffer-Carry, kein M2-Output |
| `e1_repetition_formation_planner.py` | Wiederholung vorbereiteter Quellen vor dem Lauf | Orchestrierungsquelle, kein kausaler Baselinezustand |
| `s1r_phase_separation_matrix.py` | Erzeugung von Nullkontaktintervallen | Gap-Konstruktion, kein Delaypuffer |
| Rezeptor- und Medienpuffer | Aufnahme, Ordnung und Dockuebergabe | Eingabeinfrastruktur, keine Gegenbaseline |
| `previous_state_contribution_hook.py` | Eingriff auf vorhandenen Feldzustand | kein gespeicherter Eingabeverlauf |
| DTS-1/T1-Sequenzen | geschlossene Dreirollenbaseline | Ressourcenledger, kein M2 |
| M1 und M5_DIRECT | passive Mehrspur- beziehungsweise Einspurretention | keine exakte Positionsauswahl |

Vorhandene Replaybezeichnungen in geschlossenen oder historischen Modulen
sind keine Freigabe. Kein Bestandsmodul besitzt gemeinsam einen endlichen
privaten Eingabepuffer, eine feste Auswahlposition, atomaren Carry,
Auswahlprovenienz und einen vollstaendigen S/H-Feldoutput.

## Wiederverwendbare technische Primitive

`ReceptorDistribution`, `TransientNeuronInputSet` und `MCMFieldStepTime`
stellen typisierte, geordnete und kausal begrenzte Eingabe- und Zeitrollen
bereit. Sie sind selbst zustandslos und duerfen nicht in einen M2-Puffer
umgedeutet werden.

Der vorhandene modellneutrale A1/`REPLACE_S`-Hilfskern zeigt, wie genau ein
A1-Vorschlag validiert und finales S bei unveraendertem H und genau einer
Feldzeitfortschreibung materialisiert werden kann. Das ist nur eine
moegliche Kompositionsoberflaeche. Welche kleinste modellneutrale
Recordoberflaeche M2 spaeter speichert, bleibt offen. Bild-, Audio- oder
andere Rezeptorrohdaten werden durch S1-QT nicht als Pufferinhalt zugelassen.

## Verbleibende Gegenprognosen

### Fester rollender Delay

Ein zulaessiger `M2_DELAY` gibt nach einem vorab festen diskreten Abstand
exakt die dazugehoerige fruehere Eingabeposition aus und setzt diese Regel
ueber die gesamte Geschichte fort.

Seine strukturelle Gegenprognose ist eine positionsgetreue, diskontinuierlich
verschobene Folge. Fixed Adapter besitzt keinen kausalen Verlaufspuffer;
Leaky, Integrator, M1 und M5 tragen geglaettete oder akkumulierte Zustaende,
aber keine belegte exakte Quellposition.

### Begrenztes Prefix-Replay

Ein separates `M2_REPLAY` kann nur dann eigenstaendig bleiben, wenn es ein
vorab begrenztes Eingabepraefix einmal in unveraenderter Ordnung ausgibt und
danach einen vorab gebundenen Erschoepfungszustand erreicht. Aufnahmebeginn,
Aufnahmeende, Ausgabebeginn und Erschoepfung muessen allein aus fester
Konfiguration und kausaler Position folgen.

Die Trennung gegen Delay erfordert spaeter eine Geschichte, in der nach dem
gespeicherten Praefix weitere verschiedene Eingaben folgen: Ein rollender
Delay setzt seine verschobene Ausgabe fort; ein echtes begrenztes Replay
darf nur sein registriertes Praefix ausgeben und muss danach erschoepft sein.

Kann S1-QU diese Trennung nicht ohne Ereignislabel, Zielsuche oder
nachtraegliche Auswahl binden, wird `M2_REPLAY` als eigene Rolle gestrichen
und auf den allgemeinen Delaypuffer reduziert.

## Nichtduplizierung

- Gegen Fixed Adapter: M2-Ausgabe haengt von selbst kausal empfangenen
  frueheren Records ab, nicht von einer eingefrorenen Formabbildung.
- Gegen Leaky, Integrator, M1 und M5_DIRECT: M2 waehlt eine belegte diskrete
  Quellposition; es integriert, mittelt und zerfaellt nicht.
- Gegen schnellen Nachhall A1-H: M2 darf H keine eigene Dynamik geben und
  muss seinen privaten Verlauf ausschliesslich in der S-Fortsetzung zeigen.
- Gegen M4/DTS-1/T1 und Capacity-Clamp: M2 besitzt weder Ressourcenrollen
  noch Kapazitaet, Commit, Freigabe oder Blockierung.
- Gegen Orchestrator-Replay: Wiederholte Testquellen vor dem Lauf sind keine
  privat und kausal gespeicherten Baselineeingaben.

## Verwerfungsbedingungen

M2 oder eine seiner Rollen wird verworfen, wenn:

- Puffergrenze, Lag, Auswahlordnung oder Ausgaberegel pro Arm wechseln;
- ein Record vor seinem kausalen Eingang ausgegeben wird;
- Rohdaten, Kandidatenzustand, Feldresultate oder Observerwerte als
  versteckte Zusatzinformation gespeichert werden;
- Replaybeginn oder -ende ein Gap-, Probe-, Ergebnis- oder Familienlabel
  benoetigt;
- Replay nur ein anders benannter rollender Delay ist;
- ein Zielmuster gesucht oder eine Ausgabe nach Ergebnissicht ausgewaehlt
  wird;
- Geschichte unbegrenzt waechst oder zwischen Armen geteilt wird;
- H veraendert, A1 mehrfach fortgeschrieben oder Feldzeit mehrfach
  weitergesetzt wird;
- nur ein Skalar oder Observerwert statt eines atomaren vollstaendigen
  Feldoutputs entsteht;
- das Fehlen eines zulaessigen M2-Kerns als Kandidatenresiduum gilt.

## Offene Bindungen

Vor jeder M2-Implementierung fehlen mindestens:

- die kleinste kanonische modellneutrale Eingaberecordoberflaeche;
- die Entscheidung, ob Delay und Replay beide die Verwerfungspruefung
  bestehen;
- eine feste endliche Pufferanatomie je verbleibendem Modus;
- Aufnahme-, Auswahl-, Cursor- und Erschoepfungsrollen;
- Frischstart, atomarer Carry und vollstaendige Provenienzdigests;
- das Verhalten vor einer ausgabefaehigen Position und nach Erschoepfung;
- die S/H-Komposition ohne doppelten A1- oder Feldzeitschritt;
- deterministische Fail-Closed- und spaetere Testgrenzen.

## Paketstatus und Aussagegrenze

Nach S1-QT bleibt M2 strukturell als negative Gegenbaseline begruendbar, ist
aber nicht implementierbar oder ausfuehrbar. Die vorhandenen Primitive
schliessen nur Teile der technischen Huelle, nicht den Pufferkern.

S1-QT bestaetigt keine Feldwirkung, keinen Kandidaten und keinen Befund zu
einer hypothetischen MCM-Memory. Der primaere MCM-Wahrnehmungsfeldkern, alle
geschlossenen Zweige sowie API, Runtime, Runner und Orchestrator bleiben
unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QU - statischer M2-Modusfamilien-, Eingaberecord-, Pufferanatomie- und
        Falsifikationsvertrag
```

S1-QU muss zuerst entscheiden, ob neben einem festen rollenden Delay ein
kausal und endlich gebundenes Prefix-Replay eigenstaendig bleibt. Danach darf
es genau die kleinste Recordoberflaeche, Modus- und Pufferrollen,
Frischstart, Carry, Auswahlprovenienz, Erschoepfung und S/H-Komposition
binden. Bleibt keine nichtduplizierte endliche Rolle uebrig, wird M2
gestoppt. Keine Gleichung, Parameterwahl, Implementierung, Fixture,
Testausfuehrung oder Ergebnisentscheidung.
