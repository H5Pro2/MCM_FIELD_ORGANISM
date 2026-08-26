# S1-JT: Endlicher Adapterpayload-, Roundtrip- und Ausgabevertrag

## Ergebnis

S1-JT schliesst die in S1-JS festgestellten privaten Payload-, Roundtrip-,
Diagnostik-, Outputdigest- und Fehlerluecken. Alle Werte stammen aus den
bereits registrierten S1-JA-Konfigurationen. Kein Adapter ist implementiert
und kein Modellkern wurde aufgerufen.

## Gemeinsamer schneller Runtimekontext

Fuer B1 und B3 bis B6 sind exakt gebunden:

- `NeutralLocalFieldSubstrateConfig(1.0)`,
- `NeutralFastAfterimageConfig(0.5)`,
- `NeutralFieldDissipationConfig(0.0)`.

Diese Werte sind keine neue Auswahl. Sie entsprechen den vorhandenen
S1-JA-Records.

## Private Payloads

B1 verwendet `mcm.s1jt.b1-fixed-adapter.v1`. Das Payload enthaelt Aktivflag,
Basisrate, Geometriedigest und vollstaendige kanonische Kantenraten. Fuer die
Zweiknotenlinie ist die Rate `1.2`; fuer beide Kanten der Dreiknotenlinie
`1.1`. Die Werte folgen direkt aus festem leitendem Anteil, Kapazitaet und
Antwortzeit. Payload und `DTS1BackreactionResult` muessen exakt ineinander
ueberfuehrbar sein.

B2 verwendet `mcm.s1jt.b2-private-L.v1`. Jeder kanonisch geordnete Feldknoten
besitzt genau einen endlichen L-Wert im geschlossenen Bereich `[-1, 1]`.
Frische Sequenzen starten bei bitgenauem positiven Null. Der Rundlauf erfolgt
ueber `S2ReferenceState.development`.

B3 bis B6 besitzen feste Armidentitaeten und exakt die bereits registrierten
Raten, Kopplungswerte, Gesamtmasse, Rechneridentitaeten und
Konfigurationsdigests. Der M-Zustand bleibt im vollstaendigen Feld.

B6 bindet zusaetzlich den vollstaendigen Payload
`mcm.s1jt.b6-const-v-spec.v1` mit Modell-, Gleichungs- und Parameterrecord.
Sein kanonischer Spezifikationsdigest lautet:

`bd30dd584dd81d447aab6c55f24a99fbbdb89ad116b07ef0b831f65a41443172`

## B2-Feldabschluss

B2 liest S/H aus dem materialisierten Feld und L aus dem privaten Payload.
Generator und Rand werden nur aus Feldgeometrie, Distribution und dem
gebundenen schnellen Antwortrecord erzeugt. `model-b2` wird einmal ueber die
vollstaendige Dauer ausgewertet. Das resultierende S/H wird durch genau einen
normalen `SharedMCMField.advance` mit der urspruenglichen Distribution und
Schrittzeit abgeschlossen. Dadurch entstehen der Standardtick, Perzeption,
lokale Samples und letzte Distribution. Das resultierende L wird vollstaendig
als naechster privater Zustand ausgegeben.

## Ausgabe und Fehler

Drei Diagnostikvarianten sind gebunden: B1-exakt, B2-exakt und der vorhandene
F3-Runtimerecord fuer B3 bis B6. Der vollstaendige Ausgabepayload enthaelt nur
Schema-ID, Modellrolle, vollstaendiges Feld, naechsten privaten Zustand und
Diagnostik. Kontrolllabel, Envelope, Sequenz, Checkpoint, Integritaetsdigests
und Kandidatensidecar sind ausgeschlossen.

Die kanonische Darstellung verwendet endliche Binary64-Werte, normalisiert
negatives Null, sortiert Mapping-Schluessel und bildet kompaktes UTF-8-JSON
mit SHA-256. Jeder Fehler wird vor Ausgabe als
`DTS1PrivateBaselineAdapterError` vereinheitlicht. Teilausgabe, Reparatur und
Retry sind verboten.

## Entscheidung

`FINITE_PRIVATE_ADAPTER_PAYLOAD_ROUNDTRIP_OUTPUT_AND_ERROR_SCHEMAS_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`10a01aa9275a3bb571f3d5113126e90a0183d862c42cf1a9f8a2b58da1285d40`

S1-JT zeigt weder numerische Zulaessigkeit noch Baselinepassung oder
Kandidatenueberlegenheit. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JU darf ausschliesslich die privaten unveraenderlichen Payload-, Kontext-,
Diagnostik- und Ausgaberecords sowie die sechs Adapterbruecken gegen die
zwanzig technischen Klassen implementieren. Nur synthetische technische
Einzelintervalle und unabhaengige Kontrollreplikate sind erlaubt. Noch kein
Profilfall der 24-Fall-Matrix, kein gemeinsamer Vergleich, keine Runtime oder
Forschungsprobe.
