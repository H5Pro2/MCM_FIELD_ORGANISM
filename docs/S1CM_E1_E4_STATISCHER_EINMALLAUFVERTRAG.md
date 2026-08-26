# S1-CM: E1 E4 statischer Einmallaufvertrag

## Status

Der spaetere E4-Gesamtlauf ist als genau ein Versuch statisch registriert.
S1-CM hat keinen Runner aufgerufen, keine Gesamtmatrix erzeugt, keine
Ergebnisdatei geschrieben und keine E4-Entscheidung getroffen.

## Gebundene Grenze

Der Vertrag bindet:

- Ausfuehrungskennung `e1.e4.s1cn.once.v1`;
- S1-CL-Inventardigest `e76d4154...c25c1`;
- den unveraenderten S1-CG-Ausfuehrungsvertragsdigest;
- genau eine Ergebnis-, Versuchsnachweis- und Sperrdatei im selben Ordner;
- kanonischen JSON-Ergebnisdigest mittels SHA-256;
- atomare Veroeffentlichung durch einen exklusiven Same-Directory-Link;
- permanenten Versuchsnachweis nach einem gestarteten Fehler;
- ein Verbot automatischer Wiederholung.

Fuer den aktuellen Projektpfad ergeben sich:

```text
Einmallauf-Vertragsdigest: f4b225564f3d085ac61a99453b2415b14b294a67d3b92b3609ca2887269f6cf1
S1-CG-Ausfuehrungsdigest:  1f7e14c31a85ae578d18760d42ebb5cc8dcaab5b55765263864771a335a0f1f8
```

Die vier einzig zulaessigen technischen Entscheidungen bleiben in der
bereits registrierten Reihenfolge:

```text
INVALID_E4_RUN
TECHNICALLY_INCOMPATIBLE_BASELINE_SET
E4_EXPLAINED_BY_NARROW_BASELINE
E4_RESIDUAL_AFTER_REGISTERED_BASELINES
```

## Ablagevertrag

Der fuer S1-CN reservierte Ergebnisname ist:

```text
reports/e1_e4_s1cn_once_v1.json
```

Vor dem spaeteren Start muessen Ergebnis, Versuchsnachweis und Sperrdatei
fehlen. Der Versuchsnachweis wird unmittelbar vor dem ersten Runneraufruf
exklusiv angelegt. Nach einem gestarteten Fehler bleibt er fuer manuelle
Pruefung bestehen; ein automatischer zweiter Lauf ist damit unzulaessig.
Das Ergebnis darf erst nach vollstaendiger Komposition und externer
Entscheidung atomar sichtbar werden.

## Technische Abnahme

Sieben fokussierte Tests pruefen Pfade, Digests, Feld- und
Entscheidungsreihenfolge, Nebenwirkungsfreiheit der Vorbereitung,
Wiederholungsschutz und die private API-Grenze.

Gemeinsam mit Inventar, Einzelrunnern, Baseline-Handoffs, Kompositorvertrag
und den benoetigten E1/E3-Zustandsarmen bestehen 72 relevante Tests. Die
abgeschlossenen S1-BZ- und S1-CD-Einmallaufsuiten wurden nicht wiederholt.

## Aussagegrenze

S1-CM ist ausschliesslich ein technischer Ausfuehrungs- und
Persistenzvertrag. Es existiert weiterhin kein E4-Gesamtergebnis und daraus
folgt kein Memory-, Lern-, Organisations-, Semantik- oder KI-Befund.

## Bester naechster Schritt

S1-CN implementiert den bereits gebundenen Aufrufweg und fuehrt ihn nach
erneuter statischer Digest- und Pfadpruefung genau einmal aus. Erst dieser
Schritt darf die neun Runner auswerten, den Ergebniscontainer bilden, die
registrierte technische Entscheidung anwenden und das Resultat atomar
ablegen.
