# S1-ZK: Statischer Quelllayer-, Vorzustands- und Drive-Payload-Vertrag

## Ergebnis

S1-ZK schliesst den einzelnen S1-ZJ-Blocker statisch. Der gemeinsame
Ein-Neuron-Quelllayer ist nun als vollstaendiger kanonischer Payload gebunden:
Position null, Aktivierung `0.0`, Nachhall `0.125` und eine initiale
Tick-0-Perception ohne Rezeptorkontakt oder lokale Samples.

Aus diesem Payload sind literal gebunden:

- Neuronendigest;
- Quelllayerdigest;
- Feldvorzustandsdigest;
- Zielschritt-, Kontakt-, Transient- und Eingabebundledigest;
- erwarteter Digest des einzigen vorab abgeleiteten Drives.

Alle acht Arme verwenden dasselbe unveraenderliche Quelllayerobjekt und
dasselbe Eingabebundle. Die vier Vergleichspaare teilen zusaetzlich jeweils
denselben abgeleiteten Drive-Satz.

## Grenze

S1-ZK implementiert und berechnet nichts zur Laufzeit. S1-ZL muss die
kanonischen Payloads, literal gebundenen Digests und Objektidentitaetsregeln
statisch abnehmen. Erst danach koennte privater S1-ZM-Code freigegeben werden.

LPRH-1F bleibt generisch reduzierbares Engineering ohne Feldwirkungs-,
Memory- oder MCM-spezifischen Mechanismusbefund.

Maschinenlesbarer Vertrag:
[S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG_V1.json](S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG_V1.json).
