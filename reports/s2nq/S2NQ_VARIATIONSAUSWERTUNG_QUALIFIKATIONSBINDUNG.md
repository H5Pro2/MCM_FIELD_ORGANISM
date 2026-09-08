# S2-NQ: fokussierte Bindung der Variationsauswertung

Stand 2026-09-08. Nur die freigegebene Auswerterkorrektur. Die technische
24/24-Qualifikation bleibt unveraendert; der Hauptlauf bleibt gesperrt.

## Zwei getrennte Merkmale

`receptor_variation` vergleicht die indexgebundenen Cuewerte mit den
urspruenglichen, quellengebundenen Halbprofil-Formationswerten derselben
Geschichte vor dem Hinweis. Referenzdaten stammen aus dem gespeicherten
Quellenbeleg, nicht aus Slots, rekonstruierten Digests oder Rohwertrekonstruktion.
Die globale technische Belegpruefung ist weiterhin Voraussetzung der Auswertung.
Zusaetzlich werden Ereignis-/Quelldigest, Projektionsform und Ereigniszeit
geprueft. Quellen-IDs lokalisieren nur die Referenz; Labels beweisen keine
numerische Variation.

Pro Sicht werden ausschliesslich dieselben 24 Originalindizes verglichen.
Mehrere Referenzen sind nur bei gleichen beobachteten Tupeln eindeutig.
Fehlende, ungueltige oder innerhalb einer Sicht unterschiedliche Referenzen
ergeben `null` mit Status, niemals `false`. Unterschiede ausschliesslich im
Komplement begruenden fuer diese Sicht keine Variation. Keine Toleranz.

`cue_candidate_deviation` behaelt die bisherige Cue-/Slotabweichung aus den
gespeicherten Termbelegen. Damit bleibt PPB-Drift sichtbar, ohne als
Rezeptorvariation zu zaehlen. Nur `receptor_variation` gruppiert N/D/R/L.
Treffer, Herkunftsentscheidung und Nennerdefinitionen bleiben unveraendert.

## Einziger neutraler Aufruf

Einstieg: `python -m reports.s2nq.qualify_variation_once`.
Neue ID: `s2nq-variation-evaluation-qualification-20260908-01`.
Der Einstieg erstellt die Preregistrierung mit acht konkreten Testnamen,
Interpreterbindung und SHA-256 vor genau einem Unittest-Prozess mit `-f`.
Kein Retry. Ein existierendes Zielverzeichnis sperrt den Aufruf.

Festes Inventar:

1. Exaktcue trotz synthetischer PPB-Rundungsdrift.
2. Sichtbare numerische Variation unabhaengig vom Variantenlabel.
3. Variation ausschliesslich ausserhalb der jeweiligen Sicht.
4. Fehlende gebundene Formationswerte ergeben nicht bestimmbar.
5. Mehrdeutige Formationsreferenzen je Sicht getrennt behandeln.
6. Fehlende Referenzidentitaet und ungueltige Digestform.
7. Erhaltung, Gewinn, Verlust sowie leerer Nenner bleiben getrennt.
8. Nicht bestimmbare Variation aendert keine Entscheidungen oder Nenner.

Die Fixtures sind ausdruecklich synthetische Auswerterformen, keine echten
Memoryzustaende und keine technisch verifizierten Hauptlaufbelege. Der
Projektionsdatentyp und seine Validierung werden verwendet, die NJ-Rechnung
wird nicht aufgerufen. Die Drift ist ein festes benachbartes Binary64-Tupel;
es findet kein PPB-Update statt.

Grenzen: acht Tests, maximal 16 Auswerteraufrufe (gebunden erwartet: 14),
64 synthetische Formationsreferenzen und 24 synthetische Cuefaelle; zwei
Sichten, je hoechstens vier Referenzen mit 24 Originalpositionen. Die
Ausgabegrenze bleibt 4.194.304 Byte; die konkrete maximale Testausgabe wird
gemessen. Keine neue Grenze fuer Hauptlauf oder Verifikation.

Null Aufrufe fuer Scan, Baseline, Formation, Rezeptor, NJ-Projektion, Feld,
Kontext und Runtime; keine NP-Payloads, NP-Werte oder reale NQ-Geschichte.
Die vormaligen 24 Tests werden nicht wiederholt. Quellen-, Kern-, Scan-,
Baseline- und historische Belegdateien werden nur gehasht, nicht veraendert.
Vor-/Nachhashes und Originalprotokolle werden aufbewahrt. Bei Fehler Stopp.
