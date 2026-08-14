# 190 - Implementierungsvorabnahme einer privaten Orchestrator-Uebergabe

## 1. Zweck und Sperrwirkung

Dieses Dokument spezifiziert den maximal zulaessigen Umfang einer spaeteren privaten Orchestrator-Uebergabe. Es ist eine reine Implementierungsvorabnahme und keine Freigabe zur Implementierung oder Ausfuehrung.

Jeder reale Aufruf von `_orchestrate_runtime_fixation_with_operations(...)` bleibt reale Fixierungsausfuehrung. Die reale Adapterfabrik darf nicht zusammen mit diesem Orchestrator ausgefuehrt werden.

## 2. Gepruefter Byte-Stand

| Datei | SHA-256 |
|---|---|
| `docs/forschung/189_STATISCHE_VORABNAHME_PRIVATE_ORCHESTRATOR_UEBERGABE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `2ab72a64f3911224241c4ed48e9daf42cc4194c1f47f3685de3a467df1f2cfbd` |
| `docs/forschung/188_TECHNISCHE_ABSCHLUSSABNAHME_PRIVATE_BINDUNGSBRUECKE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `90b371dbd551df8363c39a31650be5e18807a6461dc41b3db87d06b42e23cda6` |
| `mcm_field_organism/_runtime_fixation_binding.py` | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

Die spaeter vorgesehenen Dateien existieren in diesem Stand nicht:

- `mcm_field_organism/_runtime_fixation_handoff.py`
- `tests/test_runtime_fixation_handoff.py`

## 3. Spaeter maximal zulaessiger Dateiumfang

Eine gesonderte Implementierungsfreigabe duerfte genau zwei neue Dateien umfassen:

- `mcm_field_organism/_runtime_fixation_handoff.py`
- `tests/test_runtime_fixation_handoff.py`

Keine bestehende Implementierungs-, Test-, Runtime- oder Exportdatei duerfte geaendert werden.

## 4. Spaeter maximal zulaessige Produktionsoberflaeche

Das Produktionsmodul duerfte genau ein eigenes Produktionssymbol definieren:

```python
def _execute_private_runtime_fixation(
    binding: _PrivateFixationBinding,
) -> _FixedDigestBundle:
```

Die Funktion duerfte weder optionale Parameter noch Positionsvarianten, Callbacks, Schalter oder Konfiguration annehmen. Der Funktionsname muss die reale Ausfuehrungswirkung sichtbar halten.

## 5. Zulaessige statische Imports

Das spaetere Produktionsmodul duerfte ausschliesslich statisch importieren:

```python
from ._previous_state_minimal_runner import PreviousStateMinimalRunnerError
from ._runtime_fixation_binding import _PrivateFixationBinding
from ._runtime_fixation_structure import (
    _FixedDigestBundle,
    _orchestrate_runtime_fixation_with_operations,
)
```

Insbesondere verboten bleiben Imports von:

- `_build_private_fixation_binding`;
- `_build_private_fixation_operations`;
- `build_locked_runtime_fixation_structure`;
- Runnern, Integratoren, Hooks, Executoren oder Public-AV-Modulen.

Damit darf das Handoff-Modul weder Struktur noch Operationen selbst erzeugen. Es darf nur ein explizit uebergebenes, bereits typgueltiges Bindungsobjekt verwenden.

## 6. Spaeter zulaessiger Funktionsablauf

Eine gesondert freigegebene Implementierung duerfte ausschliesslich:

1. `binding` direkt als `_PrivateFixationBinding` typpruefen;
2. genau einmal `_orchestrate_runtime_fixation_with_operations(binding.structure, binding.operations)` aufrufen;
3. die Rueckgabe direkt als `_FixedDigestBundle` typpruefen;
4. genau dieses Rueckgabeobjekt unveraendert zurueckgeben.

Jede Eingangs-, Orchestrator- oder Rueckgabeabweichung muss mit einer festen `PreviousStateMinimalRunnerError` ohne Teilbuendel, Objektinhalte oder fremde Ausnahmeinhalte abbrechen. Ein zulaessiger fester Fehlertext waere:

```text
private runtime fixation execution failed
```

Verboten bleiben:

- Retry, Schleife oder zweiter Orchestratoraufruf;
- Aufruf einer Operationsrolle direkt aus dem Handoff-Modul;
- Mutation, Kopie, Speicherung oder Serialisierung von Bindung oder Ergebnis;
- Ergebnisumformung, Filterung oder fachliche Bewertung;
- Cache, Singleton oder Importnebenwirkung;
- dynamische Symbolaufloesung.

## 7. Testdoublepflicht

Die spaeteren Handoff-Tests duerften den realen Orchestrator nicht ausfuehren. Das im Handoff-Modul statisch importierte Orchestratorsymbol muss vor jedem Funktionsaufruf durch ein Testdouble ersetzt werden.

Die Tests duerften ein typgueltiges, aber nicht ausfuehrbares Bindungsobjekt nur aus uninitialisierten privaten Traegern zusammensetzen. Dabei darf weder `_build_private_fixation_binding()` noch `_build_private_fixation_operations()` noch `build_locked_runtime_fixation_structure()` aufgerufen werden.

Ein positiver Orchestrator-Testdouble muss ein typgueltiges, nicht berechnetes `_FixedDigestBundle` liefern. Keine Operationsrolle darf erreichbar oder aufrufbar sein.

Mindestens zu pruefen waeren:

- genau ein privates Produktionssymbol;
- exakte Funktionssignatur und Parameterpflicht;
- genau ein Testdouble-Aufruf mit identischen `structure`- und `operations`-Objekten;
- unveraenderte Identitaet des typgueltigen Rueckgabeobjekts;
- Abbruch vor dem Orchestrator bei fremdem Bindungstyp;
- bereinigter Abbruch bei Orchestratorausnahme;
- bereinigter Abbruch bei fremdem Rueckgabetyp;
- keine Preisgabe geheimer Eingaben oder fremder Ausnahmeinhalte;
- keine Importnebenwirkung, dynamische Aufloesung oder oeffentliche Exportflaeche;
- statisch kein Import einer Fabrik, eines Runners, Integrators, Hooks, Executors oder Public-AV-Moduls.

## 8. Isolations- und Ausfuehrungsgrenze

Selbst eine spaetere Implementierung dieser einen Funktion waere noch keine Freigabe, sie mit einer real erzeugten Bindung aufzurufen. Die technische Implementierung und die reale Fixierungsausfuehrung bleiben getrennte Freigabestufen.

Nicht freigegeben sind:

- reale Adapterfabrik plus Orchestrator;
- reale Bindungsfabrik plus Handoff-Funktion;
- Runner-, Integrator-, Hook- oder Executor-Anbindung;
- Public-AV-Anbindung;
- Produktionsschalter oder automatische Ausfuehrung;
- Runtime-Aufruf und reale Fixierung.

## 9. Import- und Exportgrenze

Die einzig zulaessige spaetere Abhaengigkeitsrichtung waere:

```text
_runtime_fixation_handoff
  -> _runtime_fixation_binding
  -> _runtime_fixation_structure

_runtime_fixation_handoff
  -> _runtime_fixation_structure._orchestrate_runtime_fixation_with_operations
```

Rueckimporte in das Handoff-Modul bleiben verboten. `mcm_field_organism/__init__.py` darf weder das Modul noch `_execute_private_runtime_fixation` exportieren.

## 10. Freigabefelder

```text
real_operations_binding_release: false
real_fixation_execution_release: false
runtime_release: false
runner_release: false
integrator_release: false
hook_release: false
executor_release: false
public_av_release: false
production_switch_release: false
automatic_execution_release: false
orchestrator_handoff_release: false
minimal_test_release: false
```

## 11. Vorabnahmeentscheidung

Der beschriebene Implementierungsumfang ist statisch eng genug, um unabhaengig geprueft zu werden. Eine Implementierung bleibt bis zu einer positiven Review dieses Dokuments gesperrt. Auch eine spaetere positive Implementierungsreview duerfte keine reale Fixierung oder Runtime freigeben.

## 12. Aussagegrenze

Kein Teil dieses Vertrags begruendet einen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 13. Zielbezug

Es besteht keine erkennbare Zielabweichung. Der Vertrag fuegt keine Labels, Rewards, Zielantworten, Erinnerungsinhalte oder Topologien hinzu. Er begrenzt ausschliesslich eine technische Ausfuehrungsschnittstelle.

## 14. Naechster Pruefschritt

Dieses Dokument ist unabhaengig und ausschliesslich statisch zu pruefen. Zu bestaetigen sind mindestens:

- alle fuenf SHA-256-Digests;
- Nichtexistenz der zwei vorgesehenen Handoff-Dateien;
- Zwei-Dateien- und Ein-Symbol-Obergrenze;
- exakte Signatur, Imports und Einmalaufrufvertrag;
- Testdoublepflicht und bereinigte Fehlergrenze;
- Sperre gegen reale Fabriken plus Orchestrator;
- Import-, Export-, Dynamik- und Runtime-Sperren;
- genau zwoelf `false`- und kein `true`-Freigabefeld;
- `git diff --check`.

Die Review darf keine Implementierungsdatei aendern, keine Handoff-Datei anlegen und keine Fixierung oder Runtime ausfuehren. Erst nach positiver Review darf ein ausfuehrender Agent die konkrete Zwei-Dateien-Implementierung als eigenen Auftrag erhalten.
