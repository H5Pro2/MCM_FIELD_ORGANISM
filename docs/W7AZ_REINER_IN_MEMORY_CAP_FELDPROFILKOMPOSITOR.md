# W7-AZ: Reiner In-Memory-CAP-Feldprofilkompositor

## Entscheidung

`CAP_PATH_CONTRASTS_AND_FIELD_PROFILES_COMPOSED`

W7-AZ implementiert den W7-AY-Vertrag als passiven Verbraucher bereits
vorhandener W7-AG- und W7-AK-Objekte. Er startet keine neue Integration,
keinen Runner und keinen Browser und schreibt keinen Forschungsreport.

## Rohe Pfadkontraste

Fuer acht vorregistrierte Pfadpaare und fuenf Checkpoints werden die
sampleweisen S- und H-Linf-Abstaende getrennt erhalten. Die gemeinsame
Effektkurve ist an jedem Checkpoint ihr Maximum. Ticks, Sampleanzahl und
Geometrie muessen exakt uebereinstimmen; es gibt keine Interpolation.

W7-AK wird auf identische W7-AG-CAP-Messobjekte und passende Quellenbindung
geprueft. Seine CAP/P0-Werte werden nicht als Pfadeffekte verwendet.

## Profile und Grenze

Aus den acht Rohkurven entstehen mit dem W7-P-Kompositor genau ein AB- und
ein BA-Profil fuer CAP. Der W7-AT-Effektboden begrenzt den eigenen
Anfangsnenner. W7-AZ vergleicht diese Profile noch nicht mit Observerprofilen
und trifft keine Feldfunktions- oder Memoryentscheidung.

## Technische Abnahme

Die acht Kontrastkurven enthalten 40 Effektwerte zwischen `0.0` und
`0.00020628305122732948`; vier Werte sind exakt null. AB und BA besitzen
jeweils einen gegen den W7-AT-Boden aufgeloesten Anfangsnenner. Der
Kompositionsdigest lautet `ecb14d76...4d9f`; `7 tests, OK` bestehen. Dies ist
keine Observerpassung und kein Funktionsbefund.

## Naechster Schritt

Nach technischer Abnahme muss W7-BA statisch den einzigen zulaessigen
dimensionslosen CAP-gegen-Observer-Profilvergleich binden. Erst danach darf
ein separater Auswerter die feste LEAK-/SAT-/NORM-Praezedenz anwenden.
