# Minimale passive Weltfamilie: verdeckte Fortsetzung

## Status

Vorregistrierter Welt- und Beobachtungsvertrag auf
`E1 / WORLD_FAMILY_PREREGISTERED`.

```text
Weltprozess:                  vorregistriert
Geschichtszweige:             vorregistriert
Angleichungsgrenze:           vorregistriert
Holdoutfortsetzung:           vorregistriert
Null- und Leckkontrollen:     vorregistriert
Memory-Rolle:                 nicht vorhanden
Runtime-Erweiterung:          gesperrt
Ausführung:                   noch offen
```

Die Weltfamilie operationalisiert die
[weltbegründete Relevanzgrenze](054_WELTBEGRUENDETE_RELEVANZGRENZE.md).
Sie prüft ausschließlich, ob eine vergangene lokale Weltgeschichte nach
Angleichung des schnellen Feldzustands Information über eine noch unbekannte
spätere Rezeptorfortsetzung trägt.

Sie prüft noch nicht, ob der Organismus diese Information bewahrt.

## 1. Forschungsfrage

```text
verschiedene sichtbare Anfluggeschichte
+ gegenwärtig identische verdeckte Rezeptorlage
+ vollständig angeglichener schneller Feldzustand
-> unterschiedliche spätere sichtbare Fortsetzung aus derselben Weltregel?
```

Ist diese Frage positiv beantwortet, existiert in der Welt eine Information,
für die ein späteres Memory funktional relevant sein könnte.

## 2. Warum eine verdeckte Bewegung

Eine fortlaufende lokale Bewegung besitzt einen inneren Weltzustand, der
während einer Verdeckung nicht direkt am Rezeptor sichtbar ist.

```text
sichtbarer Anflug
-> verdeckter Verlauf
-> sichtbarer Austritt
```

Während der Verdeckung können aktuelle Rezeptorlage, `activation` und
`afterimage` zwischen zwei gespiegelten Geschichten vollständig gleich
werden. Die spätere Weltfortsetzung bleibt trotzdem durch den zuvor
beobachtbaren Verlauf bestimmt.

Damit wird weder ein Objektname noch eine gewünschte Antwort benötigt.

## 3. Technische Weltgeometrie

Die kleinste Grundwelt ist eine eindimensionale lokale Bahn innerhalb einer
normalen visuellen Rezeptorfläche.

```text
sichtbar links | verdeckter Bereich | sichtbar rechts
```

Verbindliche Eigenschaften:

- mindestens zwei sichtbare lokale Positionen vor der Verdeckung;
- mindestens zwei sichtbare lokale Positionen nach der Verdeckung;
- ein zusammenhängender verdeckter Bereich;
- gleiche Bahnlänge für beide Bewegungsrichtungen;
- gleiche Anzahl und Dauer aller Weltframes;
- ein einzelner lokaler Reiz ohne Objekt-, Richtungs- oder Episodenlabel;
- Übergabe über die vorhandene visuelle Rezeptorfläche und den normalen Dock.

Die Verdeckung ist eine Eigenschaft der simulierten Außenwelt. Sie ist kein
Runtime-Signal und kein besonderer Kontaktzustand.

## 4. Weltzustand und Dynamik

Nur der äußere Weltgenerator kennt:

```text
Position q(t)
lokale Bewegungsrichtung d
Geschwindigkeit v
Verdeckungsmaske O
```

Der Reiz entwickelt sich während sichtbarer und verdeckter Abschnitte nach
derselben vorregistrierten lokalen Fortsetzungsregel:

```text
q(t + 1) = q(t) + d * v
```

Die visuelle Rezeptorquelle erhält nur die sichtbare Projektion:

```text
q(t) außerhalb O -> lokaler sichtbarer Kontakt
q(t) innerhalb O -> kein sichtbarer Kontakt des Reizes
```

`q`, `d`, `v` und `O` werden nicht an Rezeptor, Dock, Feld oder Neuron
übergeben.

## 5. Gespiegelte Geschichtszweige

Es gibt zwei kausal symmetrische Hauptzweige:

```text
H+ : sichtbarer Anflug von links nach rechts
H- : sichtbarer Anflug von rechts nach links
```

Beide Zweige besitzen:

- dieselbe Reizstärke;
- dieselbe Geschwindigkeit;
- dieselbe sichtbare Kontaktanzahl;
- dieselbe Verdeckungsdauer;
- dieselbe Gesamtenergie;
- dieselbe Organismuszeitgrenze;
- dieselbe technische Framezahl.

Sie unterscheiden sich nur durch die räumlich gespiegelte abgeschlossene
Weltgeschichte.

## 6. Angleichungsphase

Nach dem letzten sichtbaren Anflugkontakt bleibt der Reiz lange genug
verdeckt, damit die vorhandene schnelle Runtime vollständig kollidiert.

Die Prüfschwelle ist nicht eine vorab angenommene Anzahl leerer Frames,
sondern die exakte Zustandsbedingung:

```text
vollständige activation-Vektoren gleich
vollständige afterimage-Vektoren gleich
vollständige bekannte MCMNeuronLayer-Zustände gleich
keine offenen transienten Rezeptorabschlüsse
gleiche Organismuszeitgrenze
```

Erst die erste Grenze, an der alle Bedingungen gemeinsam gelten, ist die
zulässige Vergleichsgrenze `t*`.

Falls die Zustände vor dem Austritt nicht vollständig kollidieren, ist diese
Weltgeometrie für die Relevanzprüfung ungeeignet und muss vor einem Lauf
vergrößert werden. Es darf keine manuelle Zustandskopie und keinen Reset geben.

## 7. Holdoutfortsetzung

Nach `t*` setzt der äußere Weltprozess seine bereits laufende Bewegung fort.

```text
H+ -> neuer sichtbarer Austritt auf der rechten Seite
H- -> neuer sichtbarer Austritt auf der linken Seite
```

Die Austrittsframes wurden dem Organismus während der Anfluggeschichte nicht
angeboten. Sie entstehen erst nach `t*`.

Der Holdout besteht nicht aus dem erneuten Abspielen derselben konkreten
Anflugframes. Er verwendet neue Kombinationen aus:

- anderer Bahnübersetzung innerhalb der Rezeptorfläche;
- anderer zulässiger Zeile;
- anderer technischer Farbkanallage;
- anderer Reizstärke innerhalb des ungeclippten Bereichs;
- anderer Verdeckungsbreite oberhalb der Angleichungsgrenze;
- anderer zulässiger Geschwindigkeit bei gleicher lokaler Dynamik.

Mindestens eine dieser Größen muss sich in jedem Holdoutlauf von allen
Bildungsläufen unterscheiden.

## 8. Keine Zukunftsinformation im Organismus

Vor dem sichtbaren Austritt darf keine der folgenden Informationen in der
Runtime vorhanden sein:

- Bewegungsrichtung;
- Geschwindigkeit;
- verdeckte Position;
- Austrittsseite;
- Weltseed;
- Zweig-ID;
- Verdeckungsstatus als Sonderflag;
- erwartete Fortsetzung;
- Holdoutzugehörigkeit.

Der Organismus erhält ausschließlich die normalen abgeschlossenen
Rezeptorkontakte.

## 9. Passive Beobachtungsgrößen

Der Forschungsobserver darf nach Abschluss jedes Laufs erfassen:

```text
vollständige Rezeptortrajektorie
Zeitgrenze t*
vollständigen schnellen Feldzustand an t*
erste neue sichtbare Kontaktposition nach t*
vollständige kausale Feldtrajektorie nach dem Austritt
Weltparameter ausschließlich zur Leck- und Symmetrieprüfung
```

Diese Größen werden nicht zurückgeschrieben.

Die primäre Weltmessung lautet:

```text
trägt die sichtbare Anfluggeschichte Information
über die erste neue sichtbare Rezeptorfortsetzung nach t*?
```

Die Feldantwort ist in dieser Stufe nur Kontroll- und Nullmessung. Es wird noch
keine geschichtsabhängige Feldwirkung erwartet.

## 10. Vorregistrierte Weltgruppen

### W0: Gespiegelte tragende Welt

Die lokale Bewegungsrichtung bleibt während der Verdeckung erhalten. Anflug
und Austritt sind dadurch kausal verbunden.

### W1: Permutierte Fortsetzung

Die Austrittsfortsetzung wird vor dem Gesamtlauf unabhängig vom Anflugzweig
permutiert. Randhäufigkeiten, Energie, Zeit und Geometrie bleiben erhalten.

Erwartung:

```text
H trägt in W0 Information über W+
H trägt in W1 keine Information über W+
```

### W2: Aktuelle Sichtbarkeit

Der Reiz bleibt bis unmittelbar vor dem Austritt sichtbar. Diese Gruppe zeigt,
dass eine triviale aktuelle Rezeptorspur die Fortsetzung unterscheiden kann.
Sie ist keine Memory-Prüfung.

### W3: Zu kurze Verdeckung

Der Austritt beginnt, bevor der schnelle Feldzustand vollständig kollidiert.
Diese Gruppe quantifiziert die Erklärung durch `activation` und `afterimage`
und ist für den Relevanznachweis ausgeschlossen.

### W4: Kontaktfreie Nullwelt

Es gibt weder sichtbaren Anflug noch Austritt. Sie prüft technische
Eigenaktivität, Zeit- und Observerlecks.

## 11. Symmetrie- und Transformationskontrollen

Die vollständige Weltfamilie wird vor dem Lauf transformiert durch:

- Links-rechts-Spiegelung;
- zulässige räumliche Übersetzung;
- Zeilenwechsel;
- technische Umordnung der Erzeugungsreihenfolge;
- Umkehr der Zweigreihenfolge;
- unabhängigen Neuaufbau jedes Laufs.

Nach kanonischer Rückabbildung muss die Weltabhängigkeit mit der Transformation
wandern. Eine feste bevorzugte Dockposition entwertet den Befund.

## 12. Pflichtbaselines

Die spätere Auswertung muss mindestens enthalten:

```text
B0  aktuelle Rezeptorlage an t*
B1  vollständige activation an t*
B2  vollständiger afterimage an t*
B3  Organismuszeit und Framezahl
B4  mehrere feste Leaky-Spuren
B5  lokale Übergangszähler
B6  fester endlicher Bewegungsautomat
B7  exakter Sequenz- oder Templatevergleich
B8  Weltseed, Zweig-ID und Generatorparameter als Leckbaseline
```

Erwartet wird:

- B0 bis B3 können W0 an `t*` nicht unterscheiden;
- B4 kollidiert nach ausreichend langer Verdeckung;
- B5 bis B7 können Teile oder die gesamte Weltregel erklären;
- B8 kann die Welt trivial unterscheiden und muss aus der Runtime vollständig
  ausgeschlossen bleiben.

Dass B6 die Weltfortsetzung vorhersagen kann, entwertet die Weltfamilie nicht.
Es zeigt nur, dass ein späterer Memory-Kandidat mindestens gegen einen festen
Bewegungsautomaten abgegrenzt werden muss.

## 13. Abnahmekriterien

Die Weltfamilie trägt ihre enge Funktion nur, wenn gemeinsam gilt:

1. H+ und H- sind vor `t*` tatsächlich verschiedene Rezeptorgeschichten.
2. Der vollständige bekannte schnelle Feldzustand ist an `t*` exakt gleich.
3. Die erste neue sichtbare Fortsetzung liegt räumlich verschieden.
4. Der Unterschied folgt in W0 aus derselben lokalen Weltregel.
5. Die Abhängigkeit verschwindet in W1.
6. Spiegelung und Übersetzung tragen kanonisch denselben Befund.
7. Kein verbotener Weltparameter erreicht Rezeptor, Dock oder Feld.
8. Jeder Holdoutlauf enthält eine neue konkrete Rezeptorfolge.
9. Observerreihenfolge und Observerentfernung verändern die Runtime nicht.
10. Vollständiger Neuaufbau reproduziert den Weltbefund.

## 14. Scheiterkriterien

Die Weltfamilie scheitert als Relevanzgrundlage, wenn:

- `activation` oder `afterimage` an `t*` noch verschieden sind;
- ein Reset oder eine manuelle Zustandskopie nötig ist;
- die Fortsetzung nur durch Zweig-ID, Zeit oder Seed unterschieden wird;
- dieselben konkreten Frames in Bildung und Holdout wiederholt werden;
- W1 weiterhin dieselbe Abhängigkeit zeigt;
- eine technische Vorzugsposition das Ergebnis bestimmt;
- der Observer die Welt oder Runtime beeinflusst;
- die Austrittsseite erst nach Sichtung der Feldantwort gewählt wird.

## 15. Erwarteter Befund

Für die Welt selbst wird erwartet:

```text
verschiedene Anfluggeschichte
+ identische verdeckte Gegenwart
-> verschiedene spätere sichtbare Fortsetzung
```

Für die bestehende Runtime wird erwartet:

```text
vollständig angeglichener schneller Feldzustand
+ keine Memory-Rolle
-> vor dem neuen Austrittskontakt keine Feldunterscheidung
```

Dieser gemeinsame Befund wäre kein Versagen. Er würde erstmals sauber zeigen:

> Die Welt bietet eine relevante geschichtliche Unterscheidung an, während der
> heutige Organismus nach Lösung seiner schnellen Spur keinen Träger dafür
> besitzt.

## 16. Aussagegrenze

Ein positiver Lauf trägt höchstens:

- die nicht tautologische Weltabhängigkeit;
- die Eignung der Weltfamilie als spätere Memory-Prüfgrundlage;
- die Null des vorhandenen schnellen Feldes;
- die Mindeststärke der notwendigen Gegenmodelle.

Er trägt nicht:

- organisches Memory;
- entwickelte Feldtopologie;
- semantische Resonanz;
- Reflexion;
- Wiedererkennen eines Objekts;
- Vorhersagefähigkeit des Organismus;
- Feldintelligenz.

## Freigabegrenze

```text
Weltfamilie konzeptionell vorregistriert: ja
vorhandener Rezeptorpfad verwendbar:      ja
Weltgenerator implementiert:              nein
passiver Weltlauf freigegeben:            ja
Memory-Rolle freigegeben:                 nein
Feldmechanikänderung freigegeben:         nein
Runtime-Erweiterung freigegeben:           nein
```

## Nächster Schritt

Als Nächstes wird ausschließlich der äußere Weltgenerator und der passive
Welt-/Leckobserver implementiert.

Der Lauf darf:

- vorhandene visuelle Rezeptor- und Feldpfade unverändert verwenden;
- den exakten schnellen Kollisionspunkt `t*` bestimmen;
- W0 bis W4 und B0 bis B8 auswerten;
- Berichte lokal und kompakt halten.

Er darf keine Memory-Rolle, Lernregel, Feldtopologie, semantische Auswertung
oder Rückwirkung ergänzen.
