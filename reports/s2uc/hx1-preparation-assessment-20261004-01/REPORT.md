# HX1: Implementierung und neutrale Qualifikation abgeschlossen

2026-10-04. **NEUTRAL_QUALIFIED_PENDING_AUTHORIZATION**.
Q1–Q7 bestanden; genau ein vollständiger neutraler Größenablauf COMPLETE.
Keine HX1-Forschungsquelle erzeugt oder abgespielt. Keine operative
Forschungsautorisierung angelegt. U unverändert; A1/K1 deaktiviert.

## Implementierter Umfang

Genau D/N und U/G/P gemäß abgenommenem Vertrag. Forschungsquellen besitzen
gesperrte Einstiegspunkte, vier getrennte SHA256-Ströme und festgelegte
Fisher-Yates-Permutationen mit Rejection-Sampling. Ihre tatsächlichen
HX1-Forschungsfolgen wurden nicht zur Vorbereitung aufgerufen.

U bleibt der vorhandene Produktionsadapter. Die neue Beobachterhülle verwendet
die unabhängige Bestandsreferenz und separat rekonstruierte Fehlerzellen.
G hat einen gepackten globalen Mittelwertzustand mit Zähler und eine unveränderliche
Prognose; P verwendet Persistenz. G-Referenz rundet die Rechenschritte unabhängig
über rationale Zwischenwerte auf binary64. Vorhersagen entstehen vor dem Ziel.

Primärkontraste D:U−G, D:U−P und (D:U−G)−(N:U−G), jeweils auf vollständigem Q.
10.000 nach Gegenorientierung geschichtete, gepaarte Bootstrapziehungen;
rationale Aggregation und Quantile 1/120 sowie 119/120. Drei notwendige
Nachweise; zwei erfolgreiche Kontraste reichen nicht aus. Referenzauswerter
und unabhängig rekonstruierte Ziehungsmatrix sind geprüft. Intervallabdeckung
bleibt nominal/approximativ, wie im Vertrag festgelegt.

V0–V3, Originalverfügbarkeit, Zellalter, dominante Verfügbarkeit in D,
Rollen/Generationen, Rückmeldungen, Promotionen und Verluste werden vollständig
exportiert. Unterschiedliche U-Bestände zwischen D/N sind zulässig. Es gibt
keine Anpassung aneinander und keine ausgeschlossenen kalten/verlorenen Ziele.

## Neutrale Prüfungen

| Gruppe | Geprüfter Umfang | Ergebnis |
| --- | --- | --- |
| Q1 | Quellenzugangssperre, unabhängige kleine Permutationsreferenz, beide Orientierungen, getrennte Ströme, Rejection-Grenzen und Zähler | PASS |
| Q2 | unverändertes U, elf bestehende Zell-/Lebenszyklus-Unterprüfungen einschließlich sechs Zellen, Verlust, Promotion, Gleichständen und atomaren Fehlerpfaden | PASS |
| Q3 | getrennte G/P-Instanzen, erstes Ziel, Freeze vor Update, Phasenverhalten, veränderte Hinweise bei gleichen Fortsetzungen, veränderte Fortsetzung | PASS |
| Q4 | unabhängige Zustands-/Ausgabereferenzen; absichtlich falsche G-Zelle, falsche U-Auswahl und ungültige Eingangsphase werden erkannt | PASS |
| Q5 | gesamte Bootstrapmatrix unabhängig geprüft; rationale Handtabellen, drei gerichtete Urteile, Nullgrenze, nur zwei erfolgreiche Kontraste, fehlende Ziele/Paare | PASS |
| Q6 | V0–V3, vollständiger verlustfreier Export, einzelne Datei-/Heap-/Expansionslimits | PASS |
| Q7 | Autorisierungssperre, Prozessstartfehler, Crash, Workerfehler, Exportüberlauf, Abbruch, Zeitgrenze, Vorbereitungsgrenze, exklusive Ordner und reale Windows-Speicherabweisung | PASS |

[Gebundenes Prüfprotokoll](../hx1-neutral-20261004-01/tests.json),
[elf U-Unterprüfungen](../hx1-neutral-20261004-01/Q2-details.json),
[Statistik-Handtabellen](../hx1-neutral-20261004-01/Q5-handtables.json).
Die Fehlerprovokationen enden erwartungsgemäß NICHT_AUSWERTBAR; das ist
kein fehlgeschlagener Forschungsdurchlauf und erzeugt keine Forschungsdaten.

## Einziger vollständiger neutraler Größenablauf

| Größe | Belegter Wert |
| --- | ---: |
| Geschichten | 64 |
| Prädiktorläufe | 192 |
| Quellenframes | 65.536 |
| U/G/P-Verarbeitungen zusammen | 196.608 |
| unabhängige Referenzfortschritte | 196.608 |
| beobachtete Ziele je Prädiktor über D/N | 32.704 |
| Q-Ziele je Prädiktor über D/N | 16.384 |
| D/N-G-Vergleichspositionen | 8.192 |
| Workerzeit | 369,559 s |
| Supervisorzeit vor Abschlussdatei | 370,444 s |
| gesamte gebundene Qualifikation | 387,898 s |

Alle G-Vorzustände, Ausgaben, Fehler und Nachzustände stimmen auf Q
positionsweise zwischen D/N überein. Zusätzlich wurde das gespeicherte Archiv
ohne Replay geprüft: 16.384 G-Prognosen aus dem jeweiligen Vorzustand
rekonstruiert, kanonische Fehler nachgerechnet, 8.192 D/N-Paare abgeglichen
und alle 512 klassenspezifischen Gewinn-/Schadenszeilen exakt bestätigt.
181 Dateien des Qualifikationsabschlusses auf Länge und SHA256 geprüft.

Alle vier Diagnoseklassen sind im neutralen Material vertreten. Je D/N:
V0=108, V1=72, V2=2.008, V3=6.004; Summe 8.192. Diese Zahlen zeigen technische
Abdeckung des neutralen Musters, keinen wissenschaftlichen Hinweisnutzen.
Gleiche Klassenzahlen wurden nicht als U-Bestandsgleichheit vorgeschrieben.

[Vollständiger neutraler Abschluss](../hx1-neutral-20261004-01/integration/closure.json),
[Größenbelege](../hx1-neutral-20261004-01/full-size-facts.json),
[zusätzliche Archivprüfung](verification.json).
Worker beendet, Exitcode 0; resume_permitted=false.

## Ressourcen und Durchsetzung

| Ressource | Gemessen | Limit |
| --- | ---: | ---: |
| gemeinsamer Job-Peak Supervisor + Worker | 132.042.752 Byte | 536.870.912 Byte (512 MiB) |
| U zusätzlicher Python-Heap inkl. Transienten | 5.323 Byte | 16.384 Byte |
| G eigener Heap inkl. Transienten | 3.441 Byte | 8.192 Byte |
| P eigener Heap inkl. Transienten | 2.049 Byte | 4.096 Byte |
| U Bank | 416 Byte | 416 Byte |
| G gepackter Zustand | 400 Byte | 400 Byte |
| U konservative Originalobergrenze | 16 | 18 |
| U konservative kombinierte Obergrenze | 18 | 20 |
| U Ausgabeslots | 2 | 2 |
| G/P Ausgabeslots jeweils | 1 | 1 |
| U Receipt | 751 Byte | 16.384 Byte |
| U transiente UTF-8-Obergrenze | 1.502 Byte | 32.768 Byte |
| größter expandierter Fall | 1.841.874 Byte | 4 MiB |
| größter komprimierter Fall | 102.573 Byte | 512 KiB |
| neutraler vollständiger Laufexport | 6.663.927 Byte | innerhalb aller Unterbudgets |
| kanonisches neutrales ZIP-LZMA-Archiv | 3.939.696 Byte | Teil des Vorbereitungsbudgets |
| verrechnete Vorbereitung inkl. exakt vorgesehener späterer Autorisierung | 5.108.345 Byte | 8 MiB |

Die Windows-Job-Grenze ist eine vom Betriebssystem konfigurierte Grenze für
gemeinsamen committed memory, keine bloße RSS-Stichprobe. Der Worker muss
nachweislich Mitglied desselben Jobs sein. Der erfolgreiche neutrale Größenablauf
blieb auch mit dem gemeldeten Job-Peak unter der Grenze.

Q7 forderte absichtlich 629.145.600 Byte (600 MiB) in einem Worker an. Windows
wies die Allokation mit MemoryError ab; der Fehlerabschluss ist vollständig,
der Worker beendet. Der Job meldete für diesen fehlgeschlagenen Versuch einen
Peak von 687.595.520 Byte. Dieser Fehltest wird ausdrücklich nicht als bestandener
Unter-Limit-Lauf dargestellt; er dokumentiert Abweisung und terminale Behandlung.

[Abgewiesene Allokation](../hx1-neutral-20261004-01/fault-memory/memory-enforcement.json),
[Fehltestabschluss samt gemeldetem Peak](../hx1-neutral-20261004-01/fault-memory/closure.json).
Die während der Entwicklung nötige Korrektur am Abschlussweg ist im
[Entwicklungsprotokoll](../../../docs/S2UC_HX1_ENTWICKLUNGSPROTOKOLL_20261004.md)
offengelegt. Kein Limit und kein Vertragsparameter wurde verändert.

G/P benötigen keine Produktionsreceipts (0 Byte). Die eigenen Heaps von G/P
und der zusätzliche Heap von U haben die im Vertrag verschiedenen Zählgrenzen;
die Zahlen sind kein Gleichheitsnachweis der Architekturen. U-Basisgraph,
Framepayloads und Operationsgrenzen stehen zusätzlich in den Fallexporten.
Originalaliase physisch einmal, Ausgabeslots logisch separat zählen.
Der rohe Frame-Tracing-Zähler 0 bedeutet ausgeschaltetes Line-Tracing,
nicht null Originalbelegung. Die konservativen Obergrenzen gelten trotzdem.

## Vorstartbindung und Startbefehl

139 Dateien sind in der Code-/Runtimebindung erfasst; U-Code gegen die
vorherige ULZ1-Bindung unverändert. Python 3.14.4 einschließlich Interpreter,
Runtime-DLL und Kompressionsbibliotheken gebunden. Neutralarchiv verlustfrei
gepackt; expandierte lokale Belege bleiben lesbar, werden nicht zusätzlich als
Produktionseingang verwendet. Die Vorstartprüfung rekonstruiert die ursprünglichen
gzip-Bytes und prüft ihre Hashes.

Vorstart-SHA256:
`e8cb8f935d28a5624239aafdbab75d0cb8246b665045442afcc9ec4a8931d36e`.

Codebindung-SHA256:
`66dfca57e696747b9125333f58666afab7dd23745c69ba0a78deea7250e1bf1c`.

[Startanleitung](../../../docs/S2UC_HX1_V1_20261004_START.md),
[Vorstartbindung](../../../docs/S2UC_HX1_V1_20261004_VORSTARTBINDUNG.json),
[Autorisierungsvorlage](../../../docs/S2UC_HX1_V1_20261004_AUTORISIERUNG_VORLAGE.json).

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Nach separater Einmalbeauftragung und Erstellung der exakt gebundenen operativen
Autorisierung lautet der vorbereitete Befehl:

```powershell
C:/Python314/python.exe -m tools.s2uc_hx1 run --authorization docs/S2UC_HX1_V1_20261004_AUTORISIERUNG.json
```

Dieser Startbefehl wurde nicht ausgeführt. Die Vorlage ist PENDING; eine operative
Autorisierung und der Forschungsexportordner existieren nicht. Kein automatischer
Forschungsstart aus erfolgreicher neutraler Qualifikation.

## Anschluss

Das beauftragte Vorbereitungspaket ist vollständig. Nächster Vorschlag an den
Projektleiter: technische Abnahme dieser Bindung und anschließend gegebenenfalls
genau einen separat autorisierten Forschungsdurchlauf beauftragen. Ein Vorteil
hinweisabhängiger Erfahrung bleibt wissenschaftlich offen; die neutralen Werte
sind kein positiver Forschungsbefund. ULZ1 bleibt abgeschlossen.
