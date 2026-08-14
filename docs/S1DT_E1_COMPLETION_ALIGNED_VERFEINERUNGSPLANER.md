# S1-DT: E1 completion-aligned Verfeinerungsplaner

## Status

Der in S1-DS geforderte private Verfeinerungsplaner ist implementiert und
mit kleinen synthetischen Rezeptorfolgen abgenommen. Es wurde kein E1-
Zustand, kein S/H-Feld, keine kanonische AB-/BA-Historie und keine Probe
ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_completion_aligned_refinement.py
tests/test_e1_completion_aligned_refinement.py
```

Normalisierter Implementierungsdigest:

```text
accfe0a2ded04203785f217c6e93d3d5fbd1d46f377d4e9142b3eebd8ee59084
```

## Zeitmodell

Der Planer bildet zuerst Basisintervalle zwischen aufeinanderfolgenden
gemessenen Rezeptorabschlusszeiten. Jedes Basisintervall wird fuer `r1`,
`r2` oder `r4` in 1, 2 oder 4 exakt gleich lange ganzzahlige Tickintervalle
zerlegt.

Ein Rezeptorkontakt wird dabei nicht verteilt oder interpoliert. Er bleibt
als punktfoermiger Kontakt am urspruenglichen Abschluss und wird genau dem
letzten Teilschritt seines Basisintervalls zugeordnet. Kontaktfreie
Teilschritte tragen nur die feinere Feld- und E1-Entwicklungszeit.

Ist ein Basisintervall nicht exakt durch vier teilbar, bricht der Planer
geschlossen ab. Dadurch entstehen keine gerundeten oder verschobenen
Zeitgrenzen.

## Erhaltene Evidenz

Alle drei Plaene muessen gemeinsam erhalten:

- denselben Anfangs- und Endtick;
- dieselben geordneten Rezeptorabschlusszeiten;
- jeden eindeutigen Support genau einmal;
- denselben Digest der lokalen Kontaktwerte und Kontaktzeiten;
- dasselbe signierte Kontaktintegral;
- dasselbe absolute Kontaktintegral;
- dasselbe quadratische Kontaktintegral.

Die Plaene enthalten nur Zeitrollen und den bestehenden verlustfreien
Rezeptor-Handoff. Sie besitzen keine E1-, Feld-, Memory- oder Claimrolle und
bleiben ausserhalb der oeffentlichen API.

## Synthetische Abnahme

Die Testfolge besitzt zwei Abschlusszeiten bei Tick 8 und 16. Daraus
entstehen:

```text
r1: 2 Schritte
r2: 4 Schritte
r4: 8 Schritte
```

Beide Supports verbleiben bei Tick 8 und 16. Die drei Kontaktintegrale sind
in allen Plaenen exakt gleich:

```text
signiert    = -0.25
absolut     =  0.75
quadratisch =  0.3125
```

Ein nicht durch vier teilbares Intervall und ein Kontakt ausserhalb des
Horizonts werden abgewiesen.

```text
7 fokussierte Tests
328 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-DT zeigt nur, dass die numerische Zeitverfeinerung geplant werden kann,
ohne die gemessenen Rezeptorkontakte zu veraendern. Es zeigt weder eine
Zustandsbildung noch einen Feldtransfer und ist kein Memorybefund.

## Bester naechster Schritt

S1-DU bindet den Planer in einen nichtausfuehrenden kanonischen AB-/BA-
Preflight ein. Dabei werden nur Schrittzahlen, Abschlusszeiten,
Supportzuordnung und Kontaktintegrale beider Reihenfolgen verglichen. Erst
nach diesem Preflight darf ein neuer synthetischer E1-Bildungsrunner
implementiert werden.

## Anschlussstatus nach S1-DU

S1-DU hat den Planer inzwischen nichtausfuehrend auf die kanonischen AB-/BA-
Quellen angewendet. Kein E1- oder Feldlauf wurde gestartet. Der aktuelle
Anschluss steht in
`S1DU_E1_KANONISCHER_AB_BA_VERFEINERUNGSPREFLIGHT.md`.
