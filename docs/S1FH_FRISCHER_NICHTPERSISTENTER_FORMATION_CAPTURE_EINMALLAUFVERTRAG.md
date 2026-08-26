# S1-FH: Frischer nicht persistenter Formation-Capture-Einmallaufvertrag

## Gebundener Umfang

S1-FH bindet genau einen neuen kontrollierten Formation-Capture-Versuch:

- r2, r4 und r8;
- je fuenf Formation-Arme;
- insgesamt 15 Arme und maximal 14.000 Feldschritte;
- danach genau ein atomarer S1-FF-Capture;
- danach genau eine S1-FD-Auswertung;
- keine Probe und keine Persistenz.

Die bereits vorliegenden Ressourcenobergrenzen werden vor dem Ergebnis
uebernommen: 84 Feldknoten, 145 Zustandskanten, maximal 2.175 gehaltene
Belegungen, mindestens 4 GiB freier RAM und maximal 900 Sekunden Laufzeit.
Eine neue Ressourcenpruefung ist vor dem Versuch und unmittelbar vor dem
ersten Formation-Arm erforderlich.

## Freigabegrenze

Der Vertrag enthaelt keine Freigabe. Er verlangt eine neue ausdrueckliche
Besitzerautorisierung, die genau diesen S1-FH-Vertragsdigest bindet. Ein
`ok weiter` ersetzt diese Autorisierung nicht. Alte Freigaben, Ergebnisse,
Attempt-, Lock- oder Reportpfade duerfen nicht wiederverwendet werden.

Automatischer Retry, Nachparametrierung nach einem Ergebnis und Teilstarts
sind geschlossen. Jeder Kontroll-, Ressourcen-, Digest-, Inventar- oder
Laufzeitfehler beendet den Versuch fail-closed.

## Evidenzgrenze

Der spaetere atomare In-Memory-Rueckgabebefund muss Messung, technische
Interpretation, Nichtnachweis und offene Annahmen trennen. Auch ein
konvergenter Bildungszustand waere zunaechst nur ein kontrollierter
numerischer E1-Befund. Memory, Feldzeit, Organisation, Semantik,
Selbstregulation und KI bleiben unbelegt.

Entscheidung:
`FRESH_FORMATION_CAPTURE_ONE_SHOT_BOUND_AWAITING_PREFLIGHT_AND_OWNER_AUTHORIZATION`.

## Bester naechster Schritt

Am besten geht es mit S1-FI weiter: einen statischen Frischlauf-Preflight fuer
den vorhandenen vorbereiteten AV-Eingabebestand und die aktuellen Ressourcen
implementieren. Noch keine Besitzerautorisierung und keine Ausfuehrung.
