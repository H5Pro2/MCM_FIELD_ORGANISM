# UHR1 gebundener späterer Aufruf

Stand 2026-10-05. Dieses Dokument ist keine Forschungsfreigabe.
Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Runtime, Code, Rezept, Matrix und Qualifikation werden durch die zugehörige
Codebindung und Vorstartbindung eingefroren. U/H sind unverändert aus UH1.

Read-only Vorstartprüfung, ohne Forschungsquellen:

```powershell
C:/Python314/python.exe -m tools.s2uc_uhr1 check
```

Erst nach separater einmaliger Forschungsbeauftragung darf eine operative
`docs/S2UC_UHR1_V1_20261005_AUTORISIERUNG.json` entstehen. Sie muss exakt den
Feldern der Vorlage entsprechen, mit Status `AUTHORIZED_ONCE`; insbesondere
muss ihr Vorstart-SHA256 der abgenommenen Vorstartbindung entsprechen.
Die Vorlage mit Status `PENDING_SEPARATE_AUTHORIZATION` erlaubt keinen Start.

Exakter späterer Aufruf, heute nicht auszuführen:

```powershell
C:/Python314/python.exe -m tools.s2uc_uhr1 run --authorization docs/S2UC_UHR1_V1_20261005_AUTORISIERUNG.json
```

Exklusives Ziel: `reports/s2uc/uhr1-comparison-20261005-01`.
Der Start reserviert einen einmaligen Marker vor Materialisierung, erzeugt
und unabhängig prüft alle 64 Quellen, versiegelt das Manifest und beginnt
erst danach die 128 frischen U/H-Armläufe. Forschungsnamensraum
`MCM-UHR1/source/v1`; keine alte Forschungsquelle als Eingang.
Der Quellenhash entsteht erst innerhalb des autorisierten Versuchs.

3.600 s Gesamtfrist einschließlich Erzeugung/Prüfung, 3.540 s Workerfrist,
536.870.912 Byte gemeinsamer privater Windows-Job-Commit, 67.108.864 Byte
Gesamtexport mit allen Teilgrenzen des Prüfvertrags. Kein Retry, Resume,
Ersatzfall oder Wiederholen des neutralen Größenablaufs aus diesem Dokument.

Entwicklung: `prepare` erstellt die Code-/Runtimebindung und die unabhängig
geprüfte 320.000-Byte-Bootstrapmatrix; `qualify` führt Einzelprüfungen und nur
bei deren Erfolg den exklusiv reservierten einen neutralen Größenablauf aus.
`seal` versiegelt dessen verlustfrei rekonstruierbares Paket und die Vorstartbindung.
Diese Vorbereitungsschritte sind vom Entwicklungsauftrag gedeckt; sie erweitern
ihn nicht zur Forschungsfreigabe.
