# 179 - Gesperrter Fixierungsvertrag Runtime-Sollwerte Minimaltest Vorzustandsbeitrag

## 1. Zweck und Grenze

Dieses Dokument beschreibt ausschliesslich einen spaeteren, separat zu
genehmigenden Fixierungsschritt fuer technische Runtime-Sollwerte des in den
Dokumenten 172 bis 178 festgelegten Minimaltests. Es erzeugt in seinem
aktuellen Stand keinen Sollwert und fuehrt keine Feldkonstruktion,
Rezeptorverteilung, Integration, Hook-Ausfuehrung oder Effektmessung aus.

Der Fixierungsschritt ist kein Runnerlauf und kein Forschungsarm. Er darf
weder Aktivierung noch Nachhall fortschreiben und keine Aussage ueber die
Hypothese erzeugen.

## 2. Bereits statisch fixierte Werte

Folgende Werte sind geschlossen und werden nicht erneut erzeugt:

- A-, B-, C-, Konfigurations- und Bundle-Digests aus Dokument 175;
- Runner- und Hook-Dateidigest aus Dokument 178;
- `geometry_digest`
  `a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb`;
- `construction_digest`
  `1d1817784190c26d883c744b305634ee72cdabde84767bcc38aaee7c9f6a2b8e`;
- JSON-Regeln, Snapshot-Schema, Laufreihenfolge, Messpunkte und
  Abbruchbedingungen aus den Dokumenten 175, 177 und 178.

Eine Abweichung an einem dieser Werte beendet einen spaeteren
Fixierungsschritt vor jeder Runtime-Konstruktion.

## 3. Exakt noch fehlende Sollwerte

Es fehlen ausschliesslich die folgenden technischen, vor einem Integrator
liegenden Runtime-Ableitungen:

1. sieben `ReceptorDistribution.digest()`-Sollwerte;
2. sieben `generator_digest`-Sollwerte;
3. sieben `boundary_digest`-Sollwerte.

Die sieben Eintraege sind in dieser unveraenderlichen Reihenfolge gebunden:

```text
history.a.e1
history.a.e2
history.a.e3
history.b.e1
history.b.e2
history.b.e3
contact.c.e1
```

Jeder Eintrag bindet genau ein Tupel
`(contact_id, receptor_distribution_digest, generator_digest,
boundary_digest)`. Es gibt keine arm-, operator- oder replikatspezifischen
Varianten. Derselbe Kontakt muss vor demselben technischen Feldtraeger
dieselben drei Digests besitzen.

Nicht fehlend und nicht vorab zu fixieren sind M0- bis M3-Zustandsdigests,
Aktivierungsvektoren, Nachhallvektoren, Layerdigests, Effektgroessen,
Armvergleiche oder Hypothesenentscheidungen. Diese Werte waeren Ergebnisse
des spaeteren Forschungslaufs und duerfen nicht als erwartete Topologie oder
richtige Antwort vorgegeben werden.

## 4. Vorab gebundener Quellstand

Vor einem spaeteren Fixierungsschritt muessen die rohen Dateibytes exakt diese
SHA-256-Digests besitzen:

```text
mcm_field_organism/receptor_contract.py
af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71

mcm_field_organism/receptor_distributor.py
649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad

mcm_field_organism/shared_mcm_field.py
2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec

mcm_field_organism/field_step_time.py
2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd

mcm_field_organism/neutral_local_field_substrate.py
df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13

mcm_field_organism/mcm_neuron_layer.py
ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277

mcm_field_organism/_previous_state_minimal_runner.py
f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72

mcm_field_organism/previous_state_contribution_hook.py
2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e
```

Die Sollwerte werden nicht waehrend der Fixierung aktualisiert. Abweichende,
fehlende, umgeleitete oder nicht regulaere Dateien fuehren zum Abbruch.

## 5. Spaeteres Fixierungsverfahren

Das folgende Verfahren ist nur beschrieben, nicht freigegeben:

1. Alle statischen Digests, Quellstanddigests und
   `dissipation_config is None` pruefen.
2. Fuer jeden der sieben Kontakte einen frischen Feldkontext exakt nach
   Dokument 177 konstruieren. Kein Kontext wird wiederverwendet.
3. Den Kontakt exakt mit `_frame`, `_distribution` und `_step_time` aus
   Dokument 178 abbilden.
4. `ReceptorDistribution.digest()` unveraendert uebernehmen.
5. `_generator_and_boundary(field, distribution, substrate_config)` genau
   einmal aufrufen und Generator sowie Boundary nach Dokument 178 hashen.
6. Keinen Integrator, keinen Hook und keine Methode `field.advance(...)`
   aufrufen. Den frischen Kontext unmittelbar verwerfen.
7. Die Schritte 2 bis 6 in einem zweiten vollstaendig frischen Durchgang
   wiederholen. Nur bitgleiche Digest-Tupel beider Durchgaenge sind
   fixierbar.
8. Erst nach vollstaendig erfolgreicher Doppelableitung aller sieben
   Kontakte das unveraenderliche Bundle aus Abschnitt 6 bilden.

C darf bei der Feldkonstruktion nur als wertfreie Geometriereferenz dienen.
Seine Werte werden erst in seinem eigenen Ableitungseintrag verteilt. Eine
Verteilung darf niemals in das Feld fortgeschrieben werden.

## 6. Exaktes Ausgabeformat des spaeteren Fixierungsschritts

Das einzige zulaessige Ergebnis ist ein privates JSON-Objekt unter den
kanonischen Regeln aus Dokument 178:

```json
{"entries":[{"boundary_digest":"<sha256>","contact_id":"history.a.e1","generator_digest":"<sha256>","receptor_distribution_digest":"<sha256>"}],"schema_version":1,"source_digests":[["mcm_field_organism/receptor_contract.py","<sha256>"]],"static_contract":{"construction_digest":"1d1817784190c26d883c744b305634ee72cdabde84767bcc38aaee7c9f6a2b8e","geometry_digest":"a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb"}}
```

`entries` muss alle sieben Eintraege in der Reihenfolge aus Abschnitt 3
enthalten. `source_digests` muss alle acht Pfad-Digest-Paare in der Reihenfolge
aus Abschnitt 4 enthalten. Platzhalter werden erst im separat freigegebenen
Fixierungsschritt ersetzt. Der Bundle-Digest ist SHA-256 ueber die
kanonischen UTF-8-Bytes dieses vollstaendigen Objekts.

Keine Konsole, kein Logger, Callback oder Fortschrittsobjekt darf einzelne
Digests oder Zwischenpayloads vor dem vollstaendigen Doppelabgleich
veroeffentlichen. Bei einem Fehler wird nur ein technischer Abbruch erzeugt;
es entsteht kein Teilbundle.

## 7. Abbruchgrenzen

Der spaetere Fixierungsschritt bricht sofort ab bei:

- abweichendem statischem Vertrags- oder Quellstanddigest;
- aktivem oder nicht exakt `None` gesetztem Dissipationspfad;
- abweichender Kontakt-ID, Eingabebytefolge, Zeit, Modalitaet oder Geometrie;
- nicht frischem oder wiederverwendetem Feldkontext;
- abweichendem Geometrie- oder Konstruktionsdigest;
- mehr oder weniger als genau einer Verteilung pro Kontakt und Durchgang;
- unzulaessiger Generator- oder Boundary-Form;
- nicht-endlichen Generator- oder Boundary-Werten;
- einem Integrator-, Hook-, `field.advance`-, Snapshot- oder Effektaufruf;
- nicht bitgleichen Digest-Tupeln zwischen den zwei frischen Durchgaengen;
- Einsicht in Teilwerte vor vollstaendigem Abschluss;
- einer Ausnahme oder einem nicht vollstaendig gebildeten Siebenerbundle.

Nach dem ersten Abbruch wird kein weiterer Kontakt bearbeitet. Diagnosen sind
auf Bedingungs-ID, Kontakt-ID, Durchgang, technische Rolle, erwarteten Digest
und tatsaechlichen Digest begrenzt.

## 8. Review- und Freigabefolge

Vor jeder Umsetzung dieses Fixierungsschritts sind erforderlich:

1. unabhaengige statische Review dieses Dokuments;
2. gesonderte Freigabe einer privaten, standardmaessig gesperrten
   Fixierungsimplementierung mit reinen Strukturtests;
3. unabhaengige technische Review dieser Implementierung;
4. gesonderte Ausfuehrungsvorabnahme fuer genau den beschriebenen
   Doppelableitungslauf;
5. nach der Ausfuehrung unabhaengige Pruefung des vollstaendigen Bundles,
   bevor irgendein Executor-Implementierungsauftrag formuliert wird.

Keine dieser Stufen gibt den Forschungsrunner oder eine Effektmessung frei.

## 9. Freigabezustand und Aussagegrenze

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

Aus diesem Fixierungsvertrag folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI.

## 10. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument statisch gegen die Dokumente 175, 177 und 178 sowie
die genannten Quelldateien. Pruefe insbesondere, ob die fehlende Sollwertmenge
vollstaendig und minimal ist, keine Ergebniswerte vorfixiert werden, der
Doppelableitungslauf keinen Feldfortschritt erlaubt und alle Sperren aktiv
bleiben. Keine Fixierungsimplementierung und keine Runtime-Ausfuehrung.
