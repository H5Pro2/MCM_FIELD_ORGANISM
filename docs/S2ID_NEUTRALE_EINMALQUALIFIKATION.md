# S2-ID - Neutrale Einmalqualifikation

## Status

`S2ID_PRIVATE_TWO_AREA_CONFLICT_SIGNAL_QUALIFICATION_VALID`

Die private S2-IC-Signalbildung und ihre unabhaengige Direktbaseline wurden
genau einmal mit neutralen synthetischen A/B-Befunden qualifiziert.

```text
Testmodul: tests.test_s2id_private_two_area_conflict_signal
Testaufrufe: 1
Tests: 14/14
Exit-Code: 0
Terminal: OK
Wiederholung: keine
```

Es wurden keine B4-, TSPM-1-, PPB-1-, Rezeptor-, Feld- oder
Memory-Zustandsfunktionen aufgerufen. Die Tests erzeugten ausschliesslich
neutrale Instanzen der bereits qualifizierten privaten Befundtypen.

## Qualifizierter Umfang

- alle fuenf regulaeren Statuswerte;
- alle zehn Entscheidungspfade jeweils auch mit vertauschter A-/B-Belegung;
- `NO_CONTEXT` ausschliesslich bei zweimal `ABSENT_VALID`;
- `NO_APPLICABLE_CONTEXT` bei vorhandenem, aber nicht anwendbarem Kontext;
- exakte Regeln fuer `SINGLE_SOURCE`, `CONSISTENT` und `CONFLICT`;
- gleiche Status- und Differenzbefunde von Signal und unabhaengiger
  Direktbaseline;
- identischer Status bei A/B-Vertauschung ohne funktionale Rollenpraeferenz;
- alle acht Fehlercodes `S2HZ-E001` bis `S2HZ-E008` durch je eine isolierte
  Mutation;
- Fehlerabschluss ohne regulaeres Teilergebnis;
- atomarer Ownererfolg, terminale Wiederverwendungssperre und unveraenderliche
  Erfolgsobjekte;
- identische Vor-/Nachzustandsdigests fuer alle gueltigen read-only Aufrufe;
- alle erreichbaren Ledgerpaare `(P,K)` sowie maximale Owner-ID und
  Erfolgsartefakte innerhalb der gebundenen Grenzen;
- Ablehnung einer ID oberhalb der 96-Zeichen-Grenze vor Ownerbildung.

## Quellenbindung

Der statische Preflight hat die bereits vertraglich geforderte Relation
zwischen aktueller Probe und A/B-Bundle explizit in O1 geschlossen:

```text
bundle.probe_digest == probe.probe_digest
```

Diese Korrektur fuegt keine Funktion hinzu. Sie verhindert, dass ein formal
gueltiges Bundle einer anderen Probe als aktuelle Kontextquelle akzeptiert
wird.

## Quellhashvergleich

| Datei | SHA-256 vor/nach Lauf | Identisch |
| --- | --- | --- |
| `_s2ic_private_two_area_conflict_contract.py` | `625ea362bf08ca1aa808df992ca7ffda0d3382c42a57fcc5e8f4862696af6281` | ja |
| `_s2ic_private_two_area_conflict_signal.py` | `93578aa91bf16804bd57525604651e220c0fda69fea17840ce916e020a9d7cff` | ja |
| `_s2ic_private_direct_two_area_conflict_baseline.py` | `26b6063c9f794df92ab43581b7a8959db861c4af2c41bd329e047011a511dde3` | ja |
| `test_s2id_private_two_area_conflict_signal.py` | `9f64396031a0320628dffc20f5d4d68528b8c76dafe63d6c0c4882324e8059d2` | ja |

## Einordnung und Grenze

S2-ID bestaetigt die private technische Konflikt- und Konsistenzanzeige fuer
bereits vorhandene A/B-Kontextbefunde. Das Signal waehlt keinen Bereich,
veraendert keinen Speicher und wird vollstaendig durch den direkten Vergleich
beider rollenadressierter Ergaenzungen erklaert.

Es entstand kein Memory-, Lern-, Feld- oder automatischer Kontextwahlbefund.
Ein Funktionslauf mit tatsaechlich erzeugten A/B-Kontexten bleibt bis zu einer
separaten Planung und ausdruecklichen Freigabe gesperrt.
