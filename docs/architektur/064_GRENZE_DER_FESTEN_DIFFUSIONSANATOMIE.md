# Grenze der festen Diffusionsanatomie

## Zweck

Der instantane Feldfluss ist vollständig aus dem schnellen Feldzustand und
der festen lokalen Anatomie ableitbar. Dieser Audit prüft, welche der offenen
Funktionen mit dieser Anatomie überhaupt darstellbar sind.

Er führt keine veränderliche Kante, Kopplung, Ressource oder neue
Zustandsrolle ein.

## Zwei verschiedene Topologiebegriffe

### Technische Anatomie

Die heutige Runtime legt fest:

- Positionen der MCM-Neuronen;
- lokale symmetrische `sample_offsets`;
- optionale periodische Achsen;
- Rezeptordocks;
- eine einheitliche Reaktionszeit.

Diese Angaben bestimmen, welche Feldorte einander technisch erreichen. Sie
sind unveränderlicher Teil des Runtimevertrags und des Snapshots.

### Funktionale Feldorganisation

Eine funktionale Organisation wäre dagegen eine durch Weltgeschichte
entstandene unterschiedliche Wirksamkeit innerhalb dieses Raums. Sie müsste
entstehen, alte Wirkung verlieren und unter neuer Geschichte anders wirksam
werden können.

Technische Nachbarschaft und funktionale Beziehung dürfen deshalb nicht
gleichgesetzt werden.

## Was die feste Diffusion tatsächlich kann

Die gegenwärtige Feldtransition kann:

1. Weltkontakt lokal aufnehmen;
2. Aktivierung über feste Nachbarschaften ausbreiten;
3. räumlich unterschiedliche schnelle Feldlagen bilden;
4. diese Feldlagen ohne Kontakt relaxieren lassen;
5. neuen Kontakt nach der Relaxation wieder aufnehmen.

Während eine Feldlage besteht, können verschiedene aktuelle Aktivierungen zu
verschiedenen weiteren Trajektorien führen. Das ist reale gegenwärtige
Feldwirkung.

## Was sie nicht kann

Jede technische Nachbarschaft besitzt zu jedem Zeitpunkt dieselbe
Leitbedingung:

```text
Nachbarschaft vorhanden -> Kopplungsrate r
Nachbarschaft nicht vorhanden -> keine Kopplung
```

Der momentane Fluss kann null werden, wenn benachbarte Aktivierungen gleich
sind. Dadurch ist die Kante aber nicht gelöst. Bei einem neuen Unterschied
wirkt sofort wieder dieselbe feste Kopplung.

Die Runtime enthält keinen Zustand dafür, dass:

- eine frühere lokale Einbindung eine bestimmte Wirkung erworben hat;
- diese Wirkung ihre funktionale Bindung vollständig verliert;
- dadurch etwas lokal freigegeben wird;
- neue Geschichte dieselbe Möglichkeit anders organisiert.

## Abgleich der drei offenen Funktionen

### 1. Freigabefunktion

```text
schnelle Aktivierung kann abklingen: ja
technische Kopplung kann verschwinden: nein
gebundene Beziehungswirkung kann gelöst werden: nicht vorhanden
Ressource kann freigegeben werden: keine Ressource vorhanden
```

Relaxation ist daher keine Beziehungsfreigabe. Sie löscht nur die schnelle
Feldlage innerhalb unveränderter Anatomie.

### 2. Wiederbindungsfunktion

```text
neuer Kontakt kann wieder eintreten: ja
neue Aktivierung kann sich ausbreiten: ja
freigewordene Beziehung kann anders binden: nicht darstellbar
```

Die erneute Ausbreitung nutzt exakt dieselben technischen Wege. Sie zeigt
Offenheit für neuen Weltkontakt, aber keine Wiederbindung einer Organisation.

### 3. Funktionswechsel

```text
verschiedener aktueller Schnellzustand -> andere Feldtrajektorie: ja
verschiedene Geschichte nach Schnellzustandsangleichung
-> andere Feldtrajektorie: nein
```

Die bestehende Anatomie trägt damit aktuellen Feldkontext, aber keinen
geschichtlich fortbestehenden Funktionswechsel.

## Mathematische Grenze

Bei fester Anatomie und fester Reaktionszeit ist die kontaktfreie schnelle
Transition ein fester linearer Operator. Für einen gegebenen
Aktivierungszustand ist ihre weitere lokale Wirkung eindeutig bestimmt.

```text
gleiche activation
+ gleiche afterimage
+ gleiche Anatomie
+ gleiche weitere Rezeptorevidenz
-> gleiche weitere Feldtrajektorie
```

Der Fluss-Redundanzbefund bestätigt diese Grenze direkt. Eine andere
Geschichte kann nach Angleichung der schnellen Rollen nicht mehr kausal
wirken.

## Bedeutet das veränderliche Kanten?

Nein. Aus dem Scheitern der festen Diffusionsanatomie folgt nicht automatisch,
dass technische Kanten lernen oder wachsen müssen.

Eine veränderliche Kante wäre bereits:

- eine zusätzliche Zustandsrolle;
- eine programmierte Bildungsregel;
- eine programmierte Wirkungsregel;
- eine programmierte Lösungsregel.

Damit würde die gesuchte Organisation leicht in die Mechanik geschrieben.
Die zuvor verworfene Familie adaptiver Kanten bleibt geschlossen.

Ebenso wenig ist belegt, dass eine unabhängige Knotenspur, Ressource,
Empfänglichkeit oder Flussakkumulation die richtige Darstellung wäre.

## Tragfähiger Negativbefund

Die feste Diffusionsanatomie verhindert nicht jede dynamische Feldform. Sie
verhindert innerhalb des heutigen Zustandsvertrags jedoch eine
geschichtsabhängige Änderung der lokalen Übertragungsbedingung nach
Angleichung des schnellen Zustands.

Damit gilt:

```text
gegenwärtige Feldwahrnehmung:              vorhanden
schneller Feldkontext:                     vorhanden
geschichtlich entwickelte Organisation:   nicht darstellbar
natürliche funktionale Lösung:             nicht darstellbar
andere Wiederbindung:                      nicht darstellbar
```

## Sättigungsgrenze

Die vorhandene Runtime und ihre schnellen Zustände sind für diese Frage
ausgeschöpft. Weitere Umbenennungen von Aktivierung, Nachhall, Gradient oder
Fluss erzeugen keinen neuen Informationsgehalt.

Gleichzeitig wählt der bisherige Befund keine zulässige neue
Memory-Darstellung aus. Ein weiterer mechanischer Kandidat wäre derzeit eine
unbegründete Programmierung.

## Freigabegrenze

```text
Grenze der festen Anatomie bestimmt:       ja
Relaxation als Beziehungsfreigabe:         nein
erneuter Kontakt als Wiederbindung:        nein
veränderliche technische Kante nötig:      nicht gezeigt
neue Zustandsrolle ausgewählt:             nein
Runtime-Erweiterung freigegeben:            nein
```

## Ergebnis der Substratklärung

Die
[physische Mindestanforderung](065_PHYSISCHE_MINDESTANFORDERUNG_ORGANISCHES_MEMORY_SUBSTRAT.md)
ist als begrenzte, lokal feldgetriebene und funktional reversible
Pfadabhängigkeit bestimmt. Dabei wurde die Flussgrenze präzisiert: Der
momentane Fluss ist kein zusätzlicher Zustand, kann aber eine lokale Ursache
für die Verformung eines noch nicht bestimmten Substrats sein.

## Nächster Schritt

Vor jeder Implementierung wird geprüft, ob ein einzelner begrenzter lokaler
Substratzustand diesen Lebenszyklus überhaupt ohne Leaky-Spur,
Schwellenautomat oder adaptive Kante tragen kann.
