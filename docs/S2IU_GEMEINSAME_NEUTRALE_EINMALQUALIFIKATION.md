# S2-IU: Gemeinsame neutrale Einmalqualifikation

S2-IU qualifiziert den aktuellen S2-IC-Quellstand gemeinsam mit Bootstrap-Lifecycle, `ParentSetV1`, append-only Recorder, unabhaengigem Verifikator und den kompakten S2-IT-Aufzeichnungsprojektionen.

Die aktive Suite wurde vor dem Lauf statisch auf 42 eindeutige Test-IDs und 42 eindeutige Zielrollen gebunden. Sie bestand aus 14 Status- und Fehlerpruefungen, 20 Laufhuellenpruefungen und acht neuen ID-/Receiptpruefungen. Der einzige erlaubte Testaufruf bestand vollstaendig mit Exit-Code `0` und terminalem `OK`.

Die Qualifikation bestaetigt insbesondere:

- 154 gueltige und eindeutige Invocation-/Owner-IDs;
- 183 gueltige und eindeutige Operations-IDs;
- acht tatsaechlich erreichte Signal-/Baseline-Aufrufpaare;
- kanonische Offline-Rekonstruktion der kompakten Dual- und Armreceipts;
- getrennte fail-closed Ablehnung fehlender, vertauschter, fremder und manipulierter Rekonstruktionsfelder;
- unveraenderte Grenzen von 1.299 und 1.999 Byte;
- unveraenderte Registry `183/366` und Pfadbudgets `1.037.466/1.044.634`;
- unveraenderte Produkt- und Testquellen waehrend der Ausfuehrung;
- geschlossenes Hauptgate.

S2-IU ist kein Memory-Funktionslauf. Es wurden keine realen Geschichten oder Memory-Zustandsfunktionen ausgefuehrt. S2-IQ bleibt dauerhaft `NOT_EVALUABLE`; ein neuer Fuenf-Status-Hauptlauf benoetigt eine eigene Freigabe.
