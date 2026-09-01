# S2-IT: Kompakte Receiptprojektion und statischer Codeaudit

Status: `S2IT_PRIVATE_COMPACT_RECEIPT_IMPLEMENTATION_STATICALLY_VALID`

## Grenze

S2-IT aendert ausschliesslich die private S2-IG-Aufzeichnungsprojektion und
deren unabhaengigen read-only Verifikator. Es wurden keine Projektmodule
importiert, keine Tests ausgefuehrt und keine Rezeptor-, Speicher-, Signal-,
Baseline- oder Runnerfunktion aufgerufen.

S2-IQ bleibt dauerhaft `NOT_EVALUABLE`. Das Hauptgate bleibt `False`. Die
unversionierte Bootstrap-Datei wurde weder gelesen noch veraendert. README,
Speicherkerne, API und Feldpfad bleiben unveraendert.

## Implementierte Projektionen

`CompactDualProbeBindingReceiptV1` speichert fuer jede der acht
`DUAL_PROBE_AND_ARM_INPUTS_BIND`-Operationen ausschliesslich:

- Case-Plan-, Kontextprobe- und Signalprobedigest;
- Dual-Binding-, Signalinput-, Baselineinput- und Quellenledgerdigest;
- Dual-Owner-ID und Dual-Owner-Prestate-Digest.

Der vollstaendige `DualProbeCaseBinding`, der vollstaendige Owner-Vorzustand
und beide nativen Arminputs bleiben waehrend der Ausfuehrung unveraendert im
Speicher. Sie werden lediglich nicht erneut vollstaendig serialisiert.

Die bestehende Signal-/Baseline-Aufzeichnungsprojektion erhaelt genau die drei
in S2-IS gebundenen Rekonstruktionsfelder:

- `invocation_id`;
- `input_digest`;
- `owner_prestate_digest`.

Die nativen Signal- und Baselineergebnisse, Owner-Zustaende und Receipts werden
nicht veraendert.

## Offline-Rekonstruktion

Der stdlib-only Verifikator rekonstruiert die Dual-Binding-Preimages aus den
bereits aufgezeichneten History-, Receptor-, Masked-Probe-, Registry- und
START-Belegen. Er prueft anschliessend:

- Case-Plan, typisierte Probenrollen und feste Ressourcenledger;
- Quellen-, Fixture-, Zeitfenster- und Parentbindung;
- Dual-Binding- und Dual-Owner-Prestate-Digest;
- native S2-IC-Result-, Owner-Poststate- und Receipt-Digests beider Arme;
- unmittelbare Nachfolgerbindung bis zum Case-Evidence-Beleg.

Fehlende, vertauschte, fremde, doppelte oder nachtraeglich widerspruechliche
Rekonstruktionsquellen erzeugen einen Verifikationsfehler. Ein Digest ersetzt
keinen fehlenden Elternbeleg.

## Groessen und Budgets

Die kanonische Huelle von `CompactDualProbeBindingReceiptV1` bleibt im
96-Zeichen-Worst-Case bei exakt `1.299` Byte. Die anhand der unveraenderten
S2-IS-Fallformen neu gebundenen Signal-/Baseline-Huellen bleiben bei maximal
`1.999` Byte. Der Verifikator erzwingt beide S2-IT-Obergrenzen zusaetzlich zu
den unveraenderten Registrygrenzen.

| Bindung | Wert |
| --- | ---: |
| Erfolgsoperationen | 183 |
| Ereignisse | 366 |
| Maximales Erfolgsbudget | 1.037.466 Byte |
| Maximales Fehlerpfadbudget | 1.044.634 Byte |
| Dual-Receipt-Maximum | 1.299 Byte |
| Arm-Receipt-Maximum | 1.999 Byte |

Keine Registryzeile, Einzelgrenze, Operationszahl, Ereigniszahl oder
funktionale Ressourcenposition wurde geaendert.

## Statische Nachweise

- AST-Parsing beider geaenderter Module: bestanden;
- exakte Datentraegerfelder: `10` Dualfelder und `24` Armfelder;
- Verifikator besitzt getrennte Dual- und Armrekonstruktion;
- `git diff --check`: bestanden;
- Hauptgate: `False`;
- Tests und Funktionsausfuehrungen: `0`.

Quell-SHA-256 nach S2-IT:

```text
tools/_s2ig_private_runner.py
1408971e056b08c718e3704d211d63b72a788b578ff70fe2077819a16a3c3e07

tools/_s2ig_private_result_verifier.py
12fcbf08f1ced3caaccf6ab97b4de0eb5497f22e9e1bb9c84f1992383fd6dfe4
```

## Entscheidung

Die S2-IT-Korrektur ist statisch implementiert. Sie erzeugt keinen neuen
Memory- oder Signalfunktionsbefund. Vor einem weiteren Hauptlauf ist eine neue,
separat freizugebende gemeinsame Qualifikation des aktuellen Testsatzes und
aller acht Signal-/Baseline-Aufrufstellen erforderlich.
