# S1-GK: Fixed-Adapter-Realwrapper-Vertrag

Stand: 2026-08-15

Status: `IMPLEMENTIERUNGSVERTRAG_AUSFUEHRUNG_GESCHLOSSEN`

## Gebundene Grenze

S1-GK verbindet die vollstaendige reale Eingabeseite aus S1-GH mit der
synthetisch abgenommenen atomaren Ausgabeseite aus S1-GJ.

```text
6 exakte Fresh-Field-/Invocation-/State-/Adapter-Gruppen
-> 6 geordnete Probeplaene
-> 2.800 Fixed-Adapter-Kernelaufrufe
-> 6 terminale Rohvektorausgaben
-> 6 gemeinsame Receipts
-> eine atomare Gesamtrueckgabe
```

Der Vertrag bindet 2.800 Feldschritte und 660 Supportereignisse. Der lebende
E1-Zustand dient nur der Vorher-/Nachher-Attestierung und darf nie an den
Fixed-Adapter-Kernel uebergeben werden.

## Ablauf

Vor dem ersten Kernelaufruf muessen alle sechs Eingabegruppen vollstaendig
validiert sein. Danach werden Rollen und Batches genau einmal in der
gebundenen Reihenfolge verarbeitet. Ein Snapshot und Receipt duerfen erst
nach vollstaendig abgeschlossenem Arm entstehen. Die Sechsergruppe darf erst
nach vollstaendiger Schlussvalidierung zurueckgegeben werden.

## Abbruchregel

Jeder Binding-, Digest-, Reihenfolge-, Zeit-, Dock-, Projektions-, Kernel-,
Vektor-, Bilanz- oder Erhaltungsfehler verwirft alle sechs Felder, Outputs und
Receipts. Es gibt kein partielles Ergebnis, keinen Retry, keine
Nachparametrierung und keine Persistenz.

## Freigabegrenze

Die private Realwrapper-Implementierung ist unter diesem Vertrag zulaessig.
Eine Ausfuehrung wird nicht freigegeben:

```text
Implementierung erlaubt: ja
Besitzerfreigabe vorhanden: nein
Ausfuehrung erlaubt: nein
Feldschritte ausgefuehrt: null
```

Entscheidung:

```text
FIXED_ADAPTER_REAL_WRAPPER_CONTRACT_BOUND_IMPLEMENTATION_ALLOWED_EXECUTION_CLOSED
```

## Bester naechster Schritt

S1-GL implementiert den privaten Sechsarm-Realwrapper hinter einer explizit
geschlossenen Ausfuehrungsgrenze. Seine Tests verwenden ausschliesslich
injizierte synthetische Batch-Kernels; der echte Fixed-Adapter-Kernel wird
weder als Standard gesetzt noch ausgefuehrt.
