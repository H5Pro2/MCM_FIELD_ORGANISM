# S1-ZU: Statischer Regressionspartitions-, Abhaengigkeits- und Rohbyte-Portabilitaetsvertrag

## Auftrag und Grenze

S1-ZU ordnet den fehlgeschlagenen S1-ZT-Gesamtverbund, ohne einen Test,
Projektpfad oder Browser erneut auszufuehren. Der Vertrag implementiert noch
keine EOL-Regel, installiert keine Abhaengigkeit und aendert keinen Test.

## Verbindliche Testpartition

Die Zuordnung erfolgt in fester Prioritaet. Ein Testmodul darf nur der ersten
zutreffenden Klasse angehoeren.

### T0 - Aktiver schneller Kern

T0 enthaelt zunaechst genau sechs eng gebundene Module:

```text
test_active_engineering_surface_boundary.py
test_active_field_state_contract.py
test_current_architecture_api.py
test_mcm_neuron_layer.py
test_browser_payload_source.py
test_browser_payload_smoke.py
```

T0 ist ein schneller Architektur-, API- und technischer Smoke-Guard. Er ist
noch keine vollstaendige Funktionsabdeckung des Feldkerns. Weitere Module
duerfen erst nach Ownership-, Laufzeit- und Abhaengigkeitspruefung aufgenommen
werden.

### T1 - Optionale Abhaengigkeiten

Neun Testmodule importieren `pytest`. Ein weiterer Container-Preflight besitzt
einen positiven PyAV-Pfad. Diese zehn Module duerfen nur laufen, wenn das
jeweilige Abhaengigkeitsgate vorab bestanden ist. Fehlende Pakete sind `SKIP`
oder klarer Umgebungsstopp, kein Feldkernfehler.

### T2 - Terminal geschlossene Historie

Die Namensraeume E1, G2/D3, DTS-1 und ACM-1H umfassen zusammen 395
Testmodule. Sie bleiben historische Regressionen und sind nicht Teil des
aktiven Schnellgates:

```text
E1:      239
G2/D3:    11
DTS-1:   142
ACM-1H:    3
```

Ein Fehler in T2 reaktiviert keinen Forschungszweig.

### T3 - Private Engineeringreferenzen

PPB-1 und LPRH-1F umfassen 95 private Engineering- und Regressionmodule:

```text
PPB-1:   61
LPRH-1F: 34
```

Sie bleiben von API, Produktion und aktivem Feldkern getrennt.

### T4 - Unklassifiziert oder langsam

Alle verbleibenden Module sind fail-closed ausserhalb von T0. Sie werden erst
nach einem separaten statischen Ownershipaudit und einer zeitgebundenen
Laufzeitmessung entweder T0, einem optionalen Gate oder einer langsamen
Regression zugeordnet. S1-ZU erfindet aus dem punktweisen S1-ZT-Output keine
ungenauen Einzeltestlaufzeiten.

## Rohbyte-Portabilitaetsinventar

Git meldet im aktuellen Windows-Arbeitsbaum insgesamt 2.520 versionierte
Textpfade mit `i/lf` und `w/crlf`. Diese Gesamtmenge darf nicht global
normalisiert werden.

Der fachlich begruendete enge Korrekturbestand umfasst:

1. 60 versionierte JSON-Reports unter `reports/`, davon aktuell 55 mit
   CRLF-Arbeitsbaumdarstellung;
2. drei bytegenau gebundene Assets unter
   `tools/controlled_av_canonical_audio_world/`;
3. die bereits korrigierten drei W1-F-Assets, deren Regeln unveraendert
   erhalten bleiben.

59 Quellmodule enthalten Rohbyte-/Digestrollen. Deshalb wird die
Portabilitaetsgrenze am kanonischen Datenkorpus gebunden, nicht durch
nachtraegliches Normalisieren in jedem Leser.

## Gebundene spaetere Attributdatei

S1-ZV darf die bestehende `.gitattributes` nur auf genau sieben wirksame
Regeln erweitern:

```gitattributes
tools/controlled_browser_payload_world/index.html text eol=lf
tools/controlled_browser_payload_world/styles.css text eol=lf
tools/controlled_browser_payload_world/world.js text eol=lf
tools/controlled_av_canonical_audio_world/index.html text eol=lf
tools/controlled_av_canonical_audio_world/styles.css text eol=lf
tools/controlled_av_canonical_audio_world/world.js text eol=lf
reports/**/*.json text eol=lf
```

Die Regel fuer Reports umfasst auch top-level JSON-Reports und Unterordner.
Asset- und Reportinhalte sowie gebundene Digests bleiben unveraendert. Andere
Docs, Tests, Quelltexte, synthetische Runs und Werkzeuge sind ausgeschlossen.

## Naechster Schritt

S1-ZV darf nur diese vier neuen Regeln implementieren und die 60 Reports sowie
drei kanonischen Assets kontrolliert aus ihren unveraenderten Git-Blobs als LF
materialisieren. Danach sind nur statische Digest-/Attributpruefungen und eng
ausgewaehlte synthetische kanonische Browser- sowie representative
Reportaudit-Tests zulaessig. Ein weiterer Gesamtlauf bleibt gesperrt.

Maschinenlesbarer Vertrag:
[S1ZU_STATISCHER_REGRESSIONSPARTITIONS_ABHAENGIGKEITS_UND_ROHBYTE_PORTABILITAETSVERTRAG_V1.json](S1ZU_STATISCHER_REGRESSIONSPARTITIONS_ABHAENGIGKEITS_UND_ROHBYTE_PORTABILITAETSVERTRAG_V1.json).

