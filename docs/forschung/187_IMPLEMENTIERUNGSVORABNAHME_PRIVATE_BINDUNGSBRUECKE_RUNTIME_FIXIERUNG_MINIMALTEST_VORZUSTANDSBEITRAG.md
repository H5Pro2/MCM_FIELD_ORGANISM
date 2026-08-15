# 187 - Implementierungsvorabnahme private Bindungsbruecke Runtime-Fixierung Minimaltest Vorzustandsbeitrag

## 1. Zweck und Sperrgrenze

Dieses Dokument spezifiziert ausschliesslich den maximal zulaessigen Umfang
einer spaeter gesondert freizugebenden Implementierung der in Dokument 186
statisch abgegrenzten privaten Bindungsbruecke. Es implementiert keine
Bindungsbruecke, stellt keine reale Operationsbindung her und fuehrt weder
Ablaufkoordination noch Fixierung oder Runtime aus.

Die Bindungskonstruktion ist bereits als reale Operationsbindung eingestuft.
Eine spaetere Implementierung benoetigt deshalb nach diesem Dokument zuerst
eine unabhaengige statische Review und danach einen ausdruecklichen separaten
Implementierungsauftrag.

## 2. Gebundener Ausgangsstand

Vor jeder spaeteren Implementierung muessen die rohen Dateibytes exakt diese
SHA-256-Digests besitzen:

```text
docs/forschung/186_STATISCHE_VORABNAHME_PRIVATE_BINDUNGSBRUECKE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md
1dcfa46e5be53071e5fdc864dcf3be1018e194281e422c47f2e1637828858fb5

docs/forschung/185_TECHNISCHE_ABSCHLUSSABNAHME_PRIVATE_ADAPTERGRENZE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md
2e33efa8db66cdd7d0eadf7e10304999237fb642f9f5be2fb57b5ba7ffbe06fb

mcm_field_organism/_runtime_fixation_adapters.py
422f511c54da7cecce541313ab23bcb37d5d8edab6a97a5cfe04768f111048fc

mcm_field_organism/_runtime_fixation_structure.py
399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e

mcm_field_organism/__init__.py
c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0
```

Eine Abweichung beendet die Vorabnahme. Digests duerfen nicht automatisch
aktualisiert werden.

## 3. Ausschliesslich zulaessiger spaeterer Dateiumfang

Eine erst gesondert freizugebende Implementierung darf genau diese zwei neuen
privaten Dateien anlegen:

```text
mcm_field_organism/_runtime_fixation_binding.py
tests/test_runtime_fixation_binding.py
```

Beide Dateien existieren im gebundenen Ausgangsstand nicht. Bestehende Module,
Tests, Runner, Integratoren, Hooks, Executor-, Public-AV-, Export- und
Runtime-Dateien duerfen nicht geaendert werden. Insbesondere bleibt
`mcm_field_organism/__init__.py` unveraendert.

## 4. Exakte private Symboloberflaeche

Das spaetere Produktionsmodul darf genau diese beiden privaten Symbole
definieren:

```text
_PrivateFixationBinding
_build_private_fixation_binding() -> _PrivateFixationBinding
```

Weitere Klassen, Fabriken, Ausfuehrungshelfer, Registries oder Modulobjekte
sind verboten. Typaliase und rein statische Importnamen duerfen keine
zusaetzliche aufrufbare Bindungsoberflaeche bilden.

## 5. Vertrag von `_PrivateFixationBinding`

`_PrivateFixationBinding` muss ein slots-begrenzter, nicht oeffentlich
exportierter und nach Konstruktion unveraenderlicher Besitzer genau dieser
beiden Referenzen sein:

```text
structure: _LockedFixationStructure
operations: _FixationOperations
```

Der Konstruktor muss beide Werte per `isinstance` gegen die direkt
importierten privaten Typen pruefen. Fremde Struktur- oder Operationstypen
muessen mit einer bereinigten `PreviousStateMinimalRunnerError` abbrechen.
Dabei darf weder ein Teiltraeger noch eine der beiden Referenzen ausgegeben
oder in den Ausnahmeinhalt aufgenommen werden.

Der Traeger darf ausschliesslich lesende Eigenschaften fuer `structure` und
`operations` bereitstellen. Er darf keine Aufrufmethode, kein `__call__`,
keinen Kontextmanager, Callback, Logger, Destruktor, Iterator, Registry- oder
Persistenzpfad besitzen. Kopieren, Deepcopy, Hashing und Serialisierung muessen
abbrechen. Der Traeger darf keine Ergebnisse, Teilwerte, Digests, Frames,
Verteilungen, Generatoren, Boundaries oder Kontexte speichern.

## 6. Vertrag von `_build_private_fixation_binding()`

Die Funktion muss parameterlos sein und darf keine Defaults, Overrides,
Konfiguration, Registry oder Umgebungswerte akzeptieren. Pro Aufruf darf sie
in dieser Reihenfolge genau ausfuehren:

```text
structure = build_locked_runtime_fixation_structure()
operations = _build_private_fixation_operations()
return _PrivateFixationBinding(
    structure=structure,
    operations=operations,
)
```

Beide Rueckgaben muessen vor Rueckgabe des Traegers typgeprueft werden. Bei
einem Fehler muss die Funktion mit genau einer festen bereinigten technischen
Fehlermeldung und `from None` abbrechen. Fremde Ausnahmeinhalte, Fabrikwerte
und Teilreferenzen duerfen nicht nach aussen gelangen.

Die Funktion darf keine der zehn Operationsrollen aufrufen. Sie darf weder
Source-Digests pruefen noch Kontext, Frame, Distribution, Schrittzeit,
Generator, Boundary oder Einzeldigest erzeugen.

## 7. Exakte Importgrenze

Das spaetere Produktionsmodul darf auf Modulebene ausschliesslich die fuer den
Vertrag notwendigen Standardbibliotheksnamen und diese direkten relativen
Importe verwenden:

```text
from ._previous_state_minimal_runner import PreviousStateMinimalRunnerError
from ._runtime_fixation_adapters import _build_private_fixation_operations
from ._runtime_fixation_structure import (
    _FixationOperations,
    _LockedFixationStructure,
    build_locked_runtime_fixation_structure,
)
```

Ausdruecklich verboten sind Importe von:

```text
_coordinate_runtime_fixation_with_operations
_derive_contact_with_operations
execute_runtime_fixation
```

Verboten sind ausserdem `importlib`, `__import__`, `getattr`, Namenslookup,
Registry, Pluginauflosung, Umgebungsvariablen und verzoegerte Funktionsimporte.
Adapter- und Strukturmodul duerfen die Bindungsdatei nicht rueckimportieren.

## 8. Modulimport- und Nebenwirkungssperre

Der Import des spaeteren Moduls darf keine Fabrik aufrufen und keine Struktur,
Operationsbindung oder Traegerinstanz konstruieren. Verboten sind insbesondere:

- Modul-Singletons oder vorgebaute Bindungen;
- automatische Aufrufe durch Import oder Test-Discovery;
- `if __name__ == "__main__"`-Ausfuehrung;
- Thread, Prozess, Scheduler, Callback oder Kontextmanager;
- CLI-, Runner-, Integrator-, Hook-, Executor- oder Public-AV-Anbindung;
- Feldfortschritt, Snapshot, Effektmessung, Logger oder Persistenz.

Nur ein spaeter ausdruecklich freigegebener privater Funktionsaufruf duerfte
den Bindungstraeger konstruieren. Auch dieser Aufruf waere reale
Operationsbindung, nicht Fixierungsausfuehrung.

## 9. Ablaufkoordinator- und Ausfuehrungssperre

Das Produktionsmodul und sein Test duerfen
`_coordinate_runtime_fixation_with_operations(...)` weder importieren noch
aufrufen. `binding.structure` und `binding.operations` duerfen nicht gemeinsam
an irgendeine Funktion uebergeben werden.

Eine solche Uebergabe wuerde die zehn realen Adapterrollen ausfuehren und ist
reale Fixierungsausfuehrung. Sie benoetigt eine separate spaetere
Ausfuehrungsvorabnahme und ist nicht Bestandteil dieser
Implementierungsvorabnahme.

## 10. Verbindliche isolierte Testanforderungen

Die spaetere Testdatei muss beide importierten Fabriken vor jedem Aufruf von
`_build_private_fixation_binding()` durch isolierte Testdoubles ersetzen. Die
reale Adapterfabrik und der reale Ablaufkoordinator duerfen im Test niemals
gemeinsam ausgefuehrt werden.

Mindestens zu pruefen sind:

- die Produktionsdatei definiert nur die zwei freigegebenen privaten Symbole;
- die Fabrik ist parameterlos und besitzt keine Defaults;
- Struktur- und Operationsfabrik werden in fester Reihenfolge genau einmal
  aufgerufen;
- die Testdoubles liefern typgerechte, aber nicht ausfuehrbare Instanzen;
- der Traeger bewahrt exakt deren Objektidentitaeten;
- beide Eigenschaften sind nach Konstruktion nicht ersetzbar;
- keine der zehn Operationsrollen wird aufgerufen;
- fremder Strukturtyp fuehrt zu bereinigtem Abbruch ohne Teiltraeger;
- fremder Operationstyp fuehrt zu bereinigtem Abbruch ohne Teiltraeger;
- `RuntimeError(secret)` aus jeder Fabrik gibt `secret` nicht preis;
- `PreviousStateMinimalRunnerError(secret)` aus jeder Fabrik gibt `secret`
  nicht preis;
- Kopieren, Deepcopy, Hashing und Serialisierung brechen ab;
- Modulimport erzeugt keine Fabrikaufrufe oder Bindungsinstanz;
- kein dynamischer Import, keine Namensaufloesung und kein Ablaufkoordinatorimport;
- keine oeffentlichen Exporte in `mcm_field_organism.__init__`.

Tests duerfen ausschliesslich Referenz-, Typ-, Aufrufzaehler-, Fehler- und
Importvertraege pruefen. Sie duerfen keine Aussage ueber Feldwirkung treffen.

## 11. Spaetere technische Verifikation

Eine erst gesondert freizugebende Implementierung muesste danach mindestens
ausfuehren:

```text
py_compile der zwei neuen Dateien
private Bindungsstrukturtests
private Adaptertests
private Ablaufkoordinationsstrukturtests
statische Import-/Exportpruefung
statische Pruefung auf dynamische Aufloesung und Ablaufkoordinatorimport
git diff --check
```

Keiner dieser Laeufe darf reale Operationsbindung mit Ablaufkoordinatorausfuehrung
kombinieren.

## 12. Fortbestehende Freigabesperren

```text
fixation_implementation_released: false
fixation_execution_released:      false
executor_implementation_released: false
runner_execution_released:        false
field_construction_released:       false
receptor_distribution_released:   false
integration_released:             false
hook_execution_released:          false
effect_evaluation_released:        false
public_av_released:                false
production_switch_released:        false
dynamics_change_released:          false
```

Dieses Dokument gibt weder die zwei neuen Dateien noch einen Aufruf der
Bindungsfabrik frei.

## 13. Aussagegrenze

Aus dieser Implementierungsvorabnahme folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI. Sie spezifiziert ausschliesslich private Typ-,
Import-, Bindungs-, Fehler- und Ausfuehrungsgrenzen.

## 14. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument unabhaengig und ausschliesslich statisch gegen Dokument
186, Dokument 185, Adaptermodul, Strukturmodul und oeffentliche Exportflaeche.
Reproduziere die fuenf Digests, bestaetige den exakt auf zwei neue private
Dateien begrenzten Umfang, beide privaten Symbole, die Testdoublepflicht, die
Import- und Ablaufkoordinatorsperren sowie alle zwoelf deaktivierten
Freigabefelder. Fuehre `git diff --check` aus. Keine Implementierungsaenderung,
keine reale Operationsbindung und keine Runtime-Ausfuehrung.
