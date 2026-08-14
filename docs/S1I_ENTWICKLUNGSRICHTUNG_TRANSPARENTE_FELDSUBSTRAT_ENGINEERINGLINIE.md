# S1-I: Entwicklungsrichtung transparente Feldsubstrat-Engineeringlinie

Stand: 2026-08-09

Entscheidung: `TECHNICAL_FIELD_SUBSTRATE_ENGINEERING_OPEN_F3_REFERENCE_SELECTED`

Runtimeaenderung: nein

Forschungslauf: nein

## Ausgangslage

S1-H hat aus dem heutigen schnellen MCM-Feld keine neue unabhaengige
Naturursache fuer eine irreduzible langsame Substratrolle hergeleitet. Die
Suche nach immer neuen Gleichungen bleibt deshalb pausiert. Dieser Nullausgang
verbietet jedoch nicht, ein technisch funktionierendes feldbasiertes System
aus bereits bekannten und vollstaendig transparenten Mechaniken aufzubauen.

S1-I trennt daher zwei Arbeitslinien verbindlich:

| Linie | Status | Zulaessige Arbeit |
|---|---|---|
| neue irreduzible Substratphysik | pausiert | erst nach einer extern begruendeten neuen lokalen Naturursache mit eigener Bilanz |
| transparente Feldsubstrat-Engineeringlinie | offen | bekannte Mechaniken technisch integrieren, ablatieren und gegen enge Baselines pruefen |

Die Engineeringlinie ist kein Ersatzbeleg fuer die pausierte Neuphysiklinie.
Sie untersucht, welche nachvollziehbare feldgebundene Verlaufsfunktion mit
dem vorhandenen System tatsaechlich gebaut werden kann.

## Bestandsvergleich B2 und F3

### B2

B2 ist die implementierte lineare reziproke S-L-Akkommodation. Sie ist
deterministisch, lokal, transparent und deshalb eine geeignete enge
Gegenbaseline. Ihre Wirkung gehoert jedoch genau zu der bereits bekannten
linearen Relaxationsklasse. B2 wird nicht als neuer produktiver
Geschichtstraeger ausgegeben.

### F3

F3 ist bereits als optionaler Substratzustand des `SharedMCMField` technisch
integriert. Der Zustand besitzt:

- eine nichtnegative lokale M-Masse auf derselben Feldgeometrie;
- eine feste Gesamtmasse von 1.0;
- symmetrischen lokalen Austausch entlang des vorhandenen Kanteninventars;
- transparente Rueckwirkung auf S;
- asynchrone transiente Felduebergabe;
- Snapshot- und Restore-Unterstuetzung;
- einen exakten P0-Nullpfad und getrennte Rueckwirkungsablation.

Die historischen Laeufe begrenzen die Aussage klar. Lauf 192 erklaert den
engen Mechanikrest durch die lineare gekoppelte Feldbaseline. Lauf 194 zeigt
passiven Wirkungsverlust und Wiederverwendung, aber keine konkurrierende
Reorganisation. F3 ist damit keine neue Physik und kein Memorybefund. Es ist
aber der technisch reifere, geometrisch wirksame und bereits in die heutige
gemeinsame Feldruntime eingebundene Feldverlaufs-Traeger.

## Auswahl

F3 wird fuer den naechsten Prototyp als **transparente technische
Feldverlaufs-Referenz** ausgewaehlt. Diese Auswahl behauptet weder, dass F3
das spaetere MCM-Memory ist, noch dass seine Gleichung unveraendert produktiv
bleiben muss.

B2 bleibt als lineare Pflichtbaseline gebunden. Ein positiver F3-Effekt ist
nur dann technisch informativ, wenn er gegen B2, den exakten Nullarm und die
Rueckwirkungsablation getrennt sichtbar bleibt. Eine Baselineabgrenzung waere
noch kein Memory-, Lern- oder Organisationsnachweis.

## Gebundene Begriffssprache

Zulaessig sind vor einem Funktionsnachweis nur:

- `technischer Feldverlaufs-Traeger`;
- `M-Zustand` oder `F3-Zustand`;
- `geschichtsabhaengige Feldwirkung`;
- `passiver Verlust und Wiederverwendung`;
- `technischer Kandidat fuer spaetere Lernuntersuchungen`.

Nicht zulaessig sind als Befund:

- organisches oder MCM-Memory;
- Lernen, Praegung oder Vergessen;
- relative Feldzeit oder Feldzeitverdichtung;
- innerer Kontext, Bedeutung oder Semantik;
- Organisation, Topologie oder Selbstregulation;
- feldbasierte KI.

Diese Begriffe werden erst nach jeweils eigenen kontrollierten
Funktionsnachweisen und Gegenbaselines neu bewertet.

## Kleinster naechster Prototyp S1-J

S1-J ist eine reine technische Kompatibilitaetsscheibe unter synthetischen
Fakes. Sie bindet F3 an die aktuelle gemeinsame AV-Geometrie aus acht
auditiven und achtzehn visuellen Feldneuronen. Es wird noch kein
Geschichts-/Probeexperiment ausgefuehrt.

Der aktive Referenzarm bleibt unveraendert bei den historisch gebundenen
Parametern:

```text
arm_id:       p1.active
lambda:       1.0
kappa:        0.5
eta:          1.0
total_mass:   1.0
```

Pflichtkontrollen von S1-J:

1. Aktivierung auf der bestehenden 26-Neuronen-Geometrie ohne neue Kante,
   Identitaet oder Topologie.
2. Nichtnegative M-Werte und Erhaltung der Gesamtmasse 1.0.
3. Exakter P0-Nullpfad ohne zusaetzliche Feldwirkung.
4. B2 beziehungsweise die lineare gekoppelte F3-Form als Pflichtbaseline.
5. `eta=0` als getrennte Rueckwirkungsablation.
6. Kausalitaet ueber abgeschlossene transiente Rezeptorbatches.
7. Exaktes Snapshot/Restore an der naechsten Feldgrenze.
8. Keine Rohdatenhaltung, Objektidentitaet, Labels, Ergebnisrueckschreibung
   oder Observersteuerung.

S1-J darf vorhandene F3-Gleichungen und Parameter nicht veraendern. Es darf
keinen Browser starten, keinen Runner fuer einen Forschungsversuch erzeugen,
keinen Report schreiben und keine Laufnummer reservieren.

## Abgrenzung zu geschlossenen Zweigen

S1-I und S1-J setzen weder 213ZZR bis 213ZZU noch Z4 oder die historischen
K2-Laeufe fort. Sie diagnostizieren und wiederholen diese Laeufe nicht. Der
neue Weg verwendet ausschliesslich die bereits vorhandene technische
F3-Runtime in einer neuen Kompatibilitaetspruefung mit der aktuellen
26-Neuronen-AV-Geometrie.

W1-O und W1-Q bleiben einmalige abgeschlossene reale Quellen- und
Feldpaarpruefungen. Die Engineeringlinie arbeitet vorerst nur mit
synthetischen Fakes und lokalen Dateien.

## Aussagegrenze

S1-I ist ein Entwicklungsentscheid, kein empirischer Befund. Die Wahl von F3
belegt keinen funktionalen Vorteil, kein Lernen und kein Memory. Sie waehlt
den kleinsten bereits integrierten technischen Traeger, an dem weitere
Entwicklung falsifizierbar und ohne versteckte Zielmechanik stattfinden
kann.

## Bester naechster Schritt

S1-J implementiert die beschriebene technische Kompatibilitaetsscheibe und
ihre Tests. Erst nach deren Bestehen darf ein eigener, vorregistrierter
Funktionsvergleich fuer Wiederholung, spaetere Feldwirkung und Loesbarkeit
entworfen werden.

## Spaeterer Umsetzungsstand S1-J

S1-J ist inzwischen in der
[`technischen F3-AV-Kompatibilitaetsscheibe`](S1J_TECHNISCHE_F3_AV_KOMPATIBILITAETSSCHEIBE.md)
umgesetzt. F3, lineare gekoppelte Baseline, `eta=0` und P0 bestehen auf der
aktuellen 26-Neuronen-AV-Geometrie. Dies ist nur technische Kompatibilitaet.
Naechster Schritt ist der statische S1-K-Funktionspruefvertrag.
