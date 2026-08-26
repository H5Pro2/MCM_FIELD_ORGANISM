# S1-JI: STOPP wegen unvollstaendigem Materialisierungsschema

## Ergebnis

S1-JI stoppt vor der Implementierung der gemeinsamen Intervallhuelle. Die in
S1-JH gebundenen Werte, Sequenzen, Digests, Sidecars, Budgets und
Quarantaeneregeln bleiben gueltig. Sie reichen jedoch noch nicht aus, um die
Huelle ohne neue implizite Festlegungen in vollstaendige MCM-Objekte zu
materialisieren.

## Gebundene Grundlage

S1-JH liefert sieben eindeutige Sequenzen, 23 Intervalle, zwei Geometrien,
sechs S/H-Vorzustandsquellen, geometriebreite Nullkontakte, Trageridentitaeten,
Quellfenster und einen neutralen positiven Zeitwert. Kandidatenseitige
Sidecars bleiben korrekt ausserhalb der Huelle.

## Fehlende Bindungen

Vier unabhaengige Gruppen sind noch offen:

1. **Rezeptor- und Dockidentitaet:** `modality_id`,
   `receptor_geometry_id`, `dock_id` und die vollstaendige
   Carrier-zu-Neuron-Zuordnung fehlen.
2. **Feldeingabe- und Vorzustands-API:** Die Rollen fuer das vollstaendige
   Eingabefeld, den vorherigen Intervalldigest, die Direktivenauswahl und die
   Erhaltung modelleigener L-/M-Zustaende sind nicht als API gebunden.
3. **Modellseitiges Eingabedigest-Schema:** Es fehlt eine kanonische,
   ausschliesslich wertbasierte Serialisierung fuer Feld, Distribution, Zeit
   und Geometrie. Objekt-Repr, Prozessidentitaet oder implizites Hashing sind
   unzulaessig.
4. **Atomare Ausgabe- und Fehlergrenze:** Unveraenderliche Objektformen,
   Validierungsreihenfolge, Fehleruebersetzung und Teilausgabeverbot sind noch
   nicht festgelegt.

Die vorhandenen Konstruktoren verlangen diese Angaben fuer
`ReceptorContactFrame`, `DistributedReceptorContact`,
`ReceptorNeuronDockMap` und die Dockpruefung von `SharedMCMField`. Eine Wahl
erst im Implementierungscode waere eine nicht vorregistrierte Erweiterung der
Exposition.

## Konsequenz

Kein Fixture- oder Modellansichtsobjekt ist implementierungsbereit. Alle 24
Baseline-Rollen-Block-Faelle bleiben blockiert. Es wurde kein Feld,
Ressourcenmodell oder Baselinekern aufgerufen und kein technischer oder
forschungsbezogener Feldschritt ausgefuehrt.

## Entscheidung

`STOPP_PRIVATE_COMMON_INTERVAL_FIXTURE_IMPLEMENTATION_MATERIALIZATION_SCHEMA_INCOMPLETE`

Kanonischer Auditdigest:

`652fea995a72b1dd8b7ed0ae4845a43dfd36327402206c25516db5d787c60b30`

Der STOPP ist kein negativer Funktionsbefund zu DTS-1. Baselinepassung,
Kandidatenueberlegenheit sowie Speicher-, Lern- und KI-Claims bleiben
unentscheidbar und gesperrt.

## Naechster zulaessiger Schritt

S1-JJ darf ausschliesslich einen korrigierten statischen
Materialisierungsschemavertrag binden. Er muss die fehlenden Identitaeten, die
reine Ein-/Ausgabe-API, kanonische Wertpayloads und Digests sowie atomare
Fail-Closed-Regeln vollstaendig festlegen. Noch keine Implementierung, kein
Adapter- oder Modellaufruf, keine Runtime und keine Forschungsprobe.
