# ULZ1: gebundener Start nach separater Einmalbeauftragung

**Aktualisierung: Einmalfreigabe VERBRAUCHT.** Der Forschungsdurchlauf ist
COMPLETE; der unten dokumentierte Start wurde genau einmal ausgeführt.
Nicht erneut starten. [Ergebnisbericht](../reports/s2uc/ulz1-assessment-20261004-01/REPORT.md).
Die folgenden Vorbereitungsanweisungen sind der historische Stand vor Ausführung.


Dieser Aufruf ist vorbereitet, nicht ausgeführt. Die Implementierung/neutrale
Qualifikation erteilt keine Freigabe für die Forschungsquellen.

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Reine Bindungsprüfung ohne Quellenmaterialisierung:

```powershell
C:/Python314/python.exe -m tools.s2uc_ulz1 check
```

Erst nach ausdrücklicher separater Einmalbeauftragung: Die dann gebundene
`S2UC_ULZ1_V1_20261004_AUTORISIERUNG_VORLAGE.json` als operative Datei
`S2UC_ULZ1_V1_20261004_AUTORISIERUNG.json` übernehmen und ausschließlich den
Status von `PENDING_SEPARATE_AUTHORIZATION` auf `AUTHORIZED_ONCE` setzen.
Keine Felder, Quellen, Masken, Budgets oder Zielpfade ändern.

Vorbereiteter Forschungsstart:

```powershell
C:/Python314/python.exe -m tools.s2uc_ulz1 run --authorization docs/S2UC_ULZ1_V1_20261004_AUTORISIERUNG.json
```

Festes exklusives Ziel: `reports/s2uc/ulz1-comparison-20261004-01`.
Genau 64 Quellen, 128 Arme, 1.040 Frames je Armgeschichte. Code, Runtime,
Quellenrezept, Masken, Bootstrap und Vorbereitung werden vor dem Worker geprüft.
Vorhandenes Ziel wird nicht überschrieben; Teilbestand oder Abbruch rechtfertigt
keinen Neustart. Auch ein gescheiterter Start wird mit Abschlussbeleg gesichert.

Vorstart-SHA256 und Ressourcenbefund stehen im
[Qualifikationsbericht](../reports/s2uc/ulz1-preparation-assessment-20261004-01/REPORT.md).
Die Forschungsabfolge wurde während der Vorbereitung nicht gezogen.

Archivformat der neutralen Qualifikation: ZIP/LZMA, mit normalisiertem Inhalt
der eingebetteten `*-case.json.gz`-Einträge (dort unkomprimiertes Fall-JSON).
`check` rekonstruiert diese gzip-Dateien mit der gebundenen Runtime und prüft
exakte Länge/SHA256 gegen die ursprünglichen neutralen Belege. Die ZIP-Einträge
sind deshalb nicht als direkt extrahierte gzip-Dateien zu verwenden. Die
unveränderten Originaldateien liegen außerdem im neutralen Qualifikationsordner.
Die Normalisierung ist verlustfrei und ermöglicht die 8-MiB-Vorbereitungsgrenze;
im eigentlichen Laufexport bleiben es reguläre gzip-Dateien.
