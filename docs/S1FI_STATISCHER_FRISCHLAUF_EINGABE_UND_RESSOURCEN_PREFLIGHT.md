# S1-FI: Statischer Frischlauf-Eingabe- und Ressourcen-Preflight

## Formationseingaben

S1-FI loest den bestehenden kontrollierten AV-Bestand frisch und ohne alte
Laufidentitaet auf. Das neue Manifest enthaelt ausschliesslich sechs
Formationseingaben: Forschungsdescriptor, AV-Permutation, AB- und BA-Plaene,
neutrales Anfangsfeld und neutralen E1-Zustand. Probequelle und Probeplaene
werden nicht erzeugt oder gebunden.

Alle sechs Eingaben werden typisiert und digestgebunden. Der Preflight prueft
die AV-Quellintegrale gegen beide Planreihen, die r2/r4/r8-Schrittinventare,
die neutrale Anfangslage und die gemeinsame Geometrie aus 84 Feldknoten und
145 E1-Kanten.

## Ressourcen

Das gebundene Budget bleibt bei 15 Armen, 14.000 Feldschritten und maximal
2.175 gehaltenen Kantenbelegungen. Ein typisierter Windows-Snapshot liefert
den aktuell freien physischen Speicher. Mindestens 4 GiB muessen frei sein.
Die Ressourcenmessung selbst fuehrt kein Feld aus und schreibt keine Datei.

Ein bestandener Preflight lautet
`TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION`. Er autorisiert den
Lauf nicht. Ein Speicher- oder Eingabefehler liefert
`RESOURCE_OR_INPUT_PREFLIGHT_FAILED` ohne Teilstart.

## Grenzen

S1-FI fuehrt keine Formation, keinen Capture und keine Probe aus. Es erzeugt
keine Attempt-, Lock- oder Reportdatei und uebernimmt keine historische
Laufautorisierung. Memory, Feldzeit, Organisation, Semantik,
Selbstregulation und KI bleiben unbelegt.

## Bester naechster Schritt

Am besten geht es mit S1-FJ weiter: die neue Formation-Capture-Koordination
mit injizierten synthetischen Formationsergebnissen als vollstaendige
Trockenintegration abnehmen. Noch keine Besitzerautorisierung und keine reale
Feldentwicklung.
