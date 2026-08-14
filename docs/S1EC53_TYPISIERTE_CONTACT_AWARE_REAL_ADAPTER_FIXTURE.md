# S1-EC53: Typisierte kontaktbewusste Real-Adapter-Fixture

## Ziel

EC53 implementiert den EC52-Datenfluss als typisierten Adapter mit vier
injizierbaren Stufen:

1. Planauflosung;
2. Bildung;
3. Fresh-Field-Erzeugung;
4. Probe.

Die Abnahme verwendet ausschliesslich Nullschritt-Kerne. Keine reale
Schnittstelle wird aufgerufen.

## Ergebnis

- sechs Planreceipts fuer n1/n2 und r2/r4/r8;
- 24 Bildungsreceipts fuer vier Zustandsrollen;
- 48 Fresh-Field-Receipts mit identischem Felddigest und getrennten
  Objekttokens;
- 48 Probereceipts mit exakter Zustands-, Kernel- und
  Rueckwirkungszuordnung;
- null Feldschritte;
- keine Persistenz, Forschungsentscheidung oder Claims.

Der Adapter lehnt untypisierte oder falsch adressierte Receipts fail-fast ab.
Er bestaetigt nur die technische Orchestrierung, nicht die Funktion realer
Kerne.

Zwoelf fokussierte gemeinsame Tests bestehen.

Fixture-Digest:
`929d3cbb1b0fdb632a785cabe39d2ce76d888410b26cd77bfad73ae41d00042d`

## Naechster Schritt

Am besten geht es mit S1-EC54 weiter: die vier injizierbaren Schnittstellen
als private Wrapper um die bereits gebundenen realen Plan-, Bildungs-,
Fresh-Field- und Probe-Kerne implementieren. Die Wrapper werden zunaechst
nur statisch und mit kleinen kontrollierten Fixtures geprueft; die volle
Common-Probe-Matrix bleibt gesperrt.
