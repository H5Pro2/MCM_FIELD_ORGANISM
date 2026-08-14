# Statischer Korrekturvorschlag: AST-Aktionsbindung nach Pruefung 233

## Forschungsfrage und Auftrag

Wie kann die in Dokument 233 festgestellte Luecke der statischen Testabsicherung minimal geschlossen werden, sodass die vorhandenen Finalisierungslabels ihren konkreten Aktionen zugeordnet sind und die bedingte Uebernahme der Nachbeobachtung in `observations` strukturell nachgewiesen wird?

Der Auftrag ist auf einen statischen Korrekturvorschlag fuer `tests/test_binding_preflight_supervisor_structure.py` begrenzt. Dieser Vorschlag ist keine Implementierungsfreigabe und kein Forschungs- oder Programmlauf.

## Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/233_ERNEUTE_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_231.md`
- `tests/test_binding_preflight_supervisor_structure.py`

Es wurden keine externen Quellen verwendet.

## Verwendete Dateien und Schnittstellen

Vorgesehener alleiniger Aenderungsumfang:

- `tests/test_binding_preflight_supervisor_structure.py`

Unveraendert bleiben insbesondere:

- `tools/binding_preflight_supervisor.py`
- alle Projekt-, Prozess-, stdin-, Preflight- und wissenschaftlichen Schnittstellen

## Statischer Korrekturvorschlag

### 1. Labels an die jeweiligen Aktionen binden

Der bestehende Strukturtest soll nicht nur die ersten drei Argumente der fuenf Aufrufe von `_run_finalization_step` pruefen. Fuer jeden Aufruf wird zusaetzlich das vierte Argument als parameterlose `ast.Lambda` ausgewertet. Der Lambda-Koerper muss genau ein direkter Funktionsaufruf ohne Keywords, Sternargumente oder zusaetzliche Verschachtelung sein.

In Quellreihenfolge ist folgende vollstaendige Zuordnung zu verlangen:

| Label | Aufgerufene Aktion | Positionsargumente |
|---|---|---|
| `pipe closure` | `_close_finalization_pipes` | `ledger` |
| `reader completion` | `_finish_readers` | `readers`, `finalization_deadline` |
| `process resource closure` | `_close_process_resources` | `ledger` |
| `after observation` | `_after_observations` | `api`, `observations` |
| `after manifest` | `_verify_after_manifest` | `before` |

Die Pruefung soll fuer jeden Schritt sicherstellen:

- genau vier Positionsargumente an `_run_finalization_step`,
- keine Keywordargumente,
- Argument vier ist eine `ast.Lambda` ohne Parameter,
- der Lambda-Koerper ist ein direkter `ast.Call` auf den erwarteten einfachen Funktionsnamen,
- dessen Positionsargumente sind genau die erwarteten `ast.Name`-Knoten in der festgelegten Reihenfolge,
- der Aktionsaufruf besitzt keine Keywordargumente.

Damit kann weder ein korrektes Label mit einer falschen Aktion noch eine korrekte Aktion mit falschen Eingaben den Strukturtest bestehen.

### 2. Rueckgabebindung der Nachbeobachtung absichern

Der vierte Finalisierungsschritt muss sein Ergebnis weiterhin genau in `(after_value, after_ok)` schreiben. Nach diesem Schritt und vor dem Schritt `after manifest` soll im selben direkten Block von `if process_ended` genau die folgende Kontrollstruktur nachgewiesen werden:

```python
if after_ok and after_value is not None:
    observations = after_value
```

Die AST-Pruefung soll hierzu verlangen:

- Bedingung ist ein `ast.BoolOp` mit `ast.And` und genau zwei Operanden,
- erster Operand ist der Name `after_ok`,
- zweiter Operand ist ein einzelner Vergleich `after_value is not None`,
- der Vergleich verwendet genau `ast.IsNot` und die Konstante `None`,
- der `if`-Koerper enthaelt genau die Zuweisung `observations = after_value`,
- es existiert kein `else`-Zweig,
- die Struktur steht nach der Zuweisung von `(after_value, after_ok)` und vor dem Aufruf fuer `after manifest`.

Dadurch wird sowohl die Erfolgsbedingung als auch der Ausschluss eines fehlenden Nachbeobachtungswerts statisch gebunden. Eine unbedingte Uebernahme, eine vertauschte Bedingung oder eine Zuweisung an ein anderes Ziel muss fehlschlagen.

### 3. Direkte Blockposition absichern

Die fuenf Finalisierungsschritte und die bedingte Beobachtungsuebernahme sollen anhand der direkten Anweisungen im Koerper von `if process_ended` bestimmt werden. Eine rekursive Suche ueber beliebige Unterbaeume ist dafuer nicht ausreichend, weil sie eine Verschiebung in einen zusaetzlichen bedingten oder wiederholten Unterblock verdecken koennte.

Die bestehende Hilfslogik darf dafuer eng lokal ergaenzt oder durch eine auf direkte `Expr`- und `Assign`-Anweisungen begrenzte Extraktion ersetzt werden. Andere Strukturtests und Produktionsdateien bleiben unberuehrt.

## Durchgefuehrte Schritte

- Die zwei offenen Befunde aus Dokument 233 wurden gegen den aktuellen Strukturtest abgegrenzt.
- Die fehlenden AST-Invarianten wurden als konkrete Knotenformen, Namen, Argumentfolgen und Blockpositionen formuliert.
- Der Aenderungsumfang wurde auf eine Testdatei begrenzt.
- Es wurden keine Dateien implementiert oder veraendert, keine Tests oder Parser ausgefuehrt und keine Projektmodule importiert.

## Messergebnisse und Gegenbaselines

Es liegt kein Messergebnis vor, da dieser Arbeitsschritt ausschliesslich ein statischer Korrekturvorschlag ist.

Als Gegenbaselines fuer die spaetere statische Implementierungspruefung gelten:

- Ein Test, der nur die fuenf Labels prueft, ist unzureichend, weil Label und Aktion vertauscht werden koennen.
- Ein Test, der nur die Lambda-Existenz prueft, ist unzureichend, weil Funktionsname oder Argumente falsch sein koennen.
- Ein Test ohne Kontrolle der bedingten Zuweisung ist unzureichend, weil `after_value` ungeprueft, unter falscher Bedingung oder gar nicht in `observations` uebernommen werden kann.
- Eine rekursive Knotensuche ist unzureichend, wenn sie die geforderte direkte Reihenfolge im `process_ended`-Block nicht bindet.

## Entscheidungskriterien fuer eine spaetere Implementierungspruefung

Eine Umsetzung ist statisch freigabefaehig, wenn alle folgenden Punkte sichtbar erfuellt sind:

- ausschliesslich `tests/test_binding_preflight_supervisor_structure.py` wurde fuer diesen Korrekturschritt geaendert,
- alle fuenf Label-Aktions-Argument-Zuordnungen werden exakt geprueft,
- die Tupelbindung `(after_value, after_ok)` wird dem Schritt `after observation` zugeordnet,
- die bedingte Zuweisung an `observations` wird mit exakter Bedingung und Position geprueft,
- die neuen Pruefungen beruhen auf AST-Struktur und nicht auf blosser Textsuche,
- es wurden keine Produktionslogik und keine fachlichen Aussagegrenzen veraendert.

## Grenzen und nicht gepruefte Annahmen

- Dieser Vorschlag wurde nicht implementiert oder ausgefuehrt.
- Die syntaktische und operative Funktionsfaehigkeit einer spaeteren Umsetzung ist nicht nachgewiesen.
- Tests, Parserlaeufe, Projektimporte, Prozessstarts, stdin-Transport und Preflight-Ausfuehrungen bleiben ausgeschlossen.
- Der Windows-ABI-Abgleich bleibt offen.
- Es erfolgt kein Nachweis zu MCM-Memory, Organisation, Topologie, Bedeutung, Selbstregulation oder KI.

## Konkrete Schlussfolgerung

Die beiden offenen Strukturtestbefunde aus Dokument 233 lassen sich innerhalb der bestehenden Dateigrenze schliessen. Erforderlich ist eine exakte AST-Bindung der fuenf Labels an ihre Lambda-Aktionen und Argumente sowie der bedingten Uebernahme von `after_value` in `observations`. Eine Aenderung der bereits statisch als sichtbar korrekt bewerteten Quellimplementierung ist dafuer nicht vorgesehen.

Eine Zielabweichung ist nicht erkennbar.

## Naechster begrenzter Entwicklungsschritt

Als naechster Schritt sollte ausschliesslich dieser statische Korrekturvorschlag unabhaengig geprueft werden. Erst nach gesonderter Freigabe darf die beschriebene Aenderung in `tests/test_binding_preflight_supervisor_structure.py` implementiert werden; auch danach ist zunaechst nur eine erneute unabhaengige statische Implementierungspruefung vorgesehen.

Das Ergebnis wird dem Forschungspruefer zur Pruefung uebergeben.
