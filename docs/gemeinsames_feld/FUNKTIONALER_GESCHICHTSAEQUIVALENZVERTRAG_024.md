# Funktionaler Geschichtsäquivalenzvertrag 024

## Status

Dieser Vertrag ist eine unveränderliche Architektur- und Prüfgrenze auf
Evidenzstufe E0. Seine Runtimefreigabe lautet `CONTRACT_ONLY`.

Er führt weder einen Geschichtsträger noch eine Leserform, Feldwirkung oder
Speicherung ein.

## Ausgangspunkt

Der [Exakte lineare Zeitprojektions-Nullraum 023](EXAKTER_LINEARER_ZEITPROJEKTIONS_NULLRAUM_023.md)
zeigt, dass vollständige eindeutige Bewahrung beliebig reicher Geschichte
nicht durch eine feste endliche lineare Kennwertbank erreicht werden kann.

Damit muss die Forschungsfrage wechseln:

```text
nicht:
Welche Darstellung speichert jeden Verlauf eindeutig?

sondern:
Welche Verlaufsunterschiede verändern eine spätere lokale Feldwirkung?
```

## Definition funktionaler Äquivalenz

Zwei verschiedene Geschichten gelten nur relativ zu einer vorregistrierten
Probenfamilie als funktional äquivalent, wenn:

1. die äußere Gegenwart identisch ist,
2. Rezeptorgegenwart und schneller Feldzustand angeglichen sind,
3. ein möglicher Geschichtsträger als einzige verbleibende Zustandsdifferenz
   isoliert ist,
4. alle vollständig abgeschlossenen Feldantworten auf die registrierten Proben
   gleich sind.

Kurz:

```text
verschiedene Geschichte
+ kontrolliert gleiche Gegenwart
+ gleiche registrierte Probe
-> gleiche kausale Feldantwort
```

Diese Aussage gilt ausschließlich für die geprüfte Probenfamilie. Sie beweist
keine absolute Gleichheit aller möglichen zukünftigen Wirkungen.

## Geschichte muss nicht identisch bleiben

Funktionale Äquivalenz verlangt ausdrücklich nicht:

- identische Rohgeschichte,
- identische Segmentfolge,
- ein Sequenzarchiv,
- eindeutige Rekonstruktion der Vergangenheit,
- Bewahrung jedes messbaren Zeitunterschieds.

Verschiedene Verläufe dürfen im Organismus zusammenfallen, wenn ihre
Unterscheidung unter den kontrollierten Feldproben keine kausale Funktion
trägt.

## Definition funktionaler Verschiedenheit

Ein bloßer Antwortunterschied genügt nicht. Funktionale
Geschichtsverschiedenheit darf erst behauptet werden, wenn gemeinsam gilt:

1. dieselbe registrierte Probe erzeugt verschiedene Feldantworten,
2. der Unterschied reproduziert sich bei unabhängigem Neuaufbau,
3. er wandert beim Tausch des isolierten Geschichtsträgers mit,
4. er verschwindet bei dessen Neutralisierung,
5. er fehlt in einer angeglichenen Nullgeschichte,
6. er bleibt bei entferntem Observer unverändert.

Damit lautet der notwendige Kausalpfad:

```text
verschiedene Geschichte
-> isolierter geschichtlich entstandener Träger
-> verschiedene spätere lokale Feldantwort
```

## Pflichtkontrollen

Jede spätere Umsetzung benötigt mindestens:

- verschiedene vollständig gestützte Geschichten,
- identische Holdout-Probe,
- angeglichene Rezeptorgegenwart,
- angeglichenen schnellen Neuronenzustand,
- Isolation eines möglichen Geschichtsträgers,
- Trägertausch,
- Trägerneutralisierung,
- Nullgeschichte,
- unabhängigen Neuaufbau aller Zweige,
- vollständige Observerentfernung.

Ohne isolierten Träger kann die bestehende Runtime nur auf einen erwarteten
Nullbefund geprüft werden. Eine positive geschichtliche Funktion ist dann
nicht kausal zuordenbar.

## Verbotene Abkürzungen

Der Vertrag verbietet:

- Geschichtstemplates oder Sequenzarchive,
- semantische Klassen und Musterkennungen,
- vorgegebene Zielantworten,
- branchenspezifische Leser,
- globale Gewinner,
- Reward oder Lernregel,
- eine vorab ausgewählte Repräsentation,
- eine fest eingebaute Geschichtswirkung,
- Observer- oder Runtime-Writeback,
- vorgegebene Zieltopologie.

Eine Wirkung darf nicht dadurch entstehen, dass die Versuchskonstruktion
bereits festlegt, welche Geschichte wie gelesen werden soll.

## Verhältnis zum organischen Memory

Dieser Vertrag definiert kein Memory. Er legt nur fest, wann ein später
beobachteter Feldrest funktional als geschichtlich vermittelt gelten dürfte.

Organisches Memory wäre damit nicht:

```text
gespeicherte Vergangenheit
```

sondern höchstens:

```text
aus Weltkontakt entstandene,
gegenwärtig wirksame und wieder lösbare Feldorganisation
```

Ob eine solche Organisation im gemeinsamen MCM-Feld entstehen kann, ist
weiterhin offen.

## Evidenzgrenze

Der Vertrag selbst trägt:

```text
Prüfgrenze und Invarianten: E1
funktionale Geschichtsäquivalenz: E0
geschichtsvermittelte Feldwirkung: E0
organisches Memory: E0
```

Vorarbeiten aus historischen Projektphasen liefern hierfür keine übertragene
Evidenz.

Feldintelligenz ist kein Kriterium dieses Vertrags und keine eigene
Evidenzachse. Der Begriff bliebe höchstens eine mögliche spätere Interpretation
offener, durch eigenständige Befunde abgegrenzter Feldentwicklung.

## Stopplinie

`GF_001` bleibt geschlossen. Nicht freigegeben sind:

- ein Geschichtsträger,
- eine Leserform oder Feldgleichung,
- Zeitfenster, Zerfall oder Schwellen,
- Memory, Topologie oder Beziehung,
- Reflexion, Offline-Wirkung oder Lernen.

## Nächster Prüfpunkt

Als nächstes darf nur die erwartete Nullfunktion der vorhandenen gemeinsamen
Feldruntime vorregistriert werden:

```text
verschiedene gestützte Geschichte
+ vollständige Angleichung des vorhandenen Zustands
+ identische spätere Probe
-> identische Feldantwort
```

Dieser Lauf soll die aktuelle Scheitergrenze bestätigen. Er darf keinen neuen
Geschichtsträger ergänzen und gibt bei einem Nullbefund keine Mechanik frei.

Die [Aktuelle Feldruntime-Geschichtsnullfunktion 025](AKTUELLE_FELDRUNTIME_GESCHICHTSNULLFUNKTION_025.md)
bestätigt diese Grenze ohne Reset oder Zustandskopie. Erst nach zwei neutralen
Takten sind auch die nachlaufenden lokalen Vorfeldproben vollständig
angeglichen; danach erzeugt dieselbe Probe exakt denselben Layerzustand.
