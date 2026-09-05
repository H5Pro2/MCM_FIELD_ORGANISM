# S2-MU: Fehlerbeobachtbarkeit der S2-MT-Laufhuelle

## Entscheidung

Die private S2-MT-Fehlerbeobachtung ist unter der Qualifikations-ID
`s2mu-neutral-failure-observability-20260905-01` neutral qualifiziert.

Der historische Lauf `s2mt-presealed-transfer-runtime-20260905-01` bleibt
unveraendert `NOT_EVALUABLE`. Es wurde kein neuer Hauptlauf ausgefuehrt und
kein fachlicher Transferbefund erzeugt.

## Korrektur

Ein unveraenderlicher `S2MTFailureReceiptV1` bindet ausschliesslich:

- eine der Phasen `SOURCE_PLAN`, `MATERIALIZATION`, `RUNTIME_INIT`,
  `EVENT_PROCESSING`, `RUNTIME_CLOSE` oder `EVALUATION`;
- die aktuelle Ereignisordinalzahl oder `None`;
- die Anzahl vollstaendig abgeschlossener Ereignisse;
- den letzten gueltigen Runtime-Snapshot-Digest oder `None`;
- einen phasengebundenen neutralen Fehlercode;
- Quellen-, Plan-, Konfigurations- und Runtimevertragsdigests;
- den kanonischen Fehlerbelegdigest.

Bei einem Fehler bleiben `execution` und `evaluation` `null`. Exceptiontexte,
Stacktraces, fachliche Rollen, Zielwerte und Teilbewertungen sind in der Form
nicht zulaessig. Der Verifikator rekonstruiert die vier Vertragsbindungen
unabhaengig und weist falsche Phase-/Code-, Fortschritts-, Snapshot- und
Digestkombinationen fail-closed ab.

Die Phasengrenzen wurden statisch an den tatsaechlichen Aufrufstellen des
Runners geprueft. Corpusmodul, Ereignisfolge, S2-MR-Runtime, Schwellen,
Rezeptoren und Memorymodule blieben unveraendert. Der Quellenplan behielt den
SHA-256
`ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`.

## Qualifikation

Genau ein Testaufruf wurde ausgefuehrt:

```text
python -m unittest -v tests.test_s2mu_private_transfer_failure_observability
```

Ergebnis:

- `8/8` Tests bestanden;
- Exit-Code `0`;
- terminales `OK`;
- alle sechs Phasenformen geprueft;
- kompakte kanonische Fehlerform unter 2.048 Byte geprueft;
- Unveranderlichkeit und Ausschluss von Teilresultaten geprueft;
- isolierte Phase-, Fortschritts-, Snapshot-, Code- und Bindungsmutationen
  fail-closed abgewiesen;
- keine Rezeptor-, Feld-, Memory-, Kontext- oder Hauptausfuehrung;
- Gate vor und nach der Qualifikation `False`;
- Einmalmarke vor und nach der Qualifikation unverbraucht.

Produkt- und Testquellhashes waren vor und nach dem Test identisch:

- Runner: `c8a76f797f3c8012291d61a6aedb6c9f48ddec1e5f6cd2e3a68b4a8fd67518e0`
- Verifikator: `ef8ee3fb444db075a49b30b529ee2372f55f563a8dc638bd73cbf16eef8cce2c`
- Test: `e034ae0decd805a4a5620d3101e4ce63cabfceab5be302cbc76a5406bb7f950a`

Damit darf ein neuer S2-MT-Transferlauf erst unter einer neuen Lauf-ID und mit
separater Freigabe erfolgen. Der bereits versiegelte Korpus bleibt dabei
unveraendert.
