# S2-OC: Neutrale Sitzungsqualifikation

Genau ein Aufruf unter `s2oc-session-qualification-20260910-01`, 24 Prüfgruppen.
Keine historische Testwiederholung, reale Aufruferfolge oder Hauptlauffreigabe.
OB run_once, Materialisierer, Runtime, Profile und Kerne bleiben unverändert.

## Prüfgruppen

1. Identische Eingangs-/Quellenbelege je Ereignis.
2. Gleiche Feld-/Memoryzustände und native Zustandsdarstellungen.
3. Gleiche tatsächliche Generationsketten.
4. Kanonisch identischer Gesamtbeleg einschließlich Scans und close.
5. Unveränderliche Rückgaben; keine Owner-/Rohdatenreferenzen.
6. Kein Zukunftszugriff; kurze Aufruferpausen ändern keine Ereigniszeit.
7. Doppelte Übergabe vor Payloadzugriff abweisen.
8. Vertauschte Übergabe ohne Zustandsänderung abweisen.
9. Vollständige Quellen-/Ereignisbindung und Budgetablehnung vor Payloadzugriff prüfen.
10. Keine veränderbare Manifestreferenz vom Aufrufer behalten.
11. Ereignis nach close abweisen.
12. Manifestende ausdrücklich prüfen; gültige Nullzustands-Enthaltung.
13. Vorzeitiger Abschluss: INCOMPLETE, keine fachliche Auswertung.
14. Wiederholtes close ohne zweite Veröffentlichung.
15. Wiedereintritt während Materialisierung und Verarbeitung, auch für close, abweisen.
16. Payloadfehler nach einem erfolgreichen Schritt; frühere Rückgabe vollständig erhalten.
17. Memoryfehler: unabhängige Feldwirkung erhalten.
18. Feldfehler: atomare Memorybildung erhalten.
19. Scanfehler: Feld fortschreiben, Memory read-only erhalten.
20. Gemeinsame Metadaten- und Globalgrenzen; Summeneingang ist kein erreichbarer Vollfall.
21. Manipulierte Einzelergebnisbindung abweisen.
22. Fremde Sitzungsquellenbindung abweisen.
23. Gate und vorhandene Ergebnisablage vor Initialisierung abweisen.
24. Vollständige Paketbilanz und unabhängige read-only Prüfung.

Die neue Gleichheitsfolge AV, A, AV, V wird zweimal frisch gebildet: einmal
durch OB run_once, einmal in vier Sitzungsaufrufen. Gleiche IDs, Manifest-,
Profil-, Quellen- und Codebindungen; getrennte Objekte und Ergebnisverzeichnisse.
PCM konstant 0,046875, RGB (30,90,150), visuell verdeckte Kanäle bereits vor
Analyse null. Keine realen OA-/OB-Payloads; Datei-Lesesperren sind aktiv.
Die Fehlerprüfungen besitzen eigene Sitzungen, nicht die große Vergleichsfixture.
Ein Fehler im Vergleich startet keinen zweiten Vergleichsversuch.

## Unveränderliche Ergebnisse und Belegklassen

Jede Rückgabe ist kanonisches JSON als bytes, maximal 16.384 Byte. Bei Erfolg
ist ihr vollständiger Inhalt bereits in execution.rows[n].step enthalten;
session.json bindet ihn eindeutig durch Ordinalzahl, Länge und SHA-256. Es
werden keine Pflichtinhalte außerhalb der Bilanz gespeichert. Bei technischem
Abbruch ohne execution enthält session.json die bereits ausgegebenen Schritte
vollständig als failed_prefix_steps. Diese gehören zur Ereignisschrittklasse,
nicht zu Metadaten. Alle Bytes bleiben in der Gesamtsumme; Metadaten enthalten
weiterhin Schlüssel, Listenhüllen, Rückgabereferenzen und Sitzungsbindungen.
Ein Fehlerpräfix ist kein fachlich auswertbarer Gesamtverlauf.

Sitzungsquellen, Einzelergebnisse, Gesamtbeleg, Baseline-/Verifikationsbelege,
Einmalmarker und Abschlussdateien werden gemeinsam bilanziert. Ein zusätzliches
Rohdatenjournal gibt es nicht. Die Rückgabe erzeugt höchstens einen zusätzlichen
16-KiB-Transportwert; der bereits gespeicherte Schritt wird nicht neu verarbeitet.
Ein neuer Speicherkern oder eine neue numerische Regel wird nicht eingeführt.

## Arbeit und vollständige Vorabbilanz

Ein Stapelaufruf und zwölf Sitzungen, insgesamt 16 tatsächlich versuchte
Runtimeereignisse, zehn Formationsversuche; 13 Audioanalysen, 13 NJ-Projektionen
und 13 visuelle Analysen. Ein absichtlich falscher Hash verursacht keine Analyse.
13 unabhängige OB-Verifikationen, davon zwölf mit zusätzlicher Sitzungsprüfung.
Je Prüfer gelten die unveränderten Obergrenzen: 116 Zustandsvalidierungen,
20 Formationsprüfungen, 20.160 Fast-, 30.720 PPB-, 13.440 Update- und 11.712
Scanvergleiche. Keine Verifikation darf Memory oder Rezeptoren wieder ausführen.

Vor dem Test gebunden: 16 Zustandsbelege à 98.304 Byte, je 16 Eingangs-/
Ereignisschrittbelege à 16.384 Byte, zwölf Scans à 32.767 Byte. NJ 13 × 1.024,
Formations- und Generationsbelege jeweils 10 × 1.536; Quellenbeilagen gemeinsam
65.536 Byte, Verifikation gemeinsam 262.144 Byte. Keine lokalen Maxima als
gemeinsame Freigabe: die vollständige Summe wird vor dem Test ausgegeben.

Runtime-/Sitzungsmetadaten gemeinsam maximal 57.344 Byte. Zusätzlich werden
die erforderlichen historischen OB-Qualifikationsdateien mit ihren tatsächlichen
3.131 Byte mitgezählt; sie sind kein ausgeblendetes Archiv. Die bestehende
4.096-Byte-Qualifikationsreserve gilt für den aktuellen vollständigen Nachweis,
Berichtreserve 512 Byte. Gesamtmetadaten damit höchstens 65.083 Byte, unter
65.536. Keine zweite neue 4-KiB-Reserve. Quelleninventare werden vollständig
gezählt, qualifizierte Softwaredateien bleiben gehashte installierte Voraussetzungen.

Neue Vorregistrierung, vollständiges Log, Metriken, Ergebnis und abschließendes
Ledger müssen gemeinsam innerhalb der 4.096 Byte bleiben. Die Ledgerzeilen
verwenden vorab benannte Spalten für jede tatsächlich geschriebene Laufdatei;
das ist eine verlustfreie tabellarische Darstellung, kein Weglassen von Dateien.
Bei Fehlern bleiben Logs vollständig, auch bei Überschreitung. Keine Korrektur
oder Wiederholung nach dem einmaligen Aufruf.

Gesamtlimit 4.194.304 Byte, gemeinsame Quellen-/NJ-/Formations-/Generationshülle
262.144 Byte. Verifikation und Rückgabebindungsprüfung sind zusätzliche Arbeit.
Für die Sitzungsprüfung: maximal 28 Rückgaben à 16.384 Byte pro Sitzung,
Vergleich ihrer gespeicherten kanonischen Bytes/Hashes, kein neuer Scan.
Hauptgates außerhalb neutraler Öffnungen False; ME/MI und Systemintegration
gesperrt, Prognosezweig ruhend. Der reale ereignisweise Aufruferlauf bleibt separat
freizugeben; ein Testpass allein ist keine allgemeine Dauerbetriebsfreigabe.
