# S1-GX: Deterministisches Einbatch-Pilotziel

Stand: 2026-08-15

Status: `ZIEL_GEBUNDEN_KEINE_FREIGABEANFRAGE_KEINE_AUSFUEHRUNG`

## Auswahlregel

Das spaetere kleinste Pilotziel wird ohne Ergebniskenntnis bestimmt:

```text
1. kleinste vorhandene Batchanzahl
2. erste Rolle der kanonischen S1-GF-Reihenfolge
3. exakter erster Batch mit Index 0
```

Die sechs Kandidaten besitzen folgende Batchzahlen:

```text
r2/AB 200   r2/BA 200
r4/AB 400   r4/BA 400
r8/AB 800   r8/BA 800
```

Damit ist eindeutig ausgewaehlt:

```text
Lauf: S1-GY-REAL-SINGLE-CARRIER-BATCH-PILOT
Rolle: r2 / fixed-adapter-ab
Batch: 0
Umfang: maximal 1 Adapteraufruf und 1 Feldschritt
```

Gebunden sind das exakte S1-GH-Fresh-Binding, sein unveraenderter initialer
S1-GN-Carrier und das konkrete erste Batchobjekt.

## Geschlossene Grenze

Es wurde keine Transition erstellt, kein Token erzeugt, keine Autorisierung
angefragt und kein Feldschritt ausgefuehrt. `ok weiter` bleibt nur der Auftrag
fuer diese statische Zielauswahl.

Entscheidung:

```text
R2_AB_FIRST_BATCH_DETERMINISTICALLY_BOUND_NO_AUTHORIZATION_REQUESTED
```

Dies ist eine technische Zielbindung, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GY erstellt einen abschliessenden nicht ausfuehrenden Gesamtpreflight fuer
dieses exakte Ziel gegen Gate, Autorisierungsschema, Tokenanforderung,
Receipt-Schema, Transition-Builder-Vertrag und Envelope. Erst nach bestandenem
Preflight kann eine separate ausdrueckliche Besitzerfreigabe angefragt werden.
