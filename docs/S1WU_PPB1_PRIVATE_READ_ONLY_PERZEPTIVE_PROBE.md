# S1-WU: Private read-only perzeptive Probe

## Auftrag und Grenze

S1-WU implementiert die in S1-WS gebundene Probe als privaten, reinen
In-Memory-Baustein. Ein spaeterer normalisierter Rezeptorzustand wird gegen
bereits stabilisierte private PPB-1-Zustaende verglichen. Das einzige
Ergebnis ist ein unveraenderlicher digestgebundener Befund.

Die Probe liefert keinen Nachzustand und aendert weder Bank noch Plaetze.
`advance_ppb1_bank`, der S1-WQ-Lebenszyklus, Prototypbildung, Stabilisierung,
Ablauf und Ersatz werden nicht aufgerufen. Oeffentliche API, Feldsnapshot,
Produktion, Dateisystem, Semantik und Feldrueckwirkung bleiben unberuehrt.

## Wiederverwendete Rollen

Die Implementierung verwendet die im S1-WT-Preflight bestaetigten privaten
Rollen:

- `_validate_state` und `_validate_frame`;
- `normalized_mean_l1_distance`;
- `_input_projection` und `_digest`;
- `PPB1BankState.digest` und `PPB1BankConfig.digest`;
- `_state_identity_payload` fuer die feste Bank-/Konfigurations-/Platzrolle.

Es gibt keine neue Distanz, Matchschwelle oder Gleichstandsregel.

## Probeablauf

1. Konfiguration, Bankzustand und Rezeptorframe werden validiert.
2. Die Probe muss dieselbe Clock verwenden und ein groesseres Kontaktende als
   der letzte gebundene Bankkontakt besitzen.
3. Nur belegte Plaetze mit `support_count >= stable_after` sind zulaessig.
4. Fuer diese Plaetze wird die vorhandene normalisierte L1-Distanz bestimmt.
5. Kleinste Distanz und danach lexikographische Platz-ID entscheiden.
6. Der vorhandene `match_threshold` trennt Match und Nicht-Match.
7. Vor Rueckgabe werden Bank- und Identitaetsdigest erneut auf
   Unveraendertheit geprueft.

Wenn kein stabilisierter Platz existiert, entsteht ein negativer Befund ohne
Platz, Distanz oder Prototypdigest. Bei vorhandenen stabilisierten Plaetzen
wird auch fuer einen Nicht-Match der naechste Platz mit seiner Distanz
ausgewiesen. Dadurch bleibt die Aehnlichkeitsmessung von der binaeren
Wiedererkennungsentscheidung getrennt.

## Read-only Befund

Der Befund bindet:

- Probe-, Bank- und Modalitaetsidentitaet;
- Konfigurations-, Bankzustands-, Zustandsidentitaets- und Probeinputdigest;
- Anzahl zulaessiger stabilisierter Plaetze;
- Matchentscheidung, naechste Platz-ID und Distanz;
- Digest, aber keine Werte des ausgewaehlten Prototyps;
- S1-WS-Vertrags- und S1-WT-Preflightdigest.

Der Befundtyp besitzt keine Rolle fuer Nachzustand, Prototypwerte, Semantik
oder Feldwirkung. Manipulierte Rollen, Digests und nichtendliche Distanzen
stoppen fail-closed.

## Reproduzierbare Abnahme

- S1-WU-Quelldigest:
  `1e47680f9c340149c99e0fb182fc1f25d475b773ce34b37a9d2103fad05303ef`
- Digest des gebundenen exakten synthetischen Befunds:
  `02929eab57e8ce7ec0ea6a66962138e93a75fcfec62f036f3f03a23d86ad02e4`
- Unveraenderter Bankzustandsdigest dieses Falls:
  `4908264cadaf0789e29937504b7745d9439f4344cff8540aed45fdb8fb9ffcc1`

`12 von 12` fokussierte synthetische Vertragstests bestehen. Sie pruefen
Match, Nicht-Match, fehlende Stabilisierung, Schwellenrand, Gleichstand,
Determinismus, kausale Clockgrenze, Anatomiefehler, Digestmanipulation,
fehlende Nachzustandsrollen sowie private API- und Snapshotneutralitaet.

S1-WU nimmt damit den privaten technischen Abruf- beziehungsweise
Wiedererkennungsbaustein ab. Daraus folgt noch kein Funktionsbefund fuer eine
vollstaendige perzeptive Memory und keine Feldwirkung.

## Naechster Schritt

S1-WV ist als rein statischer Abschlussaudit der S1-WU-Quelle vorgesehen.
Er muss Quellbindung, reine Rollenwiederverwendung, fehlenden Advance-Aufruf,
Unveraenderlichkeitspruefung, Befundschema und Oberflaechentrennung ohne
Ausfuehrung einer Probe- oder Zustandsfunktion bestaetigen.

## Grundlagen

- [S1-WS statischer read-only Probevertrag](S1WS_PPB1_STATISCHER_READ_ONLY_PERZEPTIVER_PROBEVERTRAG.md)
- [S1-WT statischer Implementierungspreflight](S1WT_PPB1_STATISCHER_READ_ONLY_PROBE_IMPLEMENTIERUNGSPREFLIGHT.md)
