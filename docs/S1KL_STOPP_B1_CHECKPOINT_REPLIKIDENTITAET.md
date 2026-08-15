# S1-KL: STOPP wegen B1-Checkpoint-Replikidentitaet

## Befund

S1-KL prueft statisch die Beziehung zwischen der Replik-ID eines
vollstaendigen Outputs und den Replik-IDs seiner vier Checkpoints. Die
notwendige Identitaetsregel lautet: Jeder Checkpoint muss dieselbe
`replica_id` wie sein uebergeordneter Output tragen.

Die historischen B1-Ausgaben r4 und r8 verletzen diese Regel. Ihre jeweils
vier Checkpoints tragen die r2-ID. Betroffen sind damit zwei Repliken und
acht Checkpoints. B1/r2 sowie B2/r2, B2/r4 und B2/r8 sind nicht betroffen.

## Wirkung

Die numerischen Checkpoints, signed Komponenten und Adapterdiagnostik der
B1-Ausgaben werden dadurch nicht ungueltig. Auch der identitaetsneutrale
Refinement-Vergleichsdigest bleibt gueltig, weil die Checkpoint-Replik-ID aus
seinem Payload ausdruecklich ausgeschlossen ist.

Die vollstaendigen B1-r4/r8-v2-Provenienzoutputs sind jedoch keine korrekten
Provenienzrecords. Ihre bestehenden Digests bleiben unveraendert als
historische, manipulationssichere Belege des fehlerhaften Zustands erhalten.
Sie werden weder ueberschrieben noch uminterpretiert.

## Entscheidung

`STOP_C01_C05_COMPOSITION_EIGHT_B1_R4_R8_CHECKPOINT_IDENTITIES_REQUIRE_VERSIONED_CORRECTION`

Audit-Digest:

`5f19cfa319ee82838ec5a6af12d92d7e945591bdc5ba3f11ce4d499d4b86ebff`

## Grenzen

S1-KL aendert weder Runner noch Outputschema und fuehrt keine Replik oder
kein Intervall aus. Eine korrigierte C01-Komposition, die C05-Komposition und
jede weitere Matrixausweitung bleiben bis zur Korrektur gesperrt. Es folgt
kein Baseline- oder Kandidatenurteil.

## Naechster zulaessiger Schritt

S1-KM darf ausschliesslich einen versionierten Korrekturvertrag binden. Er
muss die Identitaet von Checkpoint und uebergeordnetem Output erzwingen, die
historischen v2-Ausgaben erhalten und eine kontrollierte Neuausfuehrung nur
von B1/r4 und B1/r8 mit hoechstens acht Intervallen vorsehen. Noch keine
Implementierung oder Ausfuehrung.
