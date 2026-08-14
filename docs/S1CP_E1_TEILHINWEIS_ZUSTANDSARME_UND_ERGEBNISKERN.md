# S1-CP: E1 Teilhinweis-Zustandsarme und Ergebniskern

## Status

Die in S1-CO registrierten langsamen Zustandsarme und der
interpretationsfreie Ergebniskern sind implementiert und technisch
abgenommen. Es wurde kein realer Teil- oder Vollhinweis ausgefuehrt und
keine Forschungsentscheidung erzeugt.

## Implementierung

```text
mcm_field_organism/e1_partial_cue_execution.py
tests/test_e1_partial_cue_execution.py
```

Alle Rollen bleiben privat und sind weder ueber die Paketwurzel noch ueber
`current_api` erreichbar.

## Zustandsarme

Aus dem unveraenderten neutralen Drei-Knoten-Eingang werden die bestehenden
gespiegelten H8-Geschichten erzeugt. Beide E1-Zustaende durchlaufen danach
mit der vorhandenen analytischen Freigabefunktion vier Sekunden uniforme
Nullkontaktentwicklung.

```text
left-g4
right-g4
neutral
```

Die G4-Bindungen bleiben bis `1e-12` gespiegelt. Eingangsfeld und neutraler
E1-Eingang bleiben unveraendert. Die Zustandsarmfunktion gibt keine Cue-
Beobachtung und kein Proberesultat zurueck.

## Beobachtungsmatrix

Der Kompositor akzeptiert spaeter exakt 36 injizierte Beobachtungen:

```text
3 Modelle * 3 Geschichten * 4 Hinweise = 36

Modelle:     E1, P0, B1-static-H8
Geschichten: left-g4, right-g4, neutral
Hinweise:    left-full, right-full, left-partial, right-partial
```

Jede Beobachtung traegt ausschliesslich signierte `Delta_S`- und
`Delta_H`-Dreiervektoren, eine n=2-Kontrollbeobachtung sowie Zeitplan- und
Invariantenflags.

## Interaktionsrechnung

Fuer Teil- und Vollhinweise wird getrennt die passende minus gekreuzte
Geschichtswirkung gebildet. Die rechte Seite wird geometrisch gespiegelt und
mit der linken Seite gemittelt. P0 und B1 durchlaufen dieselbe Rechnung.

Der Ergebniscontainer berichtet:

- Teil- und Vollkontaktinteraktion;
- gerichtetes Skalarprodukt beider Interaktionen;
- P0- und B1-Interaktionsboden;
- gekreuzten Historykontrast;
- Spiegelungsfehler;
- maximalen relativen n=2/n=4-Rest.

Die technische Entscheidung bleibt eine getrennte Funktion in der bereits
registrierten Reihenfolge. Der Ergebniscontainer besitzt kein eingebettetes
Entscheidungs-, Rekonstruktions- oder Memoryfeld.

## Technische Abnahme

14 fokussierte Tests und 44 relevante Verbundtests bestehen. Geprueft
wurden Zustandsarmspiegelung, Eingangsunveraenderlichkeit, exakte
Matrixvollstaendigkeit, endliche Vektoren, synthetische Entscheidungsfolge,
private Rollen und die bestehenden Einmallaufgrenzen.

## Aussagegrenze

Die synthetische positive Entscheidung prueft nur die mathematische
Verdrahtung. Sie ist kein Projektbefund. S1-CP zeigt nicht, dass E1 auf einen
Teilhinweis history-spezifisch reagiert, und begruendet weder Rekonstruktion
noch Memory.

## Bester naechster Schritt

S1-CQ implementiert die isolierten Cue-Runner fuer E1, P0 und den einen
statischen H8-Gain. Er prueft jeden Arm einzeln auf identische frische
Probefelder, P0-Subtraktion, n=2/n=4, Spiegelung und unveraenderte langsame
Zustaende. Eine vollstaendige 36er-Matrix oder Entscheidung bleibt dabei
noch gesperrt.
