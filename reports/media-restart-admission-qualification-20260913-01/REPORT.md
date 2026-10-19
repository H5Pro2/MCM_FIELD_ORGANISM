# Reale Zulassungsanbindung: Vorabstopp

**PRESTART_BLOCKED, null Testaufrufe.** Die Kennung bezeichnet eine
Qualifikationsvorbereitung, keine ausgeführte Qualifikation. Kein Zugriff
auf die ausgewählte MP4, keine Rezeptor-/Memory-/Feldausführung. Gates wurden
nicht geöffnet. Die reale Einmallauffreigabe bleibt ausgesetzt.

## Implementierter, noch unqualifizierter Entwurf

`tools/_media_restart_admission.py` enthält eine gemeinsame versionierte
Prüfung für beide bisherigen Sperrstellen. Der Realmodus bindet den exakt
ausgewählten Pfad, vollständigen SHA-256, 83.498.438 Byte, FULL-Manifest,
Profil, Codebindung, Lauf-ID und ausdrückliche Autorisierung. Die bisherige
Neutralzulassung bleibt getrennt. Keine Downloads-Verzeichnisfreigabe.

`Player._authorize()` und `Session.__init__()` rufen diese Prüfung vor
Runtime-/Decoderinitialisierung auf. Der unveränderte `CountedFile` prüft
später die tatsächlichen Dateibytes vor dem Decodieren und zählt Hashlesen
auch bei einem anschließenden Hashfehler zum Arbeitsbudget.

`reports/run_selected_media_restart_once.py` ist der neue Dateieinstiegsentwurf:
Referenzprozess, Suspend-19-Prozess, frischer Restoreprozess; ein Verifikator-
und anschließender Auswertungsaufruf, keine automatische Autorisierung.
Dieser Einstieg ist **nicht startbereit und nicht qualifiziert**.

Zwölf Prüfgruppen sind in `tests/test_media_restart_real_admission.py`
vorbereitet: unveränderliche Zulassung, Quellenfelder, Profil/Lauf/Manifest/
Code, Autorisierung/Modus, Neutralbedingungen, reale Player-Sitzungsübergabe,
Dateibindung, Abweisung vor Start, Prozessrollen und einmalige Verifikation,
Hash-Lesekonto, beide Prüforte über den Dateieinstieg sowie Primärfehler.
Die ausgewählte MP4 wäre in jedem Test mit einer Lesesperre geschützt.
Ein Bestehen wird ausdrücklich nicht behauptet.

## Erste vollständige Vorrechnung des Entwurfs

| Klasse | Prospektive Belegung | Grenze | Überschreitung |
| --- | ---: | ---: | ---: |
| Metadaten einschließlich Reserven | 145.722 | 131.072 | 14.650 |
| Quellen | 1.919.275 | 327.680 | 1.591.595 |
| Gemeinsame Zusatzhülle | 1.919.275 | 393.216 | 1.526.059 |
| Gesamt einschließlich Reserven | 2.064.997 | 4.194.304 | keine |

Metadaten vor Zukunfts-/Fehlerreserven: 104.762 Byte. Diese Vorrechnung
enthält beide Veröffentlichungskopien der Vorregistrierung und 24.576 Byte
für alle neutralen Fixtures. Hinzu kommen 8.192 Byte Logs, 24.576 Byte
Abschluss und 8.192 Byte Primärfehlerreserve. Das sind prospektive Beträge,
keine gemessenen Testausgaben. Die jetzt nachträglich dokumentierenden
Vorabstoppdateien sind darin nicht rückwirkend als enthalten behauptet;
es existiert keine tragfähige finale Qualifikations- oder Laufbilanz.

**Wichtiger Unterschied zur bisherigen Rechnung:** Der neue Entwurf zählt
alle 118 Dateien des geerbten Codeinventars als physische Quellenbelege.
Die -05-Bindung unterscheidet hingegen vollständiges Hashinventar und die
wesentlich kleinere Liste tatsächlich berechneter `external`-Quellen.
Die 1.919.275 Byte sind deshalb kein nachgewiesener Mindestbedarf der kleinen
Zulassungserweiterung, sondern der Betrag dieser weiter gefassten Rechnung.
Die fehlende explizite Zuordnung des geerbten Inventars zur aktiven
Belegklasse wird nicht durch stillschweigendes Weglassen behoben.

## Verbleibende Korrektur und Grenzen

Vor dem einzigen Testaufruf muss die aktive Quellenbilanz konsistent zur
bisherigen Ledger-/Abhängigkeitsgrenze zugeordnet werden: welche Dateien
physisch erforderliche Laufbelege sind und welche unverändert installierte,
vollständig hashgeprüfte Basis darstellen. Alle neuen Anschluss-, Test- und
Aufrufdateien sind erforderlich. Ebenso muss die konkrete vollständige
Qualifikationshülle innerhalb der Metadatengrenze liegen. Keine Grenzerhöhung
und keine neue Verpackung wurden vorgenommen.

Das vollständige Inventar und der Quellenstand dieser Vorrechnung stehen in
`PRESTART.json`. HEAD: `537109994cf777f8d36cda617aafe12226806c25`, bestehender
schmutziger Arbeitsbaum. Historische Dateien bleiben unverändert.

Die acht -05-Prüfungen wurden nicht wiederholt. Work-/Decoder-, Codec-,
Serialisierungs- und Ledgerdateien blieben unverändert; deren historischen
Befunde bleiben erhalten. Die geänderten Zulassungsstellen und der neue
Dateieinstieg haben noch keinen Anschlussnachweis. Keine neue reale
Lauf-ID oder finale Ausführungsbindung ist freigegeben/verbrauchbar erzeugt.
