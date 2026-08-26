# S1-PW: Statischer Abdeckungsaudit der Root-Importverbraucher

## Status und Umfang

S1-PW prueft alle Python-Dateien unter `mcm_field_organism/`, `tests/` und
`tools/` ausschliesslich mit dem Python-AST auf Verbraucher der breiten
Paket-Root. Es importiert kein Projektmodul und fuehrt keine Tests, Browser,
Sensoren oder Feldlaeufe aus. Runtime und Lazy-Root-Implementierung bleiben
unveraendert.

Entscheidung:

```text
ROOT_CONSUMERS_STATICALLY_COVERED_NO_NEW_LAZY_BEHAVIOR_NO_ADDITIONAL_REGRESSION_RUN_CONSOLIDATION_COMPLETE
```

## Reproduzierbarer Audit

Der statische Builder liegt in:

```text
tools/build_s1pw_root_consumer_audit.py
```

Sein kanonisches Ergebnis liegt in:

```text
docs/S1PW_ROOT_CONSUMER_AUDIT_V1.json
contract_id: mcm.s1pw.root_consumer_audit.v1
```

Das Artefakt bindet fuer jede Verbraucherdatei Importformen, Namen,
Submodule, Aliasattribute, Introspektionsformen und die zugeordnete
Lazy-Verhaltensklasse.

## Gesamtinventar

| Groesse | Statischer Befund |
|---|---:|
| gescannte Python-Dateien | 1.722 |
| Root-Verbraucherdateien | 305 |
| davon Tests | 280 |
| davon Werkzeuge | 25 |
| davon interne Paketmodule | 0 |
| bereits im S1-PV-Verbund enthaltene Verbraucherdateien | 8 |
| weitere Verbraucherdateien | 297 |
| `from mcm_field_organism import ...`-Anweisungen | 340 |
| Root-Aliasimporte | 120 |
| benannte Root-Exportvorkommen | 1.236 |
| verschiedene benannte Root-Exporte | 544 |
| Root-Submodulvorkommen | 187 |
| verschiedene Root-Submodule | 29 |
| Sternimporte im gescannten Quelltext | 0 |
| dynamische Root-Imports | 0 |
| unaufgeloeste Importnamen | 0 |

Die zwei weiteren Dateien des 41-Methoden-Verbunds sind keine direkten
Root-Verbraucher im aeusseren AST: Der End-to-End-Consumer importiert nur aus
`current_api`, und der Unterprozesstest enthaelt seine Root-Importarme in
expliziten frischen Interpreter-Skripten.

## Verhaltensklassen

| Klasse | Dateien | S1-PV-Abdeckung |
|---|---:|---|
| benannter Root-Exportimport | 152 | alle 1.267 Namen gegen Ursprungsidentitaet geprueft |
| Root-Submodulimport | 153 | `current_api` und mehrere Grenzsubmodule im vorhandenen Verbund geprueft |
| Root-Aliasimport | 120 | reiner Paketimport und Aliaszugriff geprueft |
| Root-Aliasattribut | 7 | Identitaet, Caching, `__all__`, `__dict__` und `dir()` geprueft |
| allgemeine Root-Introspektion | 118 | vollstaendige Identitaet, unbekannter Name und `dir()` decken beide Faelle ab |
| konstante Abwesenheitspruefung | 21 | fail-closed `AttributeError` geprueft |

Die Dateizaehler ueberlappen, weil eine Datei mehrere Importformen verwenden
kann.

## Benannte Root-Exporte

Die 297 nicht einzeln im S1-PV-Verbund ausgefuehrten Verbraucher erzeugen
keine neue Namenssemantik. Jeder benannte Import ruft dieselbe
`__getattr__`-Aufloesung auf, die S1-PV fuer alle 1.267 gebundenen Namen gegen
das jeweilige Ursprungsobjekt geprueft hat.

Die gescannten Verbraucher verwenden 544 verschiedene Root-Exporte. Diese
Menge ist eine echte Teilmenge des vollstaendig abgenommenen
1.267-Namen-Inventars.

## Submodulimporte

187 Vorkommen importieren 29 vorhandene Fachsubmodule ueber die Pythonform:

```text
from mcm_field_organism import <submodule>
```

Diese Namen sind keine Root-Exporte. Die Lazy-Root-Fassade gibt fuer sie
zuerst `AttributeError` zurueck; der normale Python-Importmechanismus laedt
danach das vorhandene Submodul. S1-PV pruefte diese Form mit `current_api`
und mehreren vorhandenen Architekturgrenztests.

Es gibt keinen internen Paketverbraucher der Root-API. Daher kann kein
Fachmodul waehrend seiner eigenen Initialisierung ueber die Lazy Root auf
einen anderen Root-Namen zurueckgreifen. Eine neue zirkulaere oder
importreihenfolgeabhaengige Paketkopplung ist statisch nicht vorhanden.

## Introspektion und Abwesenheit

Die 28 statisch benannten `hasattr`-Ziele sind ausnahmslos bewusst fehlende
Root-Namen. Kein statisch benannter `hasattr`-Zielname ist ein vorhandener
Root-Export.

Dynamisch ueber Schleifen gebildete `hasattr`- oder `getattr`-Pruefungen
bilden keine dritte Semantik:

```text
Name registriert
-> identisches Ursprungsobjekt

Name nicht registriert
-> AttributeError ohne Modulsuche
```

Beide Pfade sowie `__all__`, Caching, `__dict__` und importfreies `dir()`
sind im einmaligen S1-PV-Verbund abgenommen.

Im gescannten Quelltext gibt es keinen Sternimport und keinen dynamischen
Root-Import. Der ausdrueckliche Sternimport wurde dennoch separat im frischen
S1-PV-Unterprozess mit allen 1.267 Namen geprueft.

## Digests

```text
scanned_source_set_sha256:
85c661793c68cb3612059e7f601a9511acd85f3055427bac7bd0f2cec90c02e2

consumer_records_sha256:
399b2518cf8dc52e9df4d2cce00cd1460668ba24d8c580dd5a8786f49b3aeb04
```

Der erste Digest bindet Pfad und SHA-256 aller 1.722 gescannten Pythonquellen.
Der zweite bindet die kanonischen 305 Verbraucherrecords.

## Abdeckungsentscheidung

Es verbleibt keine neue Lazy-Verhaltensklasse, die durch einen weiteren
Regressionstest Erkenntnis gewinnen wuerde:

- benannte Exporte sind vollstaendig durch das 1.267-Identitaetsgate
  abgedeckt;
- vorhandene und fehlende Aliasnamen sind durch Identitaets- und
  `AttributeError`-Gate abgedeckt;
- Submodulimport ist durch `current_api` und vorhandene Grenztests abgedeckt;
- Sternimport ist im frischen Unterprozess abgedeckt;
- dynamischer Root-Import kommt im gescannten Bestand nicht vor;
- interne Paketmodule konsumieren die Root-API nicht.

Deshalb wird kein weiterer Testlauf freigegeben. Die 41-Methoden-Abnahme wird
nicht wiederholt und nicht durch einen unbegrenzten historischen Vollverbund
ersetzt.

## Projektabschluss dieser Linie

Die Aktivkern- und Archivgrenzenkonsolidierung S1-PQ bis S1-PW ist technisch
abgeschlossen:

- der primaere Feldkern ist als aktive technische Architektur abgegrenzt;
- Referenzen, geschlossene Kandidaten, historische Runner und inaktive
  Sensorik sind klassifiziert;
- die breite Root-Kompatibilitaet bleibt erhalten;
- Paket- und Aktivkernimport sind von nicht angeforderten Root-Modulen
  getrennt;
- alle im Bestand vorkommenden Lazy-Verhaltensklassen sind abgedeckt.

Die Substrat- und technische Memory-Funktionsforschung bleibt pausiert, weil
weiterhin keine unabhaengige, vorab falsifizierbare Gegenprognose vorliegt.

## Naechster Zustand

Es gibt keinen automatisch freigegebenen Folgeschritt. Das Projekt bleibt am
stabilen MCM-Wahrnehmungsfeldkern und dem erhaltenen Forschungsarchiv stehen.

Ein neuer Abschnitt benoetigt entweder:

1. eine konkrete technische Engineeringanforderung mit klarer Abnahme; oder
2. eine fachlich neue Forschungsrichtung mit eigener, vorab definierter und
   nicht baseline-reduzierbarer Gegenprognose.

`ok weiter` allein reicht an dieser Richtungsgrenze nicht aus. Bis zu einer
ausfuehrlichen neuen Entscheidung werden keine weiteren Dateien, Tests,
Mechaniken oder Forschungszweige begonnen.
