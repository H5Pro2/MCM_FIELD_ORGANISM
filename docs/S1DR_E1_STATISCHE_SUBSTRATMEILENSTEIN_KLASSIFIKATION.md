# S1-DR: E1 statische Substratmeilenstein-Klassifikation

## Forschungsfrage

Welche minimale Substratfunktion ist nach S1-DQ technisch belegt und welche
Funktionen duerfen daraus noch nicht abgeleitet werden?

## Verfahren

Die Klassifikation liest ausschliesslich den bereits veroeffentlichten und
in S1-DQ digestgebundenen Ergebnisbericht. Sie startet weder Produzent noch
Executor oder Feldruntime und erzeugt keinen neuen Forschungsbericht.

```text
mcm_field_organism/e1_substrate_milestone_classification.py
tests/test_e1_substrate_milestone_classification.py
```

Klassifikationsdigest:

```text
bb8fe7f2137a931b0d0e697226154ea58013fb9b6ae2b6f3e11416b878dfb9df
```

## Entscheidung

```text
GIVEN_STATE_TRANSFER_MILESTONE_ONLY
```

Technisch erfuellt sind genau diese Punkte:

- zwei gegebene lokale E1-Zustaende veraendern eine spaetere identische
  S/H-Feldaufnahme unterschiedlich;
- die Wirkung ist ablatierbar;
- die Wirkung liegt klar ueber dem eigenen Probe-Partitionsrest;
- die eingefrorenen E1-Zustaende bleiben waehrend der Probe unveraendert.

Die Wirkung ist zugleich bitgenau durch den jeweiligen festen,
zustandsabgeleiteten Adapter erklaert. S1-DQ belegt deshalb einen
Zustandstransfer, aber keine waehrend der Probe weiterentwickelte
Substratdynamik.

## Offene Anforderungen

Weiterhin nicht belegt sind:

- numerisch kontrollierte Bildung verschiedener E1-Zustaende aus
  verschieden geordnetem, ansonsten identischem Weltkontakt;
- eine nichttriviale Rekonstruktion aus Teilhinweisen;
- ein zusammenhaengender Lebenszyklus aus Praegung, Erhaltung,
  Abschwaechung, Freigabe, Wiederverwendung und spaeterer Rueckwirkung;
- MCM-Memory oder staerkere Claims.

Der Status des naechsten Forschungsabschnitts lautet:

```text
NEW_REFINED_WORLD_FORMATION_CONTRACT_REQUIRED
```

**STOPP bleibt auf dem alten vollen S1-DC-Zweig und auf jeder Wiederholung
von S1-DI oder S1-DQ.** Das ist kein Stopp des Gesamtprojekts. Der engere
Transfermeilenstein ist gueltig abgeschlossen; die offene Forschung darf mit
einem neuen, vorab numerisch kontrollierten Bildungsvertrag weitergehen.

## Technische Abnahme

```text
6 fokussierte Klassifikationstests
12 gemeinsame S1-DQ/S1-DR-Nachlauftests
315 Tests im vollstaendigen E1-Verbund
OK
```

## Bester naechster Schritt

S1-DS bindet statisch einen neuen Weltkontakt-Bildungsvertrag. Er muss vor
jeder Ausfuehrung mindestens drei feste Zeitverfeinerungen, frische
Anfangszustaende, identische AV-Multisets, AB/BA-Reihenfolge, eine
Identitaetskontrolle, eine Bildungsablation sowie eine identische spaetere
Probe festlegen. Erst wenn Zustandsbildung und spaetere Wirkung gemeinsam
gegen ihren jeweiligen Verfeinerungsrest entscheidbar sind, darf ein neuer
Einmallauf erwogen werden.

## Anschlussstatus nach S1-DS

S1-DS hat diesen statischen Vertrag inzwischen gebunden. Es wurde noch kein
neuer Lauf ausgefuehrt. Der aktuelle Anschluss steht in
`S1DS_E1_VERFEINERTER_WELTKONTAKT_BILDUNGSVERTRAG.md`.
