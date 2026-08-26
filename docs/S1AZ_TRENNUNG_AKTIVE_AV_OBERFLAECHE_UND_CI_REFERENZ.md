# S1-AZ: Trennung aktive AV-Oberflaeche und C_i-Referenz

## Status

Technische API-Bereinigung. Keine neue Mechanik, kein Forschungslauf und kein
Memory-, Substrat- oder KI-Befund.

## Ausgangslage

S1-AV klassifiziert `C_i` als abgeschlossene technische Referenzbaseline.
Im Modul `mcm_field_organism.current_api` lagen seine acht Rollen jedoch noch
im Manifest `CURRENT_CONTROLLED_FIELD_EXPORTS`. Damit waren aktive
AV-Engineeringrollen und die abgeschlossene C_i-Referenz begrifflich
vermischt, obwohl die Funktionen selbst getrennte Module besitzen.

## Umsetzung

Die acht vorhandenen Rollen wurden in ein eigenes Manifest verschoben:

```text
CI_REFERENCE_EXPORTS
```

Enthalten bleiben:

```text
CIAccommodationBaselineError
CIAccommodationConfig
CIAdvanceResult
CIState
apply_ci_backreaction
advance_ci_accommodation
advance_ci_from_field_snapshot
advance_ci_null_exposure
```

`current_api.__all__` enthaelt sie weiterhin. Bestehende explizite Importe
bleiben deshalb kompatibel. Es wurde keine Funktion, Signatur, Gleichung oder
Zustandsdarstellung veraendert.

## Neue technische Grenze

```text
CURRENT_CONTROLLED_FIELD_EXPORTS = aktive kontrollierte Feld-Engineeringrollen
CI_REFERENCE_EXPORTS            = abgeschlossene C_i-Referenzbaseline
F3_REFERENCE_EXPORTS            = vorhandene F3-Referenzbaseline
S1B_REFERENCE_EXPORTS           = opt-in S1-B-Referenzpfad
```

Manifesttests sichern Vollstaendigkeit, paarweise Trennung der
Referenzgruppen vom aktiven Kern und die fortbestehende Importierbarkeit der
C_i-Namen ab.

## Aussagegrenze

Die neue Gruppierung wertet C_i nicht auf. C_i bleibt gegen leaky im
Nullkontakt nicht hinreichend eigenstaendig und ist kein MCM-Memory-Kandidat.
Die Aenderung beseitigt nur eine technische Rollenvermischung.

## Bester naechster Schritt

Als naechstes wird der aktive Kern manifestgenau darauf geprueft, ob nach der
C_i-Ausgliederung noch weitere abgeschlossene Substrat- oder Versuchsnamen in
`CURRENT_CONTROLLED_FIELD_EXPORTS` liegen. Nur konkret gefundene
Fehlklassifikationen duerfen kompatibel verschoben werden.

