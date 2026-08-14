# Getrennter Implementierungsauftrag: AST-Aktionsbindung nach Pruefung 235

## Auftrag und Abgrenzung

Dieser Vorschlag betrifft ausschliesslich:

- `tests/test_binding_preflight_supervisor_structure.py`

Nicht geaendert werden darf:

- `tools/binding_preflight_supervisor.py`
- jede weitere Projektdatei

Der Auftrag ist eine eng begrenzte strukturelle Absicherung der bereits vorhandenen Finalisierungslogik. Er ist kein Forschungs- oder Programmlauf und enthaelt keine wissenschaftliche Interpretation.

## Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/234_STATISCHER_KORREKTURVORSCHLAG_AST_AKTIONSBINDUNG_NACH_PRUEFUNG_233.md`
- `docs/forschung/235_UNABHAENGIGE_STATISCHE_PRUEFUNG_KORREKTURVORSCHLAG_234.md`
- `tests/test_binding_preflight_supervisor_structure.py`, ausschliesslich als statisch gelesener Iststand
- aktueller Freigabe-Eingang des Forschungshelfers

Es wurden keine externen Quellen verwendet.

## Verwendete Dateien und Schnittstellen

Die genannten Dateien wurden ausschliesslich als Text gelesen. Es wurden keine Parser-, Projektimport-, Prozess-, stdin-, Preflight- oder wissenschaftlichen Schnittstellen verwendet.

Der alleinige vorgesehene Aenderungsumfang nach gesonderter Freigabe ist:

- `tests/test_binding_preflight_supervisor_structure.py`

## Vorgesehene Implementierung

Die Strukturpruefung fuer den direkten `process_ended`-Block wird so verschaerft, dass die fuenf Aufrufe von `_run_finalization_step` nur als direkte Anweisungen in `ended.body` anerkannt werden. Eine rekursive Suche mit `ast.walk` darf fuer diese Zuordnung keine verschachtelten Aufrufe als direkte Finalisierungsschritte akzeptieren.

Fuer die fuenf Aufrufe in Quellreihenfolge wird jeweils statisch verlangt:

- genau vier positionale Argumente und keine Keyword-Argumente,
- das erwartete konstante Label als erstes Argument,
- der Name `finalization_deadline` als zweites Argument,
- der Name `finalization_errors` als drittes Argument,
- eine parameterlose `ast.Lambda` als viertes Argument,
- ein Lambda-Rumpf aus genau einem direkten `ast.Call` mit einfachem `ast.Name` als Ziel,
- ausschliesslich die jeweils erwarteten einfachen Namensargumente, ohne Keywords oder Sternargumente.

Die Lambda darf keine positional-only, positionalen oder keyword-only Parameter, keine Varargs, keine Kwargs und keine Defaults besitzen.

Die konkrete Bindung lautet:

| Reihenfolge | Label | Lambda-Aktion |
| --- | --- | --- |
| 1 | `pipe closure` | `_close_finalization_pipes(ledger)` |
| 2 | `reader completion` | `_finish_readers(readers, finalization_deadline)` |
| 3 | `process resource closure` | `_close_process_resources(ledger)` |
| 4 | `after observation` | `_after_observations(api, observations)` |
| 5 | `after manifest` | `_verify_after_manifest(before)` |

Die ersten drei und der fuenfte Schritt muessen direkte `ast.Expr`-Anweisungen sein. Der vierte Schritt muss eine direkte `ast.Assign`-Anweisung mit genau einem Ziel sein. Dieses Ziel muss das Tupel `(after_value, after_ok)` aus zwei `ast.Name`-Knoten im Store-Kontext sein.

Unmittelbar nach dem vierten Schritt und vor dem fuenften Schritt muss ein direkter `ast.If`-Block liegen. Seine Bedingung muss exakt der Konjunktion aus `after_ok` und `after_value is not None` entsprechen. Sein Rumpf muss ausschliesslich die Zuweisung `observations = after_value` enthalten; ein `else`-Zweig ist nicht zulaessig.

Damit ist die direkte Reihenfolge fest gebunden:

1. `pipe closure`
2. `reader completion`
3. `process resource closure`
4. Zuweisender Schritt `after observation`
5. Bedingte Uebernahme in `observations`
6. `after manifest`

## Statische Akzeptanzkriterien

Die Aenderung ist statisch akzeptabel, wenn die Testdatei nachweisbar alle folgenden Strukturabweichungen verwirft:

- ein korrektes Label mit einer falschen oder beliebigen Lambda-Aktion,
- falsche Aktionsargumente oder zusaetzliche Lambda- beziehungsweise Aufrufargumente,
- ein nur verschachtelt vorhandener `_run_finalization_step`-Aufruf,
- eine fehlende oder abweichende Bindung von `(after_value, after_ok)`,
- eine unbedingte oder falsch bedingte Uebernahme nach `observations`,
- eine abweichende Reihenfolge oder eine Zuordnung ausserhalb des direkten `process_ended`-Blocks.

## Gegenbaselines

Als statische Gegenbaselines gelten mindestens:

- reine Labelpruefung ohne Aktionsbindung,
- beliebiger Lambda-Rumpf bei korrektem Label,
- richtige Aktion mit falschen Argumenten,
- rekursiv gefundener, aber nicht direkter Aufruf,
- unbedingte Uebernahme von `after_value`,
- richtige Einzelteile in falscher Reihenfolge.

## Durchgefuehrte Schritte und Messergebnisse

- Die freigegebenen Strukturvorgaben aus Dokument 234 wurden in einen getrennten Implementierungsauftrag ueberfuehrt.
- Die Freigabe- und Dateigrenzen aus Dokument 235 wurden beibehalten.
- Aktionsbindung, Tupelbindung, bedingte Uebernahme und direkte Blockreihenfolge wurden als statische Akzeptanzkriterien festgelegt.
- Es wurde keine Implementierung, Untersuchung oder Ausfuehrung vorgenommen.

Es liegen keine Messwerte und keine experimentellen Gegenbaselines vor. Die oben genannten Gegenbaselines sind ausschliesslich vorab festgelegte statische Fehlformen fuer eine spaetere Implementierungspruefung.

## Grenzen und nicht gepruefte Annahmen

- Dieser Auftrag erlaubt noch keine Dateiaenderung.
- Testausfuehrung, Parserlauf, Projektimport, Prozessstart, stdin-Transport und Preflight-Ausfuehrung bleiben ausgeschlossen.
- Der Windows-ABI-Abgleich bleibt offen.
- Es entstehen keine Messwerte und kein Forschungsbefund.
- Die statische Absicherung ist kein Nachweis von Memory, Organisation, Topologie, Bedeutung, Selbstregulation oder KI.

## Schlussfolgerung und naechster Schritt

Der kleinste naechste Schritt ist die unabhaengige statische Pruefung dieses Implementierungsauftrags. Erst nach ausdruecklicher Freigabe darf ausschliesslich `tests/test_binding_preflight_supervisor_structure.py` entsprechend geaendert werden. Danach ist zunaechst nur eine unabhaengige statische Implementierungspruefung zulaessig.

Eine Zielabweichung ist nicht erkennbar. Das Ergebnis wird dem Forschungspruefer zur Pruefung uebergeben.
