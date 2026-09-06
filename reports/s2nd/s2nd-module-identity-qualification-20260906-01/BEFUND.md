# S2-ND: Neutrale Modulidentitaetsqualifikation

ID: `s2nd-module-identity-qualification-20260906-01`.
Genau ein vorregistrierter Aufruf:

```text
python -m unittest tests.test_s2nd_module_identity -v
```

Ergebnis: `5/5`, Exit-Code `0`, `Ran 5 tests in 0.020s`, `OK`.
Status: `S2ND_MODULE_IDENTITY_QUALIFIED`. Kein Retry.

## Korrektur und Pruefumfang

`math_identity` akzeptiert Built-in-Herkunft ausschliesslich bei
`__spec__.origin == 'built-in'` und bestaetigter Zugehoerigkeit zu
`sys.builtin_module_names`. Sie bindet diese beiden Befunde ohne erfundene
Datei oder Dateihash. Das Ergebnis ist Teil derselben Generatoridentitaet
wie Python-Build, Interpreterpfad/-hash und Generatorpfad/-hash.

Dateibasierte Herkunft verlangt dagegen eine nicht eingebaute, lokalisierte
Modulform, eine tatsaechliche Datei und uebereinstimmende aufgeloeste Pfade
von Spec-Origin und `__file__`; Dateipfad und SHA-256 bleiben gebunden.
Fehlende, widerspruechliche, relative oder ungeklaerte Herkunft stoppt.

Fuenf neutrale Pruefgruppen:

1. Tatsachliche Built-in-Herkunft des lokalen `math`, ohne Dateierfindung.
2. Beide Built-in-Belege erforderlich; fehlende Herkunft wird nicht erraten.
3. Synthetische Dateiform mit tatsaechlichem Inhalt und exaktem SHA-256.
4. Fehlende Datei, Origin-Konflikt, Built-in-Widerspruch, Verzeichnis,
   relative oder nicht aufloesbare Herkunft werden abgewiesen.
5. Fremder Modulname wird nicht als `math` gebunden.

Die AST-Diffpruefung gegen `db8cfa6` bestaetigte unveraenderte
PCM-Erzeugung, Rezepte, Panels, Evaluation und Budgets. Ausser der
Identitaetsbindung wurde nur die autorisierte Vorversiegelungs-ID auf
`s2nd-source-panel-preseal-20260906-02` geaendert.

Kein PCM wurde in der Qualifikation erzeugt. Generator-, Inventar-, Panel-,
Evaluations- und Hauptaufrufe waren in den Tests gesperrt. Keine Rezeptor-,
Distanz-, Regel-, Memory-, Kontext-, Feld- oder Runtimefunktion.

`qualification-plan.json` bindet die fuenf Test-IDs und elf Vorhashes;
`call-result.json` erhaelt Kommando und Originalausgabe. `postcheck.json`
bestaetigt identische Nachhashes und das noch unbenutzte Ergebnisverzeichnis
fuer die freigegebene anschliessende Vorversiegelung.
Der alte Fehlbeleg bleibt unveraendert; der damalige Sealerstand ist unter
Commit `db8cfa6` erhalten.

Nach Bestehen wurde ausschliesslich der vom Benutzer bereits bedingt
freigegebene neue Vorversiegelungsaufruf ausgefuehrt. Dessen eigener Befund
liegt unter `../s2nd-source-panel-preseal-20260906-02/BEFUND.md`.
