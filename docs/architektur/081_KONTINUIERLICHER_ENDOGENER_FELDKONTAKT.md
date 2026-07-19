# Kontinuierlicher endogener Feldkontakt

## Status

Architekturvertrag und neutrale technische Rezeptorgrenze auf Evidenzstufe E0.

Es wird kein biologischer Körper simuliert. Insbesondere werden weder
Stimmung, Müdigkeit, Schmerz noch künstliches Rauschen erzeugt.

## Ausgangspunkt

Kamera und Mikrofon tragen äußeren Weltkontakt. Bei Dunkelheit und Stille
kann ihre aktuelle Wirkung jedoch weitgehend verschwinden. Ein biologischer
Organismus hat zusätzlich fortlaufenden Kontakt mit seinem eigenen
körperlichen Zustand.

Für das Projekt wird dieser fehlende Anteil als **endogener Eigenkontakt**
bezeichnet:

```text
äußere Rezeptoren  --\
                      -> neutraler Rezeptorenverteiler -> gemeinsames MCM-Feld
innere Rezeptoren  --/
```

Der Eigenkontakt ist kein separates inneres MCM-Feld. Er ist eine weitere
lokale Herkunft innerhalb desselben Organismusfeldes.

## Abgrenzung zum Rauschen

Eine dauernde Feldanregung darf nicht durch einen programmierten
Zufallsgenerator ersetzt werden. Zufall würde lediglich eine technische
Quelle hinzufügen und könnte fälschlich als innere Dynamik erscheinen.

Zulässige Quellen sind zunächst ausschließlich:

- tatsächlich gemessene innere oder gerätenahe Zustände;
- kontrolliert simulierte Werte in einer ausdrücklich gekennzeichneten
  Testwelt;
- lokal und zeitlich abgeschlossene Rezeptorzustände.

Aus diesen Werten werden keine Kategorien wie warm, kalt, angespannt, müde
oder angenehm abgeleitet. Solche Bedeutungen dürften erst aus späterer
Weltteilnahme entstehen.

## Technischer Vertrag

`EndogenousReceptorSurface` ist eine offene, zustandslose Rezeptorfläche. Sie
besitzt nur:

- eine technische Quellenidentität;
- eine explizite Rezeptorgeometrie;
- lokale Trägeridentitäten.

Jeder Kontakt muss vollständig von außen übergeben werden. Die Rezeptorfläche
speichert keinen vorherigen Wert, hält bei einer Lücke keinen letzten Zustand
und ergänzt keine Schwankung.

Der abgeschlossene Kontakt wird als regulärer `ReceptorContactFrame` mit der
Herkunft `endogenous.<source_id>` ausgegeben. Danach gelten unverändert:

- derselbe Rezeptorenverteiler;
- dieselbe Dockgrenze;
- dieselbe gemeinsame Organismusuhr;
- dieselbe MCM-Neuronenschicht;
- dieselbe atomare Feldübergabe.

Es existiert kein Sonderweg vom Eigenkontakt direkt zu Neuron, Memory,
Kontaktmaterial oder Reflexion.

## Kontinuität

`audit_endogenous_contact_continuity` beobachtet ausschließlich, ob eine
Folge derselben Quelle zeitlich lückenlos ist. Eine Lücke wird gemeldet, aber
nicht gefüllt.

```text
gemessene Lücke
!= Nullkontakt
!= gehaltener letzter Kontakt
!= ausgeschaltetes gemeinsames Feld
```

Kontinuierlicher Eigenkontakt ist daher eine Eigenschaft der realen Quelle
und ihrer Abtastung, keine durch die Runtime erfundene Daueraktivität.

## Verhältnis zu Feldtopologie und Memory

Endogener Eigenkontakt kann später eine reale Feldursache sein. Er ist aber
weder bereits organisches Memory noch automatisch die Ursache einer
Materialbewegung.

Vor einer solchen Interpretation muss getrennt werden:

1. aktuelle endogene Rezeptorwirkung;
2. schneller neuronaler Nachhall;
3. bereits entstandene Feldorganisation;
4. mögliche spätere reflexive Rückwirkung.

Eine länger getragene Gesamtlage darf erst dann als entwickelte innere
Mitprägung gelten, wenn sie nicht vollständig aus aktuellen Eingangswerten
und schnellem Nachhall folgt.

## Implementierungsstand

Umgesetzt und geprüft sind:

- eine offene zustandslose Eigenkontakt-Rezeptorfläche;
- verlustfreie signierte lokale Werte;
- Weitergabe über den vorhandenen neutralen Rezeptorenverteiler;
- Wirkung im gemeinsamen MCM-Feld ohne Sonderpfad;
- passive Erkennung zeitlicher Lücken;
- Nullkontrolle gegen gehaltene Werte und erzeugtes Rauschen.

Nicht umgesetzt sind:

- reale innere Sensorhardware;
- Auswahl biologischer Messgrößen;
- künstliche Stimmung oder Grundaktivierung;
- Rückwirkung auf Kontaktmaterial;
- Memory-, Reflexions- oder Sprachwirkung.

## Nächster Schritt

Als Nächstes wird eine kleine kontrollierte endogene Testquelle benötigt, die
langsame und schnelle Veränderungen vorgibt, ohne sie semantisch zu
bezeichnen. Erst damit kann geprüft werden, wie äußerer und endogener Kontakt
im selben Feld gleichzeitig wirken.

Der passive radiale Flussvertrag bleibt weiterhin notwendig. Eine endogene
Feldwirkung darf jedoch nicht ungeprüft als Materialgeschwindigkeit
eingesetzt werden.
