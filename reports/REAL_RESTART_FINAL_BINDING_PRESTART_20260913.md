# Finale reale Laufbindung: gesonderter Vorabstand

Der Anschlussnachweis `media-restart-admission-qualification-20260913-02`
ist **12/12 QUALIFIED**, genau ein Testaufruf. Seine abgeschlossene Istbilanz
bleibt unverändert: Metadaten 91.490 Byte, Quellen 290.408 Byte, Gesamt
381.898 Byte. Einschließlich ungenutzter Primärfehlerreserve: Metadaten
99.682 Byte und Gesamt 390.090 Byte. Keine Grenzverletzung der Qualifikation.

## Davon getrennte Vorbereitung des realen Laufs

Der danach aufgerufene administrative Helfer `prepare_real()` in
`reports/qualify_media_restart_admission_once.py` hat vor Erstellung der
Laufbindung mit `REAL_ADMINISTRATIVE_BUDGET` angehalten. Keine Medienbytes
gelesen, keine Runtime gestartet, keine neue Qualifikation ausgeführt.

Die erste Ausgabe enthielt nur den Traceback. Die folgenden Zahlen wurden
anschließend durch eine ausdrücklich administrative Nachrechnung desselben
unveränderten Helfers aus den vorhandenen Dateien ermittelt; sie werden
nicht als zuvor gespeicherte Fehlerdetails ausgegeben:

| Beitrag | Byte |
| --- | ---: |
| Historische Nachweise, vollständige neue Qualifikationsablage und externe Fixturebelege | 91.490 |
| Geplante Laufbindung und Autorisierungsvorlage zusammen | 15.123 |
| Vollständige Prozesslogs, Reserve | 8.192 |
| Auswertung und Abschluss, Reserve | 8.192 |
| Primärfehler einschließlich temporärer Veröffentlichung, Reserve | 8.192 |
| Metadaten einschließlich Reserven | **131.189** |
| Unveränderte Metadatengrenze | **131.072** |

Überschreitung: **117 Byte**. Quellen und Zusatzhülle jeweils 290.408 Byte;
Gesamt einschließlich dieser Reserven 421.597 Byte. Keine native
Ergebnisgröße oder universelle Erfolgshülle wird damit vorhergesagt.

## Einordnung und kleinste offene Bindungsarbeit

Der Helfer übernimmt mit `OUT.rglob("*")` sämtliche neutralen Testfixtures
als neue aktive Laufreferenzen, nicht nur den qualifizierten Nachweis. Eine
Vertragsstelle, die gerade diese vollständige Archivübernahme für den
realen Lauf zwingend fordert, ist nicht belegt. Deshalb sind die 117 Byte
**keine nachgewiesene unvermeidbare Vertragsüberschreitung**. Es wurde weder
eine Grenze erhöht noch eine Pflichtdatei zur Entlastung entfernt.

Offen bleibt die ausdrückliche Zuordnung dieser neutralen Fixturedateien
zu Qualifikationsarchiv oder notwendigen realen Laufreferenzen. Die
Qualifikation selbst zählt weiterhin alle ihre Dateien vollständig.
Neue Code- oder Teständerungen wurden nach dem Testaufruf nicht vorgenommen.

Vorgesehene ID `media-restart-real-20260913-01` ist nicht verbraucht;
Ergebnis- und Bindungsverzeichnis fehlen weiterhin. Es gibt noch keinen
startbereiten Hauptlauf. Die reale Ausführungsfreigabe bleibt ausgesetzt.
Gates False; historische Dateien und die bestandenen Nachweise unverändert.
