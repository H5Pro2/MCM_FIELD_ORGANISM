# S2-FV: Privater Runner, Recorder und Verifikator

## Auftrag und Grenze

S2-FV materialisiert ausschliesslich die private technische Ausfuehrungs- und
Beleggrenze fuer die gebundene S2-FU-18-Schritt-Geschichte. Der Hauptschalter
bleibt geschlossen. Es wurde keine Zustands-, Rezeptor-, Speicher-, Probe-
oder Runnerfunktion ausgefuehrt.

Neu angelegt wurden genau drei private Module:

```text
495675b846698f57517a0f0cf94df55849062e027d0e56c7929223f7fef133ec  tools/_s2fv_private_runner.py
e86191b0a9a6feaf78e7310343a874047df1c005bf9c816fc52c288499857b04  tools/_s2fv_private_recording.py
ef2d7c18a6436ea8673c9387a5f0cb7a3b2e001d0dedd48ec558d4e8e5bca8c0  tools/_s2fv_private_result_verifier.py
```

## Privater Runner

Der Runner bindet den unveraenderten S2-FU-Fixturebestand an folgende feste
Operationsfolge:

- 24 Rezeptoranalysen;
- 54 Bildungen, je 18 fuer `COMPOSITE`, `B4` und `TSPM1`;
- 18 Komponentenidentitaetspruefungen;
- eine B4-Folgenprobe;
- sechs getrennte Inhaltsproben;
- insgesamt 103 Operationen und 206 unmittelbar gepaarte
  `START`-/`RESULT`-Ereignisse.

Jeder Bildungsschritt verwendet fuer alle drei Arme dasselbe gebundene
Quellobjekt. Erst nach den drei lokalen Resultaten wird die Identitaet des
Composite-B4- und Composite-TSPM-Zustands mit den Standalone-Armen geprueft.
Die Folgenordnung wird ausschliesslich aus B4 gelesen. TSPM-1 bleibt auf Fast-
und Slow-Inhaltsbefunde begrenzt. Der S2-FU-Auswerter wird weder importiert
noch aufgerufen.

`MAIN_EXECUTION_ENABLED = False` ist vor Planmaterialisierung, Recorderanlage
und jedem Zustandsaufruf das erste ausfuehrbare Gate von `run_main_once`.

## Append-only Aufzeichnung

Der Recorder erstellt ein neues, nicht ueberschreibbares Laufverzeichnis und
verwendet:

- `manifest.json`;
- `events.jsonl.partial` bis zum vollstaendigen Journalabschluss;
- das anschliessend umbenannte `events.jsonl`;
- `evidence.json` mit Status `RECORDED_UNEVALUATED`;
- `terminal.json`;
- `COMPLETE` als letzten Abschlussmarker.

Alle Ereignisse sind indexiert, an Plan und Lauf gebunden und ueber
`previous_event_digest` hashverkettet. Jeder Schreibschritt wird geflusht.
Nur die exakten Ereignisbudgets koennen Evidenzpaket, Terminal und Marker
erzeugen. Fehler hinterlassen keinen erfolgreichen Abschluss; ein moeglicher
Teilstand bleibt `NOT_EVALUABLE`.

## Unabhaengiger Verifikator

Der read-only Verifikator verwendet ausschliesslich die Standardbibliothek.
Er importiert weder Recorder noch Runner, Rezeptor-, Speicher-, Koordinator-,
Feld- oder Auswertermodule. Er prueft:

- die exakte Fuenf-Dateien-Inventur;
- Plan-, Datei-, Ereignis-, Evidenz-, Terminal- und Markerdigests;
- 206 lueckenlos verkettete Ereignisse und 103 eindeutige Operations-IDs;
- unmittelbare und vollstaendige START-/RESULT-Paarung;
- dieselbe Quelle fuer die drei Formationsarme jedes Schritts;
- alle 18 gueltigen Komponentenidentitaeten;
- read-only Unveraendertheit aller Folgen- und Inhaltsproben;
- genau eine B4-Folgenprobe und zwei vollstaendige Dreiergruppen von
  Inhaltsbefunden;
- das Fehlen einer automatischen Sichtauswahl oder Funktionswertung.

Jede Abweichung ergibt `NOT_EVALUABLE`. Der Verifikator kann nur technische
Aufzeichnungsvollstaendigkeit, niemals Memory-Funktion bestaetigen.

## Statischer Codeaudit

Der Audit wurde ausschliesslich durch Lesen, AST-Parsing, Symboltabellen- und
Quelltextpruefung durchgefuehrt. Er bestaetigt:

- Syntax und Symboltabellen aller drei Module;
- feste Budgets `24/54/18/1/6`, `103` und `206`;
- geschlossenes Hauptgate vor jedem Seiteneffekt;
- unabhaengige Standardbibliotheksgrenzen von Recorder und Verifikator;
- Ausschluss des S2-FU-Auswerters, oeffentlicher API, Snapshot und Feldpfad;
- getrennte B4-, TSPM-Fast- und TSPM-Slow-Sichten ohne `BEST_MEMORY`;
- unveraenderte B4-, TSPM-1-, PPB-1-, S2-FS-, S2-FU- und Feldquellen.

`PASS_S2FV_PRIVATE_RUNNER_RECORDING_VERIFIER_STATIC_CODE_AUDIT`

Es wurden keine neuen Module importiert, keine Tests ausgefuehrt und keine
Datei-, Rezeptor-, Zustands-, Probe-, Recorder-, Verifikator- oder
Runnerfunktion aufgerufen. Qualifikation und 18-Schritt-Hauptlauf bleiben
gesperrt und benoetigen jeweils eine eigene Freigabe.

## Nachfolgende S2-FW-Qualifikation

Die technische Qualifikation wurde spaeter getrennt als S2-FW freigegeben und
genau einmal ausgefuehrt. Die zwoelf neutralen Tests bestanden vollstaendig
mit Exit-Code `0` und terminalem `OK`. Geprueft wurden kleine neutrale
Rezeptor-, Composite-, B4-, TSPM-, Folgen- und Inhaltspfade sowie eine
synthetische vollstaendige 103/206-Aufzeichnung und ihre unabhaengige
Verifikation. Manipulationen und Teilstaende endeten fail-closed.

Der Status lautet
`PASS_S2FW_NEUTRAL_RUNNER_RECORDING_VERIFIER_QUALIFICATION_AUDIT`. Die
18-Schritt-Hauptgeschichte wurde nicht ausgefuehrt und bleibt gesperrt.

## Spaeterer S2-FX-Hauptlauf

Diese Sperre wurde spaeter einmalig und ausdruecklich fuer S2-FX geoeffnet.
Der Lauf `s2fx-main-20260830-01` erzeugte die vollstaendige 103/206-
Aufzeichnung; die einmalige unabhaengige Verifikation ergab
`RECORDING_COMPLETE`. Das Gate wurde anschliessend wieder geschlossen.

Die Funktionsauswertung blieb wegen eines widerspruechlichen visuellen
Support-Belegs `NOT_EVALUABLE`. Der abgeschlossene Lauf wurde weder wiederholt
noch repariert. Der aktuelle Status ist in
`docs/S2FX_EINMALIGER_18_SCHRITT_HAUPTLAUF_VERIFIKATION_UND_AUSWERTUNGSGRENZE.md`
dokumentiert.
