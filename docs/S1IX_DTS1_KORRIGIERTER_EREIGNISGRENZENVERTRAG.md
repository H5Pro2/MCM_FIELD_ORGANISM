# S1-IX: Korrigierter DTS-1-Ereignisgrenzenvertrag

## Zweck

S1-IX behebt ausschliesslich die in S1-IW festgestellte zeitliche
Fehlzuordnung der A/B/Gap-Ereignisse. Der Zustand bindet noch keine
Grenzwerte, Dauern, Parameter, Implementierung oder Ausfuehrung.

## Gemeinsame Grenzrollen

Vor jedem positiven Aktivintervall ersetzt ein zeitloser Grenzoperator nur
die vollstaendigen S/H-Vektoren des exponierten Dreiknotenfeldes. Fuer DTS-1
und B1 bis B6 gilt innerhalb eines Arms derselbe kanonische Grenzzustand:

- `A_BOUNDARY`: positive S1-HK-Beteiligung auf A und exakt null auf B.
- `B_BOUNDARY`: exakt null auf A und positive S1-HK-Beteiligung auf B.
- `GAP_BOUNDARY`: exakt null auf A und B.
- `PROBE_BOUNDARY`: ein vollstaendiger, innerhalb eines Arms identischer
  S/H-Vorzustand fuer den gemeinsamen Readout.

Die konkreten S/H-Vektoren bleiben offen. Sie duerfen nicht vom Arm, Fall,
Modell, Ergebnis, einem zukuenftigen Zustand oder einer verborgenen
Koordinate abhaengen.

## Grenzoperator und Zustandsfuehrung

Der Grenzoperator verbraucht keine Zeit und ruft keine Modellgleichung auf.
Er erzeugt weder Ressourcentransfer noch Feldschritt oder Checkpoint. Er
ersetzt ausschliesslich S/H und erhaelt folgende modelleigene Zustaende
bitgenau:

- DTS-1-Anatomie,
- fester B1-Adapter,
- B2-Zustand L,
- B3- bis B6-Zustand M.

Erst nach dieser Grenze wird die DTS-1-Beteiligung aus dem geklemmten
S-Vorzustand abgeleitet. Alle Modelle beginnen das anschliessende Intervall
mit demselben S/H-Zustand und ihrem jeweils erhaltenen internen Zustand.
Waerend des positiven Intervalls gilt ein gemeinsamer Nullkontakt an allen
Knoten. Die naechste Grenze ersetzt erneut nur S/H.

## Gebundene Ablaufstruktur

P_IK vergleicht `A-B-A` mit `A-Gap-A`. Nur die mittlere Grenzrolle
unterscheidet die Arme. Danach erhalten beide Arme dieselbe Probegrenze und
denselben Nullkontakt-Readout.

P_IN fuehrt in beiden Armen `A-Gap-B` mit identischen Grenzen und Kontakten
aus. Ausschliesslich der interne DTS-1-Recoverykanal ist waehrend des
Gap-Aktivintervalls an beziehungsweise aus. B1 bis B6 bleiben zwischen den
Armen konfigurations- und parameteridentisch und erhalten weder diesen
Schalter noch DTS-1-Beteiligung oder Ressourcenstaat.

Vorgrenz-, Nachgrenz- und Nachintervallzustaende werden spaeter jeweils mit
vollstaendigen S/H- und internen Zustandsdigests pruefbar gemacht. S1-IX
waehlt oder erzeugt diese Digests noch nicht.

## Fortgeltende Sperren

Die alten P_IK-/P_IN-Feldvektoren bleiben fuer den gemeinsamen Vergleich
gesperrt. Die direkten Ledgerbefunde bleiben erhalten. P_IE und P_IH werden
nicht veraendert. Eine kontrollierte Neuregistrierung darf keine alten
numerischen Ergebnisse wiederverwenden.

S1-IX zeigt weder Baselineabschluss noch Kandidatenvorteil oder eine
Speicher-, Lern- oder KI-Faehigkeit. Es wurden null technische und null
Forschungsfeldschritte ausgefuehrt.

## Entscheidung

`CORRECTED_COMMON_SH_BOUNDARY_EXPOSURE_CONTRACT_BOUND_NO_VALUES_OR_EXECUTION`

Kanonischer Vertragsdigest:

`7606b7b175cc7bbad64a89d917fa752ea56448ca054a703df62ccdab800064d3`

## Naechster zulaessiger Schritt

S1-IY darf nur einen endlichen statischen Fixturevertrag fuer die vier
Grenzrollen binden. Exakte S/H-Grenzvektoren, Dauern, strukturelle Nullfaelle,
Toleranzen und ein maximales technisches Aufrufbudget muessen vor jeder
Implementierung feststehen. Adapterkonfiguration, Modellausfuehrung, Runtime
und Forschungsprobe bleiben gesperrt.
