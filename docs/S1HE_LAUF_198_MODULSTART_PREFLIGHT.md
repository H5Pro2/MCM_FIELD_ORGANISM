# S1-HE: Lauf-198-Modulstart-Preflight

S1-HE bereitet nach dem technischen Vorstartabbruch von Lauf 197 einen
getrennten Einstieg fuer einen moeglichen Lauf 198 vor. Die Startform ist
verbindlich der Projektwurzel-Modulstart:

```text
python -m tools.run_e1_s1gu_fixed_adapter_six_arm_lauf_198
```

Ein eigener `--import-preflight-only`-Modus prueft exakt diese Importstrecke,
ohne `main()`, Fixturekonstruktion, S1-GU, S1-GS oder einen Feldschritt
aufzurufen. Der reale Einstieg enthaelt weiterhin genau eine S1-GU-
Aufrufstelle mit S1-GS-Transition und S1-HB-Terminalabschluss sowie keinen
Writer, keine Persistenz und keinen Retry.

S1-HE ist keine Einmallauffreigabe. Eine reale Ausfuehrung von Lauf 198 bleibt
bis zu einer neuen ausdruecklichen Besitzerautorisierung geschlossen.
