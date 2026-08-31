# S2-HO: Statische rezeptorrealistische Kontextkonflikt-Fixture

Status: `STATIC_FIXTURE_RECONSTRUCTED_IMPLEMENTATION_LOCKED`

## Ziel und Grenze

S2-HO ersetzt ausschliesslich die in S2-HM gebundene, unter der aktiven
Funktionsschwelle nicht erreichbare Kandidaten- und Probengeometrie. Die
Zwei-Bereich-Aufgabe, die Schwelle `44/765`, die Rollenregeln und die
Falsifikationsbedingungen bleiben unveraendert.

Es wurden keine Fixtures implementiert, keine Bilder analysiert, keine
Zustandsfunktionen aufgerufen und keine Tests oder Laeufe ausgefuehrt.

## Erzeugbare visuelle Bilder

Die vorhandene visuelle Geometrie besteht aus einem `uint8`-Bild mit
`120 x 80 x 3` Werten und einem Raster aus drei Spalten und zwei Zeilen. Ein
konstanter `40 x 40`-Block je Rasterzelle und Kanal erzeugt daher exakt einen
der 18 gebundenen Rezeptorwerte.

Die folgenden Tupel geben die 18 Blockwerte in Rezeptorreihenfolge als
`uint8`-Werte an. Jeder Wert wird innerhalb seines Blocks konstant gesetzt.

```text
V0 = (255,  0,  0,255,255,  0,  0,255,255,  0,  0,255,255,  0,  0,255,255,  0)
V1 = (255,255,  0,  0,255,  0,  0,255,255,  0,  0,255,255,  0,  0,255,255,  0)
Q0 = (255,127,  0,128,255,  0,  0,255,255,  0,  0,255,255,  0,  0,255,255,  0)
Q1 = (255,128,  0,127,255,  0,  0,255,255,  0,  0,255,255,  0,  0,255,255,  0)
```

`V0` und `V1` unterscheiden sich ausschliesslich an den maskierten
Positionen `1` und `3`. Dort werden `0` und `255` vertauscht. Sichtbare
Positionen, Werthistogramm und Gesamthelligkeit bleiben gleich.

`Q0` und `Q1` sind vollstaendige read-only Rezeptorproben. Die Werte `127`
und `128` sind reale `uint8`-Blockwerte und werden vom vorhandenen Rezeptor
als `127/255` und `128/255` ausgegeben. Die beiden Proben spiegeln die
unvermeidliche Ein-Byte-Asymmetrie gegeneinander.

## Exakte visuelle Abstaende

Fuer die normalisierte mittlere L1-Distanz ueber 18 Werte gilt:

```text
d(V0,V1) = (1 + 1) / 18
          = 1/9
          = 85/765

d(Q0,V0) = d(Q1,V1)
          = (127/255 + 127/255) / 18
          = 127/2295

d(Q0,V1) = d(Q1,V0)
          = (128/255 + 128/255) / 18
          = 128/2295

tau       = 44/765
          = 132/2295
```

Damit sind alle geforderten Relationen erfuellt:

```text
127/2295 <= 132/2295
128/2295 <= 132/2295

44/765 < 85/765 <= 88/765
```

Die kleinere Probedistanz zeigt jeweils zum spaeter gebildeten
`A_RECENT`-Kandidaten. Ueber beide Richtungen sind die Distanzen gespiegelt
balanciert; keine Richtung erhaelt einen systematischen Quantisierungsvorteil.

## Auditive Trennung der Bildungsspuren

Die visuellen Kandidaten liegen mit `1/9` innerhalb der nativen
TSPM-Fast-Schwelle `1/5`. Damit die spaetere A-Exposition nicht denselben
Fast-Slot und dadurch B-Slow aktualisiert, bleiben zwei getrennte
synthetische auditive Rezeptorzustaende gebunden:

```text
M0 = (1,1,1,1,0,0,0,0)
M1 = (1,1,1,0,1,0,0,0)
MQ = (1,1,1,1/2,1/2,0,0,0)
```

Es gilt:

```text
d(M0,M1) = 1/4 > 1/5
d(MQ,M0) = d(MQ,M1) = 1/8 <= 1/5
```

Die auditive Trennung verhindert einen gemeinsamen Fast-Match bei der
fuenften Exposition. Der dabei entstehende partielle visuelle Match ist im
vorhandenen TSPM-Vertrag ein dokumentierter Konfliktbefund; ohne gemeinsamen
audiovisuellen Match wird dennoch ein separater Fast-Slot erzeugt und keine
Slow-Konsolidierung ausgeloest.

`MQ` ist ein synthetischer auditiver Rezeptorzustand, kein analysiertes
Audiosignal. Diese Rollenbezeichnung muss in einer spaeteren Fixture erhalten
bleiben.

## Korrigierte Bildungsgeschichten

Beide Geschichten beginnen mit frischen Composite-, B4- und TSPM-Zustaenden.

### H0

```text
Schritte 1-4: (V1,M1) viermal
Schritt 5:    (V0,M0) einmal
Vollprobe:    (Q0,MQ)
```

- `V1/M1` erreicht durch drei konsolidierende Updates Slow-Support `3` und
  bildet `B_STABLE`.
- `V0/M0` erzeugt einen zweiten Fast-Slot und den juengsten B4-Eintrag.
- Die Vollprobe liegt visuell und auditiv innerhalb der Funktionsschwellen
  beider Inhalte.
- B4 und der funktionale Fast-Vergleich waehlen wegen `127/2295` gegen
  `128/2295` eindeutig `V0/M0` als A-Inhalt.
- Der einzige stabile Slow-Prototyp bleibt `V1/M1` als B-Inhalt.

### H1

```text
Schritte 1-4: (V0,M0) viermal
Schritt 5:    (V1,M1) einmal
Vollprobe:    (Q1,MQ)
```

- `V0/M0` erreicht Slow-Support `3` und bildet `B_STABLE`.
- `V1/M1` wird der juengste B4- und getrennte Fast-Inhalt.
- Die gespiegelte Probe waehlt `V1/M1` als A-Inhalt.
- Der stabile Slow-Prototyp bleibt `V0/M0` als B-Inhalt.

Nach Schritt 5 ist der B-Fast-Slot nur einen nicht ausgewaehlten Schritt alt.
Er kann bei `expire_after_exposures = 8` nicht ablaufen. Zwei belegte
Fast-Slots unterschreiten die Kapazitaet `3`. Da die A-Exposition keinen
gemeinsamen audiovisuellen Fast-Match erzeugt, ruft sie PPB-1 nicht auf und
kann B weder aktualisieren noch verdraengen.

## Vier rollenadressierte Faelle

Alle Faelle verwenden dieselbe spaetere maskierte Probeform. Nur die
ausdruecklich gebundene Rolle darf die neun maskierten Positionen fuellen.

| Fall | Geschichte | `A_RECENT` | `B_STABLE` | angeforderte Rolle |
|---|---|---|---|---|
| HO-01 | H0 | V0/M0 | V1/M1 | `A_RECENT` |
| HO-02 | H0 | V0/M0 | V1/M1 | `B_STABLE` |
| HO-03 | H1 | V1/M1 | V0/M0 | `A_RECENT` |
| HO-04 | H1 | V1/M1 | V0/M0 | `B_STABLE` |

Die zwei Faelle je Geschichte verwenden dasselbe validierte A/B-Bundle. Sie
duerfen keine zweite Bildung und keine neue Kontextprobe ausloesen.
Verbraucher und unabhaengige direkte Rollenbaseline erhalten je Fall
identische Eingaben und Funktionsbudgets.

## Quellen- und Rollenbindung

Eine spaetere Materialisierung muss folgende vorwaertsgerichtete Bindung
erhalten:

```text
uint8-Blockbild und synthetischer auditiver Rezeptorzustand
-> Rezeptor- und Envelopebeleg
-> gebundener Formationseingang
-> atomarer Composite-Schritt
-> gebundene Vollprobe
-> S2-FS-read-only-Finding
-> S2-GC-Bundle
-> S2-GI-A/B-Projektion
-> explizite Rollenbindung
-> Verbraucher oder unabhaengige Baseline
-> getrennte Auswertung
```

Der Ausfuehrungspfad darf keine Fallkennung, Sollrolle oder Zielwerte sehen.
Die Rollenbindung benennt nur `A_RECENT` oder `B_STABLE`; sie darf keinen
Kandidaten suchen, gewichten oder erzeugen. `TSPM_FAST` bleibt interne
A-Evidenz und darf den oeffentlichen B4-Inhalt nicht ersetzen.

## Statische Entscheidung

Die rezeptorrealistische Fixture ist unter den bestehenden Schwellen
materialisierbar:

- beide Kandidaten unterscheiden sich auf zwei maskierten Positionen;
- ihr Abstand liegt strikt ueber `tau` und nicht ueber `2*tau`;
- beide gespiegelten Vollproben liegen zu beiden Kandidaten innerhalb `tau`;
- alle visuellen Werte stammen aus konkreten `uint8`-Blockbildern;
- B erreicht vor A stabilen Support `3`;
- A bleibt gleichzeitig als juengster B4- und separater Fast-Inhalt erhalten;
- A loest keine weitere Slow-Konsolidierung aus;
- beide Konfliktrichtungen und alle vier Rollenfaelle sind strukturell
  budgetgleich.

S2-HO veraendert keine Schwelle, Speichermechanik oder Aufgabenentscheidung.
Die Implementierung und Ausfuehrung bleiben gesperrt. Der naechste zulassbare
Schritt ist ein rein statischer Materialisierungs- und Nichtzirkularitaetsaudit
dieser korrigierten Fixture gegen die konkreten Datentypen und Validatoren.
