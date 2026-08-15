# S1-JN: Endlicher Materialisierungs-Identitaets- und API-Vertrag

## Ergebnis

S1-JN schliesst die in S1-JI verbliebenen statischen Identitaets-, API-,
Payload- und Atomaritaetsluecken. Zwei vollstaendige Feldschalen, sieben
private Zustandsrollen, exakte Materialisierungseingaben und eine atomare
Ausgabe sind gebunden. Noch ist kein Materializer implementiert.

## Feld- und Rezeptoridentitaeten

Gebunden sind eine offene Zweiknoten- und eine offene Dreiknotenlinie mit:

- festen Feld-, Layer- und Geometrieidentitaeten,
- `node-a`, `node-b` und bei Breite drei `node-c` an den Positionen 0, 1, 2,
- den Samplingoffsets `(-1)` und `(1)` ohne periodische Achse,
- auditiver technischer Modalitaet,
- je Geometrie eigener Rezeptorgeometrie und eigenem Dock,
- eindeutigen Zuordnungen `carrier-a -> node-a`, `carrier-b -> node-b` und
  gegebenenfalls `carrier-c -> node-c`.

Die S1-JH-Nullkontakte, Snapshotidentitaeten und Quellfenster werden um diese
fehlenden Angaben ergaenzt. Die gemeinsame Distributionszeit stammt
ausschliesslich aus dem monotonen S1-JK-Zeitplan.

## Frische und getragene Felder

Jede unabhaengige Sequenz beginnt bei Layer-Tick 0 ohne letzte Distribution,
lokale Samples oder vorangegangene Feldzeit. S/H und Dockkontakte beginnen bei
bitgenauem positiven Null, bevor genau eine registrierte Anfangs- oder
Grenzoperation wirkt.

DTS-1, B1 und B2 besitzen keinen eingebetteten M-/L-Zustand. B3 bis B6 tragen
nur ihren eigenen registrierten uniformen M-Zustand im Feld. DTS-1-Anatomie,
B1-Adapter, B2-L und die eingefrorene B6-Spezifikation bleiben getrennte
private Payloads.

Ab Ordinal 2 sind der genaue vorherige S1-JK-Intervalldigest und der erfasste
vollstaendige Modellausgangsdigest Pflicht. Die letzte Distribution des
getragenen Feldes muss auf demselben Takt exakt am Starttick des neuen
Intervalls enden.

## Reine API

Die spaetere Materialisierung erhaelt genau:

1. ein registriertes S1-JK-Envelopefixture,
2. eine der sieben Modellrollen,
3. das vollstaendige unveraenderliche Eingabefeld,
4. den vollstaendigen rollengerechten privaten Zustand,
5. den vorherigen Envelope-Digest oder bei Ordinal 1 `null`,
6. den vorherigen Outputdigest oder bei Ordinal 1 `null`.

Sie liefert atomar einen Orchestrierungsrecord mit zwei getrennten Teilen:

- Modellaufruf: materialisiertes Feld, Distribution, Zeit, Geometriedigest,
- Integritaet: Common Exposure, Private Prestate, Materialized Input und
  Orchestration Control Digest.

Nur die vier Modellaufrufwerte duerfen an einen spaeteren Adapter gehen.

## Vorzustandsoperationen

- `INITIAL_REGISTERED_SH` ersetzt nur S/H durch den registrierten
  P_IE-Anfangszustand.
- `CARRY_PRIOR_SH` erhaelt das vollstaendige Eingabefeld als identisches
  Objekt.
- `APPLY_BOUNDARY_2N` und `APPLY_BOUNDARY_3N` ersetzen nur S/H durch die
  jeweilige registrierte Grenze.

Identitaeten, Perzeptionen, Docks, Feldzeit, M/L und sonstiger privater Zustand
bleiben erhalten. Keine Operation verbraucht Zeit oder ruft ein Modell auf.

## Abnahmegrenze

Zwanzig technische Klassen pruefen Identitaeten, alle Rollen, 23
Envelopeobjekte, frische und getragene Provenienz, vier
Vorzustandsoperationen, Distribution und monotone Zeit, Digesttrennung,
Kanonisierung, Fail-Closed-Verhalten, Determinismus, Eingabeunveraenderlichkeit
und fehlende Modell-/Runtimepfade.

Jeder Fehler wird als einheitlicher
`DTS1CommonIntervalMaterializationError` ohne Teilausgabe, Reparatur oder
Wiederholung ausgegeben.

## Entscheidung

`FINITE_COMMON_INTERVAL_MATERIALIZATION_IDENTITIES_AND_API_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`b0edec20c6d27d98ba8a523c3034d8890b01cfe514eede1d72d05c2e548dd281`

S1-JN zeigt keine Materialisierbarkeit, numerische Zulaessigkeit,
Baselinepassung oder Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims
bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JO darf ausschliesslich die privaten unveraenderlichen Fixture-,
Modellaufruf- und Integritaetsrecordobjekte sowie den reinen Materializer
implementieren und gegen die 20 technischen Klassen pruefen. Noch kein
Baselineadapter, Modellaufruf, Profilvergleich, keine Runtime und keine
Forschungsprobe.
