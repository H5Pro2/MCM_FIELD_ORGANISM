# S1-QU: Statischer M2-Modusfamilien-, Eingaberecord-, Pufferanatomie- und Falsifikationsvertrag

## Status und Umfang

S1-QU bindet die kleinste statische Anatomie der privaten M2-Gegenbaseline.
Es entscheidet die in S1-QT offengebliebene Trennung zwischen rollendem
Fest-Lag-Delay und begrenztem Prefix-Replay und legt deren gemeinsame
Informations-, Zustands- und Feldkompositionsgrenze fest.

S1-QU waehlt keinen numerischen Kapazitaetswert, keine Gleichung, keine
Fixture und keine Testfolge. Es implementiert und fuehrt nichts aus. API,
primaerer Feldkern, Runtime, Runner und Orchestrator bleiben unveraendert.

Vertragsentscheidung:

```text
M2_MODE_FAMILY_BOUND_TO_DELAY_AND_ONE_SHOT_PREFIX_REPLAY
COMMON_FINITE_CAPACITY_ROLE_REQUIRED_VALUE_UNREGISTERED
CANONICAL_A1_S_EVIDENCE_RECORD_BOUND_NO_RECEPTOR_RAW_DATA_NO_FULL_FIELD
DELAY_USES_ROLLING_OLDEST_SELECTION_AFTER_WARMUP
REPLAY_USES_POSITIONAL_CAPTURE_EMIT_EXHAUSTED_PHASES
CURRENT_A1_S_IS_THE_ONLY_WARMUP_AND_EXHAUSTION_FALLBACK
REPLACE_S_PRESERVES_CURRENT_A1_H_PERCEPTION_AND_FIELD_TIME
NO_EQUATION_NO_IMPLEMENTATION_NO_EXECUTION
```

## Gemeinsame Modusfamilie

M2 besitzt genau zwei fest konfigurierte private Modi:

```text
DELAY
REPLAY
```

Die Modusidentitaet wird beim Frischstart gebunden und darf innerhalb eines
Arms nicht wechseln. Beide Modi verwenden dieselbe positive, endliche und
noch numerisch unregistrierte Kapazitaetsrolle `K`. `K` ist eine Zahl von
vollstaendigen Eingaberecords, keine Zeitdauer und kein frei wachsender
Verlauf.

Jeder Modus erhaelt dieselbe kausale Intervallgeschichte und dieselbe
aktuelle A1-S-Evidence. Die Modusregel darf weder Familie, Arm, Gap, Probe,
Ziel noch spaeteres Ergebnis kennen.

## Kanonischer M2-Eingaberecord

Pro gueltigem Intervall wird A1 genau einmal auf dem aktuellen gemeinsamen
Feld und der aktuellen modellneutralen Eingabe fortgeschrieben. Erst nach
vollstaendiger Validierung dieses Vorschlags darf M2 genau einen
unveraenderlichen Record bilden.

Ein Record enthaelt ausschliesslich:

1. den vollstaendigen signed A1-S-Evidencevektor in kanonischer
   Neuronenreihenfolge;
2. den Digest des Eingabefeldes vor A1;
3. den Geometriedigest und die kanonische Neuronenreihenfolge;
4. den Digest der aktuellen Rezeptorverteilung;
5. den Digest der synchronen oder transienten Intervallhuelle;
6. den Digest des vollstaendigen validierten A1-Vorschlags;
7. einen Digest des gesamten Recordpayloads.

Nicht gespeichert werden:

- Bild-, Audio- oder sonstige Rezeptorrohdaten;
- der vollstaendige Eingabefeld- oder A1-Feldzustand;
- A1-H als eigener Pufferwert;
- Wahrnehmungs-, Dock- oder Rezeptorobjekte;
- Kandidaten-, Comparator- oder Observerzustand;
- Arm-, Familien-, Ereignis-, Gap-, Probe- oder Ergebnislabels;
- Zielvektoren, Fits, Toleranzen oder spaetere Eingaben.

Der Record ist modellneutral, weil er genau die A1-S-Evidence bindet, die
auch den bereits zugelassenen privaten S-Kompositoren als aktueller lokaler
Baselineeingang dient. Er ist kein Feldsnapshot und keine Aussage ueber eine
hypothetische MCM-Memory.

## Gemeinsame private Zustandsrollen

Jeder M2-Zustand bindet mindestens:

- die unveraenderte Vertrags- und Modusidentitaet;
- den spaeter registrierten Konfigurationsdigest;
- `K` und den Geometriedigest;
- die feste kanonische Neuronenreihenfolge;
- hoechstens `K` vollstaendige M2-Records;
- eine moduskonforme, auf `K` begrenzte Auswahl- oder Cursorrolle;
- den Digest des gesamten Vor- beziehungsweise Folgezustands.

Die private Anatomie darf keinen unbegrenzt steigenden Ereigniszaehler
benoetigen. Ringposition, Fuellstand, Replayphase und Replaycursor bleiben
durch `K` begrenzt. Absolute Quellprovenienz folgt aus den im Record
gebundenen Feld-, Intervall- und Vorschlagsdigests.

Der Frischzustand besitzt:

- genau einen vorab gewaehlten Modus;
- die registrierte gemeinsame Kapazitaet `K`;
- die aktuelle Geometrie- und Ordnungsbindung;
- einen leeren Recordbestand;
- die fuer diesen Modus kanonische Anfangsposition.

Frischzustaende verschiedener Arme sind getrennte, digestgleiche Instanzen.

## Modus DELAY

### Anatomie

`DELAY` besitzt einen geordneten Ringpuffer mit hoechstens `K` Records und
einen durch `K` begrenzten Fuell- beziehungsweise Schreibcursor. Die
Auswahlregel ist ueber alle Geschichten fest: Sobald `K` fruehere Records
vorliegen, ist der aelteste Record die einzige Ausgabequelle.

### Warm-up

Solange vor dem aktuellen Intervall weniger als `K` fruehere Records
vorliegen, existiert keine gueltige Delayquelle. In diesem Fall wird der
aktuelle A1-S-Evidencevektor unveraendert als S-Output verwendet. Danach wird
der aktuelle Record atomar in den Puffer aufgenommen.

Der Warm-up ist kein dritter Modus und kein Nulloutput. Er fuegt keine
historische Wirkung hinzu.

### Rollender Betrieb

Sobald der Puffer vor dem aktuellen Intervall voll ist:

1. wird der aelteste vorliegende Record als einzige S-Ausgabequelle
   selektiert;
2. wird dieser Record aus dem rollenden Puffer entfernt;
3. wird der aktuelle Record angehaengt;
4. wird der Folgezustand wieder mit exakt `K` Records atomar ausgegeben.

Damit bleibt die Auswahl ein fester diskreter Lag von `K` akzeptierten
Intervallen. Intervalllaengen duerfen variieren; sie veraendern den
diskreten Lag nicht.

## Modus REPLAY

### Anatomie

`REPLAY` besitzt genau die drei kanonischen Phasen:

```text
CAPTURE -> EMIT -> EXHAUSTED
```

Es traegt hoechstens `K` Records und einen durch `K` begrenzten
Replaycursor. Die Phase folgt ausschliesslich aus Frischstart, erfolgreicher
Recordannahme und Cursorposition. Kein externes Ereignis startet oder endet
Replay.

### CAPTURE

In `CAPTURE` wird pro gueltigem Intervall der aktuelle Record angehaengt und
der aktuelle A1-S-Evidencevektor unveraendert ausgegeben. Mit Annahme des
`K`-ten Records wird der Folgezustand auf `EMIT` mit Cursor am ersten Record
gesetzt.

### EMIT

In `EMIT` wird pro gueltigem Intervall genau der durch den Replaycursor
bezeichnete gespeicherte S-Evidencevektor ausgegeben. Die aktuelle Eingabe
wird weiterhin vollstaendig validiert und A1 genau einmal fortgeschrieben,
aber nicht dem eingefrorenen Prefix hinzugefuegt. Nach jeder atomaren Ausgabe
rueckt der Cursor um genau eine begrenzte Position vor.

Nach Ausgabe des `K`-ten Prefixrecords wechselt der Folgezustand auf
`EXHAUSTED`. Reihenfolge, Wiederholungszahl und Ende koennen nicht durch den
Inhalt der Records beeinflusst werden.

### EXHAUSTED

In `EXHAUSTED` findet keine weitere Replayausgabe und keine weitere
Pufferaufnahme statt. Der aktuelle A1-S-Evidencevektor wird unveraendert
ausgegeben. Phase, Prefix und Endcursor bleiben unveraendert und belegen,
dass die eine Replayfolge beendet ist.

Replay wird innerhalb eines Arms nicht zurueckgesetzt, erneut gestartet oder
zyklisch wiederholt.

## Atomare Feldkomposition

Beide Modi verwenden pro Intervall genau einen validierten aktuellen
A1-Vorschlag. Der durch Modus und Phase bestimmte S-Vektor ersetzt
ausschliesslich dessen Aktivierungsrolle S.

Unveraendert vom aktuellen A1-Vorschlag bleiben:

- H und alle weiteren Neuronenrollen;
- aktuelle Perzeption und aktuelle Rezeptorprovenienz;
- Docks, Feld- und Geometrieidentitaet;
- die aktuelle Feldzeitfortschreibung;
- die Abwesenheit aktiver Kandidaten-, Substrat- oder Entwicklungszustaende.

Das Ergebnis muss ein vollstaendiges gemeinsames Feld, den vollstaendigen
M2-Folgezustand und einen Receipt gemeinsam liefern. Bei jedem Fehler sind
Feld und Folgezustand gemeinsam `NOT_COMPUTABLE`; Teilresultate sind
verboten.

## Auswahlprovenienz

Jede spaetere erfolgreiche Ausgabe muss eindeutig als eine der folgenden
Rollen belegt werden:

```text
CURRENT_A1_WARMUP
DELAY_OLDEST_RECORD
CURRENT_A1_CAPTURE
REPLAY_PREFIX_RECORD
CURRENT_A1_EXHAUSTED
```

Bei einer Recordausgabe bindet der Receipt mindestens Recorddigest,
Quellfeld-, Quellverteilungs-, Quellintervall- und A1-Vorschlagsdigest sowie
die begrenzte Puffer- oder Cursorposition. Bei aktueller A1-Ausgabe bindet er
den aktuellen Vorschlagsdigest und bestaetigt, dass keine Recordposition
selektiert wurde.

Diese Rollen sind technische Provenienz und keine Orchestrierungs- oder
Ergebnislabels.

## Nichtduplizierung und Gegenprognose

`DELAY` und `REPLAY` bleiben mit derselben spaeter registrierten Kapazitaet
strukturell getrennt. Fuer eine Folge mit mindestens `K` Prefixintervallen,
`K` Emissionsintervallen und einem weiteren unterschiedlichen Intervall gilt:

- `DELAY` setzt die rollende Auswahl des jeweils `K` Positionen frueheren
  Records fort;
- `REPLAY` gibt waehrend `EMIT` genau das erste Prefix aus und danach wieder
  den aktuellen A1-S-Vektor;
- beide sehen und validieren in jedem Intervall dieselbe aktuelle Eingabe.

Die spaetere Divergenz muss auf Quellpositionen und Recorddigests, nicht nur
auf numerische Ungleichheit gestuetzt werden. Sind die selektierten
Quellrollen nicht verschieden oder benoetigt Replay ein externes Startlabel,
ist Replay auf Delay reduzierbar und wird als separater Modus gestoppt.

Fixed Adapter besitzt keinen kausalen Puffer. Leaky, Integrator, M1 und
M5_DIRECT waehlen keine exakte fruehere Recordposition. M4/DTS-1/T1 und
Capacity-Clamp besitzen Ressourcen- oder Kapazitaetsrollen, die M2
ausdruecklich nicht traegt.

## Fail-Closed-Regeln

M2 ist ungueltig oder `NOT_COMPUTABLE`, wenn:

- `K` nicht positiv, endlich und fuer beide Modi identisch registriert ist;
- Modus, `K`, Geometrie oder Neuronenreihenfolge waehrend eines Arms
  wechseln;
- ein Record unvollstaendig, nicht endlich, nicht kanonisch geordnet oder
  digestinkonsistent ist;
- Pufferlaenge, Fuellstand, Phase oder Cursor ausserhalb ihrer durch `K`
  begrenzten Anatomie liegen;
- eine Delayquelle vor vollstaendigem Warm-up oder eine Replayquelle
  ausserhalb `EMIT` selektiert wird;
- Replay Records ausserhalb des ersten Prefix aufnimmt, umordnet,
  ueberspringt, erneut ausgibt oder nach `EXHAUSTED` neu startet;
- eine Quelle anhand ihres Inhalts, eines Zielwerts oder eines spaeteren
  Ergebnisses ausgewaehlt wird;
- Rezeptorrohdaten, vollstaendige Felder, H, Kandidaten- oder Observerdaten
  im Puffer erscheinen;
- ein Arm Pufferzustand eines anderen Arms liest;
- der aktuelle A1-Vorschlag fehlt, mehrfach erzeugt oder nach der
  Recordauswahl neu berechnet wird;
- finales H, Perzeption, Docks oder Feldzeit nicht exakt vom aktuellen
  A1-Vorschlag stammen;
- Feld oder Folgezustand trotz Fehler teilweise veroeffentlicht werden.

## Weiterhin offene Bindungen

Vor einer Implementierung fehlen:

- genau ein numerischer positiver Kapazitaetswert `K` fuer beide Modi;
- eine endliche positionsunterscheidbare Registrierungsfolge;
- kanonische Vertrags-, Konfigurations- und Fixture-Digests;
- konkrete Datentypen fuer Record, Moduszustaende, Resultat und Receipt;
- deterministische Phasen- und Fehlercodes;
- Mutationsklassen und ein endliches Testbudget;
- eine begrenzte Implementierungs- und Einmalabnahmefreigabe.

## Aussagegrenze

S1-QU bindet nur eine private technische Gegenbaseline. Es bestaetigt keine
Delay- oder Replaywirkung im Feld, keinen Kandidaten und keinen Befund zu
einer hypothetischen MCM-Memory. M2 darf nicht als Feldfunktion, Lernregel
oder Kandidatenabkuerzung bezeichnet werden.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QV - statischer M2-Kapazitaets-, Positions- und
        Divergenzregistrierungsvertrag
```

S1-QV darf genau einen gemeinsamen positiven Kapazitaetswert `K`, eine
kleinste endliche Recordfolge und die erwarteten Quellrollen von `DELAY` und
`REPLAY` vorregistrieren. Es muss statisch belegen, dass die Modi nach der
Replayerschoepfung unterschiedliche Quellpositionen besitzen. Scheitert
diese Trennung, wird `REPLAY` gestoppt. Keine Implementierung, Fixture,
Testausfuehrung oder Feldentscheidung.
