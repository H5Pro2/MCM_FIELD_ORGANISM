# W7-AW: Vertrag fuer Observer-eigenen Aufloesungs- und Profilvergleich

## Entscheidung

`OBSERVER_PROFILE_EVALUATION_PREREGISTERED`

W7-AW legt wertfrei fest, wie die W7-AV-Rohkontraste spaeter aufgeloest,
normalisiert und mit Feldprofilen verglichen werden duerfen. Der Vertrag
nimmt keine Ergebniswerte entgegen und trifft keine Profilentscheidung.

## Observer-eigener Numerikboden

Der Observerboden stammt ausschliesslich aus 105 identischen Wiederholungen
derselben Modell-, Pfad- und Checkpointprobe:

```text
observer_epsilon = max gleicher Wiederholungsabstaende
observer_effect_floor = 10 * observer_epsilon
```

Sind alle Identitaetsabstaende exakt null, bleibt der Boden null. Ein Profil
ist nur aufgeloest, wenn sein eigener Anfangseffekt strikt ueber diesem Boden
liegt. Es gibt keine Epsilonersetzung. Der W7-AT-S/H-Feldboden wird nicht auf
Observerausgaben angewendet.

## Profilbildung

Pro Modell werden AB und BA spiegelbildlich aus je drei W7-AV-Kurven gebildet:
alte Wirkung unter Gegenkontakt, alte Wirkung nach Unterbrechung und neue
Wirkung nach altem Kontakt. Jede Kurve wird durch den eigenen aufgeloesten
Anfangseffekt der alten Gegenkontaktwirkung geteilt. Die jeweilige
Neutral-vor-neu-Kurve bleibt eine verpflichtende Auditkontrolle, ist nach
W7-O aber keine vierte Profilkoordinate.

## Erklaerungsvergleich

Der Abstand zweier Profile ist das Maximum aller absoluten Differenzen ueber
drei Kurven und fuenf Checkpoints. Ein Observermodell kann ein Feldprofil nur
dann erklaeren, wenn AB und BA jeweils hoechstens `0.05` entfernt sind. Bei
mehreren Treffern gilt unveraendert `LEAK > SAT > NORM`.

Zulaessige spaetere Ausgaben sind ausschliesslich `NOT_RESOLVED`,
`PROFILE_NOT_MATCHED`, `PROFILE_EXPLAINED_BY_LEAK`,
`PROFILE_EXPLAINED_BY_SAT` oder `PROFILE_EXPLAINED_BY_NORM`. Auch eine
Observererklaerung ist kein Feldfunktions- oder Memorybefund.

## Naechster Schritt

W7-AX darf einen reinen In-Memory-Auswerter fuer Wiederholungskontrollen und
Observerprofile implementieren. Eine Erklaerungsentscheidung bleibt gesperrt,
solange keine rollenrein gebildeten CAP-Feldprofile fuer beide Richtungen
vorliegen.
