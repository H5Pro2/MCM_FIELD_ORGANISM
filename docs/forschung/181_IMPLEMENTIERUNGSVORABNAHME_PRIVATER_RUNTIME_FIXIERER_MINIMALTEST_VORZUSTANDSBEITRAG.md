# 181 - Implementierungsvorabnahme privater Runtime-Fixierer Minimaltest Vorzustandsbeitrag

## 1. Zweck und Grenze

Dieses Dokument beschreibt ausschliesslich den minimal zulaessigen Umfang
einer spaeteren privaten Implementierungsaenderung fuer die Runtime-Fixierung
aus den Dokumenten 179 und 180. Es implementiert diese Aenderung nicht, fuehrt
keine Fixierung aus und gibt keine reale Runtime-Bindung frei.

Die spaetere Aenderung darf nur eine mit Testdoubles pruefbare private
Orchestrierung vorbereiten. Sie darf weder die 21 technischen Sollwerte
erzeugen noch Feldresultate, Bedeutung oder eine erwartete Topologie
vorfixieren.

## 2. Gebundener Ausgangsstand

Vor jeder spaeteren Implementierung muessen die rohen Dateibytes exakt diese
SHA-256-Digests besitzen:

```text
docs/forschung/180_AUSFUEHRUNGSVORABNAHME_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md
39fb3a756f066bacf0e40d0a7748c5927f58ffbc79e3f32b620e57a8c69fca03

mcm_field_organism/_runtime_fixation_structure.py
27c661d3e9f2738a18434fb8a03388c1621b3db083a020480454f0003c43de0e

tests/test_runtime_fixation_structure.py
db13044921cb96f3c28cf0fda8bc7ac93dac92a5766c6fd8e5de61a324a765f2
```

Auch die in Dokument 180 gebundenen Sperr-, Quellstand-, Geometrie- und
Konstruktionsdigests bleiben unveraendert wirksam. Eine Abweichung beendet
die spaetere Implementierungsvorabnahme vor jeder Dateiaenderung.

## 3. Ausschliesslich zulaessiger Dateiumfang

Eine spaetere, gesondert freigegebene Implementierung darf nur diese Dateien
aendern:

```text
mcm_field_organism/_runtime_fixation_structure.py
tests/test_runtime_fixation_structure.py
```

Nicht zulaessig sind insbesondere Aenderungen an:

- `mcm_field_organism/_previous_state_minimal_runner.py`;
- `mcm_field_organism/previous_state_contribution_hook.py`;
- Feld-, Distributor-, Integrator-, Generator- oder Substratmodulen;
- `mcm_field_organism/__init__.py` oder anderen oeffentlichen Exportflaechen;
- Forschungsrunnern, Produktionsschaltern oder Public-AV-Pfaden.

Neue Produktionsdateien, CLI-Einstiege, Logger, Persistenzadapter oder
oeffentliche Symbole sind nicht erlaubt.

## 4. Minimal zulaessige private Implementierungsform

Das private Strukturmodul darf um genau eine rein injizierte
Orchestrierungsoberflaeche und die dafuer notwendigen privaten,
unveraenderlichen Datentraeger erweitert werden. Die Oberflaeche muss:

1. eine bereits validierte `_LockedFixationStructure` verlangen;
2. alle technischen Operationen ausschliesslich als privaten injizierten
   Operationsdatentraeger erhalten;
3. keine reale Feld-, Distributor-, Generator-, Hook-, Integrator- oder
   Snapshot-Implementierung importieren oder selbst aufloesen;
4. genau zwei Durchgaenge ueber die sieben gebundenen Kontakte koordinieren;
5. fuer jeden Kontakt und Durchgang ein eigenes Kontextobjekt verlangen;
6. Zwischenwerte ausschliesslich lauflokal halten;
7. nur nach vollstaendig bitgleichem Doppelabgleich ein vollstaendiges
   unveraenderliches Bundleobjekt zurueckgeben;
8. bei jedem Fehler alle lauflokalen Ergebnisse verwerfen und nur
   `PreviousStateMinimalRunnerError` mit begrenzter technischer Diagnose
   ausloesen.

Die private Orchestrierung darf keine Default-Operationen besitzen. Ohne
explizit injizierten Operationsdatentraeger muss ihre Konstruktion oder ihr
Aufruf abbrechen. Das Produktionsmodul darf keinen Adapter enthalten, der
die injizierten Rollen mit realen Runtime-Funktionen verbindet.

## 5. Abschliessende injizierbare Rollen

Der private Operationsdatentraeger darf ausschliesslich folgende Rollen
bereitstellen:

```text
verify_bound_source_bytes
build_fresh_context
frame_for_contact
distribution_for_frame
distribution_digest
step_time_for_frame
generator_and_boundary
generator_digest
boundary_digest
discard_context
```

Diese Rollen bilden die erlaubte Aufrufliste aus Dokument 180 ab. Die
Orchestrierung muss Reihenfolge und Aufrufanzahl pruefen. Pro Kontakt und
Durchgang sind genau ein Kontext, eine Verteilung, ein Verteilungsdigest,
eine Schrittzeitpruefung, eine Generator-/Boundary-Ableitung und je ein
Generator- und Boundary-Digest zulaessig. `discard_context` muss fuer jeden
erzeugten Kontext auch im Fehlerfall genau einmal versucht werden.

Der Operationsdatentraeger darf keine generische Callable-Sammlung, keinen
Namenslookup und keinen dynamischen Import erlauben. Zusaetzliche Rollen
muessen konstruktiv abgewiesen werden.

## 6. Standard-Einstieg und Freigabesicherung

`execute_runtime_fixation(...)` bleibt der standardmaessige Einstieg und muss
weiterhin unabhaengig von Argumenten mit

```text
runtime fixation is not released
```

abbrechen. Er darf die private Orchestrierungsoberflaeche nicht aufrufen.

`fixation_execution_released` bleibt `false`. Kein anderes Freigabefeld darf
auf `true` wechseln. Die spaetere Implementierung darf weder Umgebungsvariable
noch Kommandozeilenargument, Dateimarker, Callback oder importierbaren
Schalter einfuehren, der diese Sperre umgeht.

Die private Orchestrierungsoberflaeche ist kein Ausfuehrungseinstieg. Sie ist
nur eine noch runtimefreie, durch injizierte Testdoubles pruefbare
Kontrolllogik. Eine reale Operationsbindung erfordert eine weitere
gesonderte Implementierungsvorabnahme.

## 7. Ergebnis- und Teilwertsperre

Der vollstaendige Rueckgabedatentraeger darf nur die Bundleform aus Dokument
179 abbilden. Nicht erlaubt sind Rueckgaben oder beobachtbare Callbacks fuer:

- einzelne Kontakt-Digests;
- einen einzelnen Durchgang;
- teilweise gefuellte Eintragslisten;
- Kontext-, Frame-, Verteilungs-, Generator- oder Boundary-Objekte;
- M0- bis M3-Zustaende, Aktivierung, Nachhall, Layer oder Effekte.

Bei nicht bitgleichen Durchgaengen, einer Ausnahme oder einem unvollstaendig
verworfenem Kontext darf kein Ergebnisobjekt entstehen. Fehlermeldungen
duerfen keine synthetischen oder spaeter realen Ableitungsdigests enthalten.

## 8. Verbindliche Tests mit Testdoubles

Die spaetere Testaenderung darf ausschliesslich deterministische Testdoubles
verwenden. Sie darf keine echte Feldkonstruktion, Rezeptorverteilung,
Generator-/Boundary-Bildung oder sonstige Runtime-Funktion aufrufen.

Positive Strukturtests muessen nachweisen:

- sieben Kontakte in richtiger Reihenfolge in beiden Durchgaengen;
- 14 verschiedene Kontextidentitaeten;
- exakte Rollenreihenfolge und Aufrufanzahlen;
- Verwerfen jedes Kontexts;
- Bundlebildung nur nach vollstaendigem bitgleichem Doppelabgleich;
- keine Teilwertbeobachtung vor der atomaren Rueckgabe;
- weiterhin konstruktiv abbrechenden Standard-Einstieg.

Negative Tests muessen mindestens abweisen:

1. eine zusaetzliche oder verbotene Operationsrolle;
2. einen Integrator-, Hook-, `field.advance`-, Snapshot- oder Effektversuch;
3. Teilwertausgabe ueber Rueckgabe, Callback, Logger oder Ausnahme;
4. Wiederverwendung eines Kontextobjekts innerhalb oder zwischen
   Durchgaengen;
5. ungleiche Digest-Tupel der beiden Durchgaenge;
6. fehlenden Kontakt, falsche Reihenfolge oder mehr als sieben Kontakte;
7. Teilbundle oder vorzeitige Bundlebildung;
8. einen nicht verworfenen oder doppelt verworfenen Kontext;
9. ein aktives Freigabefeld;
10. fehlende, umgeleitete oder digestabweichende gebundene Quelldateien.

Synthetische Testdigests duerfen nur als inhaltsfreie Strukturmarker dienen.
Sie sind keine Fixierungs-Sollwerte und duerfen nicht in Produktionskonstanten
uebernommen werden.

## 9. Abbruch- und Reviewpflichten

Jede spaetere Implementierung muss vor Tests statisch auf verbotene Imports,
oeffentliche Exporte, dynamische Aufloesung und reale Runtime-Bindungen
geprueft werden. Ein Treffer beendet die Abnahme.

Danach sind ausschliesslich `py_compile`, die privaten Strukturtests und
`git diff --check` zulaessig. Eine erfolgreiche Testausfuehrung gibt weder
die reale Operationsbindung noch den Fixierungslauf frei. Vor jeder weiteren
Stufe ist eine unabhaengige technische Review der konkreten Aenderungen
erforderlich.

## 10. Freigabezustand

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

Dieses Dokument erteilt noch keine Implementierungsfreigabe. Es bindet nur
den pruefbaren Umfang eines spaeter gesondert freizugebenden
Implementierungsauftrags.

## 11. Aussagegrenze

Aus dieser Implementierungsvorabnahme folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI. Sie definiert ausschliesslich technische
Kontrolllogik fuer noch nicht erzeugte Vorintegratorwerte.

## 12. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument unabhaengig und ausschliesslich statisch gegen die
Dokumente 179 und 180, das private Strukturmodul, seine Tests und die
oeffentliche Exportflaeche. Pruefe insbesondere Dateiumfang, injizierbare
Rollen, Standardabbruch, Teilwertsperre, Testdouble-Grenze, Negativtests und
alle zwoelf Freigabefelder. Keine Implementierungsaenderung und keine
Runtime-Ausfuehrung.
