# S2-MW: Audio-Rezeptor-Kompatibilitaetsaudit

## Entscheidung

Der einmalig gestartete rezeptor-only Audit unter der ID
`s2mw-audio-receptor-compatibility-20260905-01` ist `NOT_EVALUABLE`.

Der Prozess stoppte vor dem Import des Projektrezeptors. Deshalb wurden weder
die 13 unveraenderten Audiorezepte analysiert noch ein gemeinsamer
Eingangsskalierungsfaktor abgeleitet oder geprueft. Ein dritter
S2-MT-Transferlauf bleibt gesperrt.

## Gebundener Auditpfad

Der private Auditpfad war statisch auf Folgendes begrenzt:

- 13 Originalanalysen durch `LogSpectralReceptor`;
- Erfassung von Maximum, betroffenen Baendern und Grenzueberschreitungen;
- genau ein gemeinsamer Faktor nach der Formel
  `nextafter(float32(1/global_original_maximum), float32(0))`;
- genau 13 Analysen der gemeinsam skalierten Eingaben;
- Neuberechnung aller 78 Rezeptpaardistanzen und der 12 gebundenen
  auditiven Cue-Distanzen;
- kein Clipping und keine Ausgangsnormierung;
- null Memory-, Feld-, Kontext- und Runtimeaufrufe.

Korpus und Rezeptor waren vor dem Aufruf an folgende Quellhashes gebunden:

- Quellenplan:
  `ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15`
- Audiorezeptor:
  `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0`

## Einmalaufruf

Genau ein Auditaufruf wurde ausgefuehrt:

```text
python tools/_s2mw_private_audio_receptor_compatibility_audit.py --output reports/s2mw/s2mw-audio-receptor-compatibility-20260905-01/result.json
```

Ergebnis:

- Exit-Code `1`;
- kein Ergebnisartefakt;
- `0` Rezeptoranalysen;
- `0` abgeleitete oder gepruefte Faktoren;
- `0` Memory-, Feld-, Kontext- und Runtimeaufrufe.

Der erste Fehler entstand beim Modulimport:

```text
ModuleNotFoundError: No module named 'mcm_field_organism'
```

Der direkte Dateistart setzte `tools/` statt des Workspace-Roots an den
Anfang des Python-Modulpfads. Der Fehler liegt damit im Aufrufweg des
privaten Auditwerkzeugs und liefert keinerlei Aussage ueber Quellen-,
Rezeptor- oder Distanzkompatibilitaet.

Es erfolgte kein Retry, keine Quellen-, Schwellen- oder Architekturanderung
und keine fachliche Interpretation. Der S2-MT-Korpus ist durch diesen
Versuch weder bestaetigt noch geschlossen.
