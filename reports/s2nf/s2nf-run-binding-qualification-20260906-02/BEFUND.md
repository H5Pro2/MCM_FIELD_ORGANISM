# S2-NF: Quellenbelegform korrigiert und neutral qualifiziert

Status: **S2NF_RUN_BINDING_QUALIFIED**. Genau ein Qualifikationsaufruf,
**24/24**, Exit-Code `0`, `OK`. Kein Retry und keine Korrektur nach dem Lauf.
Ausgangscommit: `041b9d4`.
Qualifikations-ID: `s2nf-run-binding-qualification-20260906-02`.

## Aufruf und Vorbindung

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.

```text
C:\Python314\python.exe -m reports.s2nf.qualify_source_guard_once
```

Der neue Aufrufer hat vor der Ausfuehrung Syntax, geschlossenes Hauptgate,
geschuetzte Quellen sowie 24 eindeutige Test-IDs mit Zielpfaden geprueft und
in `preregistration.json` gebunden. Genau ein Testprozess wurde gestartet:

```text
C:\Python314\python.exe -m unittest tests.test_s2nf_private_run -v
```

`stdout.txt` und `stderr.txt` enthalten die unveraenderten Prozessausgaben.
`result.json` bindet diese und die neutralen Ergebnisartefakte.
Kanonischer Ergebnisdigest:
`08739f5e322aee06843151fbbcb250bcbd8ebbd4e2f963909490973be6afc7d0`.

## Eng begrenzte Korrektur

Nur die NF-Quellenbelegpruefung im Verifikator wurde produktseitig erweitert.
`check_source_binding` steht unmittelbar vor der unveraenderten Delegation
an `old._source`. Sie prueft die exakte Belegform, Ereignisidentitaet,
auditive Quelle, Payload-/Eltern-/Werte-/Framedigests und native Audiozeit.

Ein auditiver Cue verlangt fehlenden visuellen Frame und fehlenden
visuellen Payloadbeleg. Bei einer Formation werden Frameform, Geometrie,
Frameordinalzeit, Quellenordinalbindung und visuelle Digests geprueft.
Ein unzulaessiger visueller Cue-Beleg scheitert vor einem visuellen
Katalogzugriff. Der typisierte Fehler lautet `NF_SOURCE_BINDING_INVALID`.
Es gibt keine pauschale KeyError-Umdeutung oder erweiterte Akzeptanz
untypisierter Fehler. Korrekte Formations- und Cuebelege bleiben unveraendert
akzeptiert; die bestehende NE-Delegation prueft danach weiterhin den Inhalt.

## Qualifizierter Umfang

Die vier bisherigen Manipulationen sind eigene Testmethoden: fehlendes
Ereignis, vertauschte Ereignisse, fremder Formationsbeleg im Cue und fremder
Vorzustand. Keine dieser Kontrollen wird durch das Ergebnis einer anderen
verdeckt. Zusammen mit den unveraenderten uebrigen 15 Testmethoden und
fuenf neuen Bindungsgruppen ergeben sich 24 Tests.

Die neuen Gruppen pruefen gueltige Belegformen und Delegationsreihenfolge,
Audio-/Ereignis-/Zeit-/Digestmanipulationen, visuelle Cuebelege ohne
Katalogzugriff, visuelle Frame-/Ordinalbindungen sowie fehlende,
zusaetzliche und ungueltige Belegfelder. Semantische Manipulationen erhalten
auch neu berechnete Eigendigests; die Ablehnung haengt nicht nur von einem
veralteten Digest ab.

Die neutrale Gesamtaufzeichnung und ihre read-only Verifikation sind beide
`RECORDING_COMPLETE`: sechs Ereignisse, zwei neutrale Formationen, vier
Hinweise, 16 Abrufbelege, 320 Slotbesuche. Die Quellen sind synthetische
neutrale Zustandswerte, nicht die sieben versiegelten NF-PCM-Quellen.
Die beiden Direktbaselines stimmen mit ihren Primaerarmen ueberein.

Der absichtliche neutrale Verlust bleibt separat auswertbar:
`N=2, D=2, R=1, L=1`, funktional **FALSIFIED** fuer diese synthetische
Erhaltungsprognose. Leere Nenner bleiben `ERHALTUNG_NICHT_GEPRUEFT`.
Technisch gueltige Enthaltungen bleiben akzeptiert.

Der neutrale Gesamtbeleg umfasst 300.477 Byte, 1.152 Banddifferenzen,
288 Gleichheitsvergleiche, 1.440 Abrufwertvergleiche und 224 logische
Abrufoperationen. Die Formations-L1-Obergrenze betraegt 7.104 Terme.
Die bisherigen Tests fuer vollstaendige Scans, Arithmetik, Slow-Regel,
Read-only-Verhalten, Schreibkonflikte, Ressourcen und Fehlerabschluss
sind Bestandteil desselben Aufrufs.

## Unveraenderlichkeit und Grenze

Alle **71** vorab gebundenen Dateien besitzen identische Vor-/Nachhashes.
Die vollstaendige Liste steht in `result.json`. Vor dem Test wurden zudem
alle Quellen der fehlgeschlagenen Qualifikation gegen deren gespeicherte
Nachhashes geprueft, mit genau zwei erlaubten Aenderungen: NF-Verifikator
und NF-Testdatei. Der neue Qualifikationsaufrufer ist separat gebunden.

| Datei | SHA-256 vor und nach dem Lauf |
| --- | --- |
| tools/_s2nf_private_run_verification.py | c438c801793b832c39389ffcdae6bbb4021b043573be41ad9e09b7aba6ae51a8 |
| tests/test_s2nf_private_run.py | 44220e407217f65ed9b9867972e7ef9d154bd1c3420d9ed6385797028517042e |
| reports/s2nf/qualify_source_guard_once.py | 0107e98c30da0d001f32058595f7c76ae8ea20076ff0cd950ea3999941c7d0f2 |

Historische NE-Komponenten, NF-Quellenversiegelung, NF-Runner und Auswerter,
Regeln, Schwellen und Memorykerne blieben unveraendert. Die gesamte alte
Qualifikation `...-01`, einschliesslich ihres Aufrufers und Fehlbefunds,
bleibt unveraendert **NOT_QUALIFIED**; ihre Dateien sind mitgebunden.

NF-PCM-Erzeugung, Rezeptoranalysen, reale Hauptgeschichte, Feld- und
Runtimeausfuehrung: jeweils **0**. Der bestehende Test des gesperrten
Haupteinstiegs prueft nur die Gate-Ablehnung, keine Hauptausfuehrung.
`MAIN_GATE` bleibt **False**. Keine Quellenmaterialisierung oder separate
Rezeptormessreihe wurde eingeschoben.

Dieser Befund qualifiziert die technische NF-Laufanbindung, nicht den
Erhalt unter realer Konkurrenz. Die zwei frischen NF-Zustaende mit drei
Formationen und zehn Hinweisen bleiben einer separaten Freigabe vorbehalten.

RUECKMELDUNG ERFORDERLICH: Analystenpruefung und separate Einmallauffreigabe.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses Befunds
und danach gegebenenfalls der separaten Freigabe des NF-Funktionslaufs weiter.
