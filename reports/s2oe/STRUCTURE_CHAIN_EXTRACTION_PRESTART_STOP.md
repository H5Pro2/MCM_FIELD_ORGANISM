# Reine PPB-Diagnose getrennt: verbleibender Vorabstopp

Die freigegebene Auslagerung ist implementiert, aber **noch nicht qualifiziert**.
`tools/_ppb_visual_transition_table.py` enthält ausschließlich die bisherigen
Funktionen `table`, `verify`, `need` und deren Fehlerklasse. Historischer
Diagnosepfad und neuer Kettenbinder importieren dieselben Funktionen.
Die unabhängige Prüfung berechnet weiterhin Terme, fsum, Auswahl, Support
und Prototypupdate selbst; sie übernimmt nicht bloß das produktive Ergebnis.

Der ursprüngliche historische Modulstand bleibt bytegleich unter
`reports/s2oe/structure-location-chain-qualification-20260912-02/previous_diagnostic.py`
erhalten. Sein Hash wurde vor dem Vorabstopp gegen die ursprüngliche
e03/e04-Diagnosebindung bestätigt. Archiv, Herkunftsbindung und aktueller
historischer Einstieg sind vollständig mitgezählt. Der alte Diagnoseversuch
wurde nicht erneut ausgeführt; seine Belege sind unverändert.

Vorbereitet sind die acht Kontakt-/Kettentests plus vier neue Kontrollen:
AST-Gleichheit der ausgelagerten Funktionen und gemeinsame Importbindung,
neutrale Funktionsgleichheit an einer inklusiven Grenze, gleiche Fehlerabweisung
und Verifikation ohne produktiven Distanzhelfer. **Alle zwölf Tests sind
unausgeführt.** Funktionsgleichheit wird noch nicht als qualifiziert behauptet.

## Vollständige aktualisierte Vorbilanz

| Klasse | Erfolg | Fehler |
| --- | ---: | ---: |
| Software-/Testquellen | 590.453 | 590.453 |
| Metadaten einschließlich Berichtreserve | 95.824 | 95.824 |
| Evidenz einschließlich neutraler Hülle | 2.525.777 | 3.574.353 |
| Verifikation | 35.446 | 35.446 |
| Gesamt | **3.247.500** | **4.296.076** |

Die Metadatengrenze 98.304 Byte bleibt eingehalten. Die vollständige
Fehleralternative überschreitet **4.194.304 Byte um 101.772 Byte**.
Softwarebelege sanken gegenüber der vorherigen Bindung von 1.404.438 auf
590.453 Byte. Nur die tatsächlich nicht mehr importierten Extraktions- und
Runtimeabhängigkeiten entfielen aus dem neuen aktiven Pfad.

Die Vorregistrierung hätte 6.579 Byte. Der Schutz in
`reports/qualify_structure_chain_once.py::prepare` gab die vollständigen
Klassenbeträge aus und stoppte mit `ChainError: PRESTART_LIMIT`, bevor er
die Vorregistrierung veröffentlichte oder eine Qualifikation startete.
Keine neue Qualifikationsclaimdatei und kein Hauptlauf.

Die konservative Bilanz enthält weiterhin drei volle 1.048.576-Byte-Reserven:
neutraler Erfolgsbeleg, späterer realer Gesamtbeleg und möglicher realer
Teilbeleg. Der verbleibende Konflikt betrifft daher die gemeinsame
Evidenzhülle, nicht weitere ausgeführte Memoryarbeit. Eine kleinere vollständige
Reserve müsste aus der konkreten Ausgabeform begründet werden; eine passende
Beispielgröße wäre kein Obergrenzennachweis. Nach dem Stopp wurden weder
Reserven reduziert noch Fixtures erleichtert oder weitere Funktionen ausgelagert.

Neutrale Zusatzarbeit ist prospektiv getrennt erhöht gebunden: höchstens
zehn produktive neutrale Übergänge, 2.592 produktive und 7.488 diagnostische
Differenzen sowie zwölf unabhängige Prüfversuche mit höchstens 31.104
Differenzen. Das reale Neun-Schritt-Budget bleibt unverändert. Diese Arbeit
wurde nicht ausgeführt.

Keine Quellenregeneration, Rezeptoranalyse oder reale PPB-Folge; keine
Fast-/Memory-/Feldintegration, Gates False. Historische Fehlbefunde erhalten.
Noch keine tragfähige Einmalbindung; keine zusätzliche Grenzerhöhung.
