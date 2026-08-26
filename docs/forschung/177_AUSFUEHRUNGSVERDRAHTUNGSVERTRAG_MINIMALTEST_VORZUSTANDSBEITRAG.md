# 177 - Ausfuehrungsverdrahtungsvertrag Minimaltest Vorzustandsbeitrag

## 1. Zweck und Grenze

Dieses Dokument fixiert ausschliesslich die spaetere private Verdrahtung des in
den Dokumenten 172 bis 176 vorregistrierten Minimaltests. Es implementiert
keinen Executor, konstruiert kein Feld und fuehrt keinen Test- oder Effektlauf
aus.

Der strukturell abgenommene Manifestcode in
`mcm_field_organism/_previous_state_minimal_runner.py` bleibt unveraendert und
standardmaessig gesperrt. Dieser Vertrag fuegt keine Hypothese, Metrik,
Toleranz, Bedeutung, Belohnung, Zieltopologie oder Organismusfunktion hinzu.

## 2. Einzige zulaessige Runtime-Bausteine

Eine spaetere private Executor-Implementierung darf fuer die Feldverdrahtung
nur die folgenden bestehenden Schnittstellen verwenden:

- `ReceptorContactFrame` und `CommonFieldTime` aus `receptor_contract.py`;
- `ReceptorDock`, `ReceptorDistribution` und `ReceptorDistributor` aus
  `receptor_distributor.py`;
- `ReceptorDockAnatomy`, `SharedMCMField` und `build_shared_mcm_field` aus
  `shared_mcm_field.py`;
- `MCMFieldStepTime` aus `field_step_time.py`;
- `NeutralLocalFieldSubstrateConfig` und `NeutralFastAfterimageConfig` aus
  `neutral_local_field_substrate.py`;
- den bestehenden privaten, zustandsneutralen Helfer
  `_generator_and_boundary` ausschliesslich zur Bildung der bereits
  vorregistrierten Generator- und Boundary-Digests;
- `advance_neutral_fast_shared_field` fuer alle Ereignisse der Geschichte;
- den privaten `advance_with_previous_state_operator` ausschliesslich fuer C.

`NeutralFieldDissipationConfig` darf weder konstruiert noch als Typ eines
Laufobjekts gespeichert werden. An jedem Aufruf ist
`dissipation_config=None` explizit zu uebergeben.

`ReceptorDistribution` ist ausschliesslich als Rueckgabe von
`ReceptorDistributor.distribute(...)` und als Typ der privaten
`_distribution`- und `_measure`-Schnittstellen zulaessig. Der Executor darf
sie weder manuell neu modellieren noch kopieren oder durch einen eigenen
Verteilungstyp ersetzen.

Die gebuendelte Funktion `run_neutral_asynchronous_field` ist fuer diesen Test
nicht zulaessig. Sie stellt die Messgrenzen M0 bis M3 und den isolierten
Hook-Aufruf fuer C nicht einzeln bereit.

`_generator_and_boundary` darf sein Rueckgabeformat nicht veraendern und darf
nicht kopiert oder neu implementiert werden. Generator und Boundary werden als
verschachtelte beziehungsweise einfache Floatlisten mit den kanonischen
JSON-Regeln aus Dokument 175 serialisiert und getrennt per SHA-256 gebunden.

## 3. Feste private Datentypen und Signaturen

Die spaetere Implementierung muss private, unveraenderliche Dataclasses mit
mindestens den folgenden technischen Rollen verwenden:

```python
@dataclass(frozen=True, slots=True)
class _RunContext:
    run_id: str
    field: SharedMCMField
    distributor: ReceptorDistributor
    substrate_config: NeutralLocalFieldSubstrateConfig
    afterimage_config: NeutralFastAfterimageConfig
    geometry_digest: str
    construction_digest: str

@dataclass(frozen=True, slots=True)
class _Measurement:
    run_id: str
    point: str
    snapshot_digest: str
    layer_digest: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_tick: int
    common_interval: tuple[int, int] | None
    receptor_distribution_digest: str | None
    generator_digest: str | None
    boundary_digest: str | None
    geometry_digest: str

@dataclass(frozen=True, slots=True)
class _TechnicalAbort:
    condition_id: str
    run_id: str | None
    point: str | None
    diagnostics: tuple[tuple[str, str], ...]
```

Die privaten Hilfsfunktionen werden auf folgende Rollen begrenzt:

```python
def _validate_preflight(manifest: _LockedRunnerManifest) -> None: ...
def _build_fresh_run_context(manifest: _LockedRunnerManifest, run_id: str) -> _RunContext: ...
def _frame(contact: _ContactSpec) -> ReceptorContactFrame: ...
def _distribution(context: _RunContext, frame: ReceptorContactFrame) -> ReceptorDistribution: ...
def _step_time(frame: ReceptorContactFrame) -> MCMFieldStepTime: ...
def _measure(context: _RunContext, point: str, pending: ReceptorDistribution | None) -> _Measurement: ...
def _advance_history(context: _RunContext, frame: ReceptorContactFrame) -> _RunContext: ...
def _advance_c(context: _RunContext, frame: ReceptorContactFrame, operator: str | None) -> _RunContext: ...
```

Der vorhandene Einstiegspunkt
`execute_previous_state_minimal_runner(manifest) -> None` bleibt bis zu einer
separaten Ausfuehrungsfreigabe eine immer abbrechende Sperre. Es darf kein
Umgebungsvariablen-, CLI-, Konfigurations- oder Produktionsschalter ergaenzt
werden.

## 4. Vorlaufvalidierung

`_validate_preflight` muss vor jeder moeglichen Feldkonstruktion erfolgreich
alle folgenden Bedingungen pruefen:

1. Das Manifest besteht seine eigene Konstruktorvalidierung unveraendert.
2. Die 24 Laufzeilen sind byte- und wertgleich zu Dokument 173.
3. A, B, C, Konfiguration und Digest-Tupel sind bytegleich zu Dokument 175.
4. Die vier Einzeldigests und der Bundle-Digest werden neu berechnet.
5. `dissipation_config` ist vorhanden und exakt `None`.
6. `numeric_zero == 1e-12`, `rtol == 0.0` und `ticks_per_second == 10.0`.
7. Die zwoelf Abbruchbedingungen und M0 bis M3 sind vollstaendig und geordnet.
8. Hook- und Runner-Quellstand werden durch vorab fixierte Dateidigests
   identifiziert; die Sollwerte duerfen nicht erst waehrend eines Laufs
   erzeugt werden.

Ein Fehler erzeugt nur `_TechnicalAbort`. Danach darf kein Kontext gebaut
werden.

## 5. Frische Konstruktion je Laufzeile

`_build_fresh_run_context` wird fuer jede der 24 Laufzeilen genau einmal neu
aufgerufen. Kein Objekt aus einem frueheren Kontext darf uebernommen werden.

Die Konstruktion ist exakt:

1. C wird nur als bytegleiche, wertfreie Geometriereferenz in einen
   `ReceptorContactFrame` umgewandelt. Seine Kontaktwerte werden dabei nicht
   verteilt und gelangen nicht ins Feld.
2. `build_shared_mcm_field` wird signaturgetreu und ausschliesslich so
   aufgerufen:

   ```python
   anatomy = ReceptorDockAnatomy(
       "synthetic",
       "dock.synthetic",
       ((0,), (1,), (2,)),
   )
   field = build_shared_mcm_field(
       reference_frames=(c_reference_frame,),
       anatomies={"synthetic": anatomy},
       sample_offsets=((-1,), (1,)),
       field_id="organism.mcm_field",
       layer_id="organism.mcm_layer",
       geometry_id="organism.shared.v1",
   )
   ```

   `reference_frames` bleibt damit ein einelementiges Iterable und
   `anatomies` ein exakt nach Modalitaet indiziertes Mapping.
3. Ein neuer `ReceptorDistributor` wird erzeugt und genau ein
   `ReceptorDock("dock.synthetic", "synthetic", "synthetic.line3.v1")`
   angehaengt.
4. Die Konfigurationen werden neu als
   `NeutralLocalFieldSubstrateConfig(1.0)` und
   `NeutralFastAfterimageConfig(0.5)` konstruiert.
5. Der Konstruktionsdigest wird aus kanonischen Geometrie-, Dock-, Layer- und
   Konfigurationsrollen gebildet. Er muss in allen 24 Kontexten bitgleich sein.

Die Verwendung von C als Referenz bestimmt nur die bereits fixierte
Traegeranatomie. Sie darf weder einen Feldtick noch Rezeptorkontakt,
Aktivierung oder Nachhall erzeugen.

## 6. Zeit- und Ereignisabbildung

Jede `_ContactSpec` wird ohne Werte- oder Identitaetsaenderung in genau einen
`ReceptorContactFrame` ueberfuehrt. Fuer jedes Ereignis gelten:

```text
CommonFieldTime.clock_id:          organism.minimal.v1
CommonFieldTime.window_start_tick: ContactSpec.window_start_tick
CommonFieldTime.window_end_tick:   ContactSpec.window_end_tick
MCMFieldStepTime.clock_id:         organism.minimal.v1
MCMFieldStepTime.start_tick:       ContactSpec.window_start_tick
MCMFieldStepTime.end_tick:         ContactSpec.window_end_tick
MCMFieldStepTime.ticks_per_second: 10.0
```

`ReceptorDistributor.distribute((frame,), common_field_time)` erzeugt genau
eine Verteilung je Ereignis. Ereignisse duerfen nicht gebuendelt, sortiert,
interpoliert, wiederholt oder ausgelassen werden.

## 7. Ablauf und Messpunkte

Fuer jede Laufzeile ist die Reihenfolge zwingend:

1. Vorlaufvalidierung fuer das unveraenderte Manifest.
2. Frischen Kontext konstruieren.
3. **M0** unmittelbar am frischen Kontext erfassen.
4. Die drei Ereignisse der zugeordneten Geschichte A oder B in ihrer
   fixierten Reihenfolge verteilen und jeweils mit
   `advance_neutral_fast_shared_field(..., dissipation_config=None)`
   fortschreiben.
5. **M1** nach dem dritten Geschichtsereignis erfassen.
6. C bytegleich konstruieren und verteilen, ohne das Feld fortzuschreiben.
7. **M2** mit der anstehenden C-Verteilung erfassen.
8. C genau einmal mit
   `advance_with_previous_state_operator(..., dissipation_config=None,
   previous_state_operator=operator)` fortschreiben.
9. **M3** unmittelbar am zurueckgegebenen Feld erfassen.
10. Den Kontext danach verwerfen; er darf nicht fuer die naechste Laufzeile
    wiederverwendet werden.

Der Hook wird niemals fuer A oder B aufgerufen. `None`, `identity` und `zero`
unterscheiden ausschliesslich den vorregistrierten Operator beim C-Schritt.

## 8. Zustandsneutrale Messung und M0

`SharedMCMField.snapshot()` verlangt eine abgeschlossene Verteilung und kann
deshalb an M0 nicht verwendet werden. Ein kuenstlicher Nullkontakt oder
Vorlauftick ist verboten.

`_measure` muss daher fuer alle vier Punkte denselben privaten kanonischen
Runner-Snapshot bilden. Er enthaelt ausschliesslich:

- `field.layer.digest()`;
- geordnete Aktivierungs- und Nachhallvektoren aus `field.layer.neurons`;
- `field.layer.tick`;
- kanonische Dock- und Geometrierollen;
- das letzte gemeinsame Intervall oder `null` an M0;
- Digest der anstehenden beziehungsweise letzten Rezeptorverteilung oder
  `null` an M0;
- Generator- und Boundary-Digest fuer die anstehende beziehungsweise letzte
  Verteilung oder `null` an M0;
- `run_id` und Messpunkt nur im Messumschlag, nicht im Zustandsdigest.

Der Zustandsdigest wird mit den Serialisierungsregeln aus Dokument 175
gebildet. Dieselbe Funktion und dasselbe Schema gelten an M0 bis M3. Ab M1
darf `SharedMCMField.snapshot().digest()` zusaetzlich als bereits vorhandene
technische Rolle protokolliert werden; es ersetzt nicht den punktuebergreifend
definierten Runner-Snapshot-Digest.

Die Messfunktion darf keine Methode aufrufen, die Feld, Layer, Distributor
oder Verteilung veraendert.

## 9. Abbruchbindung

Die zwoelf IDs aus `_ABORT_CONDITIONS` werden positionsgleich auf die zwoelf
Abbruchbedingungen aus Dokument 173 abgebildet. Jede Bedingung wird an der
fruehesten technisch pruefbaren Stelle ausgewertet.

Bei einem Abbruch werden ausschliesslich Bedingungs-ID, Lauf-ID, Messpunkt und
bereits vorhandene technische Diagnosen gespeichert. Es gibt keine
Hypothesenentscheidung und keine Auswertung von Teilresultaten. Nach dem
ersten Abbruch wird kein weiterer Arm begonnen.

Insbesondere muessen Konstruktion, Geometrie, Generator, Boundary,
Rezeptorverteilung und Konfiguration vor dem jeweiligen Integratoraufruf gegen
ihre fixierten Digests geprueft werden. Nicht-finite Aktivierungs- oder
Nachhallwerte und Werte ausserhalb `[-1.0, 1.0]` brechen sofort ab.

## 10. Protokoll- und Einsichtssperre

Ein spaeterer Executor darf waehrend der 24 Laufzeilen weder `_Measurement`
noch Zwischenvergleiche an Aufrufer, Konsole, Logger oder Callback ausgeben.
Er darf keine Ergebnis-Callbacks und keinen Fortschrittszustand mit
Messwerten akzeptieren.

Die Messungen werden in einer privaten, nur anhaengbaren Sequenz gesammelt.
Erst nachdem alle 24 Laufzeilen und alle technischen Abbruchpruefungen
erfolgreich abgeschlossen sind, darf ein unveraenderliches Gesamtbundle
gebildet werden. Dessen fachliche Auswertung bleibt ein separater, nicht
freigegebener Schritt.

## 11. Verbindliche Implementierungstests fuer einen spaeteren Auftrag

Eine spaetere Implementierung muss vor jeder Ausfuehrungsfreigabe mit reinen
Fakes oder Mocks nachweisen:

- 24 frische und voneinander verschiedene Kontextobjekte;
- exakte Aufrufreihenfolge M0, A/B, M1, C-Verteilung, M2, C-Hook, M3;
- genau drei neutrale Geschichtsschritte und einen C-Hook-Schritt je Lauf;
- explizites `dissipation_config=None` an jedem Feldaufruf;
- keine Hook-Verwendung fuer A oder B;
- keine Messwertausgabe vor vollstaendigem Abschluss;
- sofortigen Stopp bei jeder der zwoelf Abbruchbedingungen;
- weiterhin immer abbrechenden oeffentlich erreichbaren Einstiegspunkt.

Diese Tests duerfen keine reale Feldkonstruktion, Rezeptorverteilung oder
Integration ausloesen.

## 12. Freigabezustand und Aussagegrenze

```text
executor_implementation_released: false
runner_execution_released:        false
field_construction_released:       false
effect_evaluation_released:        false
public_av_released:                false
production_switch_released:        false
dynamics_change_released:          false
```

Aus diesem Verdrahtungsvertrag folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI.

## 13. Naechster ausfuehrbarer Auftrag

Pruefe diesen Verdrahtungsvertrag statisch gegen die Dokumente 172 bis 176 und
die genannten Runtime-Schnittstellen. Pruefe insbesondere die M0-Loesung, die
Trennung von Geschichte und C-Hook, die Frischkonstruktion, die
Abbruchzeitpunkte und die Einsichtssperre. Noch keinen Executor implementieren
und keinen Feld- oder Effektlauf ausfuehren.
