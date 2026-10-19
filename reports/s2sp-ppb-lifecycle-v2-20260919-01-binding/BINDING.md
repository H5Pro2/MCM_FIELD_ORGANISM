# S2-SP: PPB-Lebenszyklus V2 – Einmallaufbindung

Lauf-ID: `s2sp-ppb-lifecycle-v2-20260919-01`  
Ausgabeverzeichnis: `reports/s2sp-ppb-lifecycle-v2-20260919-01`  
Vorstartstatus: nicht vorhanden.

Der Lauf verwendet ausschließlich die versiegelte OA-Quellenfolge
`reports/s2oa/s2oa-source-preseal-20260909-01`. Vor jeder Materialisierung
prüft der Runner deren Ausführungsdigest, Siegel, Profile und den aktuellen
Pinbestand; während der Verarbeitung prüft er jeden PCM- und RGB-Payloadhash.
Die Quellen werden einmal gemeinsam materialisiert und nicht persistiert.

| Aktive Bindung | SHA-256 |
|---|---|
| OA-Ausführungsplan | `bef171eb24a692bc10f44ad22edb1214ea3ccf462420143789624c409ca51ca1` |
| OA-Siegel | `5bfdb2e706b3607f49687ea20a14709f90af291f6b299d0d1056d51e1c96d50c` |
| Runner-Qualifikation `...-03` | `97162ade27f707d21d2cb23bbd5ae6725118eb58cb0911d55fb18de37e76eeaa` |
| Runner-Qualifikation `...-04` | `9160919a6151a4e9c118b934db2ab19757226c67d636229a0dd1e1a815edcecc` |
| OA-Materialisierungsadapter | `f47829c96094cb1979cbd94d1990a100aef6b574b6fb5ed8c3d3746ab147612c` |
| V2-Runner | `b923bc8af77a3a31a3d3dcba8e55084abded11a9ac7764bb3e7f4bcd33b36e16` |

## Gebundener Umfang

- 20 Ereignisse je Arm: 18 Formationen und zwei read-only visuelle Hinweise;
- zwei frische Memoryarme: `historical.v1` und `identity-preserving.v1`;
- 18 Audioanalysen, 18 NJ-Projektionen, 20 visuelle Analysen;
- vier Cue-Scans einschließlich unabhängiger Direktbaselines;
- kein Feldkontakt und keine Hypothesenanwendung;
- vollständiger Record, read-only Verifikation und getrennte Auswertung
  gemeinsam höchstens 262.144 Byte.

Die Erfolgsform besteht aus `record.json`, `verification.json` und
`evaluation.json`. Funktionsabweichungen werden ausschließlich in der
getrennten Auswertung ausgewiesen. Technische Quellen-, Form-, Bindungs- oder
Budgetfehler beenden den einmaligen Lauf ohne Retry. Das Gate wird in jedem
Fall zurückgesetzt.
