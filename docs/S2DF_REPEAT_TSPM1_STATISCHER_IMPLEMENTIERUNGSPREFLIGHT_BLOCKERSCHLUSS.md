# S2-DF Wiederholung: TSPM-1 bestandener Implementierungspreflight

## Auftrag und Grenze

Der S2-DF-Wiederholungsaudit prueft ausschliesslich statisch S2-DE zusammen
mit der vorrangigen S2-DG-Korrektur. Gegenstand sind die fuenf zuvor offenen
Materialisierungsbindungen sowie Quellen, Atomaritaet, Nichtzirkularitaet,
Abruf, Digests und Einmaligkeit.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe- oder
Runnerfunktion aufgerufen, keine Tests ausgefuehrt und keine Implementierung
geaendert. API, Paketexporte, Snapshot und Feldpfad bleiben unveraendert.

## B1: Expositions- und Probehuellen geschlossen

`TSPM1BoundExposure` und `TSPM1BoundProbe` sind nun getrennte exakte Typen.
Beide binden Konfiguration, Envelope, genau ein auditives und ein visuelles
Timed-Frame-Binding, deren Provenienz- und Eingabeprojektionsdigests sowie
das positiv ueberlappende gemeinsame Feldfenster.

Die Timed-Frame-Objekte muessen per Identitaet jeweils genau einmal im
passenden Stream des eingebetteten Envelopes vorkommen. Bildungs- und
Probehuelle sind nicht austauschbar. Extern gewaehlte Expositions- oder
Probe-IDs sind ausgeschlossen. B1 ist vollstaendig geschlossen.

## B2: Gemeinsame Konfigurationsbindung geschlossen

`TSPM1ConfigBinding` haelt den exakten Fast-Konfigurationszustand und das
exakte vorhandene `PPB1ReceptorProfileBinding`-Objekt zusammen. Dadurch sind
auditive und visuelle PPB-1-Konfiguration, Modalitaet, Geometrie,
Traegerinventar, Profil und beide Vertragsdigests atomar gebunden.

Ein Austausch nur einer PPB-1-Bank oder einer redundanten Digestrolle macht
die Gesamtbindung ungueltig. Es gibt genau eine Dimensionsquelle. B2 ist
vollstaendig geschlossen.

## B3: Owner, Initialisierung und Signaturen geschlossen

Der Owner ist an genau einen Konfigurationsdigest, einen Composite-
Vorzustandsdigest und einen Expositionsdigest autorisiert. Stabile Formen
fuer `AUTHORIZED`, `CONSUMED` und `FAILED`, ein nicht wiedereintretender Lock,
Busy- und Terminalverhalten sowie ein terminaler Fehler nach jedem
Post-Lock-Fehler sind eindeutig festgelegt.

Signaturen fuer Quellenbindung, Probehuelle, Initialzustand, lokalen Fast-
Kandidaten, atomaren `consume_once`-Schritt und read-only Probe sind
vollstaendig typisiert. Initial- und Folgezustandslineage sind ueber
Generation, Parentdigest und letzten Expositionsdigest bestimmt. B3 ist
vollstaendig geschlossen.

## B4: Slot-, Ereignis- und Receiptformen geschlossen

Freie und belegte Slots besitzen disjunkte vollstaendige Formen. Erzeugung,
Ersatz, nicht bereites Match, Konsolidierungscommit und Ablauf legen jede
Support-, Zeit-, Konsolidierungs- und Digestrolle eindeutig fest.

Das Receipt trennt genau ein Primaerereignis von Konfliktflag, geordneten
Ablaufdigests, optionalem Ersatzdigest, Konsolidierungsstatus und den zwei
PPB-1-Stabilitaetsachsen. Gleichzeitiger Ablauf und Primaeruebergang sind
damit ohne Mehrfachereignis darstellbar. Der lokale
`TSPM1FastTransitionCandidate` schliesst die vorher fehlende interne
Rueckgabeform. B4 ist vollstaendig geschlossen.

## B5: Originalframe und Probe-IDs geschlossen

Der Koordinator darf an `advance_ppb1_bank` ausschliesslich diese beiden
bereits im Envelope identitaetsgeprueften Objekte uebergeben:

```text
exposure.auditory.timed_frame.frame
exposure.visual.timed_frame.frame
```

Framekonstruktion, Fast-Slot-Schleife und alte Expositionswerte sind als
Konsolidierungsquelle verboten. Die beiden S1-WU-Probe-IDs werden
deterministisch aus Modalitaet und vollem Probe-Digest gebildet. B5 ist
vollstaendig geschlossen.

## Nichtzirkularitaetsaudit der Digests

Die Materialisierung besitzt folgende gerichtete Abhaengigkeit:

```text
Vertraege + PPB-Profil + Fast-Konfiguration
-> TSPM1ConfigBinding
-> BoundExposure oder BoundProbe
-> Composite-Vorzustand
-> lokaler Fast-Kandidat
-> Konsolidierungsentscheidung
-> optionale zwei PPB-1-Readouts
-> Composite-Nachzustand + Receipt
-> Owner-Nachzustandsprojektion ohne committed_result_digest
-> Step-Resultdigest
-> vollstaendiger CONSUMED-Owner mit committed_result_digest
-> Owner-Zustandsdigest
```

Der Resultdigest verwendet weder `committed_result_digest` noch den daraus
abgeleiteten vollstaendigen Owner-Zustandsdigest. Das Receipt bindet nur den
Owner-Autorisierungsvorzustand und keinen Owner-Nachzustandsdigest. Erst nach
Berechnung des Resultdigests werden der vollstaendige terminale Owner und
sein eigener Digest gebildet. Es existiert kein Selbstbezug.

Im Fehlerfall entsteht weder Receipt, Composite-Nachzustand noch Result. Der
Fehlerowner bindet nur Fehlercode, Ausnahmeart und Autorisierungsrollen. Auch
dieser Pfad ist azyklisch.

## Quellen- und Atomaritaetsaudit

Fast-Match und Konsolidierungsberechtigung entstehen ausschliesslich aus
Vorzustand und aktueller gebundener Exposition. PPB-Readouts und spaetere
Probe wirken nicht auf diese Entscheidung zurueck. Bei Berechtigung werden
genau zwei reine PPB-1-Schritte lokal berechnet. Erst nach deren vollstaendiger
Pruefung koennen Composite-Ergebnis und `CONSUMED`-Owner entstehen.

Scheitert der zweite PPB-1-Schritt, bleibt auch das erste lokale Ergebnis
unveroeffentlicht. Ein Retry mit demselben Owner ist ausgeschlossen. Damit
sind Konsolidierungsquelle, Nichtzirkularitaet und atomare Sichtbarkeit
vollstaendig materialisierbar.

## Read-only und Fail-Closed

Fast-, auditive PPB-1- und visuelle PPB-1-Befunde bleiben getrennt. Die drei
Kontextausgaenge `SLOW_PPB1_CONTEXT`, `FAST_ASSOCIATIVE_CONTEXT` und
`NO_COMPLETE_CONTEXT` sind vollstaendig und disjunkt. Frische Slow-Baenke
werden ohne S1-WU-Aufruf als `SLOW_UNAVAILABLE` behandelt.

Typ, Vertrag, Owner, Zustand, Quelle, Modalitaet, Geometrie, Traegerordnung,
Clock, Feldfenster und Atomaritaet besitzen eine feste Fehlerprioritaet.
Read-only Abruf prueft die drei Bankdigests vor und nach dem Abruf. Es gibt
keinen Nachzustand, keine Prototypwerte und keinen Feldhandoff.

## Entscheidung

Alle fuenf S2-DF-Materialisierungsblocker sind vollstaendig und
widerspruchsfrei geschlossen:

`PASS_TSPM1_REPEAT_STATIC_PREFLIGHT_ALL_FIVE_MATERIALIZATION_BINDINGS_CLOSED`

Der private TSPM-1-Fast-Kern ist damit fuer eine getrennte ausdrueckliche
Implementierungsfreigabe technisch vorbereitet. Der Befund ist noch keine
Implementierung, keine ausgefuehrte Memory-Funktion und keine Feldwirkung.

## Naechster Schritt

S2-DH kann nach ausdruecklicher Freigabe ausschliesslich den privaten
TSPM-1-Fast-Kern, die gebundenen Quellenhuellen, den atomaren Koordinator und
synthetische Vertragstests implementieren. PPB-1 muss unveraendert bleiben.
API, Snapshot, Produktion, Replay, reale Ausfuehrung und Feldintegration
bleiben gesperrt.
