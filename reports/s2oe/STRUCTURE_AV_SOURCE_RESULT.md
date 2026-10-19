# Fünf-Ereignis-Eingang: Quellenbindung

`structure-av-source-binding-20260912-02`: **8/8** neue Quellen-, Cue- und
Zeitkontrollen in genau einem Testaufruf bestanden. Danach drei RGB-Quellen
einmal aus versiegelten Rezepten bereitgestellt und ein Cue aus q06 im selben
Puffer abgeleitet. Vorheriger Ordner -01 enthält nur Vorbereitung, keine
Tests oder Erzeugung. Keine historische Qualifikation wiederholt.

q04/q05/q06 stimmen bytegenau mit ihren historischen Payloadhashes überein.
Keine weiteren Hashgleichheiten zwischen den vier RGB-Dateien. q04 wird
einmal gespeichert, in zwei getrennten Manifestereignissen präsentiert.
OB-Audio unverändert gelesen und gegen den festgelegten Hash bestätigt.
Keine Rezeptor-, NJ-, Feld-, Memory- oder Distanzaufrufe.

Einmalige read-only Prüfung: Dateihashes, historische Quellenwurzeln,
Manifest und Zeitformen; Cuepixel unabhängig zeilenweise gegen q06 geprüft.
Keine Regeneration. Die Pixelprüfung wurde vor Speicherung des Prüfbelegs
erreicht; ihr zusätzlicher boolescher Ausweis steht nur in der Konsolenausgabe,
nicht in proof.json. Diese Einschränkung wird nicht rückwirkend korrigiert.

Manifestfolge unverändert q04/q04/q05/q06/q06-Cue. Aktuelles Softwareinventar
einschließlich transitiver OB-/OC-Abhängigkeiten in inventory.json gebunden;
Herkunftsrezepte und Präsentationszeiten getrennt. Quellenbindung ist keine
neue Runtimequalifikation. main_authorized bleibt false.

Vorregistrierung SHA-256:
`797b6a37d1ffad74eb7ce08f001f92a7601d8ca99c5d614e62ca648a309d35bf`.
Geprüfter Recorddigest:
`e22dc817b270d772faafe5282da95d8b806b0641982d6b4eca1214beeaae6d4f`.

## Bilanz und Grenze

Vorbindung: Quellenbelege 152.538 Byte; Metadaten 56.019;
gemeinsame Zusatzhülle 132.096; angesetzte Gesamthülle 1.421.995.
Alle angesetzten Grenzen eingehalten. Rohdateien sind separater Aufruferbestand:
24.902.400 Byte einschließlich Audio; geplante Lauflesemenge 31.180.800 Byte.
Tatsächlich: Manifest-/Quellenrecord 4.388 Byte, Inventar 12.442,
Vorregistrierung 3.652, Prüfbeleg 189, Qualifikationslog 849 Byte.

**Restlücken gesammelt:** Der Quellenrunner bindet noch keinen konkreten
funktionalen Einmaleinstieg oder dessen Auswerter. Seine gleich angesetzten
Erfolgs-/Fehlersummen sind Reservierungen, kein aus einem solchen Einstieg
abgeleiteter Nachweis möglicher gleichzeitiger Records/Präfixe/Temporärdateien.
Eine vollständige ausführbare Laufbilanz und aktuelle funktionale Zulassung
sind deshalb noch offen; die Zahl 1.421.995 darf nicht als abgeschlossene
Hauptlaufabsicherung verwendet werden. Erforderlich sind außerdem der
Vergleich tatsächlicher Konsolidierungskontakte/Prototypen mit dem Direktbeleg
und die getrennte Auswertung des read-only Abrufs einschließlich A-Konkurrenz.
Kein automatischer Folgelauf. Historische Belege und Regeln unverändert.
