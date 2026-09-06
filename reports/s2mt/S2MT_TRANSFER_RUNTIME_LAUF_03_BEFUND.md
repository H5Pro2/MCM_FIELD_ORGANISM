# S2-MT: Transferlauf 03

## Entscheidung

Der einmalige Lauf
`s2mt-presealed-transfer-runtime-20260906-03` ist methodisch
`NOT_EVALUABLE`.

Der Runner erzeugte zwar einen atomaren Record mit
`technical_status = RECORDING_COMPLETE`. Die anschliessende einzige
unabhaengige read-only Verifikation stoppte jedoch fail-closed, weil jeder
der 28 Runtime-Schritte einen fehlgeschlagenen Feldzweig bindet. Die im
Record enthaltene fachliche Evaluation wird deshalb nicht uebernommen oder
interpretiert.

Die frueheren S2-MT-Laeufe bleiben unveraendert `NOT_EVALUABLE`. Es gab
keinen Retry und keinen Parameterwechsel.

## Vorbindungen

Vor dem Hauptaufruf galten:

- `main` und `origin/main` standen auf
  `3b43f27eecfc25b68aab200734de6acb28bd2ce8`;
- das neue Ergebnisverzeichnis war nicht vorhanden;
- Runner-SHA-256:
  `ce71d863c054f1a0f6df41aa72f057c15586e51fb994e442fb2fd4130b706c6a`;
- Verifikator-SHA-256:
  `e58260c05d4914a2f3473b2804ae041f3ccf4ef18d0d108e40aa6867523a3df9`;
- skalierter Quellenplan-SHA-256:
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`;
- gemeinsamer Binary32-Eingangsfaktor:
  `0.989912331104279` beziehungsweise `e56a7d3f`;
- Hauptgate im Quellstand `False`.

Runner und Verifikator banden dieselbe neue Lauf-ID, denselben skalierten
V2-Quellenplan, dieselbe Quellenmenge und denselben S2-MW-Evidenzdigest.

## Einmaliger Hauptaufruf

`run_main_once` wurde genau einmal mit der autorisierten Lauf-ID aufgerufen.
Der Prozess endete mit Exit-Code `0`, erzeugte genau eine atomare
Ergebnisdatei und meldete danach:

```text
GATE=False
USED=True
```

Der Ergebnisbeleg bindet:

- Lauf-ID `s2mt-presealed-transfer-runtime-20260906-03`;
- Record-Digest
  `4a47f9c9b25f0a9c74a7ac03075c87563f88ca27b0dfa85fca12de89266413e8`;
- Datei-SHA-256
  `cc992e9c9e997ba03508439fdae8ff0a9f87cc92664b89f10ec35103190dae88`;
- Dateigroesse `148212` Byte;
- 28 Ereignisrecords.

## Einmalige read-only Verifikation

`verify_result_file` wurde danach genau einmal auf die unveraenderte
Ergebnisdatei angewendet. Der Aufruf stoppte mit Exit-Code `1` und:

```text
S2MTVerificationError: runtime event failed
```

Der Verifikator hatte zu diesem Zeitpunkt kanonische Serialisierung,
Record-Digest, Quellenbindungen, Lauf-ID, Quellenplan und Geometrie bereits
durchlaufen. Im Ereignispfad verlangte er fuer jeden Schritt:

```text
perception_status == FIELD_CONTACT_RECORDED
error_codes == []
```

Tatsaechlich binden alle 28 Ereignisse einheitlich:

```text
perception_status = FIELD_CONTACT_FAILED
error_codes       = [FIELD_BRANCH_FAILED]
```

Dies betrifft alle 20 Vollformationen und alle acht Teilhinweise. Die
Verifikation erzeugte daher keinen `verification.json`-Beleg. Sie wurde
nicht wiederholt.

## Aussagegrenze

Der Lauf ist kein auswertbarer Befund zu A/B-Stabilisierung,
C-Instabilitaet, A_RECENT-Verdraengung oder Hypothesenausgabe. Dass der
Runner trotz 28 fehlgeschlagener Feldzweige einen `RECORDING_COMPLETE`-Record
erzeugte, wird nicht nachtraeglich umgedeutet oder korrigiert.

Belastbar lokalisiert ist ausschliesslich eine technische Abweichung im
Feldgeschwisterzweig beziehungsweise dessen privater Adapterbehandlung. Der
skalierte Quellen- und Materialisierungspfad bleibt durch S2-MY qualifiziert;
Memory-, Kontext- und Transferfunktion werden aus Lauf 03 nicht bewertet.
