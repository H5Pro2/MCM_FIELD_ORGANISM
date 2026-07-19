# Minimale kontinuierliche Zwei-Beziehungs-Weltfamilie

## Status

Vorregistrierter Welt- und Beobachtungsvertrag auf
`E1 / CONTINUOUS_TWO_RELATION_WORLD_PREREGISTERED`.

```text
kontinuierlicher Weltstrom:         vorregistriert
Fortsetzungsbeziehungen R0 und R1: vorregistriert
unbezeichneter Beziehungswechsel:  vorregistriert
Erfahrungsstufen 0/1/2/4/8:        vorregistriert
Kontrollen K0 bis K7:              vorregistriert
Baselinevertrag B0 bis B9:        vorregistriert
äußerer Weltgenerator:             implementiert
passive Observer:                  implementiert
Baselineausführung B0 bis B9:     noch offen
Memory-Rolle:                      nicht vorhanden
Runtime-Erweiterung:               gesperrt
```

Diese Weltfamilie operationalisiert die
[nichtstationäre Weltbeziehungsgrenze](056_NICHTSTATIONAERE_WELTBEZIEHUNGSGRENZE.md).
Sie prüft eine äußere Weltanforderung, noch keine innere Memory-Lösung.

## 1. Forschungsfrage

```text
eine reale Fortsetzungsbeziehung R0
-> wiederholte lokale Weltkontakte
-> unbezeichneter äußerer Wechsel zu R1
-> neue reale R1-Kontakte
-> spätere neue R1-Fortsetzung
```

Die Weltfamilie soll getrennt zeigen:

1. `R0` trägt vor dem Wechsel eine reale lokale Fortsetzungsabhängigkeit.
2. Der Wechsel ist aus keinem aktuellen technischen Metadatum ablesbar.
3. Ohne neue `R1`-Erfahrung besteht keine Grundlage für eine innere Änderung.
4. Mit neuer `R1`-Erfahrung wird `R1` für spätere Fortsetzungen relevant.
5. Frühere `R0`-Geschichte liefert bei festgehaltener `R1`-Geschichte keine
   zusätzliche Zukunftsinformation.
6. Eine spätere Rückkehr zu `R0` wird erst durch neue reale `R0`-Erfahrung
   erneut getragen.

## 2. Ein Weltkontakt

Ein Kontakt ist eine einzige kausal fortlaufende Außenweltbewegung:

```text
zwei sichtbare Anflugkontakte
-> physischer Verlauf hinter einer Verdeckung
-> zwei sichtbare Austrittskontakte
-> gewöhnlicher kontaktarmer Zwischenraum
```

Es gibt keinen Episodenreset. Der nächste Kontakt beginnt auf demselben
Organismuszustand, auf dem der vorherige endete.

Der kontaktarme Zwischenraum ist in jedem Weltabschnitt vorhanden. Er ist
kein Wechselzeichen und keine technische Zustandslöschung.

## 3. Lokale Kontaktlage

Jeder Anflug erhält ausschließlich für den Forschungsobserver ein Vorzeichen:

```text
x(n) = -1  Anflug von der rechten Seite
x(n) = +1  Anflug von der linken Seite
```

Der erste sichtbare Austritt erhält entsprechend:

```text
y(n) = -1  Austritt auf der linken Seite
y(n) = +1  Austritt auf der rechten Seite
```

`x` und `y` sind Auswertungsnotation. Sie werden nicht an Rezeptor, Dock,
Neuron oder Feld übergeben.

## 4. Die beiden Weltbeziehungen

Die kleinsten technisch symmetrischen Beziehungen sind:

```text
R0: y(n) =  x(n)
R1: y(n) = -x(n)
```

In `R0` setzt sich die sichtbare Anflugrichtung hinter der Verdeckung fort.
In `R1` wird der verdeckte Verlauf räumlich symmetrisch umgelenkt.

Beide Beziehungen verwenden:

- dieselbe Rezeptorfläche;
- denselben visuellen Dock;
- dieselben sichtbaren Positionen;
- dieselben Reizstärken;
- dieselbe Anzahl sichtbarer Kontakte;
- dieselben physischen Dauerfamilien;
- denselben Energie- und Geometrieumfang.

Nur der nicht sichtbare äußere Verlauf zwischen Anflug und Austritt
unterscheidet die Beziehungen.

## 5. Keine Beziehungsidentität in der Runtime

Nur der äußere Weltgenerator kennt für den gerade laufenden Kontakt:

```text
äußere verdeckte Position
äußere Bewegungsrichtung
aktuell wirksame Weltbeziehung
späteren physischen Austritt
```

Verboten in allen Runtimeverträgen sind:

- `R0`- oder `R1`-ID;
- Phasen- oder Blockname;
- Umschaltbit;
- erwartete Austrittsseite;
- Beziehungswechselzeit;
- Kontrollgruppen-ID;
- Erfahrungsstufe;
- Weltseed;
- Ergebnis- oder Korrektursignal.

Der Organismus erhält nur die normale sichtbare Rezeptorprojektion.

## 6. Kontinuierliches Weltleben

Jeder Hauptlauf ist ein ununterbrochenes Weltleben.

```text
Trageabschnitt
-> äußerer Beziehungswechsel
-> Erfahrungsabschnitt
-> Holdoutkontakt
-> optionaler kontaktarmer Abschnitt
-> optionale äußere Rückkehr
-> weitere reale Erfahrung
-> Rückkehr-Holdout
```

Zwischen diesen Abschnitten werden nicht:

- Neuronen neu erzeugt;
- Feldzustände kopiert;
- Aktivierung oder Nachhall resettet;
- Snapshots als neuer Startzustand geladen;
- Docks ausgetauscht;
- Uhren neu begonnen.

Die Abschnittsnamen existieren nur im nachträglichen Observerbericht.

## 7. Trageabschnitt

Der primäre Trageabschnitt enthält acht abgeschlossene Kontakte derselben
Weltbeziehung. Die acht Anflüge sind exakt balanciert:

```text
viermal x = -1
viermal x = +1
```

Reihenfolge, räumliche Übersetzung, Farbkanal, Amplitude,
Verdeckungsdauer und Zwischenzeit werden vor dem Lauf aus einer
vorregistrierten Transformationsfamilie zusammengesetzt.

Keine dieser Größen darf die Beziehungsidentität vorhersagen.

Die kanonische maximale Anflugfolge ist vor der Implementierung fest:

```text
S10 = (+1, -1, -1, +1, -1, +1, +1, -1, +1, -1)
```

Ihre Präfixe bei `6`, `8` und `10` Kontakten sind jeweils seitenbalanciert.
Zulässige vollständige Ordnungsvarianten sind ausschließlich:

```text
S10
-S10
reverse(S10)
-reverse(S10)
```

Diese vier Varianten werden vollständig gekreuzt. Eine nachträgliche Auswahl
günstiger Reihenfolgen ist unzulässig.

## 8. Unbezeichneter äußerer Wechsel

Im Hauptzweig wechselt ausschließlich die verdeckte Weltursache:

```text
R0 -> R1
```

Der erste Kontakt nach dem Wechsel beginnt technisch wie jeder andere
Kontakt. Es gibt keinen zusätzlichen Leerframe, keinen abweichenden
Zeitstempel, keine besondere Reizstärke, keine neue Position, keinen
Dockwechsel und keine Unterbrechung des Feldes.

Der Organismus kann den Wechsel erstmals am real erlebten Austritt erkennen.

## 9. Erfahrungsstufen statt Lernschwelle

Getrennte kontinuierliche Lebensläufe enden vor einem neuen Holdout nach:

```text
k = 0, 1, 2, 4 oder 8
```

abgeschlossenen Kontakten der neuen Beziehung.

`k = 0` bedeutet: Die Außenwelt hat bereits gewechselt, aber noch kein
vollständiger Kontakt der neuen Beziehung wurde erlebt.

Die Werte bilden nur eine Reichweitenkarte. Kein Wert ist als notwendige oder
hinreichende Lernschwelle festgelegt.

Jeder Lauf beginnt neu am Anfang seines vollständigen Weltlebens. Innerhalb
eines Laufs bleibt der Organismus kontinuierlich; es wird kein Zustand am
Wechsel oder vor dem Holdout kopiert.

## 10. Holdoutkontakte

Jeder Holdout ist ein neuer konkreter Weltkontakt. Er verwendet mindestens
zwei Merkmale, deren konkrete Kombination in seinem vorherigen Lebenslauf
nicht vorkam:

- neue zulässige Zeile;
- neue Bahnübersetzung;
- neuer technischer Farbkanal;
- neue ungeclippte Amplitude;
- neue Verdeckungsdauer;
- neue kontaktarme Zwischenzeit.

Der lokale Beziehungstyp bleibt derselbe wie im unmittelbar vorausgehenden
Weltabschnitt.

Der Austritt wird ausschließlich durch die bereits laufende äußere
Weltursache bestimmt. Er wird nicht nach Sichtung des Feldzustands gewählt.

Für jede Kontrollgruppe, Erfahrungsstufe und Geschichtsvariante existiert je
ein vollständiger kontinuierlicher Holdoutlauf mit `x = -1` und `x = +1`.
Vergleiche zwischen Beziehungen halten die Holdout-Anflugseite exakt gleich.

## 11. Physische Zeitfamilien

Alle Zeitwerte liegen auf der vorhandenen gemeinsamen Feldzeit. Die
Mindestauflösung bleibt `10 ms`.

Vorregistrierte Verdeckungsdauern:

```text
Bildung:  30 ms, 50 ms, 80 ms
Holdout:  40 ms, 70 ms, 100 ms
```

Vorregistrierte kontaktarme Zwischenzeiten:

```text
Bildung:  20 ms, 40 ms, 70 ms
Holdout:  30 ms, 60 ms, 90 ms
```

Die Kombinationen werden über `R0`, `R1`, Anflugseite und Kontrollgruppe
balanciert. Keine Dauer bezeichnet einen Wechsel.

Die Zuordnung folgt zyklisch der kanonischen Ereignisposition. Spiegel- und
Umkehrvarianten erhalten dieselbe Dauerfolge; eine zweite vollständige
Kreuzung verwendet die um eine Position verschobene Dauerfolge. Damit wird
jede Dauer mit beiden Anflugseiten und beiden Beziehungen angeboten.

Falls die bekannte schnelle Rezeptionsruntime bei einer deklarierten
Vergleichsgrenze nicht exakt kollidiert, trägt der Lauf keine
Gegenwartsangleichung. Der Zustand darf nicht kopiert, gerundet oder
zurückgesetzt werden.

## 12. Gepaarte alte Geschichten

Zur Prüfung der bedingten Wirkungslosigkeit werden mindestens zwei
unterschiedliche `R0`-Vorgeschichten verwendet.

Sie besitzen dieselben Randhäufigkeiten, dieselbe Kontaktzahl, dieselbe
Gesamtdauer und dieselbe Gesamtenergie, aber unterschiedliche konkrete
Reihenfolgen und Übersetzungen.

Danach erhalten beide Läufe dieselbe konkrete `R1`-Geschichte und denselben
neuen Holdout.

Auf Weltebene muss gelten:

```text
gleiche R1-Geschichte
+ unterschiedliche frühere R0-Geschichte
-> gleicher späterer R1-Austritt
```

Mutual-Information-Notation wird nur als Kurzform verwendet. Ausgewertet
werden die vollständigen exakten Kontingenz- und Bedingungstabellen, kein
geschätzter Einzelwert.

## 13. Gepaarte neue Geschichten

Zur Prüfung neuer Relevanz werden bei gleicher schneller Gegenwart
unterschiedliche neue Beziehungsgeschichten gegenübergestellt:

```text
korrekte R1-Erfahrung
gegen
randgleiche permutierte Austritte
```

Nur die lokale Paarung zwischen Anflug und Austritt wird zerstört.
Kontaktzahl, Seitenhäufigkeit, Dauer, Energie und Transformationen bleiben
gleich.

Damit wird neue Weltrelevanz von bloßer Ereigniszahl getrennt.

## 14. Kontrollen K0 bis K7

### K0: dauerhaft R0

Acht `R0`-Kontakte und neue `R0`-Holdouts. Prüft die stationäre
Grundtragfähigkeit von `R0`.

### K1: dauerhaft R1

Acht `R1`-Kontakte und neue `R1`-Holdouts. Prüft die technisch symmetrische
Grundtragfähigkeit von `R1`.

### K2: R0 zu R1 bei k = 0

Acht `R0`-Kontakte, unbezeichneter äußerer Wechsel und sofortiger erster
`R1`-Holdout. Es gibt noch keine abgeschlossene neue `R1`-Erfahrung.

### K3: R0 zu R1 mit neuer Erfahrung

Acht `R0`-Kontakte, unbezeichneter Wechsel, anschließend `k` abgeschlossene
`R1`-Kontakte für `k = 1, 2, 4, 8` und danach ein neuer `R1`-Holdout.

### K4: randgleiche Permutation

Anflug- und Austrittsseiten bleiben jeweils balanciert, ihre lokale Paarung
wird unabhängig permutiert. Kein stabiler Beziehungstyp trägt den Holdout.

### K5: sichtbarer Wechselhinweis

Ein zusätzlicher normaler visueller Kontakt bezeichnet den äußeren Wechsel.
Diese Kontrolle misst die triviale Wirkung aktueller Rezeptorinformation. Sie
gehört nicht zur Memory-Prüfung und muss als abweichende Gegenwart berichtet
werden.

### K6: Rückkehr zu R0 bei k = 0

Nach acht `R0`- und acht `R1`-Kontakten kehrt die Außenwelt unbezeichnet zu
`R0` zurück. Vor dem ersten neuen `R0`-Holdout wurde seit der Rückkehr noch
kein vollständiger `R0`-Kontakt erlebt.

### K7: Rückkehr zu R0 mit neuer Erfahrung

Wie K6, anschließend jedoch `k = 1, 2, 4, 8` neue abgeschlossene
`R0`-Kontakte vor einem neuen `R0`-Holdout.

K6 und K7 trennen passive Rückkehr zu einer alten Lage von erneut
weltgetragener Prägung.

## 15. Wechselzeit- und Reihenfolgenkontrolle

Die äußere Wechselstelle wird über getrennte Lebensläufe nach:

```text
6, 8 oder 10 abgeschlossenen Kontakten
```

verschoben.

Die bis dahin geltende Beziehung bleibt jeweils balanciert. Zusätzlich
werden ausschließlich die vier in Abschnitt 7 festgelegten
Ordnungsvarianten und die beiden festgelegten Dauerzuordnungen verwendet.

Ein Weltzeit- oder Ereigniszähler, der nur eine feste Umschaltstelle kennt,
muss auf den verschobenen Läufen scheitern.

## 16. Exakte Gegenwartsangleichung

Vor jedem gepaarten Holdout werden vollständig verglichen:

```text
aktuelle Rezeptorprojektion
activation aller Neuronen
afterimage aller Neuronen
vollständiger MCMNeuronLayer-Zustand
vollständiger SharedMCMFieldSnapshot
offene Rezeptorabschlüsse
Dockanatomie und Geometrie
physische Organismuszeit
```

Die Organismuszeit wird nur zwischen zeitlich identisch aufgebauten
Paarzweigen verglichen. Unterschiedliche Erfahrungsstufen müssen nicht
dieselbe absolute Lebenszeit besitzen.

Eine Angleichung ist nur gültig, wenn sie natürlich aus dem kontinuierlichen
Weltlauf entsteht.

## 17. Beobachtungsprofil

Der passive Observer berichtet getrennt:

```text
W  R0- und R1-Weltabhängigkeit
G  exakte schnelle Gegenwartsangleichung gepaarter Zweige
E  Reichweite über alle Zeitfamilien
L  bedingte Irrelevanz alter R0-Geschichte
N  neue Relevanz realer R1-Geschichte
P  Freiheit von Phasen- und Metadatenlecks
H  Neuheit der konkreten Holdoutkontakte
```

Zusätzlich werden pro Lebenslauf kanonischer Rezeptorfolgendigest, Schicht-
und Snapshotdigest an jeder Vergleichsgrenze, vollständige Kontakt- und
Austrittsnotation, physische Dauern, Kontrollgruppe, Erfahrungsstufe sowie die
Ergebnisse aller Baselines erfasst.

Kontrollgruppe und Erfahrungsstufe existieren nur im Observerbericht.
Rohbilder und Debugfolgen bleiben lokale Prüfmittel und sind kein
Organismus-Memory.

## 18. Pflichtbaselines B0 bis B9

```text
B0  heutige unveränderte Rezeptor- und Feldruntime
B1  mehrere feste Leaky-Spuren
B2  lokale Übergangszähler
B3  begrenzte lokale Produktspuren
B4  letzter beobachteter Austritt
B5  fester Bewegungsautomat
B6  fester Zwei-Regime-Automat
B7  Ereigniszahl oder absolute Weltzeit
B8  exakter Sequenz- oder Templatevergleich
B9  permanente Doppelspeicherung mit fester Leserregel
```

B6 darf aus widersprechenden sichtbaren Austritten zwischen genau zwei
vorregistrierten internen Regimelagen wechseln. B7 wird zwingend auf
verschobenen Wechselstellen geprüft. B8 erhält keine Holdoutfolge. B9 darf
beide Beziehungstabellen bewahren, aber weder Phasenlabel noch Weltmetadaten
lesen.

Alle Baselines erhalten dasselbe Zustands-, Präzisions-, Zeit- und
Leserbudget, werden vor Holdoutauswertung parametrisiert und danach
eingefroren.

## 19. Auswertungslogik

Die Weltfamilie trägt ihre äußere Funktion nur, wenn gemeinsam gilt:

1. `R0` und `R1` sind in K0 und K1 technisch symmetrisch tragfähig.
2. K2 enthält vor dem Holdout keine neue `R1`-Erfahrung.
3. K3 trägt neue `R1`-Weltrelevanz über neue Holdouts.
4. Unterschiedliche alte `R0`-Geschichten ändern bei identischer
   `R1`-Geschichte den späteren Austritt nicht.
5. K4 entfernt die lokale Abhängigkeit bei gleichen Randgrößen.
6. K6 enthält keine neue `R0`-Erfahrung nach der Rückkehr.
7. K7 trägt erneute `R0`-Weltrelevanz erst nach neuer Erfahrung.
8. Wechselzeit, Zeitfamilie und Ereignisreihenfolge sind keine
   Beziehungsmetadaten.
9. Kein Observer schreibt in Welt oder Runtime zurück.
10. Vollständiger Neuaufbau reproduziert die kanonische Auswertung.

Dies sind Welt- und Beobachtungskriterien. Sie sind noch keine
Erfolgskriterien für einen inneren Kandidaten.

## 20. Erwartete bestehende Runtimegrenze

Die heutige Runtime besitzt nur schnelle Aktivierung und festen Nachhall.

Deshalb wird erwartet:

```text
nach natürlicher schneller Angleichung
+ ohne zusätzliche Memory-Rolle
-> keine kausale Feldunterscheidung aus gelöster älterer Geschichte
```

Ein endlicher Zwei-Regime-Automat kann die konkrete Welt wahrscheinlich
vollständig erklären. Das ist ein erwartetes starkes Gegenmodell und kein
Grund, die Baseline abzuschwächen.

## 21. Scheitergrenzen

Die Vorregistrierung oder spätere Implementierung scheitert, wenn:

- ein Abschnittsname in die Runtime gelangt;
- der Wechsel an einer einzigen festen Zeit oder Ereigniszahl liegt;
- `R0` und `R1` verschiedene Docks oder Träger verwenden;
- Dauer, Energie oder Randhäufigkeit eine Beziehung verraten;
- der Zustand zwischen Kontakten oder Abschnitten zurückgesetzt wird;
- ein Holdout aus bereits angebotenen konkreten Frames besteht;
- K4 die Randgrößen nicht exakt erhält;
- K6 durch einen technischen Rückkehrhinweis markiert wird;
- Austritte nach Sichtung des Feldzustands gewählt werden;
- Observerreihenfolge oder Observerentfernung die Runtime verändert;
- für die Weltprüfung eine neue innere Zustandsrolle eingeführt wird.

## 22. Aussagegrenze

Ein positiver äußerer Weltlauf trägt höchstens:

- eine kontinuierliche nichtstationäre Weltfamilie;
- reale Bildung, bedingte Irrelevanz und erneute Relevanz äußerer Geschichte;
- die Eignung der Welt als spätere Memory-Prüfgrundlage;
- eine genaue Reichweitenkarte der vorhandenen Runtime und der Baselines.

Er trägt nicht:

- organisches Memory;
- eine entwickelte Feldtopologie;
- natürliche Lösung eines inneren Zustands;
- semantische Resonanz;
- Reflexion oder Sprache;
- Handlung;
- Feldintelligenz.

## Freigabegrenze

```text
Weltfamilie konzeptionell vorregistriert: ja
kontinuierlicher Generator erweitert:     ja
passiver Weltlauf freigegeben:            ja
Memory-Rolle freigegeben:                 nein
Feldmechanikänderung freigegeben:         nein
Runtime-Erweiterung freigegeben:          nein
```

## Nächster Schritt

Der kontinuierliche äußere Weltgenerator und seine passiven Observer sind
implementiert. Der kanonische Lauf umfasst `768` kontinuierliche
Beobachtungen über K0 bis K7, alle Erfahrungsstufen, Wechselstellen,
Ordnungsvarianten, Dauerzuordnungen und beide Holdoutseiten.

```text
kanonischer Ergebnisdigest:
77ad7eeefd173f3d51c679009ad598c9d03ff4f756cbf883943aaecbbce03945
```

Identische unveränderliche Lebenspräfixe werden einmal berechnet und ohne
In-place-Mutation in unabhängige Holdouts fortgesetzt. Das verändert keinen
einzelnen Lebenslauf und verhindert redundanten Feldaufbau.

Als Nächstes werden ausschließlich die Baselines B0 bis B9 umgesetzt.

Die bestehende Rezeptor- und Feldruntime blieb unverändert. Erst der
vollständige Welt- und Baselinebefund entscheidet, ob diese Weltfamilie eine
tragfähige Grundlage für die spätere Suche nach einem Memory-Substrat ist.
