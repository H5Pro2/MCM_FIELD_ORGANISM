# LZ1: korrigierter Vertrag, Implementierung und neutrale Qualifikation

Stand:2026-10-04. **Vorbereitung abgeschlossen, Forschungsstart nicht erfolgt.**
Die festgelegten Forschungsfolgen wurden weder materialisiert noch abgespielt.
Eine separate Einmalentscheidung bleibt erforderlich. A1/K1 bleiben deaktiviert;
U-Produktionscode und historische T1/F-Urteile sind unverändert.

## Bewertungsvertrag

Der [korrigierte Vertrag](../../../docs/S2UC_LERNBARKEIT_ERFAHRUNGSZYKLUS_PRUEFENTWURF_20261004.md)
setzt **G_Y mit allen256 Fortsetzungen je Geschichte** als einzige primäre
Nutzenmenge. Vier primäre Kontraste: H64−P und U−P, jeweils S/W.
Die32 Wiederholungstripel bilden die gepaarten Bootstrap-Cluster;10.000 fest
bestimmte Ziehungen,98,75%-Intervalle der vier primären Kontraste, vorab bestimmte
lineare Quantile. Sekundäre Größen verwenden95%-Intervalle.

G_post, Gerüst, Präfix, Gesamtverlauf und vier feste Y-Zeitfenster bleiben
vollständig erhalten. Die N-Nullerwartung gilt ausschließlich für G_Y.
Ein Gerüstvorteil in N ist für sich kein Hinweis auf ein Informationsleck.
Ein gezielter Qualifikationstest liefert ausschließlich Gerüstvorteile und
verlangt trotzdem vier negative primäre Nachweisurteile.

Quellenformeln, Präfixausgleich,32 Wiederholungstripel, Wechsel nach128 Blöcken
und SHA256-Ziehfestlegung wurden nicht verändert. Die Quellenfunktion enthält
die festgelegte Forschungsdefinition, wird im neutralen Pfad aber nicht aufgerufen.
Neutraldaten haben andere Vektoren und eine eigene deterministische Ersatzfolge.
Auch bei der Qualifikation bleiben sämtliche96 Geschichten mit1.040 Frames erhalten.

## Implementierte Dateien und Referenzen

- `tools/_s2uc_lz1_sources.py`: gebundener Plan, Masken, gesperrte Forschungs-
  erzeugung, neutrale Ersatzdaten und verlustlose Katalog-/Indexdarstellung.
- `tools/_s2uc_lz1_h64.py`: Vergleichsarm als fester73.728Byte-Ring; exakte
  vergangene Hinweis-Ziel-Tripel, Häufigkeiten, Persistenz bei leerer Menge/Tie.
- `tools/_s2uc_lz1_reference.py`: unabhängige H64-Referenz mit Deque und Counter,
  ohne Ring-/Packcode. Referenzspeicher ist externer Prüfaufwand, kein Armzustand.
- `tools/_s2uc_lz1_engine.py`: unveränderter U-Pfad, H64, direkte Persistenz,
  Referenzabgleich, Ressourcenmessung und vollständige kompakte Ereignisse.
- `tools/_s2uc_lz1_stats.py`: gepaarte Masken-/Clusterprüfung, primäre und
  sekundäre Kontraste, Wiederholungswerte, Unsicherheit und Schadensbilanz.
- `tools/s2uc_lz1.py`: Vorbereitung, Qualifikation, Versiegelung, Prüfung und
  separat autorisierter Einmalstart; eigene Pfade und Größenkappen.
- `tests/test_s2uc_lz1.py`: zehn Qualifikationsgruppen einschließlich Vollgröße.

U verwendet den bereits qualifizierten Replaypfad aus
`_s2uc_a1_compare_engine.replay(..., enabled=False)`. Trotz des historischen
Modulnamens entsteht dabei exakt MultiErrorAdapter(FactorRecencyArm) ohne
A1/K1-Regel. Die bestehende unabhängige U-Zustandsreferenz prüft Bestand,
Fehlerzellen, Revisionen, Tickets, eingefrorene Nachfolger und Auswahl.
Keine Produktionsdatei wurde geändert. Die A1- und K1-Vorstartbindungen bestehen
weiterhin; ihre reinen Hashprüfungen wurden ohne Replay ausgeführt.

H64 bekommt weder Quellenkatalog noch Fall-/Phasenbezeichnung. Seine Schnittstelle
besteht aus den beiden bereits eingetroffenen Hinweisvektoren und später dem
beobachteten Ziel. Der Quellenkatalog ist nur verlustloses Exportformat.
U erhält eine feste Schema-Scope-ID, keinen aus Zukunftswerten erzeugten Profilhash.
P wird direkt aus dem letzten tatsächlich beobachteten Frame bewertet.

## Neutrale Prüfbelege

[Testergebnis](../lz1-neutral-20261004-01/tests.json): **10/10 PASS**.
[Qualifikationsabschluss](../lz1-neutral-20261004-01/closure.json): PASS,
190,319s insgesamt. Ein vorangegangener neutraler Entwicklungscheck über eine
Geschichte war kein Abnahmebeleg. Kein bereits bestandener Forschungsversuch
wurde erneut ausgeführt.

| Test-ID | Abgedeckter Nachweis |
| --- | --- |
| 01 | Vollständige96 Geschichten/288 Arme; unabhängige Referenzen, beide Originalspuren, alle Y-Gelegenheiten, durchlaufender Ring und vollständiger Export |
| 02 | Vollständige Masken/Partitionen; Forschungsquelle ohne Autorisierung gesperrt; Neutralpfad ruft keine Forschungsziehungen auf |
| 03 | H64-Gleichstände, Überlauf/Überschreibung, veraltete Einträge entfernt, Pending-/Feedbackgrenzen |
| 04 | H64-Speicherstress mit64 unterschiedlichen Fortsetzungen und vollständige Leerung |
| 05 | Unabhängige Bootstrapprüfung über ausgeschriebene Stichprobenindices statt Produktions-Gewichtsmatrix; Quantilprüfung |
| 06 | Ausschließlicher Gerüstvorteil erzeugt keinen primären Nachweis; N-Gerüst bleibt sekundär |
| 07 | Fehlende Ziele, falsche Clusteridentität und abweichende Maskenmittel abgewiesen |
| 08 | Autorisierungs-, Start-, Vorbereitungsgrößen- und Vorstartzeitfehler ohne Workerstart abgeschlossen |
| 09 | Prozessabsturz, Workerfehler, Exportfehler, Auswertungsfehler, Abbruch und Timeout mit NOT_EVALUABLE abgeschlossen |
| 10 | Datei-/Entpackgrenzen,61MiB-Kappensumme, unveränderte frühere Versuche bei Kollision, echter Autorisierungspfad |

Die absichtlichen Negativversuche hinterlassen eigene NOT_EVALUABLE-Abschlüsse.
Sie sind bestandene Fehlerprüfungen und keine fehlgeschlagene Qualifikation.
Es gibt keine automatische Wiederholung und kein Fortsetzen vorhandener Ausgaben.

Der neutrale Vollablauf ist COMPLETE:

- 96 Geschichten,288 Arme,99.840 Quellenframes und299.520 armbezogene Frames;
- 49.824 bewertete Ziele je Arm, davon24.576 primäre Y-Ziele;
- 99.840 U-Referenzfortschreibungen und49.824 H64-Feedbackabgleiche;
- zwei lebende Originalhypothesen an jedem der24.576 Y-Ziele, insgesamt49.152
  lebende Hypothesenfeedbacks an diesen Zielen;
- H64-Feedbackzählung durchgehend0…518 je Geschichte; bei erstem Y nach Wechsel
  (Ziel531) bereits264 Rückmeldungen, kein Reset;
- alle519 bewerteten Ziele,520 Prognosebelege einschließlich zensiertem Ziel1041
  sowie520 U-Bestandsereignisse je Geschichte exportiert.

Die Zahlen belegen technische Gelegenheit und Konsistenz, **keinen Forschungsnutzen**.
Neutrale Kontrasturteile sind keine Ergebnisse der festgelegten Quellenfamilie.

## Ressourcen und Export

| Größe | Neutral beobachtet | Grenze |
| --- | ---: | ---: |
| Worker einschließlich Gesamtauswertung | 171,868s | 3.540s |
| Supervisor bis vor Abschlussdokument | 173,275s | 3.600s mit60s Reserve |
| U-Zusatzheap | 5.498Byte | 16.384Byte |
| U-Originalframes, konservative Obergrenze | 12 | 18 |
| U-kombinierte Obergrenze | 14 | 20 |
| U-Ausgabeslots / Bank | 2 /416Byte | 2 /416Byte |
| U-Receipt / UTF-8-Obergrenze | 769 /1.538Byte | 16.384 /32.768Byte |
| H64-Heap im Vollablauf | 78.964Byte | 131.072Byte |
| H64-Heap im64-Fortsetzungen-Stress | 80.540Byte | 131.072Byte |
| Größte komprimierte Fallakte | 41.260Byte | 524.288Byte |
| Größte entpackte Fallakte | 860.616Byte | 4.194.304Byte |

P hat384Byte Vektornutzdaten. Eine ergänzende Messung auf ausschließlich
archivierten Neutralvektoren belastet die geteilte Eingabe vollständig:
1.584Byte Python-Tupel/Floats einschließlich1.200Byte Repräsentationsaufwand,
72Byte gemessener MAE-Transientpeak; zusammen1.656Byte. Diese16 einzelnen
MAE-Messungen sind keine Replays. [P-Ressourcenbeleg](p-resource.json).
H64 ist bewusst speicherreicher als U und kein kapazitätsgleicher Vergleich.

Der vollständige neutrale Laufexport umfasst4.427.810Byte inklusive Abschluss.
Die Qualifikation belastet ihn vorsorglich mit den maximal zulässigen8MiB
Vorbereitung, nicht nur dem später tatsächlich benötigten Betrag.
Die Dateikappen ergeben96×32KiB Quellen +96×512KiB Fallakten +1MiB Verwaltung
+8MiB Vorbereitung +1MiB Abschluss =61MiB, unter64MiB.
Keine Wiederholung und kein Beleg wurde zur Einhaltung weggelassen.

Die Fallakten sind verlustloses gzip-JSON. Wiederholt ausgeschriebene historische
Feedbacklisten sind durch einmalige Rückmeldungsereignisse ersetzt; Original-
Ordinalen, Schlüssel, Zellen vor Auswahl, eingefrorene Prognosen, Rückmeldungen,
H64-Stimmen, Überschreibungsziele und kumulierte Unterschiede bleiben erhalten.
Quellen lassen sich exakt aus archivierten Vektoren und Indices rekonstruieren.
Eine technische Fallakte stellt keinen Rohdatenzugriff des Mechanismus dar.

Ressourcenwerte betreffen die Arme nach bestehenden Abgrenzungen; unabhängige
Referenzen und Ergebnisarchive sind Beobachteraufwand. Die nicht aktivierten
Frame-Tracing-Zähler werden nicht als Nullbelegungen interpretiert; konservative
Framegrenzen und vorhandene Produktionsqualifikation gelten weiter.
Die Supervisorzeit endet wie im übernommenen Verfahren vor dem terminalen
Schreibvorgang. Physischer Stromausfall wird dadurch nicht als abgefangen behauptet.

## Vorstartbindung und Aufruf

[Vorstartbindung](../../../docs/S2UC_LZ1_V1_20261004_VORSTARTBINDUNG.json)

SHA256: `e4c57655eae1b954ea22807beb42d26bb28ce8df468c8c64f8048702046c9da3`

123 Code-/Vertrags-/Abhängigkeitsdateien sind gebunden. Das verlustlos geprüfte
Qualifikationsarchiv umfasst3.377.067Byte. Vorbereitung vor Eigenbindung und
Autorisierung4.445.279Byte; der spätere Start zählt deren echte Größen zusätzlich
gegen8MiB. Supervisorfunktion textidentisch zur übernommenen qualifizierten
Startlogik.197 Dateien des neutralen Vollabschlusses wurden hashgeprüft.
[Zusammengeführte Prüf- und Ressourcenbilanz](verification.json).

Reine Prüfung im Projektverzeichnis, bereits bestanden:

```powershell
C:/Python314/python.exe -m tools.s2uc_lz1 check
```

Ausführbarer Forschungsaufruf, **hier nicht ausgeführt**; nur nach separater
Einmalentscheidung und Bereitstellung der exakt gebundenen operativen Datei:

```powershell
C:/Python314/python.exe -m tools.s2uc_lz1 run --authorization docs/S2UC_LZ1_V1_20261004_AUTORISIERUNG.json
```

Die [Vorlage](../../../docs/S2UC_LZ1_V1_20261004_AUTORISIERUNG_VORLAGE.json)
steht auf PENDING_SEPARATE_AUTHORIZATION. Keine operative Autorisierung erstellt;
Zielordner `reports/s2uc/lz1-comparison-20261004-01` existiert nicht.

## Nächste Entscheidung

Empfehlung an den Projektleiter: korrigierten Vertrag und qualifizierte Hülle
anhand dieses Pakets technisch abnehmen. Danach kann eine separate Entscheidung
über genau einen gebundenen Forschungsdurchlauf folgen. Keine neue Speicher-
oder Auswahlregel ist dafür erforderlich. Ein später positiver Befund würde
zunächst Lernen einer wiederkehrenden Fortsetzungsverteilung innerhalb der
vorhandenen Kapazität zeigen; nicht Verdrängungsrobustheit, Transfer oder
MCM-spezifischen Mehrwert.
