# S2-TX: Aktualität nach exakter Wiederwahrnehmung

Status: statischer Vergleichsplan. Keine Quellenproduktion, Implementierung,
Qualifikation oder Ausführung ist freigegeben.

## Prüffrage und Grenze

Hilft eine vollständige exakte Wiederwahrnehmung, eine später benötigte Spur
unter nachfolgendem FIFO-Druck länger verfügbar zu halten, und welche andere
Spur geht dadurch früher verloren?

S2-TX ist eine handkonstruierte Aktualitätsregel für bereits vollständig
gleiche Vierframe-Spuren. Sie untersucht weder biologische Festigung noch
gelernte Variantenbindung, semantische Zuordnung oder eine allgemeine
Gedächtnistheorie. Feld, A/B-Memory und öffentliche Hypothesen bleiben
unverändert außerhalb des Plans.

## Gebundene Arme

Beide Arme erhalten denselben einmal materialisierten Strom aus geordneten
48-Wert-Halbprofilzuständen und besitzen je Kapazität `2`:

| Arm | Vollgleichheit beim Segmentabschluss |
| --- | --- |
| `S2TW_UNVERAENDERT` | Bestehende S2-TW-Regel: genau eine gleiche Spur wird bestätigt, ohne ihre FIFO-Reihenfolge, Generation oder Werte zu ändern. |
| `S2TX_CONFIRM_RECENT` | Nur bei genau einer vollständigen Gleichheit wird dieselbe Spur mit unveränderten Werten und unveränderter Generation an das jüngste FIFO-Ende versetzt. Kein zusätzlicher Platz und keine weitere Zustandsgröße entstehen. |

Bei keiner Gleichheit erfolgt in beiden Armen die unveränderte reguläre
Übernahme. Bei mehreren vollständigen Gleichheiten wird nicht gewählt und
nichts verjüngt. Read-only Hinweise können niemals eine Verjüngung auslösen.
Es gibt keine Supportgewichte, Schutzschwellen, Prioritätsklassen oder
zusätzliche Ersetzungsregel.

## Feste Ereignisfolge

`a` bis `l` sind ausschließlich vorab zu bindende Eingangspositionen. Die
Vergleichsregel sieht weder ihre Quellenidentitäten noch Planrollen, sondern
nur vier geordnete Vektorwerte.

| Ordinale | Abschnitt | Ereignisse | S2-TW unverändert | S2-TX Aktualität |
| --- | --- | --- | --- | --- |
| e01-e05 | P1 | Formation `a,b,c,d`; Close | Generation 1 | Generation 1 |
| e06-e10 | P2 | Formation `e,f,g,h`; Close | Generation 2, Inventar `1,2` | Generation 2, Inventar `1,2` |
| e11-e15 | P3 | vollständige Wiederwahrnehmung `a,b,c,d`; Close | Bestätigung 1, Inventar `1,2` | Verjüngung 1, Inventar `2,1` |
| e16-e20 | P4 | Formation `i,j,k,l`; Close | Generation 3 verdrängt 1, Inventar `2,3` | Generation 3 verdrängt 2, Inventar `1,3` |
| e21-e22 | H1 | read-only Hint `c,d` | keine passende gehaltene Spur | eindeutiger Match zu Generation 1 |
| e23-e27 | P5 | Wiederkehr `e,f,g,h`; Close | Bestätigung 2, Inventar bleibt `2,3` | keine gehaltene Vollgleichheit: neue Generation 4 verdrängt 1, Inventar `3,4` |

P1 bis P5 sind jeweils vier Formationen plus Segmentabschluss. Es gibt nur
einen Hint in diesem Endlauf, weil zwei Hintpaare zusätzlich zur
Wiederkehr P5 die bestehende Grenze von `28` Ereignissen überschreiten
würden. Der Verlust von Generation 2 nach P4 und die spätere Wiederkehr von
P2 werden deshalb durch die nativen Close-Receipts, Inventare und den
vollständigen Gleichheitsvergleich geprüft, nicht als zweiter Abrufbefund
ausgegeben.

## Gegenkontrollen für spätere neutrale Qualifikation

Die reale Folge wird nicht nachträglich verändert. Eine fokussierte neutrale
Qualifikation muss zusätzlich und getrennt prüfen:

1. unvollständige Formation: kein Vergleich, keine Bestätigung und keine
   Verjüngung;
2. umgekehrte volle Folge: keine Vollgleichheit, reguläre Übernahme;
3. teilweise gleiche Folge: keine Vollgleichheit, reguläre Übernahme;
4. gezielte einzelne Werteabweichung in einer neutralen Vierframefixture:
   keine Vollgleichheit und keine Verjüngung;
5. mehrfach gleiche gehaltene Spuren: keine Auswahl und keine Verjüngung;
6. read-only Hint: Inventar, Generation und FIFO-Reihenfolge bleiben gleich.

Die Einzelwertefixture ist keine Aussage über die späteren Rezeptorwerte.

## Getrennte Auswertung

Vorab getrennt zu berichten sind:

* Erhaltung: H1 bestätigt nur im Aktualitätsarm Generation 1;
* Verlust: P4 entfernt im Aktualitätsarm Generation 2 statt Generation 1;
* Wiederkehr: P5 bestätigt Generation 2 im unveränderten Arm, bildet aber
  nach ihrem vorangegangenen Verlust im Aktualitätsarm eine neue Generation
  und verdrängt dort Generation 1;
* alle nicht erreichten Inventare, Enthaltungen, Mehrdeutigkeiten und
  abweichenden Gleichheitsbefunde ohne Verrechnung von Gewinnen und Verlusten.

Ein Gewinn bei H1 genügt nicht für einen allgemeinen Vorteil: P5 bindet die
Gegenwirkung derselben Aktualitätsregel sichtbar ein.

## Ressourcen und Grenzen

Der Plan enthält `27` Ereignisse: `20` Formationen, zwei Hintframes und fünf
Segmentabschlüsse. Genau `22` Audioendpunkte werden einmal materialisiert und
an beide getrennten Arme übergeben. Es entstehen keine Feldkontakte oder
A/B-Scans; je Arm folgt zusätzlich ein finaler Owner-Abschluss.

Die Ereignis-, Formations- und Endpunktzahlen liegen an den bestehenden
Grenzen `28`/`20`/`22`, ohne sie zu erhöhen. Für beide Stores zusammen gilt
weiterhin konservativ höchstens `10.752` native Vektorbytes. Vor einer
späteren Umsetzung müssen Quellen-, Code-, Übergangs-, Inventar-, Fehler-,
Verifikations- und Ergebnishülle vollständig gegen `98.304` Zustands-,
`65.536` Metadaten- und `262.144` Zusatzbytes gebunden werden.

## Falsifikation

Der Plan ist begrenzt oder falsifiziert, wenn unvollständige oder nicht exakt
gleiche Folgen verjüngt werden, eine Verjüngung Generation oder Werte ändert,
P4 nicht genau die in der jeweiligen FIFO-Reihenfolge älteste Spur verdrängt,
H1 den Bestand verändert oder Gewinne aus H1 den Verlust von Generation 2
und die P5-Gegenwirkung verdecken.
