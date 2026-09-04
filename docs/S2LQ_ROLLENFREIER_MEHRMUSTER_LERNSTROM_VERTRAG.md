# S2-LQ - Rollenfreier Mehrmuster-Lernstrom

## Status und Frage

S2-LQ ist ein statischer Funktions- und Falsifikationsvertrag. Er erweitert
S2-LN nicht um neue Mechanik. Geprueft wird ausschliesslich, ob derselbe
qualifizierte Wahrnehmungsstrom mehrere zeitlich vermischte AV-Erfahrungen mit
unterschiedlicher Wiederholungsstaerke in stabile, instabile und vergessene
Inhalte trennt.

Die begrenzte Frage lautet:

> Kann der rollenfreie 336-Werte-Strom zwei wiederholt erfahrene AV-Muster
> selektiv aus B_STABLE abrufen, schwach erfahrene Inhalte nicht als stabil
> ausgeben und eine vorab gebundene sensorische Verwechslung transparent
> ausweisen?

Ein positiver Befund ist durch den bestehenden Slotscan und die adaptive
Prototypbank erklaerbar. Er belegt weder Semantik noch besondere
MCM-spezifische Physik.

## Unveraenderte Grenzen

- Default-Live-Profil: 48 auditive und 288 visuelle Rezeptorwerte.
- B4-Kapazitaet 9, Fast-Kapazitaet 3.
- Auditive Slow-Kapazitaet 8, visuelle Slow-Kapazitaet 4.
- Fast-Match nur bei Audio und Video innerhalb ihrer bestehenden Schwellen.
- Slow-Schwellen und PPB-Aktualisierungsrate bleiben unveraendert.
- Feld und atomarer B4-/TSPM-Verbund bleiben unabhaengige Geschwisterzweige.
- Teilhinweise veraendern weder Feld- noch Memoryzustand.
- Keine Vollprobe vor einem Teilhinweis.
- Keine Kontextwirkung auf Feld oder Memory.

## Reale Quellrollen

Alle funktionalen Werte entstehen aus echten kanonischen RGB8- und
PCM_F32LE-Fixtures durch die unveraenderten Rezeptoren. Es werden keine
48er-, 288er- oder 336er-Vektoren von Hand eingesetzt.

| Auswerterrolle | PCM-Rezept | RGB-Rezept | Expositionen |
|---|---|---|---:|
| A | `P` | `X` | 4 |
| B | `H` | `Y` | 4 |
| C | `D_FAR` | `B0` | 3 |
| D | `L` | `C0` | 1 |
| Druck 1 bis 9 | `D_FAR` | `D1` bis `D9` | je 1 |

Die Tabelle bindet neue AV-Paarungen aus bereits festgelegten PCM- und
RGB-Fixtures. Sie behauptet nicht, dass diese Paarungen bereits als gemeinsame
Formation ausgefuehrt wurden.

Die Rollen A bis D und Druck existieren ausschliesslich im versiegelten
Auswertungsplan. Der Laufpfad verwendet nur neutrale Inhaltscodes `p00` bis
`p12` sowie neutrale Ereignisordinalcodes.

Vor dem ersten Memoryaufruf muessen die bereits qualifizierten realen
Rezeptorausgaben erneut digestgleich gebunden werden. Zusaetzlich gelten als
Startgate:

1. A und B sind nach der gemeinsamen Fast-Regel getrennte AV-Inhalte.
2. Ihre auditiven Werte liegen gegenseitig oberhalb der auditiven
   Slow-Schwelle; X und Y liegen oberhalb der visuellen Slow-Schwelle.
3. C ist von A und B in beiden Slow-Banken getrennt.
4. Jeder Druckreiz ist nach der Fast-AND-Regel von A, B, C, D und jedem
   anderen Druckreiz getrennt.
5. `D_FAR/B0` ist von jedem `D_FAR/D1...D9` visuell ausserhalb der
   Fast-Schwelle getrennt.
6. Die auditive D-Probe `L` bleibt als vorab bekannte Interferenzkontrolle
   innerhalb der auditiven Slow-Anwendbarkeit von A; dies ist kein
   Erfolgslabel im Laufpfad.
7. Gegen die prospektiv aus den PPB-Uebergaengen abgeleiteten Slow-Prototypen
   gelten auf den tatsaechlich beobachteten Banden beziehungsweise Positionen:
   A trifft nur Muster A, B nur Muster B, C keinen stabilen Kandidaten, die
   auditive D-Probe nur Muster A und die visuelle D-Probe keinen stabilen
   Kandidaten.

Scheitert eine Beziehung, endet die Materialisierung vor Memory als
`S2LQ_SOURCE_GEOMETRY_NOT_MATERIALIZABLE`. Es gibt keine Suche, neue Fixture
oder Schwellenanpassung.

## Rollenfreie Ereignisfolge

Die 21 vollstaendigen AV-Ereignisse lauten im Laufpfad:

```text
e01 p00   e02 p01   e03 p02   e04 p00   e05 p01
e06 p00   e07 p01   e08 p00   e09 p01   e10 p02
e11 p02   e12 p03   e13 p04   e14 p05   e15 p06
e16 p07   e17 p08   e18 p09   e19 p10   e20 p11
e21 p12
```

Die getrennte Auswerterbindung lautet:

```text
p00=A  p01=B  p02=C  p03=D
p04...p12=Druck1...Druck9
```

Jedes Ereignis besitzt einen eigenen Einmal-Owner. Nach validierter
Rezeptorreduktion gehen identische Geschwisterprojektionen an Feld und Memory.
Ein Fehler eines Zweigs rollt den bereits gueltigen anderen Zweig nicht
zurueck; der Versuch wird dann jedoch `NOT_EVALUABLE`.

## Prospektive Zustandsspur

Aus den unveraenderten Fast- und PPB-Regeln folgt:

| Formation | Erwartete Wirkung |
|---:|---|
| 1, 4, 6, 8 | A: Slow `CREATED, MATCHED, MATCHED`, Support `1,2,3` |
| 2, 5, 7, 9 | B: Slow `CREATED, MATCHED, MATCHED`, Support `1,2,3` |
| 3, 10, 11 | C: Slow `CREATED, MATCHED`, Support `1,2`, nicht stabil |
| 12 | D: nur neue Fast-Spur, kein Slow-Aufruf |
| 13 bis 21 | neun getrennte Druckformationen, kein Slow-Aufruf |

Nach e21 muessen gelten:

- B4 enthaelt exakt die Bildungsindizes 13 bis 21.
- Fast enthaelt ausschliesslich spaete Druckinhalte.
- A, B, C und D sind aus B4 und Fast verschwunden.
- A und B besitzen je genau einen stabilen auditiven und visuellen Slow-Slot
  mit Support 3.
- C besitzt je einen instabilen auditiven und visuellen Slow-Slot mit
  Support 2 und bleibt oeffentlich unzulaessig.
- D besitzt keinen eigenen Slow-Prototyp.
- Kein Druckinhalt ist in einer Slow-Bank verdichtet.

Die finalen Prototypwerte werden mit der exakten Binary64-Reihenfolge aus den
tatsaechlichen PPB-Uebergaengen abgeleitet. Bitgleichheit mit dem ersten
Rezeptorwert wird nicht vorausgesetzt.

## Teilhinweise

Nach e21 folgen strikt spaeter acht reale, unvollstaendige Wahrnehmungen:

| Ereignis | Modalitaet | Quellinhalt | Erwartete Messung |
|---:|---|---|---|
| e22 | auditiv | A | eindeutiger stabiler Treffer auf Muster A |
| e23 | visuell | A | eindeutiger stabiler Treffer auf Muster A |
| e24 | auditiv | B | eindeutiger stabiler Treffer auf Muster B |
| e25 | visuell | B | eindeutiger stabiler Treffer auf Muster B |
| e26 | auditiv | C | kein oeffentlich stabiler Treffer |
| e27 | visuell | C | kein oeffentlich stabiler Treffer |
| e28 | auditiv | D | vorab gebundene Verwechslung mit A messen |
| e29 | visuell | D | kein oeffentlich stabiler Treffer |

Auditive Hinweise verwenden den qualifizierten 24/24-Bandplan. Visuelle
Hinweise entstehen als tatsaechlich okkludierte RGB-Frames mit 32 beobachteten
und 256 maskierten Rezeptorpositionen. Zielwerte werden erst nach Abschluss
aller Scanarme dem Auswerter geoeffnet.

Jeder Hinweis fuehrt den Produktionsscan und die unabhaengige Direktbaseline
unter identischen Grenzen vollstaendig aus. B4, Fast und die jeweilige
Slow-Bank werden ohne Short-Circuit vollstaendig gelesen.

## Messungen

Der nachgelagerte Auswerter berichtet getrennt:

- finalen B4-, Fast-, Auditory-Slow- und Visual-Slow-Bestand;
- PPB-Ereignis-, Support- und Prototypdigestketten fuer A, B und C;
- A/B-Selektivitaet je Modalitaet;
- fehlende eigene oeffentliche Kandidaten fuer C und D;
- die erwartete auditive D-zu-A-Verwechslung als Interferenzbefund;
- vorgeschlagene Werte und Rekonstruktions-L1 je Teilhinweis;
- vollstaendige Gleichheit von Produktionsscan und Direktbaseline;
- identische Memorydigests vor und nach jedem read-only Scan.

Ein Treffer auf A bei e28 darf nicht als Erhaltung von D bezeichnet werden.
Er ist eine sensorisch erklaerte Verwechslung. Umgekehrt bedeutet die
Abwesenheit eines eigenen C- oder D-Kandidaten kontrolliertes Nichtstabilisieren,
nicht zwingend die Unmoeglichkeit jedes aehnlichen Treffers.

## Feste Grenzen

| Position | Grenze |
|---|---:|
| Gesamtereignisse | 29 |
| vollstaendige AV-Formationen | 21 |
| auditive Teilhinweise | 4 |
| visuelle Teilhinweise | 4 |
| Feldschritte | 29 |
| Feldkontakte | `21*336 + 4*48 + 4*288 = 8.400` |
| Memory-L1-Terme | `21*3.552 = 74.592` |
| Scanvergleiche, beide Arme | hoechstens `8*528 + 8*800 = 10.624` |
| kumulierte rohe Eingangsbytes | hoechstens `156.000.000` |
| gleichzeitig gehaltene Rohdaten | ein RGB-Frame und ein PCM-Hop |

Die Laufhuelle bleibt klein: ein unveraenderliches Tupel neutraler
Ereignisspezifikationen, feste kumulative Zaehler, ein atomarer Ergebnisbeleg
und ein unabhaengiger read-only Verifikator. Die bestehende S2-LO-Struktur
wird erweitert; es entsteht kein append-only Recorder und keine neue
Registryplattform.

## Entscheidung

`S2LQ_MULTIPATTERN_STREAM_CONFIRMED` ist nur zulaessig, wenn:

1. alle 29 Ereignisse und 21 Formationen vollstaendig sind;
2. A und B in beiden Slow-Banken Support 3 erreichen und selektiv abrufbar
   sind;
3. C instabil bleibt und D keinen eigenen Slow-Inhalt erzeugt;
4. A bis D nach e21 vollstaendig aus A_RECENT verschwunden sind;
5. kein Druckinhalt stabil wird;
6. e28 als Verwechslung und nicht als D-Erhaltung ausgewiesen wird;
7. alle Scans read-only bleiben und die Direktbaseline exakt uebereinstimmt;
8. Feld- und Memoryzweig dieselben Rezeptorurspruenge, aber keine
   gegenseitige Zustandsabhaengigkeit besitzen.

Ein vollstaendiger, technisch gueltiger Lauf mit abweichender Funktion ist
`S2LQ_MULTIPATTERN_STREAM_FALSIFIED`. Quellen-, Digest-, Zeit-,
Owner-, Zweig- oder Budgetbruch ist `NOT_EVALUABLE`. Es gibt keinen Retry und
keine nachtraegliche Schwellen- oder Fixtureanpassung.

## Aussagegrenze

Ein Bestehen bestaetigt ein kleines erfahrungsabhaengiges, rollenfreies
Mehrmuster-Memory mit selektivem Abruf, Instabilitaet, Vergessen und einer
transparenten Interferenzgrenze. Nicht bestaetigt sind offene Welt,
Langzeitpersistenz, semantische Identitaet, autonome Kontextwahl oder Handeln.
