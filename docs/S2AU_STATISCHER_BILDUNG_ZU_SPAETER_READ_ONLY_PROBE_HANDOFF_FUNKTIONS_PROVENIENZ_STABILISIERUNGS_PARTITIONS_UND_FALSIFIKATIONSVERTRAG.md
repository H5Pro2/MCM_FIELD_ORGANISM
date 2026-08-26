# S2-AU: Statischer Bildung-zu-Probe-Handoffvertrag

## Ziel und Grenze

S2-AU bindet ausschliesslich den spaeteren privaten Anschluss zwischen dem
bestehenden S2-AR-Bildungsergebnis und der bestehenden S1-WU-read-only Probe.
Es werden keine neue Speicher-, Distanz-, Match- oder Feldregel eingefuehrt.

Implementierung, Zustandsbildung, Probe, Tests, Baselines und Feldpfade bleiben
gesperrt.

## Gebundene Quellen

Der spaetere Handoff muss das vollstaendige Bildungsergebnis, dessen
urspruengliche Aktivbatch-Huelle und das urspruengliche digestgleiche Profil
gemeinsam erhalten. Dadurch werden beide Konfigurationen erneut gegen Profil,
Bildungshuelle und auditive sowie visuelle Nachzustaende geprueft.

Die Probeexposition stammt aus einer zweiten Aktivbatch-Huelle. Diese muss
dasselbe Quellmodell, Profil und dieselbe Feldclock verwenden, aber einen
anderen Batch- und Huelldigest besitzen. Sie enthaelt genau ein spaeteres
Frame pro Modalitaet.

## Stabilisierung und zeitliche Trennung

Vor einem Probeaufruf muss jeder getestete Modalitaetszustand mindestens einen
belegten Platz mit `support_count >= stable_after` enthalten. Die reine Anzahl
der Bildungsframes reicht dafuer nicht. Fehlt ein solcher Platz, ist der
Ablauf methodisch ungueltig und kein negativer Wiedererkennungsbefund.

Die Probeframes muessen dieselbe Modalitaet, Geometrie, Traegerreihenfolge und
Quellclock wie der jeweilige Nachzustand besitzen. Ihr Quellfenster beginnt
nicht vor dem Ende der Bildung und endet strikt danach. Auch in der Feldzeit
liegen die Probeframes nach allen Bildungsframes. Snapshotpaare und
Provenienz-Digests beider Abschnitte muessen disjunkt sein.

## Read-only Ergebnis

Der Partitionsdigest wird vor jedem Probeaufruf aus Formation, Profil, spaeterer
Probehuelle und beiden Probe-IDs gebildet. Danach darf die vorhandene S1-WU-
Probe genau einmal fuer Audio und genau einmal fuer Video aufgerufen werden.

Beide Befunde werden nur gemeinsam zurueckgegeben. Bank- und Eingabedigests
muessen nach beiden Aufrufen unveraendert sein. Das Ergebnis enthaelt keine
Bankzustaende, Prototypwerte, Nachzustaende oder Feldwirkung.

Ein technisch gueltiger Handoff darf `recognized = true` oder `false` liefern.
Die Entscheidung veraendert die Gueltigkeit des Anschlusses nicht. Ein
positiver Befund ist noch kein Vorteil gegen eine Baseline und kein
Memory-Befund.

## Naechster Schritt

S2-AV soll Vollstaendigkeit, Nichtzirkularitaet, kausale Partition und
Materialisierbarkeit dieses Vertrags statisch pruefen. Erst danach koennte eine
private Implementierung separat freigegeben werden.

Maschinenlesbarer Vertrag:
[S2AU_STATISCHER_BILDUNG_ZU_SPAETER_READ_ONLY_PROBE_HANDOFF_FUNKTIONS_PROVENIENZ_STABILISIERUNGS_PARTITIONS_UND_FALSIFIKATIONSVERTRAG_V1.json](S2AU_STATISCHER_BILDUNG_ZU_SPAETER_READ_ONLY_PROBE_HANDOFF_FUNKTIONS_PROVENIENZ_STABILISIERUNGS_PARTITIONS_UND_FALSIFIKATIONSVERTRAG_V1.json).
