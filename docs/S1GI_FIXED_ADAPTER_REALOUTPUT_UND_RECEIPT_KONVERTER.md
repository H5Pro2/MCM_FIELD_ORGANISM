# S1-GI: Fixed-Adapter-Realoutput und Receipt-Konverter

Stand: 2026-08-15

Status: `SYNTHETISCHE_AUSGABEGRENZE_KEIN_FELDLAUF`

## Zweck

S1-GI implementiert die fehlende typisierte Ausgabegrenze des Fixed-Adapter-
Zweigs und einen reinen Konverter in das gemeinsame 22-Feld-S1-FX-Receipt.
Die Abnahme verwendet ausschliesslich synthetisch konstruierte Rohvektoren.

## Getrennte Kausalevidenz

Der Fixed-Adapter-Zweig attestiert:

- den unveraenderten Quellzustand vor und nach der technischen Ausgabe;
- den unveraenderten Fixed Adapter vor und nach der technischen Ausgabe;
- den gemeinsamen Binding- und Probequellendigest;
- Anfangs- und terminalen Felddigest;
- geordnete Aktivierungs- und Nachhallvektoren;
- Schritt- und Supportbilanz.

Im gemeinsamen Receipt gilt bewusst:

```text
source_state_digest  = gesetzt, nur Herkunft/Attestierung
fixed_adapter_digest = gesetzt, tatsaechliche feste Kernursache
state_digest_before  = None
state_digest_after   = None
```

Damit wird der eingefrorene Adapter nicht als dynamische E1-Rueckwirkung
ausgegeben.

## Abnahme

Alle sechs r2/r4/r8- und AB/BA-Rollen lassen sich verlustfrei konvertieren.
Rohvektoren und Neuronenreihenfolge bleiben exakt erhalten. Kreuzbindung,
Digestmanipulation und falsche Erhaltungsangaben brechen fail-closed ab.

Die synthetische Ausgabe bilanziert die planmaessigen Schritte und Supports,
meldet aber `actual_field_steps_executed = 0`. Kein Batch, Feldkernel oder
Snapshot wird ausgefuehrt.

Entscheidung:

```text
FIXED_ADAPTER_TYPED_OUTPUT_AND_COMMON_RECEIPT_CONVERTER_COMPLETE
```

Diese Entscheidung ist eine technische Schemaabnahme und kein Mess-,
Substrat- oder Memory-Befund.

## Bester naechster Schritt

S1-GJ integriert die sechs S1-GH-Fresh-Field-Bindungen mit sechs synthetischen
S1-GI-Ausgaben und gibt die sechs gemeinsamen Receipts erst nach vollstaendiger
Validierung atomar zurueck. Der reale Fixed-Adapter-Kernel bleibt geschlossen.
