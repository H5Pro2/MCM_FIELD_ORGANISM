# S1-YG: Statischer LPRH-1-Funktions- und Falsifikationsvertrag

## Funktionsgrenze

LPRH-1 darf spaeter genau einen stabil erkannten PPB-1-Prototyp read-only
aus dem gebundenen Bankzustand lesen und als separat typisierten lokalen
Kontext bereitstellen. Es fuehrt keine Feldkopplung aus und veraendert weder
Bank, Probe, Rezeptorframe, Dockabbildung noch Feldzustand.

S1-YG fuehrt keine Gleichung, Parameter, Implementierung oder Ausfuehrung ein.

## Read-only Herkunftsbindung

Ein positiver Handoff ist nur zulaessig, wenn gleichzeitig:

- die S1-WU-Probe positiv erkannt hat;
- Konfigurations- und beobachteter Bankzustandsdigest exakt passen;
- der Original-Probeinput den gebundenen Probeinputdigest reproduziert;
- genau der ausgewaehlte Slot vorhanden, belegt und stabil ist;
- sein Prototypdigest mit dem Probebefund uebereinstimmt;
- Modalitaet, Geometrie und geordnete Traeger mit Probe und Dockabbildung
  uebereinstimmen.

Ausgegeben werden duerften nur die exakten Prototypwerte dieses Slots. Eine
Transformation, Skalierung, Fusion oder Umordnung ist auf dieser Stufe
verboten. Ein gueltiger negativer Probebefund erzeugt nur ein ausdrueckliches
No-Context-Receipt. Jede andere Inkonsistenz bricht ohne Teilausgabe ab.

## Getrennter Kontexttyp

Der spaetere private Kontext muss Herkunftsdigests, Modalitaet, Geometrie,
Traeger- und lokale Neuronenzuordnung, exakte Prototypwerte, Probezeit,
Zielschritt und Einmaligkeitsidentitaet tragen. Er ist ausdruecklich kein
`ReceptorContactFrame`, kein Snapshotbestandteil und keine oeffentliche oder
produktive API-Rolle.

## Kausale Zeit und Einmaligkeit

Die vorhandene Quellenzeit des Probe-Rezeptorframes reicht fuer den
Feldhandoff nicht allein aus. Zusaetzlich muss die bereits vorhandene
Organismuszeit des zugehoerigen getakteten Rezeptorereignisses gebunden
werden.

Probe-Organismuszeit und Ziel-Feldschritt verwenden dieselbe Uhr. Der
Zielschritt beginnt exakt am Ende des Probeintervalls. Der Kontext gilt nur
fuer diesen einen gebundenen Vorschlag. Doppelte Handoff- oder Receipt-IDs in
einer Ausfuehrung brechen fail-closed ab.

## Getrennte duale Eingangsgrenze

Ein spaeterer privater experimenteller Envelope darf enthalten:

1. den vorhandenen `TransientNeuronInputSet` unveraendert;
2. optional einen getrennten lokalen LPRH-1-Kontextsatz.

Kontextwerte duerfen nie in die Sammlung der Rezeptorkontakte oder in den
Feldsnapshot eingehen. S1-YG legt noch nicht fest, ob und wie der Feldkern den
Kontext spaeter numerisch konsumieren koennte.

## Spaetere Kontrollen und Stoppregeln

Vor einer Feldwirkung muessen mindestens LPRH-OFF, reiner Digest ohne Werte,
eine Kopie des aktuellen Inputs, ein unverbundener kapazitaetsgleicher
stabiler Prototyp und der passende stabile Prototyp getrennt werden.

LPRH-1 wird gestoppt, wenn Herkunft und Inhalt nicht exakt bindbar sind,
Lokalisierung globale Fusion oder Umordnung verlangt, Kontext als Rezeptor
oder Snapshot gespeichert werden muesste, kausale Zeit oder Einmaligkeit
nicht pruefbar sind oder eine spaetere Wirkung bereits durch eine generische
Zusatzinputkontrolle erklaert wird.

## Blockerabschluss und Entscheidung

Die vier S1-YF-Blocker sind auf Vertragsebene geschlossen. Die duale Grenze
ist jedoch nur als Handoff-Anatomie geschlossen; eine Feldkopplung bleibt
gesperrt.

Alle `25 von 25` Vertragsrollen sind erfuellt:

`PASS_LPRH1_STATIC_HANDOFF_CONTRACT_FOUR_BLOCKERS_CLOSED_FIELD_COUPLING_REMAINS_BLOCKED`

Dies ist kein Nachweis einer Memory-Mechanik, Wahrnehmungsleistung oder
Feldwirkung. Der kanonische Vertragsdigest lautet
`85c783b34b812df5d3957552b6fa00c4502b5c0421558795d17956f60d4d826e`.

## Naechster Schritt

S1-YH darf ausschliesslich statisch Vollstaendigkeit, Nichtzirkularitaet und
eindeutige Materialisierbarkeit dieses Vertrags pruefen. Kein Code, kein
Kontextobjekt, keine Probeausfuehrung und kein Feldschritt.
