# S2-AZ: Statischer korrigierter Handoff-Abschlussaudit

## Ergebnis

S2-AZ nimmt den korrigierten privaten Handoff statisch ab. Quelldigest,
einzelne Probe-Aufrufstelle, read-only Atomaritaet und private Grenzen stimmen.
Der S2-AX-Blocker ist ohne Rest geschlossen.

Der Audit hat weder Formation noch Handoff, Probe, Tests, Baselines oder Feld
ausgefuehrt.

## Aufrufstruktur

`_probe_modality_read_only` enthaelt als einzige private Stelle den Aufruf von
`probe_s1wu_perceptual_state`. Die Handofffunktion ruft diesen Helfer genau
zweimal auf, einmal fuer Audio und einmal fuer Video. Damit entsprechen
Quellstruktur und Laufzeitbudget dem S2-AV-Vertrag.

Die Vorpruefungen und der Partitionsdigest liegen weiterhin vor beiden
Helferaufrufen. Beide Befunde bleiben lokal, und ein Fehler beim zweiten Aufruf
liefert kein Teilresultat. Ergebnisanatomie, Distanz-, Match-,
Stabilisierungs- und Partitionsregeln sind unveraendert.

## Technischer Stand

Der private Pfad `Bildung -> Stabilisierung -> getrennte spaetere read-only
Probe` ist damit technisch und vertraglich geschlossen. Oeffentliche API,
Feldsnapshot, Produktion und Feldpfad bleiben unberuehrt.

Offen ist nun keine Anschlussmechanik, sondern der Vergleich. Der bisherige
positive und negative Wiedererkennungsbefund wurde noch nicht gegen die
staerkste einfache Baseline bewertet. Ein funktionaler Vorteil ist daher nicht
belegt.

## Naechster Schritt

S2-BA soll ausschliesslich statisch pruefen, welche bestehende oder kleine
einfache Baseline den aktuellen technischen Befund am staerksten erklaert und
ob die vorhandenen Fixtures fuer einen fairen Vergleich ausreichen.
Implementierung und Ausfuehrung bleiben dabei gesperrt.

Maschinenlesbarer Audit:
[S2AZ_STATISCHER_KORRIGIERTER_HANDOFF_QUELLDIGEST_AUFRUFSTELLEN_BLOCKERSCHLUSS_UND_GRENZENAUDIT_V1.json](S2AZ_STATISCHER_KORRIGIERTER_HANDOFF_QUELLDIGEST_AUFRUFSTELLEN_BLOCKERSCHLUSS_UND_GRENZENAUDIT_V1.json).
