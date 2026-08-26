# S1-JM: Getrennte Expositions- und Vorzustandsintegritaet

## Ergebnis

S1-JM korrigiert die in S1-JL festgestellte Aequivalenzgrenze. Gemeinsame
aeussere Exposition, privater Modellvorzustand, materialisierte Eingabe und
Orchestrierungssteuerung erhalten vier getrennte Payload- und Digestrollen.
Kein Digest wird dem Modellkern als steuerbarer Eingabewert uebergeben.

## Vier Digestrollen

1. **Common Exposure Digest:** wertbasierter Digest aus Geometrie,
   S/H-Anfangs- oder Grenzwerten beziehungsweise Carry-Marker,
   Rezeptordistribution und Zeit. Er ist vor jedem Modellaufruf fuer alle
   sieben Rollen desselben Ereignisses bitgleich zu pruefen.
2. **Private Prestate Digest:** modelleigener Provenienzdigest aus
   vollstaendigem Feld, privatem Zustand sowie vorherigem Envelope- und
   Outputdigest. Gleichheit oder Ungleichheit zwischen Modellen ist weder
   gefordert noch ein Ergebnis.
3. **Materialized Input Digest:** reine Integritaetspruefung des nach der
   Vorzustandsoperation entstandenen Feldes samt Distribution, Zeit und
   Geometrie. Er bleibt im Adapterwrapper und ist kein Kernelargument.
4. **Orchestration Control Digest:** Reihenfolge, Ordinal, Intervalldigest,
   Checkpoint und gegebenenfalls DTS-1-Sidecar. Diese Daten bleiben beim
   Orchestrator.

## Modellseitige Grenze

Ein Modellaufruf erhaelt ausschliesslich:

- das materialisierte Feld,
- die Rezeptordistribution,
- den Zeitwert,
- den Geometriedigest.

Nicht uebergeben werden Digests, Payloads, Sequenz- oder Ordinallabel,
Profil, Arm, Fall, Grenzrolle, Checkpoint, Ziel, Ergebnis oder der private
Zustand eines anderen Modells. DTS-1-Sidecars bleiben fuer B1 bis B6
unerreichbar.

## Aequivalenzmatrix

- P_IE F_HIGH und R_HIGH besitzen in beiden Ordinalen dieselbe aeussere
  Exposition.
- P_IH liefert je Ordinal dieselbe aeussere Exposition an alle sieben Rollen.
- P_IK ist in Ordinal 1, 3 und 4 armgleich; Ordinal 2 unterscheidet sich
  vorregistriert als B gegen Gap.
- P_IN Recovery-on und Recovery-off sind in allen vier Ordinalen aeusserlich
  wertgleich. Nur der private DTS-1-Sidecar unterscheidet sich.

Checkpointdaten sind keine kausale Modelleingabe und werden deshalb nicht in
den Common Exposure Digest aufgenommen. Sie bleiben im getrennten
Orchestrierungscontrol.

## Kanonisierung

Alle Payloads duerfen nur primitive Werte, Listen und Mappings enthalten.
Objektrepraesentation, Speicheradresse oder Prozesszustand sind verboten.
Nicht endliche Zahlen brechen ab; negatives Null wird vor der Kodierung als
positives Null kanonisiert. Die Kodierung erfolgt als kompaktes UTF-8-JSON mit
sortierten Schluesseln und `allow_nan=false`, danach SHA-256.

## Entscheidung

`COMMON_EXPOSURE_PRIVATE_PRESTATE_AND_WRAPPER_INTEGRITY_ROLES_SEPARATED_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`1ca29d466c4244bf279eccfc3caf07d55e1ddcd73ab666ca48caf4eacdcb2f43`

S1-JM bindet noch keine vollstaendigen Rezeptor-/Dockidentitaeten und keine
ausfuehrbare Materialisierungs-API. Es wurde kein Modell ausgefuehrt.
Baselinepassung, Kandidatenueberlegenheit sowie Speicher-, Lern- und KI-Claims
bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JN darf ausschliesslich den endlichen statischen Identitaets- und
API-Vertrag fuer die Materialisierung binden: vollstaendige Feld-, Rezeptor-,
Dock- und Mappingidentitaeten, exakte Ein-/Ausgaben, Carry-Provenienz,
Validierungsreihenfolge und atomare Fehlergrenze. Noch keine Implementierung,
kein Adapter- oder Modellaufruf, keine Runtime und keine Forschungsprobe.
