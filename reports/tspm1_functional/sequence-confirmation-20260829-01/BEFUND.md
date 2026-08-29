# Befund: unabhaengige Bestaetigung kurzer visueller Folgen

## Ergebnis

Der einmalig freigegebene Lauf `sequence-confirmation-20260829-01` ist
vollstaendig und auswertbar abgeschlossen:

- Exit-Code: `0`
- Aufzeichnungsstatus: `COMPLETE`
- Bildanalysen: `56`
- tatsaechliche B4-Bildungen: `8`
- Folgeproben: `12`
- read-only Sichtentscheidungen: `24`
- verkettete Ereignisse: `152`
- nachgerechnete Paarabstaende: `192`

Resultatdigest:
`0602d3f632f3aa81f5718f829cb57d7b8eb2e62f4a917263762cb829f897c953`

Journal-SHA-256:
`e08a55c7399e8caea6859a4d9272c261d828f53983e1797bfb1d76aa99c5db86`

## Funktionsbefund

Die beiden frischen Banken wurden tatsaechlich mit N1-N2-N3-N4
beziehungsweise N1-N3-N2-N4 fortgeschrieben. Die gespeicherten
Bildungsindizes blieben 1 bis 4. Alle Proben waren read-only; Vor- und
Nachzustand waren identisch und es gab keinen falschen Rueckgabewert.

GEORDNET:

- sechs korrekte Annahmen der jeweils gebildeten Folge;
- sechs korrekte Abweisungen der Folge mit vertauschten Mittelpositionen;
- fuer Delta `0`, `-8` und `+8` jeweils zwei korrekte Annahmen und zwei
  korrekte Abweisungen.

REIHENFOLGEBLIND:

- zwoelf korrekte Inhaltsannahmen;
- die Kontrolle setzte Original- und Gegenfolge wie vorab erwartet gleich,
  weil beide dieselben vier Einzelzustaende enthalten.

Damit sind chronologische Erhaltung, geordneter Folgenvergleich und
reihenfolgeblinder Inhaltsvergleich technisch getrennt. Die Schwelle blieb
exakt `44/765`; es gab keine Parametersuche oder Ergebnisanpassung.

## Read-only Belegpruefung

Nach dem Lauf wurden ausschliesslich die gespeicherten Dateien mit Python-
Standardbibliothek gelesen. Kein Projektmodul und keine Rezeptor-, B4-,
Speicher- oder Abruffunktion wurde importiert oder aufgerufen. Geprueft wurden:

- Formen und Digests von Manifest, Ergebnis und Terminal;
- Journalhash und die vollstaendige 152-Ereignis-Kette;
- Lauf-ID, Validatorbeleg, N1-N4, Folgen, Schwelle und Budgets;
- alle archivierten Quelldigests;
- alle 192 aufgezeichneten Paarabstaende durch unabhaengige Neuberechnung;
- Klassifikationen, Zustandsunveraendertheit und Rueckgabewerte.

Ergebnis: `READ_ONLY_EVIDENCE_VALID`.

## Aussagegrenze

Der Lauf bestaetigt einen begrenzten technischen Kurzzeit-Sequenzabruf aus
expliziten, tatsaechlich erzeugten Bildungsindizes fuer vier visuelle Zustaende
innerhalb der B4-Kapazitaet. Er belegt kein selbststaendiges Segmentieren,
kein Sequenz- oder Episodenlernen, keine Langzeitverdichtung, Semantik oder
MCM-Feldwirkung.

Der alte Lauf `sequence-20260829-01` bleibt dauerhaft `NOT_EVALUABLE` und
wurde nicht fortgesetzt oder repariert. Der neue Lauf wurde nicht wiederholt.
Der private Lauf-Gate ist wieder geschlossen.

## Naechster fachlicher Schritt

Als naechste getrennte Aufgabe ist zu entscheiden, ob die bestaetigte kurze
Folge nach intervenierenden Wahrnehmungszustaenden und unter kontrolliertem
Kapazitaetsdruck erhalten bleibt. Ein solcher Plan sollte B4 gegen TSPM-1
bei identischen Folgen, Zwischenreizen, Budgets und spaeterem read-only Abruf
vergleichen. Noch ist keine solche Ausfuehrung freigegeben.
