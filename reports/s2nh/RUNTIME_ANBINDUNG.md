# S2-NH: begrenzte private Materialisierungs- und Runtime-Anbindung

Status vor Qualifikation: Hauptgate False. Keine neue Korpuserzeugung,
keine Materialisierung der versiegelten NH-Payloads, kein Hauptvergleich.
Die historische Vorversiegelung bleibt unveraendert; dies ist ihre
Anrufbindung, kein neuer Vertrag und keine neue Laufplattform.

## Dateien und Trennung

- `tools/_s2nh_private_runtime_binding.py`: gepinnte Ausfuehrungswurzel,
  einmalige streaming Materialisierung, unveraendertes NG-Runtimepaar und
  geschlossener `run_main_once(run_id, output)`-Einstieg.
- `tools/_s2nh_private_runtime_verification.py`: Quellen-/Zeit-/Wertebindung,
  Delegation an NG-Gesamtpruefung, separate nachgelagerte NH-Auswertung.
- `tests/test_s2nh_private_runtime_binding.py`: ausschliesslich neutraler
  Qualifikationsumfang. Historische Tests werden nicht erneut aufgerufen.

Im spaeter freizugebenden Hauptlauf genau 24 Audiofenster mit 240 Hops durch
einen fortgefuehrten HearingPath und 24 visuelle Analysen. Der rollende Pfad
liefert dabei 231 Audioabschluesse; gebunden werden die 24 Fensterendpunkte
mit Snapshotindizes 0, 10, ..., 230. Das sind nicht 24 direkte FFT-Aufrufe.
Reine Videoereignisse erzeugen keine Audiohops und setzen Audiozeit nicht
zurueck. Audiozeit `audio.sample`, Videozeit `video.frame`, gemeinsame Uhr
`s2nh-transfer-field-clock` bleiben getrennt. Ein erzeugter PCM-Payload und
ein RGB-Frame hoechstens gleichzeitig; der bestehende rollende Audiopuffer
ist unveraenderter Rezeptor-Arbeitsspeicher, keine Rohdatenablage.

Jeder Payloadhash wird vor Analyse geprueft. RGB-Cues kommen ausschliesslich
aus dem versiegelten bereits okkludierten RGB-Rezept. Die Belege enthalten
Quellenidentitaet, native und gemeinsame Zeiten, reduzierte Werte und
Digests, keine PCM-/RGB-Rohbytes. Fehler stoppen mit Phase, Ordinalzahl,
Quellen-ID und bis dahin abgeschlossenen Analysen; keine Ersatzquelle.

Beide Regelarme werden vor jedem Ereignis fest gebunden. NG prueft reale
Instanztrennung, gleiche Geschwisterzustaende und dieselben unveraenderlichen
Inputs. Alle Hinweise sind read-only, auch die fruehen Ereignisse e03/e04.
Feld- und Memorykern, historische Defaults, Scan- und Slow-Regeln bleiben
unveraendert. Beide Runtimeinstanzen werden geschlossen.

Die getrennte Auswertung konsumiert erst nach technischer Verifikation die
NH-Evaluationswurzel. Sie verfolgt aktuelle PPB-Generationen auch bei
Supportsaettigung, Fast-Auswahl, gemischte Herkunft, echte Inventare und
Verdraengung. Richtige Ziele stammen aus Formationen, nicht aus Hinweis-
Sollwerten. N/D/R/L, Gewinne, Verluste, ausgeschlossene Zielkandidaten,
Modalitaet, Zeitpunkt, Konkurrenz und tatsaechliche Wertevariation bleiben
getrennt. Sollsupport und erwartete Treffer sind keine Startbedingungen.

## Vorab gebundene Grenzen

Unveraendert: 28 Ereignisse/20 Formationen je Hauptarm, insgesamt 16128
Feldkontakte und 32 vollstaendige Scanbelege. 21248 Wertvergleiche fuer
Ausfuehrung und getrennt nochmals hoechstens 21248 fuer read-only
Verifikation; 142080 Formations-L1-Terme. Kein zusaetzlicher Geometriescan.

NG-Teilbudgets unveraendert: Zustand 98304, Input/Schrittpaar je 16384,
Scan unter 32768, NG-Metadaten 65536 Byte. Teilbudgetsumme 4096000 Byte.
Die zusaetzliche NH-Huelle wird auf 32768 Byte begrenzt; rechnerische Summe
4128768 Byte, einschliesslich kompletter kanonischer Huelle weiterhin
hoechstens 4194304 Byte. Ueberschreitung fuehrt zu NOT_EVALUABLE, nicht zu
einer Grenzerhoehung. Getrennte Auswertung ebenfalls hoechstens 4194304 Byte.

## Einmalige neutrale Qualifikation

ID: `s2nh-runtime-binding-qualification-20260906-01`.
Genau ein Aufruf mit 20 Tests. Testinventar, Kommando, Interpreter- und
Quellhashes werden vorher gespeichert und danach bytegleich geprueft.
Aufruf aus dem Workspace mit `C:/Python314/python.exe -B -m
reports.s2nh.qualify_runtime_once`. Kein Retry bei Fehlern.

Neutraler Ablauf: AV, Audiohinweis, Videohinweis, AV, Audiohinweis,
Videohinweis. Zwei Formationen je Arm, zusammen vier; 2688 Feldkontakte.
Vier Audiofenster/40 Hops/31 Audioabschluesse und vier visuelle Analysen.
Nur Seeds mit Praefix `neutral-`; eine leise Sinusquelle, ein binaeres
RGB-Raster und zwei okkludierte Ansichten. Keine NH-Payloads.
Neutrale Vorbindung plus Analyse erzeugt maximal fuenf PCM-Payloads und
sieben RGB-Frames, einzeln freigegeben. Keine Suche oder Nachjustierung.

Die 20 Tests decken Typen, fortlaufende Audiozeit, Cue-Digests, NH-Felduhr,
beide Arme, Instanztrennung, fruehe Read-only-Fortsetzung, gueltige
Enthaltung, Lifecycle, fehlende/vertauschte Belege, Quellen-/Zeitfehler,
Groessen, Einmalgates, technischen Fehlerabschluss, atomaren Schreibkonflikt,
Evaluationsbindung, N/D/R/L, PPB-Saettigung/Ersetzung und volle Scans ab.
Der neutrale Sollsupport wird absichtlich nicht erreicht; dies darf die
technische Verifikation nicht verhindern. Der letzte visuelle Hinweis
wird neutral als erwartete, aber ausbleibende Hypothese ausgewertet.

Erst ein bestandener Befund erlaubt die Analystenpruefung fuer eine
separate Freigabe des realen NH-Vergleichs. Keine Hypothesenanwendung.
