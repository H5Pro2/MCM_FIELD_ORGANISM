# 184 - Implementierungsvorabnahme private Adaptergrenze Runtime-Fixierung Minimaltest Vorzustandsbeitrag

## 1. Zweck und Sperrgrenze

Dieses Dokument spezifiziert ausschliesslich den minimal zulaessigen Umfang
einer spaeteren privaten Adapterimplementierung fuer die in Dokument 183
festgestellten Luecken. Es implementiert keinen Adapter, stellt keine reale
Operationsbindung her und fuehrt keine Runtime oder Fixierung aus.

Die Adaptergrenze darf nur technische Vorintegratorwerte fuer den gesperrten
Doppelableitungslauf vorbereiten. Sie ist weder Organismusfunktion noch
Runner, Integrator, Hook, Messpfad oder Produktionsschnittstelle.

## 2. Gebundener Ausgangsstand

Vor jeder spaeteren Implementierung muessen die rohen Dateibytes exakt diese
SHA-256-Digests besitzen:

```text
docs/forschung/183_STATISCHE_SCHNITTSTELLEN_VORABNAHME_REALE_OPERATIONS_BINDUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md
ab2baf5cbd58a4070e8430fd37333f3c957db7b4df37503887aa934373953f2a

mcm_field_organism/_runtime_fixation_structure.py
399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e

mcm_field_organism/_previous_state_minimal_runner.py
f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72

mcm_field_organism/receptor_contract.py
af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71

mcm_field_organism/receptor_distributor.py
649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad

mcm_field_organism/field_step_time.py
2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd

mcm_field_organism/shared_mcm_field.py
2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec

mcm_field_organism/neutral_local_field_substrate.py
df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13
```

Eine Abweichung beendet die spaetere Implementierung vor jeder
Dateiaenderung. Digests duerfen nicht automatisch aktualisiert werden.

## 3. Ausschliesslich zulaessiger spaeterer Dateiumfang

Eine gesondert freizugebende Implementierung darf nur neu anlegen:

```text
mcm_field_organism/_runtime_fixation_adapters.py
tests/test_runtime_fixation_adapters.py
```

Nicht geaendert werden duerfen das bestehende Strukturmodul, seine Tests,
der Minimalrunner, Besitzerprimitive, `mcm_field_organism/__init__.py`,
oeffentliche Exporte, Runner-, Hook-, Integrator- und Public-AV-Module.

Das neue Adaptermodul bleibt privat. Es darf keinen CLI-Einstieg, keine
Default-Ausfuehrung und keine importseitige Konstruktion besitzen.

## 4. Privater Kontexttyp und Eigentum

Der spaetere private Kontexttyp `_FixationRuntimeContext` muss ein
`slots`-begrenzter, nicht oeffentlich exportierter Besitzer genau dieser
Referenzen sein:

```text
field
distributor
substrate_config
contact_id
pass_index
owner_token
discarded
```

`owner_token` muss eine pro Konstruktion frische Objektidentitaet sein.
`discarded` beginnt als `False` und darf nur durch `discard_context` einmalig
auf `True` wechseln. Der Kontext darf keine Frames, Verteilungen, Generatoren,
Boundaries oder Digests dauerhaft speichern.

Jeder Zugriff auf `field`, `distributor` oder `substrate_config` nach der
Verwerfung muss konstruktiv abbrechen. Dazu muessen die drei Referenzen beim
Verwerfen auf `None` gesetzt werden. Eine Behauptung sofortiger physischer
Speicherloeschung oder Garbage-Collection ist unzulaessig; nachzuweisen ist
nur die Entfernung aller durch die Adaptergrenze gehaltenen Referenzen.

Der Kontext darf weder kopierbar noch serialisierbar noch als Hashschluessel
verwendbar sein. Er besitzt keinen Snapshot-, Persistenz- oder Clone-Helfer.

## 5. Exakte private Adapteroberflaeche

Das spaetere Modul darf genau diese privaten Rollen besitzen und an den
gleichnamigen Operationsdatentraeger aus Dokument 181 liefern.

### 5.1 `verify_bound_source_bytes`

```text
_verify_bound_source_bytes(source_digests: tuple[tuple[str, str], ...]) -> None
```

Die Funktion liest ausschliesslich rohe Bytes regulaerer, nicht umgeleiteter
Dateien relativ zur Projektwurzel und vergleicht SHA-256 in Kleinbuchstaben.
Sie konstruiert keine Runtime und gibt weder Dateibytes noch Teildigests
zurueck. Symlink, fehlende Datei oder Abweichung fuehren zu einer bereinigten
technischen Ausnahme ohne Dateiinhalt.

### 5.2 `build_fresh_context`

```text
_build_fresh_context(contact_id: str, pass_index: int) -> _FixationRuntimeContext
```

Die Funktion darf nur die in Dokument 178 festgelegte Geometrie konstruieren:
einen neuen Referenzframe fuer C, eine neue `ReceptorDockAnatomy`, genau einen
Aufruf von `build_shared_mcm_field(...)`, einen neuen
`ReceptorDistributor`, genau ein `attach(ReceptorDock(...))` und eine neue
`NeutralLocalFieldSubstrateConfig(1.0)`. Sie darf keine Kontaktwerte des
aktuellen Kontakts verteilen und keinen Integrator aufrufen.

Jeder Aufruf erzeugt neue Feld-, Distributor-, Dock- und Tokenidentitaeten.
`contact_id` muss einer der sieben gebundenen Kontakte und `pass_index` genau
1 oder 2 sein.

### 5.3 `frame_for_contact`

```text
_frame_for_contact(contact_id: str) -> ReceptorContactFrame
```

Die Funktion ordnet ausschliesslich die sieben gesperrten Kontakt-IDs den
positionsgetreuen `_ContactSpec`-Werten des gebundenen Manifests zu und
konstruiert einen neuen `ReceptorContactFrame`. Normalisierung,
Umbenennung, Interpolation und Wiederverwendung fremder `_frame(...)`-Helfer
sind verboten.

### 5.4 `distribution_for_frame`

```text
_distribution_for_frame(
    context: _FixationRuntimeContext,
    frame: ReceptorContactFrame,
) -> ReceptorDistribution
```

Die Funktion prueft aktiven Kontext und passenden `contact_id`, konstruiert
genau eine `CommonFieldTime` mit `organism.minimal.v1` und ruft genau einmal
`context.distributor.distribute((frame,), common_field_time)` auf. Dock-
Mutation und fremde `_distribution(...)`-Helfer sind verboten.

### 5.5 `distribution_digest`

```text
_distribution_digest(distribution: ReceptorDistribution) -> str
```

Die Funktion ruft genau einmal die konkret gebundene Methode
`distribution.digest()` auf und validiert einen SHA-256-Hexstring. Generische
Methodensuche oder Neuimplementierung der Payload ist verboten.

### 5.6 `step_time_for_frame`

```text
_step_time_for_frame(frame: ReceptorContactFrame) -> MCMFieldStepTime
```

Die Funktion konstruiert ausschliesslich `MCMFieldStepTime` mit Clock
`organism.minimal.v1`, unveraenderten Framegrenzen und
`ticks_per_second=10.0`. Sie ruft keine Feldfunktion auf.

### 5.7 `generator_and_boundary`

```text
_generator_and_boundary_for_distribution(
    context: _FixationRuntimeContext,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
) -> tuple[np.ndarray, np.ndarray]
```

Die Funktion validiert aktiven Kontext, identische Clock- und Fenstergrenzen
von Verteilung und Schrittzeit und ruft genau einmal das gebundene Primitive
`neutral_local_field_substrate._generator_and_boundary(
context.field, distribution, context.substrate_config)` auf. `step_time`
dient nur der Vertragspruefung. Integrator und Feldfortschritt sind verboten.

### 5.8 `generator_digest`

```text
_generator_digest(generator: np.ndarray) -> str
```

Die Funktion verlangt eine endliche quadratische zweidimensionale Matrix,
wandelt sie in eine zeilenweise Python-Float-Liste um und bildet exakt den
kanonischen JSON-SHA-256-Digest aus Dokument 178. Rundung, Clipping,
Bytehashing und dtype-abhaengige Kodierung sind verboten.

### 5.9 `boundary_digest`

```text
_boundary_digest(boundary: np.ndarray) -> str
```

Die Funktion verlangt einen endlichen eindimensionalen Vektor, wandelt ihn
in eine Python-Float-Liste um und bildet exakt den kanonischen JSON-SHA-256-
Digest aus Dokument 178. Formataenderung und Umhuellungsobjekt sind verboten.

### 5.10 `discard_context`

```text
_discard_context(context: _FixationRuntimeContext) -> None
```

Die Funktion akzeptiert nur einen aktiven Kontext, entfernt dessen Referenzen
auf Feld, Distributor und Substratkonfiguration und setzt `discarded` auf
`True`. Doppelte Verwerfung, fremder Kontext oder Zugriff nach Verwerfung
muessen abbrechen. Sie darf keinen Snapshot, Digest, Logger, Callback,
Destruktoraufruf oder Persistenzpfad ausloesen.

## 6. Bildung des Operationsdatentraegers

Ein spaeterer privater Fabrikhelfer darf ausschliesslich die zehn Funktionen
aus Abschnitt 5 positions- und namensgetreu in `_FixationOperations` binden:

```text
_build_private_fixation_operations() -> _FixationOperations
```

Die Fabrik darf keine Argumente, Defaults, Overrides, Registry,
Umgebungsvariablen, dynamischen Imports oder Namenslookup besitzen. Sie darf
die Orchestrierung nicht aufrufen. Der Fabrikhelfer und der Datentraeger
duerfen nicht oeffentlich exportiert werden.

## 7. Teilwert-, Fehler- und Ressourcenregeln

Frames, Verteilungen, Generatoren, Boundaries und einzelne Digests bleiben
aufruflokal. Kein Adapter darf sie loggen, persistieren, an Callbacks senden
oder in Ausnahmeinhalte aufnehmen. Fremde Ausnahmeinhalte werden bereinigt.

Schlaegt die Kontextkonstruktion vor Rueckgabe fehl, muss die Funktion alle
von ihr gehaltenen Referenzen auf bereits erzeugte Objekte entfernen. Nach
erfolgreicher Rueckgabe liegt die Verwerfung ausschliesslich bei
`discard_context` und der bereits abgenommenen Orchestrierung.

Die Tests duerfen Ressourcenfreigabe nur als Referenz- und Zustandsvertrag
pruefen. Aussagen ueber sofortige physische Speicherfreigabe sind verboten.

## 8. Spaetere Strukturtests

Eine erst gesondert freizugebende Implementierung muss mit isolierten
Konstruktor- und Primitive-Testdoubles pruefen:

- exakt zehn Rollen ohne zusaetzliche oder dynamische Bindung;
- 14 frische Kontext-, Feld-, Distributor- und Tokenidentitaeten;
- Ablehnung unbekannter Kontakte und Durchgaenge;
- positionsgetreue Framebildung;
- genau einen Verteilungs- und Generator-/Boundary-Aufruf;
- kanonische Generator- und Boundary-Digests;
- einmalige Verwerfung und entfernte Kontextreferenzen;
- Abbruch bei Doppelverwerfung und Zugriff nach Verwerfung;
- Bereinigung fremder Ausnahmeinhalte und keine Teilwertausgabe;
- fehlende Integrator-, Hook-, Snapshot-, Logger- und Persistenzaufrufe;
- weiterhin abbrechenden `execute_runtime_fixation(...)`;
- fehlende oeffentliche Exporte.

Kein Test darf die reale Orchestrierung mit den realen Adapteroperationen
ausfuehren. Eine solche Bindungs- oder Fixierungsausfuehrung erfordert eine
weitere gesonderte Vorabnahme.

## 9. Freigabezustand

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

Dieses Dokument erteilt keine Adapterimplementierungsfreigabe. Es bindet nur
den zulaessigen Umfang eines spaeter gesondert zu pruefenden Auftrags.

## 10. Aussagegrenze

Aus dieser Implementierungsvorabnahme folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI. Sie spezifiziert ausschliesslich eine weiterhin
gesperrte technische Adaptergrenze.

## 11. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument unabhaengig und ausschliesslich statisch gegen die
Dokumente 178, 181, 182 und 183 sowie die gebundenen Besitzerdateien. Pruefe
Dateiumfang, Kontextbesitz, alle zehn Adapterrollen, Fabriksperre,
Teilwertschutz, Ressourcenregeln, Testgrenzen und alle zwoelf deaktivierten
Freigabefelder. Keine Implementierung, keine reale Operationsbindung und
keine Runtime-Ausfuehrung.
