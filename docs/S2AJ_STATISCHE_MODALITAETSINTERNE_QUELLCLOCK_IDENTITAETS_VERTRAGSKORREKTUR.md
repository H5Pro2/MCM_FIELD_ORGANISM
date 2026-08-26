# S2-AJ: Statische modalitaetsinterne Quellclock-Korrektur

## Ergebnis

S2-AJ schliesst die in S2-AI gefundene Zeitidentitaetsluecke auf
Vertragsniveau. Jeder Audio- und Videostrom bindet kuenftig genau einen
`source_clock_id`.

Der Clock wird nicht als neuer Parameter uebergeben. Er stammt ausschliesslich
aus `frame.clock_id` des ersten Frames des jeweiligen nicht leeren Stroms.
Jeder weitere Frame muss exakt denselben Quellclock tragen.

## Getrennte Zeitrollen

Audio und Video duerfen unterschiedliche Quellclocks besitzen, weil sie in
getrennte PPB-1-Baenke gelangen. Quellticks werden weder zwischen den
Modalitaeten noch zwischen verschiedenen Clocks verglichen.

Innerhalb eines Stroms muss jeder spaetere `window_end_tick` den vorherigen
Endtick strikt uebersteigen. Ueberlappende Quellfenster bleiben zulaessig,
weil bestehende auditive Rezeptorfenster bei kleinerer Hopgroesse ueberlappen
koennen, obwohl ihre Endticks kausal fortschreiten.

Der kanonische Stromdigest bindet den abgeleiteten `source_clock_id`.
Die bestehenden Frame-Provenienzdigests enthalten den Quellclock bereits.
Batchdigest, Rezeptorframes und PPB-1-Eingabeprojektion werden nicht geaendert.

## Fail-Closed-Grenze

Wechselt der Quellclock innerhalb eines Modalitaetsstroms, entsteht weder ein
Teilstrom noch eine Huelle. Es findet keine Clockkonvertierung, Retiming-
Operation oder Reparatur statt.

## Naechster Schritt

S2-AJ enthaelt keine Implementierung und keine Ausfuehrung. S2-AK soll die
Gesamtbindung aus S2-AF, S2-AH und S2-AJ abschliessend statisch abnehmen.
Erst ein bestandener S2-AK-Audit kann eine spaetere private Implementierung
methodisch freigeben.

Maschinenlesbare Vertragskorrektur:
[S2AJ_STATISCHE_MODALITAETSINTERNE_QUELLCLOCK_IDENTITAETS_VERTRAGSKORREKTUR_V1.json](S2AJ_STATISCHE_MODALITAETSINTERNE_QUELLCLOCK_IDENTITAETS_VERTRAGSKORREKTUR_V1.json).
