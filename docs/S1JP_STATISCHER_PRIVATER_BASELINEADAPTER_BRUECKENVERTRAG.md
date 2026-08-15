# S1-JP: Statischer privater Baselineadapter-Brueckenvertrag

## Ergebnis

S1-JP bindet die technische Bruecke zwischen der vierwertigen S1-JO-
Modellaufrufhuelle und den bestehenden Kernen der sechs Baselines B1 bis B6.
Der Vertrag implementiert keinen Adapter und ruft keinen Modellkern auf.

## Getrennte Eingaberollen

Der gemeinsame Intervallaufruf bleibt exakt auf folgende vier Werte begrenzt:

1. materialisiertes vollstaendiges Feld,
2. Rezeptordistribution,
3. Schrittzeit,
4. Geometriedigest.

Daneben besitzt jede Baseline einen vor der Sequenz gebundenen privaten
Kontext aus ihrer Rolle, ihrem vollstaendigen S1-JN-Zustand, genau einem
S1-JA-Konfigurationsrecord und einer Refinementstufe 2, 4 oder 8. Dieser
Kontext ist kein gemeinsamer Expositionswert und fuer alle anderen Modelle
unzugreifbar.

Integritaetsdigests, Envelope, Sequenz, Ordinal, Checkpoint,
Kandidatensidecar, Referenzwerte und spaetere Ergebnisse gelangen weder in
den privaten Kontext noch in einen Baselinekern. Globaler oder verdeckter
veraenderlicher Zustand ist verboten.

## Sechs Bruecken

- B1 bindet den vorregistrierten festen Kantenadapter einmal und gibt ihn
  bitgleich als privaten Zustand zurueck.
- B2 bildet S/H und privates L auf `S2ReferenceState` ab, verwendet nur
  `model-b2` und gibt das vollstaendige resultierende L explizit zurueck.
- B3 bindet ausschliesslich den bestehenden Local-Leaky-Rechner an die
  bestehende F3-Runtime.
- B4 bindet ausschliesslich den bestehenden linear gekoppelten Rechner an die
  bestehende F3-Runtime.
- B5 erhaelt den unveraenderten Standard-F3-Rechner.
- B6 bindet den bestehenden CONST-V-Rechner mit genau einer eingefrorenen
  Spezifikation fuer beide Geometrien.

B3 bis B6 tragen M im vollstaendigen Feld und geben dessen resultierenden
Digest in ihrem privaten Zustand zurueck. Konfigurations- und bei B6
Spezifikationsdigest bleiben unveraendert.

## Zeit und Ausgabe

Physische Dauer stammt nur aus der S1-JO-Schrittzeit. Refinement teilt dasselbe
Fenster deterministisch in gleiche zusammenhaengende Unterfenster. Die bereits
materialisierte S/H-Grenze wird intern nicht erneut angewendet; Kontaktwerte
werden weder entfernt noch wiederholt. Das Abschlussfeld muss auf der
urspruenglichen Intervallgrenze enden.

Eine erfolgreiche Bruecke liefert atomar:

- das vollstaendige Abschlussfeld,
- den vollstaendigen naechsten privaten Zustand derselben Rolle,
- endliche rolleneigene Invarianten- und Numerikdiagnostik,
- einen kanonischen Digest ueber diese drei Ausgaben.

Bei einem Fehler gibt es keine partielle Feld-, Zustands-, Diagnose- oder
Digestausgabe. Clipping, Nachnormierung, Parameterwechsel, Reset, Retry und
Fallback auf eine andere Refinementstufe sind verboten.

## Technische Abnahme

Vierzehn statische Klassen pruefen Quellen, die vierwertige Aufrufhuelle, alle
sechs Rollen, private Zustandsrueckgabe, Kernidentitaeten,
Informationsbarrieren, Zeitpartition, Neutralpfade, Ausgabeatomaritaet und
fehlende Ausfuehrung.

Es wurden null Adapter konstruiert, null Modellkerne aufgerufen und null
technische oder forschungsbezogene Feldschritte ausgefuehrt.

## Entscheidung

`SIX_PRIVATE_BASELINE_ADAPTER_BRIDGES_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`2852c8215dc9cc6e20d7de5865e50f9d6badc65ed7df99e37779e281960faa7b`

Der Vertrag zeigt keine numerische Zulaessigkeit, Baselinepassung oder eigene
DTS-1-Gegenprognose. Speicher-, Lern- und KI-Claims bleiben gesperrt.

## Naechster zulaessiger Schritt

S1-JQ darf ausschliesslich die privaten unveraenderlichen Adapterkontexte,
atomaren Ausgaberecords und sechs Bruecken gegen die vierzehn technischen
Klassen implementieren. Er darf nur synthetische technische Einzelintervalle
in Tests verwenden. Kein Profilfall der 24-Fall-Matrix, kein gemeinsamer
Vergleich, keine Runtimeanbindung und keine Forschungsprobe.
