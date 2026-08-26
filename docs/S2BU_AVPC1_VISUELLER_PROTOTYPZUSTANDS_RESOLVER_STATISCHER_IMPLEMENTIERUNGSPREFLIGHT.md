# S2-BU: Statischer Implementierungspreflight des visuellen Resolvers

## Ergebnis

Der in S2-BT gebundene private read-only Resolver ist ohne neue technische
Regel materialisierbar. Alle benoetigten Typen, Validatoren und
Identitaetsregeln existieren bereits im privaten PPB-1-/AVPC-1-Pfad.

Es verbleiben keine offenen Implementierungsblocker.

## Geplanter Minimalumfang

Eine spaetere Implementierung darf genau enthalten:

- einen privaten Fehlertyp mit den fuenf gebundenen Fehlerrollen;
- den eingefrorenen Ausgabetyp `AVPC1ReadOnlyVisualPrototypeState`;
- die reine Funktion `resolve_avpc1_visual_prototype_state`;
- lokale kanonische Digest- und Identifierhilfen.

Der Resolver verwendet die bestehenden Regeln `_validate_state`,
`_state_identity_payload`, `_prototype_digest`, `_bounded_values` und
`_positive_integer`. Eine zweite Prototypidentitaet, eine Distanz- oder
Gleichstandsregel sowie jeder Zustandsfortschritt sind ausgeschlossen.

## Materialisierungsfolge

Die spaetere Funktion validiert zuerst Eingabetypen und den positiven
Relationsbefund. Danach werden Relationsslot, Profil, visuelle Konfiguration,
Bankidentitaet und Bankdigest gebunden. Erst dann darf der Zieldigest gegen
die stabilisierten visuellen Slots gefiltert werden.

Nur genau ein Treffer ist zulaessig. Die Ausgabe wird abschliessend
eigenstaendig validiert und an alle Quelldigests gebunden. Vor der Rueckgabe
muessen alle Eingabedigests unveraendert sein.

## Testgrenze

Der spaetere synthetische Testumfang umfasst acht gebundene Rollen: gueltige
Aufloesung, vollstaendige Ausgabe, negative Relationsbefunde,
Relationssubstitutionen, Profil- und Banksubstitutionen, fehlende oder
mehrdeutige Ziele, Eingabeunveraenderlichkeit und die private Systemgrenze.

S2-BU selbst fuehrt keine Tests, Bankvalidierungen oder Resolverfunktionen
aus. S2-BV darf erst als eigener Schritt den privaten Resolver und genau diese
synthetischen Vertragstests implementieren.
