# S1-PV: Implementierung und 41-Methoden-Abnahme der Lazy Root

## Status und Umfang

S1-PV setzt ausschliesslich den in S1-PU gebundenen Umfang um. Die breite
Root-Oberflaeche bleibt mit 1.267 Namen kompatibel, wird aber nicht mehr beim
Paketimport vollstaendig eager geladen. `current_api.py`, alle Feld- und
Referenzmodule, alle geschlossenen Kandidaten, historischen Runner sowie
inaktiven Sensor- und Effektorpfade blieben unveraendert.

Entscheidung:

```text
LAZY_ROOT_IMPLEMENTED_ALL_1267_IDENTITIES_PRESERVED_FORTY_ONE_METHOD_ACCEPTANCE_OK
```

## Statischer Preflight

Vor der Aenderung wurden die gebundenen Ausgangswerte bestaetigt:

```text
root_source_sha256:
f69cc32fbe7a26a4db6355e87a8b09a6456a2d2839c5036415e0d54d395f39ab

root_all_sha256:
4fdf82f4fe480e3180a6447987684093e2336837a329b95ce33b3069beb62639

sorted_records_sha256:
d783c5a0d29782c2b8f10d93ba2d048cef4c83468900e1e553050f0d84196cc1

current_api_source_sha256:
01daabe43dd52766014926f3ee30d55cd390d9d3ed6651a7bd3664997caa0360

current_api transitive Module: 57
current_api lokale Importkanten: 253
```

Alle Werte stimmten. Das S1-PT-Inventar wurde nicht neu interpretiert oder
veraendert.

## Umsetzung

Neu erzeugt wurde:

```text
mcm_field_organism/root_lazy_exports.py
```

Das Modul bindet statisch und ohne Projektimporte:

- `ROOT_ALL` mit allen 1.267 Namen in gebundener Reihenfolge;
- `ROOT_LAZY_EXPORTS` als unveraenderliche Name-zu-Modul-Attribut-Abbildung;
- `ROOT_SURFACE_CLASSES` als unveraenderliche S1-PR-Klassifikation;
- `CURRENT_API_ALLOWED_MODULES` mit 57 statisch erlaubten lokalen Modulen;
- die gebundenen Manifest-, Quell-, Modul- und Kantendigests.

Der fail-closed Generator liegt in:

```text
tools/build_s1pv_lazy_root_exports.py
```

Er importiert kein Projektmodul. Er erzeugt die Laufzeittabelle nur bei
exakten S1-PT-, `current_api`- und Importgraphwerten.

## Neue Root-Initialisierung

`mcm_field_organism/__init__.py` wurde von der breiten eager Importliste auf
eine 30-zeilige Lazy-Fassade reduziert:

```text
Root-Name angefordert
-> statischen Ursprung nachschlagen
-> genau dieses relative Modul laden
-> Attribut lesen
-> identisches Objekt im Root-Namespace cachen
```

Ein unbekannter Name erzeugt ohne Modulsuche `AttributeError`. `__dir__`
zeigt die statischen Root-Namen, ohne Ursprungsmodule zu laden. Sternimport
bleibt als ausdruecklich breiter Kompatibilitaetsarm erhalten und loest seine
1.267 Namen erwartungsgemaess auf.

## Implementierungsdigests

```text
mcm_field_organism/__init__.py:
bb9d968aafe91b4c909abcf30e59b0cc0695fb0d815f32e2014972270327c9da

mcm_field_organism/root_lazy_exports.py:
ff6689dfebbe8ba415753c7d509175322229a0c48d8d2670c2f6ec3257bfa016

tools/build_s1pv_lazy_root_exports.py:
5f2db4631e3881810cf4ad329f08aea8e3296cadedf8f09ff47f06380f5e191b

tests/test_s1pv_lazy_root_manifest.py:
8589f509d3bc6858e24b91ba9f87f678b64004426fa4ffac2e93bac777c0c126

tests/test_s1pv_lazy_root_subprocess.py:
38ca5abdeb0d57c8385129949d9acc0174c4be231fc8452eeb67d62a4838a415
```

## Einmalige Abnahme

Vor dem Lauf wurden alle fuenf geaenderten Python-Dateien statisch mit AST
gelesen. Die zwei neuen Testdateien enthielten exakt acht und fuenf Methoden.
Ausgangsdigests und Dateigrenze waren korrekt.

Der einzige freigegebene Verbund wurde genau einmal gestartet:

```text
.........................................
----------------------------------------------------------------------
Ran 41 tests in 3.499s

OK
```

Es gab keinen zweiten Testlauf.

## Abgenommene Eigenschaften

Der Verbund bestaetigt im gebundenen Umfang:

- vollstaendige Uebereinstimmung der generierten Tabelle mit allen 1.267
  S1-PT-Records;
- unveraenderte `__all__`-Reihenfolge und unveraenderten Digest;
- Objektidentitaet jedes Root-Namens mit seinem Ursprungsattribut;
- fehlerfreien unbekannten Namen, `dir()` und Root-Caching;
- keine unerlaubte Erweiterung um die 43 nur in `current_api` vorhandenen
  Namen;
- minimalen reinen Paketimport im frischen Unterprozess;
- `current_api`-Import innerhalb der statisch erlaubten Modulmenge;
- verzoegertes Laden eines aktiven und eines geschlossenen Beispielnamens;
- vollstaendigen Sternimport als getrennten Kompatibilitaetsarm;
- die 28 vorhandenen Manifest-, Architektur-, Grenz- und
  End-to-End-Methoden.

## Aussage- und Projektgrenze

S1-PV ist technische Paketkonsolidierung. Es veraendert keine Feldgleichung,
keinen Feldzustand und keine Kandidatenfunktion. Die Forschungspause und alle
Zweigstopps bleiben bestehen.

Die 41-Methoden-Abnahme deckt die vorregistrierten Kern- und
Identitaetsgrenzen ab. Sie ist noch kein Audit aller weiteren historischen
Root-Importverbraucher im Repository.

## Genau ein naechster Schritt

```text
S1-PW - statischer Abdeckungsaudit aller verbleibenden Root-Importverbraucher
```

S1-PW soll die vorhandenen Root-Importfundstellen in Tests und Werkzeugen
statisch erfassen, gegen die 41 abgenommenen Methoden abgleichen und nur bei
einer konkreten ungedeckten Kompatibilitaetsklasse ein weiteres endliches
Regressionstor vorschlagen. Keine Testausfuehrung, keine weitere
Importaenderung und keine Forschungsarbeit in S1-PW.
