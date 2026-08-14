# Korrekturplan fuer Huerde F: minimale private Produktionsverkettung

## 1. Status und Zweck

Dieses Dokument beschreibt ausschliesslich statisch die kleinste konzipierbare Korrektur des in Dokument 200 bestaetigten Huerde-F-Sperrbefunds.

Es aendert keine Implementierung und gibt weder die geplante Implementierung noch deren Ausfuehrung frei. Projektmodule, Tests, Runner, Executor, Bindung, Handoff, Fixierung und Runtime werden nicht ausgefuehrt.

Huerde F und Huerde G bleiben gesperrt. Reale Bindung, Handoff, Orchestrator, Fixierung, Minimaltest, Runtime, Hook-Ausfuehrung, Public-AV, Netzwerk-, Geraete- und Weltkontakt bleiben gesperrt.

## 2. Gebundene Planungsgrundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/194_HUERDE_B_EINMALIGER_AUSFUEHRUNGSVERTRAG_RUNTIME_FIXIERUNG.md` | `f4e2139aee4cc9f7cf95deb4cefc20881efe57aef1e17f8a9cad70b741e7274e` |
| `docs/forschung/197_KORRIGIERTE_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_RUNTIME_FIXIERUNG.md` | `644b71731a8bd539deb83b00b9e8cd38872ff8fb572711306e9ad642447644c1` |
| `docs/forschung/198_ERNEUTE_HUERDE_D_EINGANGS_UND_QUELLENBINDUNG_RUNTIME_FIXIERUNG.md` | `46b4793e0baf73dda025f5475c5ed06335b4d8b12838fb7a4220dccdeaf64878` |
| `docs/forschung/199_HUERDE_E_AUSGABE_UND_SEITENEFFEKTGRENZE_RUNTIME_FIXIERUNG.md` | `72e611d68ba330b089afc8f0ca6901aa2839088faba35e94a595571f3c0e32cc` |
| `docs/forschung/200_HUERDE_F_STATISCHE_GEGENPRUEFUNG_REALPFAD_SPERRBEFUND_RUNTIME_FIXIERUNG.md` | `9f26765b839fa2bb51e530b6cadb2d79ef6b9446e8a795c870e1318711554dd9` |
| `mcm_field_organism/_runtime_fixation_binding.py` | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `mcm_field_organism/_runtime_fixation_handoff.py` | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

Eine Abweichung einer Bindung macht diesen Plan gegenstandslos und erfordert eine neue statische Bewertung.

## 3. Exakt fehlende Produktionsverkettung

Es fehlt genau eine private Produktionsfunktion, welche die vorhandene Bindungskonstruktion und den vorhandenen Handoff direkt verbindet. Die kleinste vorgesehene Erweiterung waere genau eine neue Datei:

`mcm_field_organism/_runtime_fixation_single_use_path.py`

Diese Datei duerfte genau eine eigene Funktion definieren:

`_run_private_runtime_fixation_once() -> _FixedDigestBundle`

Die Funktion duerfte keine Parameter, optionalen Schalter, Callbacks, Provider, Pfade oder Konfigurationswerte annehmen. Ihr Funktionskoerper muesste semantisch ausschliesslich aus diesen zwei aufeinanderfolgenden Operationen bestehen:

1. genau ein Aufruf von `_build_private_fixation_binding()` und lokale Aufnahme des einen Rueckgabewerts;
2. genau ein unmittelbarer Aufruf von `_execute_private_runtime_fixation(binding)` mit genau diesem lokalen Rueckgabewert und direkte Rueckgabe des einen `_FixedDigestBundle`.

Der Plan erlaubt keine zweite Konstruktion, Kopie, Serialisierung, Zwischenspeicherung oder Ersetzung der Bindung.

## 4. Vorgesehene statische Form

Die spaetere Implementierung muesste strukturell dem folgenden nicht ausfuehrbaren Vertrag entsprechen:

```text
IMPORT _build_private_fixation_binding AUS privatem Bindungsmodul
IMPORT _execute_private_runtime_fixation AUS privatem Handoff-Modul
IMPORT _FixedDigestBundle NUR fuer den Rueckgabetyp

DEFINIERE _run_private_runtime_fixation_once OHNE Parameter:
    binding = GENAU_EIN_AUFRUF _build_private_fixation_binding
    RETURN GENAU_EIN_AUFRUF _execute_private_runtime_fixation(binding)
```

Dieser Block ist Pseudocode. Er ist kein Python-Modul, kein Befehl, kein CLI-Einstieg und keine Ausfuehrungsfreigabe.

## 5. Verbindliche Ausschluesse

Das geplante Modul duerfte nicht enthalten:

- `if __name__ == "__main__"` oder eine andere automatische Aufrufstelle;
- CLI-Parser, Konsolenbefehl oder Packaging-Einstieg;
- Runner-, Executor-, Integrator- oder Runtime-Anbindung;
- Schleifen, Rekursion, Retry, Neustart, Parallelitaet oder Nebenlaeufigkeit;
- Verzweigungen vor oder zwischen Bindung und Handoff;
- dynamische Imports oder Symbolaufloesung;
- `getattr`, `globals`, `locals`, `eval`, `exec` oder `__import__`;
- Hook-, Public-AV-, Netzwerk-, Geraete- oder Weltkontaktpfade;
- Logging, Telemetrie, `stdout`, `stderr`, Datei- oder Persistenzzugriffe;
- Ausnahmeinhalte, Teilresultate oder alternative Rueckgaben;
- Export ueber `mcm_field_organism/__init__.py`.

Die Datei selbst duerfte von keinem bestehenden Produktionsmodul, Werkzeug oder Paketexport importiert oder aufgerufen werden. Sie wuerde nur die statisch pruefbare Verkettungsdefinition bereitstellen. Ein spaeterer Prozessaufruf waere eine getrennte, weiterhin gesperrte Entscheidung unter Huerde G.

## 6. Bindung an die Huerden A bis E

Eine spaetere Implementierung dieses Plans wuerde den gebundenen Produktionsumfang veraendern. Deshalb duerfte sie nicht unmittelbar als Erfuellung von Huerde F gelten.

Vor einer erneuten Huerde-F-Pruefung waeren zwingend erforderlich:

1. neue korrigierte Huerde-A-Byte- und Umfangsbindung einschliesslich der neuen Datei;
2. erneute statische Bestaetigung des Einmallaufvertrags aus Huerde B;
3. erneute Bestaetigung der Ressourcen- und Zeitgrenzen aus Huerde C;
4. erneute Quellen- und Eingangsbindung aus Huerde D;
5. erneute Ausgabe- und Seiteneffektpruefung aus Huerde E;
6. anschliessend eine neue statische Huerde-F-Gegenpruefung des gesamten Produktionspfads.

Keine dieser erneuten Pruefungen darf die geplante Funktion ausfuehren.

## 7. Statische Abnahmekriterien einer spaeteren Implementierung

Eine spaetere Implementierung waere nur dann planentsprechend, wenn eine unabhaengige AST- und Textpruefung mindestens bestaetigt:

- genau eine neue Produktionsdatei;
- genau eine eigene Funktionsdefinition;
- genau drei statische private Importe;
- genau einen Bindungskonstruktionsaufruf;
- genau einen Handoff-Aufruf;
- direkte Datenflussidentitaet zwischen beiden Aufrufen;
- keinen direkten Orchestratoraufruf im neuen Modul;
- keine weitere Produktionsaufrufstelle der neuen Funktion;
- keine verbotenen Sprachkonstrukte oder Seiteneffektpfade;
- unveraenderten Paketexport ohne Fixierungssymbole.

Ein Texttreffer allein genuegt nicht. Definition, Import und Aufruf muessen bei der Review syntaktisch getrennt gezaehlt werden.

## 8. Freigabeblock

```yaml
byte_scope_release: false
single_execution_release: false
resource_boundary_release: false
input_source_release: false
output_side_effect_release: false
failure_abort_release: false
observation_evidence_release: false
independent_final_review_release: false
real_binding_release: false
handoff_release: false
runtime_fixation_release: false
minimal_test_release: false
minimal_test_release_recommended: false
```

Alle Huerden sind kumulativ. Dieses Dokument setzt kein Freigabefeld auf `true`.

## 9. Entscheidung und naechster Pruefschritt

Die fehlende Verkettung ist ohne Export, CLI, Runner, Executor, Hook, Public-AV, Netzwerk-, Geraete- oder Weltkontakt konzipierbar. Dieser Plan zeigt jedoch nur die statische Minimalform und gibt ihre Implementierung nicht frei.

Dokument 201 ist vor jedem weiteren Schritt unabhaengig und ausschliesslich statisch zu pruefen. Huerde F, Huerde G und jede reale Ausfuehrung bleiben bis dahin gesperrt.

## 10. Aussagegrenze und Zielbezug

Dieses Dokument macht keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI. Es programmiert keine Erinnerung, Bedeutung, Zielwirkung oder Topologie vor.

Eine Zielabweichung ist nicht erkennbar. Der Plan beschraenkt sich auf die minimale technische Verbindung bereits vorhandener privater Grenzen und trennt diese strikt von jeder Ausfuehrungs- oder Organismusbehauptung.
