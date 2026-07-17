# Methodik 037: Passive Falsifikationsmatrix der Übergangsdisposition

## 1. Status

Vorregistrierte passive Baseline- und Funktionsmatrix zu Architektur 022.

Es wird keine Übergangsdisposition implementiert. Die Matrix prüft nur, welche
geforderte Funktion von einfachen festen Zustandsfamilien getragen werden
kann und wo ein konkreter Funktionsrest bleibt.

## 2. Zentrale Funktionsfrage

Der erste nicht tautologische Funktionsmangel lautet:

> Kann neue lokale Übergangsevidenz, die dieselbe endliche lokale Ressource
> beanspruchen müsste, eine alte Einbindung stärker lösen als eine zeitlich,
> energetisch und positionsmäßig angeglichene Folge ohne diesen Übergang?

Kurz:

```text
konkurrierende lokale Evidenz
→ zusätzliche Lösung alter lokaler Einbindung
```

Diese Funktion wird **konkurrenzgekoppelte Lösung** genannt.

Der Begriff benennt eine prüfbare Funktion, noch keine Mechanik.

## 3. Warum diese Funktion nötig ist

Ohne konkurrenzgekoppelte Lösung können unabhängige lokale Spuren
nebeneinander anwachsen:

```text
Übergang A erlebt → Spur A bleibt
Übergang B erlebt → Spur B kommt hinzu
Übergang C erlebt → Spur C kommt hinzu
```

Das erzeugt mit wachsender Weltgeschichte entweder:

- unbegrenzte Akkumulation,
- nur zeitgesteuerten Zerfall,
- permanente alte Kanten,
- globale spätere Auswahl.

Eine endliche lokale Organisation muss dagegen neue Einbindung ermöglichen,
ohne jede frühere Möglichkeit dauerhaft mitzuschleppen.

## 4. Technische Welt

Die äußere Welt besitzt sieben linear angeordnete Kontaktpositionen:

```text
0, 1, 2, 3, 4, 5, 6
```

`-` bezeichnet einen vollständig kontaktlosen Takt.

Jeder Kontakt trägt Amplitude `1.0`. Pro Takt ist höchstens eine Position
aktiv.

Die Weltrollen A, B und U existieren ausschließlich im Forschungsbericht. Sie
werden keiner Runtime übergeben.

## 5. Lokale Übergänge

Vorregistriert werden:

```text
A: 2 → 3
B: 4 → 3
U: 5 → 6
```

A und B enden an derselben lokalen Zielposition `3` aus zwei
gegenüberliegenden lokalen Quellen.

U liegt räumlich getrennt und teilt weder Quelle noch Ziel mit A.

Diese Rollen sind äußere Versuchsbezeichnungen. Ein späterer Organismus dürfte
nur lokale Feldproben und aktuelle Kontakte sehen.

## 6. Phase P0: frischer Zustand

Alle Baselines beginnen exakt bei null:

```text
Neuronenhäufigkeit = 0
Übergangszähler    = 0
Leaky-Spuren       = 0
permanente Kanten  = nicht gesetzt
```

Es existiert keine frühere Einbindung.

## 7. Phase P1: gemeinsame A-Geschichte

Alle Hauptzweige erhalten vier identische A-Zyklen:

```text
(2 → 3 → - → -) x 4
```

Damit entstehen:

```text
4 Evidenzen für A
4 Kontakte an Position 2
4 Kontakte an Position 3
8 kontaktlose Takte
16 Takte gesamt
```

Zwischen den Zyklen entsteht wegen der zwei Leertakte keine zusätzliche
Übergangsevidenz.

## 8. Phase P2-B: lokale Konkurrenz

Der Konkurrenzzweig erhält:

```text
(4 → 3 → - → -) x 4
```

Damit entstehen:

```text
4 Evidenzen für B
4 Kontakte an Position 4
4 Kontakte an Position 3
8 kontaktlose Takte
16 Takte gesamt
```

B teilt die lokale Zielposition `3` mit A.

## 9. Phase P2-M: angeglichene Nicht-Konkurrenz

Der positions- und energieangeglichene Kontrollzweig erhält:

```text
(4 → - → 3 → -) x 4
```

Er besitzt exakt dieselben:

- 16 Takte,
- 8 aktiven Kontakte,
- Gesamtenergie `8.0`,
- vier Kontakte an Position `4`,
- vier Kontakte an Position `3`,
- acht kontaktlosen Takte

wie P2-B.

Es entsteht jedoch keine Evidenz für `4 → 3`, weil jeder Kontakt durch einen
Leertakt getrennt ist.

## 10. Phase P2-U: räumlich unabhängige Evidenz

Der Lokalitätskontrollzweig erhält:

```text
(5 → 6 → - → -) x 4
```

Er gleicht P2-B in:

- Taktzahl,
- Gesamtenergie,
- Zahl aktiver Kontakte,
- Zahl lokaler Übergangsereignisse.

U teilt jedoch keine lokale Quelle und kein lokales Ziel mit A.

## 11. Phase P2-I: reine Zeitkontrolle

Der Leerlaufzweig erhält:

```text
16 kontaktlose Takte
```

Dieser Zweig ist nicht energieangeglichen. Er isoliert ausschließlich die
Wirkung verstrichener Zeit und natürlicher Relaxation.

## 12. Phase P3: schnelle Feldangleichung

Nach P2 folgt in allen Zweigen ein ausdrücklich kontrollierter Leertakt.

Für die vorhandene schnelle MCM-Runtime muss danach gelten:

```text
activation = 0
afterimage = 0
lokale vorherige Feldproben = 0
```

Die Baselinezustände bleiben für die passive Auswertung getrennt erhalten.

## 13. Primärer Vergleich

Primär verglichen werden P2-B und P2-M.

Vor dem gemeinsamen P3-Leertakt besitzen beide Zweige:

```text
gleiche Dauer
gleiche Gesamtenergie
gleiche Positionshäufigkeit
gleiche Zahl kontaktloser Takte
gleiche erste A-Geschichte
gleiches Alter der letzten A-Evidenz
```

Sie unterscheiden sich ausschließlich darin, ob die späteren Kontakte
`4` und `3` lokal aufeinanderfolgend waren.

## 14. Gesuchte konkurrenzgekoppelte Funktion

Ein späterer Kandidat mit endlicher geteilter lokaler Ressource müsste
grundsätzlich ermöglichen:

```text
alte A-Wirkung nach P2-B
<
alte A-Wirkung nach P2-M
```

Gleichzeitig müsste eine neue B-Wirkung nur nach P2-B entstehen.

Die Matrix erzeugt diese Wirkung noch nicht. Sie prüft nur, welche Baselines
eine solche Differenz überhaupt darstellen könnten.

## 15. Lokalitätsbedingung

Eine lokale Ressource darf durch räumlich unabhängige U-Evidenz nicht in
gleicher Weise beansprucht werden:

```text
alte A-Wirkung nach P2-U
≈ alte A-Wirkung nach einer gleich alten nicht konkurrierenden Kontrolle
```

Falls U dieselbe A-Lösung wie B erzeugt, wäre die Ressource zu global oder der
Effekt nur allgemeine Last.

Die genaue lokale Reichweite bleibt offen und darf nicht nachträglich an das
Ergebnis angepasst werden.

## 16. B0: vorhandenes schnelles Feld

Unter `receptor_projection_baseline` gilt nach P3:

```text
alle Zweige kollidieren exakt
```

B0 besitzt keine fortbestehende A-, B- oder U-Information.

B0 trägt deshalb weder alte Einbindung noch konkurrenzgekoppelte Lösung.

## 17. B1: unabhängige Neuronenhäufigkeit

Für jede Position wird gezählt:

```text
n_i = Zahl aktueller Kontakte an Position i
```

P2-B und P2-M kollidieren in jedem `n_i`.

Damit kann B1 nicht unterscheiden, ob `4` und `3` einen lokalen Übergang
bildeten.

B1 trägt Nutzungshäufigkeit, aber keine Übergangsbeziehung.

## 18. B2: permanente Übergangszähler

Für jede technische lokale Nachbarschaft gilt passiv:

```text
c_(j→i)(t+1)
= c_(j→i)(t) + evidence_(j→i)(t)
```

Nach P1 gilt in allen Zweigen:

```text
c_A = 4
```

Nach P2 gilt:

```text
P2-B: c_A = 4, c_B = 4
P2-M: c_A = 4, c_B = 0
P2-U: c_A = 4, c_U = 4
P2-I: c_A = 4
```

Der alte A-Zähler bleibt in allen Zweigen gleich.

B2 kann neue B-Evidenz speichern, aber keine zusätzliche A-Lösung durch
Konkurrenz darstellen.

## 19. B3: unabhängige Leaky-Übergangsspuren

Für jede lokale Nachbarschaft wird getrennt geprüft:

```text
z_(j→i)(t+1)
= d * z_(j→i)(t) + evidence_(j→i)(t)
```

Vorregistrierte Zerfallsfaktoren:

```text
d = 0.25, 0.5, 0.75, 0.9
```

Da nach P1 in P2-B und P2-M:

- gleich viele Takte vergehen,
- keine neue A-Evidenz auftritt,
- das letzte A-Ereignis gleich alt ist,

muss für jede feste unabhängige A-Spur gelten:

```text
z_A(P2-B) = z_A(P2-M)
```

B3 kann B in P2-B zusätzlich tragen. Es kann aber die alte A-Spur nicht
stärker lösen als in P2-M, weil die Spuren unabhängig sind.

## 20. B4: permanente lokale Kanten

Eine permanente Kante wird nach erster Evidenz gesetzt:

```text
k_(j→i) = 1, sobald evidence_(j→i) > 0
```

Nach P2 gilt:

```text
P2-B: k_A = 1, k_B = 1
P2-M: k_A = 1, k_B = 0
P2-U: k_A = 1, k_U = 1
```

Die alte A-Kante bleibt überall vollständig erhalten.

B4 kann weder Abschwächung noch Lösung, Ressourcenfreigabe oder Wiederbindung
tragen.

## 21. B5: unabhängig gesättigte Übergangsspur

Eine einzeln begrenzte Spur darf beispielsweise tragen:

```text
s_(j→i) = clip(c_(j→i), 0, capacity)
```

Geprüft werden:

```text
capacity = 1, 2, 4
```

Auch eine unabhängige Sättigung koppelt B nicht an A:

```text
s_A(P2-B) = s_A(P2-M)
```

Sie verhindert unbegrenzte Einzelwerte, aber keine unbegrenzt wachsende Zahl
gesättigter lokaler Einbindungen.

## 22. B6: globale Normalisierung

Als starkes, aber unzulässiges Gegenmodell darf der äußere Observer alle
Übergangswerte global normieren:

```text
g_e = c_e / Summe_aller c
```

Dadurch sinkt der relative A-Anteil, wenn B hinzukommt.

B6 ist kein zulässiger Organismusmechanismus, weil:

- alle Übergänge global bekannt sein müssen,
- räumlich unabhängiges U A ebenfalls schwächt,
- lokale Ressourcen nicht getrennt bleiben.

Die U-Kontrolle muss diesen Fehler sichtbar machen.

## 23. Baselineentscheidung

Die vorregistrierte Matrix lautet:

| Baseline | erkennt B-Evidenz | löst A stärker unter B als M | bleibt lokal gegen U | vollständig lösbar | wiederbindbar |
|---|---:|---:|---:|---:|---:|
| B0 schnelles Feld | nein | nein | ja | sofort | nein |
| B1 Neuronenhäufigkeit | nein | nein | ja | nein | nein |
| B2 Übergangszähler | ja | nein | ja | nein | nein |
| B3 unabhängige Leaky-Spuren | ja | nein | ja | nur zeitlich asymptotisch | parallel |
| B4 permanente Kanten | ja | nein | ja | nein | nein |
| B5 unabhängige Sättigung | ja | nein | ja | nein | parallel |
| B6 globale Normalisierung | ja | ja | nein | formal | global |

Keines dieser Gegenmodelle erfüllt gleichzeitig:

```text
lokale Konkurrenz
+ zusätzliche Lösung
+ endliche Ressource
+ vollständige Freigabe
+ lokale Wiederbindung
```

## 24. Noch offene Funktionsmessung

Die Matrix zeigt einen Darstellungsrest, erzeugt aber noch keine
MCM-Feldwirkung.

Vor einem Kandidaten fehlt weiterhin eine nicht tautologische Probe der alten
A-Einbindung.

Nicht ausreichend wäre:

```text
gespeicherter A-Wert
x erneut präsentierte A-Evidenz
→ größere A-Ausgabe
```

Das wäre nur das Auslesen eines adressierten Übergangsspeichers.

## 25. Anforderungen an die spätere Probe

Eine spätere Probe muss:

1. in allen Zweigen identisch sein,
2. Aktivierung und Nachhall vorab angleichen,
3. A- und B-Bildungsevidenz nicht im selben Takt wiederholen,
4. eine vorhandene lokale Feldfunktion messen,
5. bei neutralisierter Disposition kollidieren,
6. beim Tausch der Disposition mitwandern,
7. ohne realen lokalen Kontakt keine Wirkung erzeugen,
8. nicht durch einen festen Zählerleser vollständig vorgegeben sein.

Die konkrete Probe bleibt geschlossen, bis diese Bedingungen gemeinsam
erfüllbar formuliert sind.

## 26. Observer- und Reihenfolgeneutralität

Eine spätere passive Implementierung der Matrix muss prüfen:

- normale und umgekehrte Zweigreihenfolge,
- normale und umgekehrte Baselinereihenfolge,
- unabhängige Wiederholung,
- leerer und sammelnder Observer,
- exakten Reset jeder Baseline,
- unveränderte Weltfolgen,
- getrennte Zustände jedes Zweigs.

Kein Baselinezustand darf zwischen Zweigen geteilt werden.

## 27. Stärkstes Gegenargument

Die Matrix postuliert, dass lokal konkurrierende Übergänge eine Ressource
teilen sollten.

Diese Annahme ist noch nicht durch die MCM-Runtime bewiesen. Es könnte sein,
dass geeignete organische Organisation anders begrenzt wird oder dass A und B
keine Ressource teilen müssen.

Deshalb ist konkurrenzgekoppelte Lösung zunächst nur ein begründeter
Funktionskandidat. Sie darf nicht als biologische Tatsache oder vorhandene
MCM-Eigenschaft ausgegeben werden.

## 28. Evidenzgrenze

```text
Baseline-Algebra B0 bis B6:          maximal E2
Funktionsmangel unabhängiger Spuren: maximal E1
lokale gemeinsame Ressource:         E0
konkurrenzgekoppelte Lösung:          E0
Übergangsdisposition:                 E0
verdichtete Feldform:                 E0
Feldintelligenz:                      E0
```

## 29. Stopplinie

Nicht freigegeben sind:

- gemeinsame Ressourcenvariable,
- Übergangsdisposition,
- adaptive Kante oder Gewicht,
- Zerfalls- oder Lernrate,
- Konkurrenzgleichung,
- lokale oder globale Normalisierung,
- Runtime-Leser,
- Feldrückwirkung,
- entwickelte Topologie,
- Handlung oder Semantik.

## 30. Bester nächster Schritt

Methodik 037 wird zunächst ausschließlich als passive Baseline-Matrix
implementiert.

Der Lauf muss bestätigen:

```text
B2 bis B5:
alte A-Komponente in P2-B und P2-M identisch

B6:
alte A-Komponente unter B kleiner,
aber fälschlich auch unter räumlich unabhängigem U kleiner
```

Auch ein vollständig bestätigter Funktionsrest gibt keine Ressource oder
Disposition frei. Danach muss zuerst die nicht tautologische spätere
Feldprobe geklärt werden.
