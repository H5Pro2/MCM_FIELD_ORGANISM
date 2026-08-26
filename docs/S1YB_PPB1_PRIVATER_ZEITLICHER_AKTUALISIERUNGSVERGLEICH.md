# S1-YB: Privater PPB-1-Aktualisierungsvergleich

## Ausgefuehrter Umfang

S1-YB implementiert und durchlaeuft ausschliesslich die zehn synthetischen
S1-XZ-Plaene fuer PPB-1 und die eingefrorene S1-YA-Prototypbaseline:

- zwei Modalitaeten und fuenf getrennte Geschichten;
- gleiche Bildungs-, Aktualisierungs- und Probeinhalte;
- gleiche Kapazitaet und gleiche zeitliche Ordnung;
- Verhaltensgleichheit vor der Aktualisierungsphase;
- Kandidatenfortschreibung mit vorhandener S1-WQ-Rolle;
- unveraenderte Baseline mit S1-YA-Handoffreceipts;
- gepaarte S1-WU-read-only Proben;
- zehn atomare Geschichtsreceipts und ein Gesamtreceipt.

## Exakte technische Bilanz

- `20` Frischzustaende;
- `64` Kandidatenuebergaenge;
- `36` Baseline-Bildungsuebergaenge;
- `28` eingefrorene Baselinehandoffs;
- `32` Kandidatenproben und `32` Baselineproben;
- `32` gepaarte Vergleichsreceipts;
- kein Retry.

Alle zehn Geschichten stimmen vollstaendig mit der vorab gebundenen Fixture
ueberein. Alle Probeaufrufe lassen Kandidaten- und Baselinezustand
unveraendert.

## Ergebnis

Die `32` gepaarten Zellen ergeben:

- `14` strikte Vorteile fuer die gebundene Aktualisierungsfunktion;
- `14` Verhaltensgleichstaende;
- `4` vorab erwartete diagnostische Verluste fuer den frueheren Ursprung in
  H2 und H5;
- alle `10` verpflichtenden Vorteilsarme erfuellt;
- alle `10` Negativkontrollen sicher.

H3 trennt Ursprung und Konflikt B wie vorregistriert. H4 verdraengt den
Ursprung deterministisch und behaelt B sowie den neuen Gegenpol C. H2 und
H5 liefern fuer den aktualisierten Zielzustand in beiden Modalitaeten einen
strikt kleineren Abstand als die statische Bank.

Die technische Entscheidung lautet
`TEMPORAL_UPDATE_SYNTHETIC_FUNCTION_VALID_AGAINST_STATIC_PROTOTYPE`.
Der Gesamtreceiptdigest lautet
`55e074641953bec27de059c32d3720361337b65e5e47a6acd6aabfe03a06ab4b`.

`14 von 14` fokussierte S1-YB-Tests bestehen.

## Ergebnisgrenze

S1-YB bestaetigt die vorab definierte technische Funktion ausschliesslich
gegen die statische Prototypbaseline in synthetischen In-Memory-Geschichten.
Das ist noch kein Nachweis einer MCM-spezifischen Memory-Mechanik, keine
reale Wahrnehmungsleistung und keine Feldwirkung. API, Snapshot, Produktion
und Feldpfad bleiben geschlossen.

## Naechster Schritt

S1-YC soll den S1-YB-Quell-, Budget-, Receipt-, Ergebnis- und
Trennungspfad rein statisch auditieren. Keine erneute Runner-, Zustands- oder
Probenausfuehrung.
