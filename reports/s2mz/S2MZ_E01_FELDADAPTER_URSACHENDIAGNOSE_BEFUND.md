# S2-MZ: e01-Feldadapter-Ursachendiagnose

## Entscheidung

Die einmalige Diagnose
`s2mz-e01-field-adapter-diagnostic-20260906-01` hat die erste
deterministische Abbruchursache im privaten Feldgeschwisterzweig eindeutig
lokalisiert:

```text
Materialisat:       s2mt-transfer-field-clock
S2-LO-Feldadapter:  s2ln-role-free-field-clock
Exception:          ReceptorTimeAlignmentError
Pruefphase:         RECEPTOR_TIME_SEQUENCE_BINDING
```

Der Adapter erzeugt eine `ReceptorTimeSequence` mit seiner fest gebundenen
S2-LN-Uhr. Die beiden gueltigen `timed_frames` von `e01` tragen dagegen die
S2-MT-Felduhr. `ReceptorTimeSequence.__post_init__` lehnt diese Mischung mit
`sequence identity must match every timed receptor state` ab.

Damit liegt ein enger Adapterbindungsfehler vor. Feldkern, Wahrnehmungswerte,
Memory und Kontext sind durch diese Diagnose nicht negativ bewertet. Ein
weiterer Transferlauf bleibt gesperrt.

## Einmaliger Aufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m tools._s2mz_private_e01_field_adapter_diagnostic --workspace . --output reports/s2mz/s2mz-e01-field-adapter-diagnostic-20260906-01/result.json
```

Es gab keinen Retry. Der Prozess endete mit Exit-Code `0`. Der direkte
S2-LO-Feldadapter wurde genau einmal aufgerufen. S2-MR-Runtime, Memoryzustand,
Kontext und S2-MT-Hauptlauf wurden nicht aufgerufen.

Der atomare Diagnosebeleg bindet:

- Status `S2MZ_FIELD_ADAPTER_CAUSE_LOCALIZED`;
- Record-Digest
  `e04524f0cda2ab0048f58996922603bf599ff454c837bf3a00dda70d95656ea0`;
- Datei-SHA-256
  `fe839664777493e9db6aa8f94685abf84396c67d0be1a3cd41bc2542d7750301`;
- Dateigroesse `5148` Byte;
- genau ein verwendetes Ereignis, `e01`.

## Eingangspruefung

`e01` stammt aus dem qualifizierten skalierten S2-MT-Materialisat. Separat
bestaetigt wurden:

- exakter Eingangstyp `S2LOFieldInputV1`;
- positives gemeinsames Zeitfenster `0..100000000`;
- genau zwei `timed_frames` in der Reihenfolge Audio, Video;
- Projektionsdigest
  `f0e1f07c6397c7d1fc690e533253070f2c5b8d26a5cb29d68a30145df7776670`;
- Ereignis- und Eingangsprojektion sind digestgleich;
- 48 endliche, normalisierte Audiowerte;
- 288 endliche, normalisierte visuelle Werte;
- beide Frames tragen `s2mt-transfer-field-clock`;
- native Audiozeit `audio.sample:0..4800`;
- native Videozeit `video.frame:2..3`;
- frischer Feldzustand `PRE_CONTACT`, Schritt `0`, letzter Endtick `0`.

Die Dockbindung besteht aus genau zwei Docks mit 48 beziehungsweise 288
Paaren. Alle `336` Dockpaare sind eindeutig und ueberschneidungsfrei.

## Abbruchphase

Die Originalexception wurde unveraendert nach Klasse, Modul, Meldung und
Pruefphase erfasst:

- Klasse `ReceptorTimeAlignmentError`;
- Modul `mcm_field_organism.receptor_time_model`;
- Blattfunktion `__post_init__`, `receptor_time_model.py:53`;
- Meldung `sequence identity must match every timed receptor state`;
- Phase `RECEPTOR_TIME_SEQUENCE_BINDING`.

Der Abbruch geschieht vor Proposal-Handoff, Dockprojektion, Feldschritt und
Publikation eines Feldnachzustands. Deshalb sind `336` erwartete Kontakte
vollstaendig gebunden, aber nicht als tatsaechlich ausgefuehrte Feldkontakte
behauptet. Resultierende Feldwerte wurden nicht erreicht und nicht
rekonstruiert.

## Aussagegrenze

Es wurden keine Quellen, Schwellen, Adapter, Rezeptoren oder Feldkerne
geaendert. Die Diagnose benennt nur die erste deterministisch verletzte
Invariante. Eine Korrektur und ein Feldadapter-Regressionstest sind getrennte
Folgeschritte; ein weiterer 28-Ereignis-Transferlauf bleibt bis dahin
gesperrt.
