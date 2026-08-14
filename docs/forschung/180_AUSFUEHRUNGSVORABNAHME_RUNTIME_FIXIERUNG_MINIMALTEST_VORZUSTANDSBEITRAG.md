# 180 - Ausfuehrungsvorabnahme Runtime-Fixierung Minimaltest Vorzustandsbeitrag

## 1. Zweck und Freigabegrenze

Dieses Dokument bindet ausschliesslich die Bedingungen eines spaeteren
Doppelableitungslaufs fuer die in Dokument 179 benannten technischen
Vorintegrator-Sollwerte. Es fuehrt den Lauf nicht aus, gibt keine
Implementierungsaenderung frei und erzeugt keinen Digest-Sollwert.

Die hier beschriebene Fixierung ist weder ein Forschungsrunner noch ein
Forschungsarm. Sie darf keinen Feldzustand fortschreiben, keinen Effekt
messen und keine Hypothesenentscheidung erzeugen.

## 2. Gebundene Vorbedingungen

Vor einer spaeteren Implementierungs- oder Ausfuehrungsfreigabe muessen die
rohen Dateibytes mit den folgenden Sperrdigests uebereinstimmen:

```text
docs/forschung/179_GESPERRTER_FIXIERUNGSVERTRAG_RUNTIME_SOLLWERTE_MINIMALTEST_VORZUSTANDSBEITRAG.md
9198dd3f44a64307d38abeab4eb329583c174a683f03cf3be420e48874f58297

mcm_field_organism/_runtime_fixation_structure.py
27c661d3e9f2738a18434fb8a03388c1621b3db083a020480454f0003c43de0e

tests/test_runtime_fixation_structure.py
db13044921cb96f3c28cf0fda8bc7ac93dac92a5766c6fd8e5de61a324a765f2
```

Zusaetzlich bleiben die acht Quellstanddigests aus Abschnitt 4 von Dokument
179 bytegenau bindend. Sie duerfen weder waehrend der Fixierung aktualisiert
noch aus einem anderen Pfad gelesen werden.

Die statischen Vertragswerte sind:

```text
geometry_digest:
a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb

construction_digest:
1d1817784190c26d883c744b305634ee72cdabde84767bcc38aaee7c9f6a2b8e
```

Alle zwoelf Freigabefelder aus Abschnitt 9 muessen vor jedem spaeteren
Implementierungs- und Ausfuehrungsschritt vorhanden und `false` sein.
`dissipation_config` muss exakt `None` sein. Eine Abweichung beendet den
jeweiligen Schritt vor jeder Feldkonstruktion.

## 3. Fixierungsmenge und Reihenfolge

Der spaetere Lauf darf ausschliesslich je einen
`receptor_distribution_digest`, `generator_digest` und `boundary_digest`
fuer diese sieben Kontakte ableiten:

```text
history.a.e1
history.a.e2
history.a.e3
history.b.e1
history.b.e2
history.b.e3
contact.c.e1
```

Die Reihenfolge ist in beiden Durchgaengen identisch. Es gibt genau zwei
Durchgaenge und damit genau 14 Feldkontexte. Jeder Kontext wird neu erzeugt,
nur fuer einen Kontakt verwendet und unmittelbar nach dessen Ableitung
verworfen. Kein Objekt oder abgeleiteter Feldtraeger darf zwischen Kontakten
oder Durchgaengen wiederverwendet werden.

## 4. Abschliessend erlaubte Runtime-Aufrufe

Eine spaetere, gesondert freigegebene Fixierungsimplementierung darf nur die
folgenden Runtime-Rollen in der angegebenen Reihenfolge verwenden:

1. rohe Bytes der gebundenen Dateien lesen und SHA-256 bilden;
2. die gesperrte Fixierungsstruktur laden und alle Vorbedingungen pruefen;
3. fuer den aktuellen Kontakt `_build_fresh_run_context(...)` entsprechend
   Dokument 178 aufrufen;
4. den Kontakt mit `_frame(contact)` abbilden;
5. `_distribution(context, frame)` genau einmal aufrufen;
6. `ReceptorDistribution.digest()` genau einmal fuer diese Verteilung
   aufrufen;
7. `_step_time(frame)` zur Vertragspruefung des Kontaktzeitpunkts aufrufen;
8. `_generator_and_boundary(field, distribution, substrate_config)` genau
   einmal aufrufen;
9. Generator und Boundary nach den kanonischen Regeln aus Dokument 178
   hashen;
10. die drei Digests nur in einem lauflokalen, nicht beobachtbaren
    Vergleichspuffer halten;
11. den frischen Kontext verwerfen.

Andere Runtime-Aufrufe sind nicht zulaessig. Insbesondere ist C bei der
Kontextkonstruktion nur wertfreie Geometriereferenz; seine Kontaktwerte
duerfen erst bei `contact.c.e1` verteilt werden.

## 5. Ausdruecklich verbotene Rollen

In beiden Durchgaengen und in jeder Fehlerbehandlung sind verboten:

- jeder Integratoraufruf;
- jede Hook-Ausfuehrung;
- `field.advance(...)` oder ein funktional gleichwertiger Feldfortschritt;
- `SharedMCMField.snapshot()` und jeder andere Snapshot-Aufruf;
- Aktivierungs-, Nachhall-, Layer-, Zustands- oder Effektauswertung;
- M0- bis M3-Digestbildung;
- Runner-, Arm-, Replikat- oder Hypothesenlogik;
- Logger, Konsole, Callback, Progress-Objekt oder Ausnahmeinhalt mit einem
  einzelnen abgeleiteten Digest oder Zwischenpayload;
- Persistenz oder Rueckgabe eines Teilbundles.

Ein Versuch, eine verbotene Rolle aufzurufen, ist ein harter Abbruch und
keine ueberspringbare Warnung.

## 6. Doppelabgleich und atomare Bundlebildung

Durchgang 1 und Durchgang 2 muessen fuer jeden Kontakt ein bitgleiches Tupel

```text
(contact_id, receptor_distribution_digest, generator_digest, boundary_digest)
```

erzeugen. Erst nachdem alle sieben Tupel beider Durchgaenge vollstaendig
vorliegen und paarweise bitgleich sind, darf das Bundle exakt nach Abschnitt
6 von Dokument 179 im Arbeitsspeicher gebildet werden.

Vor diesem Gesamtvergleich darf kein Teilwert die Fixierungsfunktion
verlassen. Die Ausgabe wird atomar behandelt: entweder entsteht genau ein
vollstaendiges Siebenerbundle mit kanonischem Bundle-Digest oder es entsteht
gar kein Ergebnis. Ein spaeterer Schreibvorgang duerfte erst nach einer
eigenen Freigabe erfolgen und muesste ueber temporaere Datei, erneute
Bytepruefung und atomare Umbenennung erfolgen. Dieses Dokument gibt keinen
Schreibvorgang frei.

## 7. Abbruch und Verwerfung

Die zwoelf Abbruchgrenzen aus Dokument 179 gelten unveraendert. Nach dem
ersten Fehler gilt zwingend:

1. keine weitere Kontaktbearbeitung;
2. alle Feldkontexte verwerfen;
3. alle lauflokalen Digests und Zwischenpayloads verwerfen;
4. kein Bundle und kein Bundle-Digest bilden;
5. keine Datei erzeugen oder veraendern;
6. nur eine begrenzte technische Diagnose ausgeben.

Eine Diagnose darf ausschliesslich Bedingungs-ID, Kontakt-ID, Durchgang,
technische Rolle sowie erwarteten und tatsaechlichen Bindungsdigest nennen.
Abgeleitete Rezeptor-, Generator- oder Boundary-Digests duerfen bei einem
unvollstaendigen Lauf weder einzeln noch gesammelt offengelegt werden.

## 8. Getrennte Freigabestufen

Dieses Dokument trennt weiterhin folgende Entscheidungen:

1. unabhaengige statische Review dieses Dokuments;
2. gesonderte Vorabnahme einer minimalen privaten Implementierungsaenderung;
3. Implementierung und reine Negativ-/Strukturtests ohne Fixierungslauf;
4. unabhaengige technische Review dieser Implementierung;
5. gesonderte Freigabe genau eines Doppelableitungslaufs;
6. unabhaengige Pruefung des vollstaendigen Bundles.

Keine Stufe darf stillschweigend die naechste freigeben. Insbesondere sind
Implementierungsfreigabe und Ausfuehrungsfreigabe zwei getrennte
Entscheidungen. Erst nach Stufe 6 duerfte ein Auftrag zur Bindung der 21
Sollwerte oder zur Executor-Implementierung geprueft werden.

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

Der konstruktive Abbruch von `execute_runtime_fixation(...)` bleibt
unveraendert. Dieses Dokument schaltet kein Freigabefeld um.

## 10. Aussagegrenze

Aus dieser Vorabnahme folgt kein Befund zu Feldwirkung, Kontaktgeschichte,
Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit
oder KI. Die spaeter ableitbaren 21 Digests sind ausschliesslich technische
Vorintegratorwerte und keine erwartete Feldtopologie oder richtige Antwort.

## 11. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument unabhaengig und ausschliesslich statisch gegen die
Dokumente 178 und 179, die private Fixierungsstruktur und ihre Strukturtests.
Pruefe insbesondere die Vollstaendigkeit der erlaubten Aufrufe, die
Sperrdigests, die Frische aller 14 Kontexte, die Verbote, die atomare
Bundlebildung, die Abbruchverwerfung und alle zwoelf Freigabefelder. Keine
Implementierungsaenderung und keine Runtime-Ausfuehrung.
