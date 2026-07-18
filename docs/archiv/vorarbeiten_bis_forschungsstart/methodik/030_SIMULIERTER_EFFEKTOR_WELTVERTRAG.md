# Methodik 030: Simulierter Effektor-Weltvertrag

## 1. Status

Vorregistrierter Invarianten- und Schnittstellentest für Architektur 018. Es
wird noch kein Pfad vom MCM-Feld zum Effektor eingeführt.

## 2. Forschungsfrage

Kann eine minimale reversible Weltwirkung vollständig deterministisch,
ursachentransparent und ausschließlich über einen späteren Rezeptorrahmen
zurückgeführt werden, ohne Handlung, Ziel oder Feldrückschreibung einzubauen?

## 3. Unveränderliche Zustandsrollen

### Weltzustand

```text
tick
position
```

`position` liegt exakt im Bereich `0..6`.

### Intervention

```text
source_tick
delta
cause
```

Zulässige Werte sind:

```text
delta ∈ {-1, 0, +1}
cause ∈ {external, effector}
```

`cause = effector` bezeichnet im ersten Test nur die technische Herkunft des
extern erzeugten Testobjekts. Es bedeutet nicht, dass das MCM-Feld die
Intervention ausgelöst hat.

### Weltübergang

```text
previous_world
intervention
next_world
effort
```

Dabei gilt fest:

```text
next_world.tick = previous_world.tick + 1
next_world.position = (previous_world.position + delta) modulo 7
effort = |delta|
```

### Rezeptorrahmen

```text
source_tick
seven local contact values
```

Genau ein Kontaktwert ist `1.0`, alle anderen sind `0.0`. Der Rahmen enthält
weder `cause`, `delta`, Weltposition noch Effort.

## 4. Kausale Erzeugungsfolge

```text
WorldState(t)
+ Intervention(source_tick=t)
→ WorldTransition(t→t+1)
→ WorldState(t+1)
→ ReceptorFrame(source_tick=t+1)
```

Der Rezeptor darf nur aus `WorldState(t+1)` erzeugt werden. Intervention und
Übergang sind keine Rezeptoreingaben.

## 5. Kanonische Digests

Getrennt gebildet werden:

### Provenienzdigest

Enthält Weltzustände, Intervention, Ursache und Effort. Externe und
Effektorintervention müssen hier unterscheidbar bleiben.

### Weltfolgendigest

Enthält ausschließlich vorherigen und nächsten Weltzustand. Bei gleichem
Startzustand und gleichem `delta` muss er unabhängig von `cause` kollidieren.

### Rezeptordigest

Enthält ausschließlich `source_tick` und Kontaktvektor. Bei gleicher
Weltfolge muss er unabhängig von `cause` kollidieren.

Diese Trennung verhindert, dass technische Ursachenprovenienz als sensorische
Eigenwahrnehmung ausgegeben wird.

## 6. Vollständige Einzelübergangsmatrix

Geprüft werden:

```text
7 Startpositionen
x 3 delta-Werte
x 2 Ursachen
= 42 Einzelübergänge
```

Jeder Einzelübergang beginnt unabhängig bei `tick = 0`. Die technische
Auswertungsreihenfolge darf den Starttick nicht fortschreiben.

Für jede Startposition und jedes `delta` wird die externe gegen die als
Effektor markierte Intervention gepaart:

```text
42 Einzelübergänge
→ 21 Ursachenpaare
```

Erwartung:

- Provenienzdigests unterscheiden sich in jedem Ursachenpaar.
- Weltfolgendigests kollidieren in jedem Ursachenpaar.
- Rezeptordigests kollidieren in jedem Ursachenpaar.

## 7. Reversibilitätsfamilie

Für jede der sieben Startpositionen werden geprüft:

```text
+1 gefolgt von -1
-1 gefolgt von +1
```

Damit entstehen 14 inverse Zweischrittfolgen. Jede Folge muss exakt zur
Startposition zurückkehren. Der Endtick liegt genau zwei Takte nach dem
Starttick.

Jede Folge beginnt unabhängig bei `tick = 0`. Beide Interventionen tragen die
Ursache `external`, weil noch keine Effektor-Runtime existiert.

## 8. Vollumlauffamilie

Für jede der sieben Startpositionen werden geprüft:

```text
siebenmal +1
siebenmal -1
```

Damit entstehen 14 Vollumläufe. Jeder Umlauf muss zur Startposition
zurückkehren und genau sieben Einheiten technischen Aufwand ausweisen.

Jeder Vollumlauf beginnt unabhängig bei `tick = 0`. Alle sieben
Interventionen tragen die Ursache `external`.

## 9. Nullintervention

Für alle sieben Startpositionen und beide Ursachen gilt bei `delta = 0`:

```text
next_position = previous_position
effort = 0
```

Die technische Ursache darf im Provenienzdigest verschieden bleiben. Welt- und
Rezeptorfolge müssen kollidieren.

## 10. Reset

Der Referenzreset verwendet:

```text
reset_position = 0
reset_tick = 0
last_cause = none
last_delta = 0
last_effort = 0
```

Der Reset erzeugt noch keinen Rezeptorrahmen. Geprüft werden vierzehn
Ausgangszustände:

```text
7 Positionen bei tick = 0
7 Positionen bei tick = 11
```

Alle vierzehn Resets müssen exakt denselben Resetstatus erzeugen.

## 11. Ungültige Eingaben

Abgelehnt werden:

- Positionen außerhalb `0..6`,
- nichtganzzahlige Positionen,
- `delta` außerhalb `-1..1`,
- nichtganzzahlige `delta`-Werte,
- unbekannte Ursachen,
- Interventionen mit falschem `source_tick`,
- mehrere Interventionen für denselben Weltübergang,
- Rezeptorbildung aus einem unvollständigen Übergang,
- Kontaktvektoren, die nicht exakt one-hot sind.

## 12. Observer- und Reihenfolgekontrolle

Ein optionaler Observer darf abgeschlossene Übergänge lesen. Vor und nach dem
Aufruf werden Digests der unveränderlichen Quelle verglichen.

Der Observer erhält ausschließlich das bereits vollständig validierte
`WorldTransition`-Objekt. Er erhält keinen veränderlichen Weltcontainer und
keinen Zugriff auf eine folgende Probe.

Zusätzlich werden Startpositionen, `delta`-Werte, Ursachen und unabhängige
Prüffamilien in umgekehrter Auswertungsreihenfolge ausgeführt. Das kanonisch
sortierte Gesamtergebnis muss identisch bleiben.

Die Referenzreihenfolgen lauten:

```text
start_position: 0, 1, 2, 3, 4, 5, 6
delta:          -1, 0, +1
cause:          external, effector
inverse Folge:  (+1,-1), (-1,+1)
Vollumlauf:     siebenmal -1, siebenmal +1
```

Technische Testreihenfolge ist keine Weltzeit. Jede unabhängige Probe beginnt
mit ihrem ausdrücklich erzeugten Weltzustand.

## 13. Pflichtentscheidungen N0 bis N8

```text
N0 delta = 0:
   Weltposition unverändert, effort = 0

N1 +1, -1:
   exakte Rückkehr

N2 -1, +1:
   exakte Rückkehr

N3 siebenmal +1:
   exakter Vollumlauf

N4 siebenmal -1:
   exakter Vollumlauf

N5 external gegen effector:
   verschiedene Provenienz, gleiche Welt- und Rezeptorfolge

N6 Observer an gegen aus:
   identisches kanonisches Ergebnis

N7 umgekehrte Auswertungsreihenfolge:
   identisches kanonisches Ergebnis

N8 Reset:
   identischer neutraler Vertragszustand
```

## 14. Öffentliche Rollen

Öffentliche Vertrags- und Ergebnisrollen dürfen enthalten:

- technische Zeit,
- Weltposition,
- `delta`, Ursache und Effort im äußeren Übergangsprotokoll,
- Kontaktvektor im Rezeptorrahmen,
- Invarianten und Digests.

Sie dürfen nicht enthalten:

- MCM-Aktivierung oder Nachhall,
- Neuronenidentität,
- Aktionswert oder Gewinner,
- Reward oder Ziel,
- Erfolg, Fehler oder Bewertung,
- semantische Bezeichnung,
- adaptive Stärke oder Lernen.

## 15. Entscheidung

Der Vertragstest trägt nur, wenn N0 bis N8 gemeinsam erfüllt sind.

Ein positiver Befund bedeutet:

> Eine begrenzte reversible Weltwirkung kann technisch von ihrer Ursache
> getrennt und ausschließlich als spätere Rezeptorfolge sichtbar gemacht
> werden.

Er bedeutet nicht:

- dass das MCM-Feld die Wirkung ausgelöst hat,
- dass Eigenwirkung erkannt wird,
- dass eine Handlung vorliegt,
- dass die Weltwirkung nützlich oder richtig ist.

## 16. Stopplinie

Nicht freigegeben sind:

- Verbindung von Feldwerten mit `delta`,
- autonome Intervention,
- Auswahl- oder Schwellenmechanik,
- Reward und Zielposition,
- organische Ressourceninterpretation des festen Efforts,
- Beziehungsmemory oder sensorische Selbstregulation,
- reale Hardware-, Browser- oder Systemsteuerung.

## 17. Evidenzgrenze

Maximal E1 für Welt-, Interventions- und Rezeptorvertrag.

E0 bleiben:

- MCM-Eigenwirkung,
- Handlung,
- organische Ressourcenwirkung,
- Feldorganisation,
- Feldintelligenz.

## 18. Bester nächster Schritt

Methodik 030 wird als unveränderliche Vertragsstruktur mit isolierten Tests
implementiert. Erst nach bestandenem Lauf darf dieselbe Rezeptorfolge über
eine vorhandene transparente MCM-Projektionsbaseline bis zu einem
Feldfenster geführt werden.
