# S2-NR: geschlossene Laufanbindung V3, neutrale Qualifikation

Qualifikations-ID: `s2nr-main-binding-qualification-20260908-01`.
Genau ein unittest-Aufruf mit 12 neuen Testkoerpern, `-v -f`, kein Retry.
Die bisherigen 16 Anschlusspruefungen werden nicht erneut ausgefuehrt.
Inventar, Interpreter und alle Quellenhashes werden vor dem Aufruf als JSON gebunden.

## Begrenzter neutraler Umfang

- Eigene Null-PCM-Rezeptur: 4800 Samples, 48 kHz, 997 Hz, Amplitude 0/1,
  Seed `neutral-nr-run-only`. Ein unabhaengiges RGB-Blockraster mit Seed
  `neutral-nr-run-grid`, unveraenderter reiner NH-Generator.
- Einmalige neutrale Hashbindung dieser zwei Quellen, danach Folge AV, Audiohinweis,
  AV, Audiohinweis. Vier Audiofenster, 40 Hops, 31 Abschluesse, vier NJ-Projektionen,
  zwei visuelle Analysen. Keine NR-Rezepte, NR-Payloads oder NR-Hauptgeschichte.
- Zwei Runtimearme: insgesamt acht Ereignisse, vier Formationen, 1536 Feldkontakte,
  acht Scanbelege. Ein zusaetzlicher absichtlich falscher Payloadhash stoppt vor
  dem ersten Rezeptoraufruf. Maximal sechs neutrale PCM- und drei RGB-Erzeugungen
  einschliesslich neutraler Quellenbindung. Keine Rohdatenablage.
- Zwoelf Gesamtverifikator-Eintritte maximal, davon zwei gueltige Belegpruefungen
  (Erfolgsbeleg sowie Kontrolle des technischen Fehlbelegs),
  uebrige Eintritte Manipulationsabwehr. Keine Memory-/Abrufwiederholung dabei.
- Hauptgate und historische Gates bleiben False. Der reservierte Hauptlauf
  `s2nr-mask-runtime-transfer-20260908-01` wird nicht aufgerufen.

## Inventar

1. Reale neutrale Materialisierung, Endpunkte und getrennte Modalitaetsfenster.
2. Offline-Elternrekonstruktion ausschliesslich aus gespeicherten gerundeten Werten.
3. Durch Hinweis fortgesetzte Memorygeschichte und geschlossene Runtimeinstanzen.
4. Technisch gueltige Enthaltung mit funktional verfehlter Vorhersage.
5. Payloadfehler vor Rezeptor/Runtime, genaue Phase und Nullzaehler.
6. Quellen-, Zeit-, Projektions-, Fehlstellen- und Reihenfolgemanipulationen.
7. Tatsaechliche Herkunft, Support, urspruengliche Rezeptorvariation, fehlende/mehrdeutige Referenzen.
8. Getrennte Gewinne/Verluste, A-/B-Nenner, D=0 bleibt ungeprueft.
9. Geschlossener Haupteinstieg, unveraenderlicher Plan, lesende historische Versionsbindung.
10. Schreibkonflikt und vollstaendige maximale Artefakthuellen.
11. Ablehnung neutraler Praefixe als Hauptlauf, feste 18/14/4-Gesamtzaehler.
12. Manipulierte Fehlerphase/Fortschritt und Auswertungsverbot ohne passende Verifikation.

## Hauptpfad und Ressourcen

Nur die neue Verbindung V3 oeffnet nach separater Freigabe den privaten
`run_main_once`-Pfad. Die Quellenversiegelung bleibt bytegleich. Ausschliesslich
der bereits qualifizierte MR-Typanschluss ersetzt die historische MR-Dateibindung
explizit; alle anderen versiegelten Quellenhashes bleiben zwingend gleich.

Hauptumfang: gemeinsame 18 Audiofenster, 180 Hops, 171 rollende Abschluesse,
18 NJ-Endpunktprojektionen und 14 visuelle Analysen; pro Arm 18 Ereignisse,
14 Formationen; insgesamt 9792 Kontakte und 16 Scanbelege.
Vorhandene Abrufobergrenzen bleiben 320 Slotbesuche, 7680 Banddifferenzen,
768 Gleichheitskomponenten. Zusaetzliche bestehende Scanverifikation bleibt
separat auf 16 Pruefungen / 8448 Wertevergleiche begrenzt.
Formation: 28 Relationspruefungen; unveraenderte Obergrenzen fuer Fast-/PPB-/Updatearbeit.

Neue Offline-Bindungsarbeit separat: maximal 18 Eltern-Decodes, 18 Quellenreceipts,
32 Modalitaetszeitpruefungen und hoechstens 144 Projektionsvalidierungspassagen
einschliesslich verschachtelter Adaptervalidierung, entsprechend 6912
Komponentenbesuchen bei 864 gespeicherten Komponenten; null rekonstruierte
Rohkomponenten. Die Auswertung liest fuer
Rezeptorvariation maximal 4*2*14*24 = 2688 Originaleingangskomponenten, ohne
neue Rezeptor-/NJ-/Abrufaufrufe. Die NR-Metadatenhuelle bleibt <=65536 Byte.
Konkrete maximale Gesamthuelle: 2730730 Byte, innerhalb unveraenderter
4194304 Byte. Teilgrenzen: Input/Paar je 16384, Scan 32768, Zustand 98304 Byte.

## Pruefgrenze

Offline werden die gespeicherten gerundeten NJ-Werte, Kontaktgleichheit,
Maskenbindung, Quellen-/Zeitdigests, Zustandsrelationen und Scanbelege geprueft.
Die Rohwertdigests belegen Herkunft, erlauben aber keine unabhaengige numerische
Neuberechnung der Halbierung. Keine Multiplikation mit zwei zur Rohrekonstruktion.
Eine gueltige Enthaltung oder unerwartete Slotbildung ist kein technischer Fehler.
Erhaltung betrifft Bereich und eindeutige Zielherkunft, nicht gleiche Komplemente.
