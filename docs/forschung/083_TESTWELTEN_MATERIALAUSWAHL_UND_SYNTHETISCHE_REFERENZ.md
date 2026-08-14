# Testwelten: Materialauswahl und synthetische Referenz

## Auftrag und Grenze

Fuer weitere Weltkontakte sollen kontrollierte Testwelten und geeignetes
oeffentliches Videomaterial verwendet werden. Diese Vorbereitung bewertet nur
Quellen, Reproduzierbarkeit und den vorhandenen Rezeptorpfad. Sie dokumentiert
keine reale Kamera- oder Tk-Sichtpruefung und keine Memory-, Bedeutungs-,
Organisations- oder KI-Funktion.

## Ausgewaehlte Weltfamilie

Die Materialrangfolge lautet:

1. Die vorhandene prozedurale Audio-Video-Welt bleibt die technische
   Referenz. Sie ist deterministisch, besitzt einen direkten synthetischen
   Rezeptoranschluss und erlaubt gleich lange Gegenbaselines.
2. `Street traffic.webm` bleibt die bevorzugte oeffentliche visuelle Welt. Die
   35-Sekunden-Originalrevision passt bereits zum vorhandenen 8-Hz-Pixelpfad
   und besitzt festgelegte Integritaetswerte.
3. `Traffic at dusk (time lapse).webm` ist eine kurze Ersatzquelle fuer einen
   getrennt vorregistrierten Lauf. Sie darf die erste Quelle nicht unter
   demselben Digest oder Laufvertrag ersetzen.
4. `City skyline (time lapse).webm` ist eine zweite kurze Ersatzquelle mit
   geringer Dateigroesse. Auch sie benoetigt einen eigenen Quellenvertrag.

YouTube-Seiten werden nur zur Herkunftsklaerung verwendet. Fuer reproduzierbare
Laeufe werden versionierte Originaldateien mit lokaler Groesse und Pruefsumme
benoetigt. Werbung, adaptive Streams, Empfehlungen, Untertitel und
Player-Oberflaechen duerfen nicht Teil des Rezeptoreingangs werden.

Die lokale Canvas-/Web-Audio-Welt bleibt eine aeussere Darstellungsbaseline.
Sie ist nicht mit dem synthetischen Rezeptorfeed gleichzusetzen.

## Ausgefuehrte synthetische Referenz

Aufruf:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python.exe tools\run_controlled_audio_video_test_world.py
```

Ergebnis:

| Welt | Dauer | Audioframes | Videoframes | Quellenstuetzungen | Felddigest |
| --- | ---: | ---: | ---: | ---: | --- |
| `world.reentry.same` | 3.0 s | 291 | 30 | 321 | `ad13b878ca4d1101eb93a500790ab26dd4679ef88b865c034d38953099e249e3` |
| `world.reentry.changed` | 3.0 s | 291 | 30 | 321 | `30a4d1169021c4abad87b0c65d03a1d76827f689d0e55ba85a0be112ce0dc06b` |

Beide Laeufe verwendeten 84 Neuronen, hielten keine rohen Sensorwerte und
schrieben nichts als Memory zurueck. Die unterschiedlichen Felddigests sind nur
eine gegenwaertige Feldreaktion auf unterschiedliche technische Weltverlaeufe.

## Verifikation

Die fokussierten Browserwelt-, synthetischen Audio-Video- und oeffentlichen
Videopfadtests ergaben:

```text
22 passed in 2.16s
```

Der Abruf der vorgesehenen Originaldatei `Street traffic.webm` scheiterte in
der Ausfuehrungsumgebung an der TLS-/Anmeldeinformationsschicht. Es wurde keine
Teil- oder Ersatzdatei angelegt. Deshalb wurde kein oeffentlicher Videolauf
ausgefuehrt und kein Lauf-106-Digest behauptet.

## Technische Eintrittskontrolle fuer oeffentliche Medien

Nach der Materialauswahl wurde eine observerseitige Integritaetskontrolle
umgesetzt:

- `mcm_field_organism/public_media_source_contract.py` beschreibt nur
  Quellenkennung, erwartete Dateigroesse und erwarteten SHA-1;
- `tools/audit_public_media_source.py` prueft eine lokale Datei, ohne sie zu
  decodieren;
- eine bestandene Integritaetspruefung erteilt ausdruecklich noch keine
  Rezeptorfreigabe;
- fehlende, anders grosse und bei gleicher Groesse byteveraenderte Quellen
  werden abgewiesen.

Fokussierter Testaufruf:

```powershell
$env:PYTHONPATH='.'
.\.venv\Scripts\python.exe -m pytest -q `
  tests\test_public_media_source_contract.py `
  tests\test_public_visual_world.py `
  tests\test_public_visual_temporal_map.py
```

Ergebnis:

```text
12 passed in 1.22s
```

Der Audit der aktuell erwarteten lokalen Datei ergab `file_present=false`,
`accepted=false` und `receptor_release_granted=false`. Dies ist ein technischer
Negativbefund zur Quellenverfuegbarkeit, kein Wahrnehmungs- oder Feldbefund.

Vor einer Verbindung des Audits mit dem visuellen Runner und vor jedem neuen
oeffentlichen Medienlauf ist diese Eintrittskontrolle dem MCM-Forschungspruefer
vorzulegen. Aus dem bestandenen Werkzeugtest wird keine Memory- oder
Organisationsaussage abgeleitet.

## Naechster ausfuehrbarer Medienlauf

Sobald die Originaldatei lokal vorliegt, sind vor jeder Feldverarbeitung exakt
zu pruefen:

- Dateigroesse: `26490572` Byte,
- SHA-1: `7f916030f14d84a65aa92077339f472897915fef`,
- Containerdauer: etwa `35.004` Sekunden,
- Aufloesung: `1920 x 1080`.

Danach darf nur der vorhandene visuelle Pfad mit 125 ms Abtastintervall und
35 Sekunden Hoechstdauer ausgefuehrt werden. Ein audiovisueller YouTube-Lauf,
eine Kamera-Rueckkehr oder Feldrueckschreibung ist damit nicht freigegeben.

## Tatsaechlich verwendete Quellen

- aktueller Benutzerauftrag,
- `docs/forschung/055_BROWSERBASIERTE_KUENSTLICHE_AUDIO_VIDEO_WELTVORLAGEN_LAUF_155.md`,
- `mcm_field_organism/browser_world_contract.py`,
- `mcm_field_organism/controlled_audio_video_test_world.py`,
- `mcm_field_organism/public_media_source_contract.py`,
- `tools/run_controlled_audio_video_test_world.py`,
- `tools/audit_public_media_source.py`,
- `tools/run_public_visual_world.py`,
- `tools/run_public_visual_temporal_map.py`,
- `sources/README.md`,
- Wikimedia Commons: `Street traffic.webm`,
  <https://commons.wikimedia.org/wiki/File:Street_traffic.webm>,
- Wikimedia Commons: `Traffic at dusk (time lapse).webm`,
  <https://commons.wikimedia.org/wiki/File:Traffic_at_dusk_(time_lapse).webm>,
- Wikimedia Commons: `City skyline (time lapse).webm`,
  <https://commons.wikimedia.org/wiki/File:City_skyline_(time_lapse).webm>.

Eine Zielabweichung ist nicht erkennbar: Die Auswahl legt keine Bedeutung,
Antwort oder gewuenschte Topologie fest und trennt externe Medien strikt von
synthetischer Rezeptoreinspeisung und menschlicher Sichtbeobachtung.
