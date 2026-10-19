# S2TU: Begrenzte Aufbewahrung abgeschlossener Spuren

Status: statischer Anschlussplan. Keine Quellenproduktion, Implementierung,
Qualifikation oder Ausführung freigegeben.

## Frage und Grenze

Kann eine abgeschlossene ältere exakte Spur nach der Aufnahme einer weiteren
Folge noch eindeutig über einen geordneten Zweiframe-Hint gefunden werden?

Der Plan untersucht ausschließlich Aufbewahrung. Er enthält keine Mittelung,
Ähnlichkeitsschwelle, Verdichtung, Objektbindung, A/B-Integration oder
gelernten Übernahmeentscheid. Ein positives Ergebnis wäre eine begrenzte
Kapazitäts- und Lebenszyklusaussage, kein Langzeit-Erfahrungsspeicher.

## Zustände und deterministische Übernahme

Der bisherige S2-TS-Aufnahmepuffer bleibt unverändert: vier vollständige,
geordnete Halbprofilzustände desselben Aufnahmesegments erzeugen genau eine
abgeschlossene Spur. Ein explizit gebundener übergeordneter Besitzer hält den
Aufbewahrungsbestand über Segmentabschlüsse hinweg. Bei Segment-Close wird
eine vollständige aktive Spur unverändert in diesen Bestand übernommen. Eine
unvollständige, abgelaufene oder technisch ungültige Spur wird nicht
übernommen.

Der Besitzer endet nur mit eigenem endgültigem Close. Spätere Hints aus einem
anderen Segment sind nur bei gleicher Besitzerbindung zulässig. Die bisherige
S2-TS-Sitzungsprüfung bleibt für den Aufnahmepuffer unverändert; die
Aufbewahrung ist ein expliziter neuer Anschluss, keine Lockerung.

Der Bestand besitzt feste Kapazität `2`. Die Reihenfolge der Übernahme ist die
Ereignisreihenfolge des jeweiligen Close-Ereignisses. Die dritte gültige
Übernahme verdrängt deterministisch die älteste aufbewahrte Generation
(`FIFO`); Slot-ID und Generation bleiben getrennt. Übernahme und Verdrängung
verwenden ausschließlich Vollständigkeit, Profil-/Sitzungsbindung und
Ereigniszeit, keine Quellenlabels, Rollen oder späteren Hints.

Hinweise lesen nur den aufbewahrten Bestand. Ein geordneter Zweiframe-Hint
liefert nur dann `TRACE_MATCH`, wenn genau eine noch aufbewahrte Generation
einen passenden Offset besitzt. Mehrere passende Generationen oder Offsets
führen zur Enthaltung. Hints ändern weder Aufnahmepuffer noch Bestand,
Generationen oder FIFO-Reihenfolge.

## Feste Ereignisfolge

`a`, `b`, `c` und `d` bezeichnen vorab gebundene volle auditive Halbvektoren;
ihre späteren Quellen werden nicht nach Abrufbarkeit ausgewählt.

| Abschnitt | Ereignisse | Erwartete technische Kontrolle |
| --- | --- | --- |
| T1 | Formation `a,b,c,d`; Close | Generation T1 wird aufbewahrt |
| T2 | Formation `c,b,d,a`; Close | Generation T2 wird zusätzlich aufbewahrt |
| H1 | Hint `b,c`; Hint `c,b` | T1 bzw. T2 eindeutig, gleiche Inhaltswerte aber andere Ordnung |
| T3 | Formation `a,c,b,d`; Close | T3 wird aufbewahrt; T1 wird als älteste Generation verdrängt |
| H2 | Hint `b,c`; Hint `c,b` | `b,c` passt zu keiner verbleibenden Spur; `c,b` ist zwischen T2 und T3 mehrdeutig |

T1 und T2 besitzen den gemeinsamen Inhalt `b,c`, aber entgegengesetzte
Reihenfolge. Das verhindert, dass eine Inhaltsmitgliedschaft den
Spurgenerationsabruf ersetzt. Die H2-Entscheidungen dürfen nicht aus einem
historischen T1-Receipt geschlossen werden. Insbesondere ist `c,b` eine
geforderte Konkurrenzkontrolle zwischen T2 und T3, kein eindeutiger T2-Abruf.

## Vergleich und Ressourcen

Die flüchtige S2-TS-Spur bleibt Vergleichsarm: Nach jedem Close enthält sie
keine aktive Spur. Eine unabhängige Direktbaseline liest dieselben gespeicherten
48-Wert-Vektoren und Generationen, nicht den produktiven Suchhelfer.

| Größe | Aufbewahrungsarm |
| --- | ---: |
| Ereignisse | 23 |
| Formationen | 12 |
| Hintframes / Entscheidungen | 8 / 4 |
| direkte Audioanalysen / NJ-Projektionen | 20 / 20 |
| Feldkontakte / A-B-Scans | 0 / 0 |
| maximal gespeicherte Vektorwerte | 2 × 4 × 48 + 4 aktiver Puffer + 2 Hintpuffer |
| native Vektorbytes ohne Bindungen | (8 + 4 + 2) × 48 × 8 = 5.376 |

Die Folge bleibt innerhalb der bestehenden Obergrenzen von 28 Ereignissen,
20 Formationen und 22 auditiven Analyse-/NJ-Aufrufen. Vor einer späteren
Anbindung müssen die vollständige Generationen-, Fehler-, Verifikations- und
Ergebnishülle gegen die bestehenden 98.304 Zustands-, 65.536 Metadaten- und
262.144 Zusatzbytes gebunden werden. Wenn diese Hülle nicht passt, wird weder
verkürzt noch eine Grenze erhöht.

FIFO-Übernahme ist atomar: Erst wird die neue vollständige Generation
validiert, dann wird der Bestand in einem Schritt auf die zwei jüngsten
Generationen gesetzt. Bei Fehler bleibt der alte Bestand erhalten oder ein
typisierter Abschluss ohne teilübernommene Generation wird publiziert.

## Falsifikation

Der Plan ist begrenzt oder widerlegt, wenn H1 Ordnung nicht von Inhalts-
Baselines trennt, ein Hint den Bestand verändert, T1 nach FIFO-Verdrängung
weiter verfügbar bleibt, T2 nach T3 ohne technische Ursache fehlt oder eine
Mehrdeutigkeit als eindeutige Generation ausgegeben wird.
