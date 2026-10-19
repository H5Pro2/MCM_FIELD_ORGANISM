# Gebundene unmittelbare visuelle Kontrolle – noch nicht ausführen

Vorgesehene unbenutzte Lauf-ID: `immediate-visual-retrieval-20260912-01`.
Ergebnisverzeichnis `reports/s2oe/immediate-visual-retrieval-20260912-01`
war bei der Vorbindung nicht vorhanden. Diese Abwesenheit muss unmittelbar
vor einem später freigegebenen Start erneut gelten.

Operative Bindung: `manifest.json`, 18.563 Byte, SHA-256
`d4d83021d733634335131307492072f6b8fd25c2cfaf2608d12635105d9416af`.
Sie enthält 107 aktuelle Code-/Dateibindungen und 25 aktive Belegreferenzen.
Identische physische Referenzen zählen einmal; tatsächliche Zugriffe separat.

Elternrecord unverändert: 1.359.778 Byte, SHA-256
`4da6485b12ce98dca625fe5998130d1f2c0f9225d78a0fefb9c4bcf18298f3e7`.
Es wird ausschließlich der vollständig gebundene e03-Eingang verwendet:
48 gespeicherte Halbwerte und 288 visuelle Werte. Keine Decoder-, Rezeptor-
oder NJ-Ausführung. Geplant sind drei vollständige Elternlesezugriffe,
zusammen 4.079.334 Byte, nicht drei physische Eingangsablagen.

## Unveränderte Folge

Leerhinweis → eine reguläre AV-Formation → unmittelbarer read-only Wiederhinweis.
Historische Herkunft bleibt erhalten. Die neue Präsentation verwendet die
qualifizierten nativen Videozeiten [9,10), [14,15), [15,16) mit getrennten
Sitzungszeiten. Vier öffentliche Scans einschließlich Direktbaseline;
anschließend einmal unabhängige Gesamtverifikation und nur danach Auswertung.
Erwartet werden ABSTAIN_NO_CONTEXT und ADMIT_SINGLE_CONTEXT. Diese Erwartungen
sind keine technischen Start- oder Verifikationsbedingungen.

Prüfdeckung: historische 22/22 Präsentation, 7/7 Gesamtverifikation und neue
4/4 Abschlussanschlüsse. Drei getrennte Prüfstände, kein behaupteter 33-Testlauf.
Die aktuelle Inventarisierung bindet die neuen Fortschritts- und Abschluss-
Quellen ausdrücklich; historische Quellhashes werden nicht überschrieben.

## Gemeinsame Vorbilanz

| Alternative | Metadaten | Gesamt |
| --- | ---: | ---: |
| Erfolg | 57.130 | 1.936.942 |
| Fehler vor Recordpublikation | 55.077 | 1.926.697 |
| Fehler nach Recordpublikation | 63.274 | 1.943.086 |
| Zusätzlicher Fehler nach vorhandenem Closebeleg | **65.322** | **1.945.134** |

Grenzen: Metadaten **65.536**, Gesamt **4.194.304**. Die größere
Qualifikationsmetadatengrenze wird nicht für den realen Lauf verwendet.
Quellenreferenzen 35.678 / 174.080, historische Eingangsdatei
1.359.778 / 2.097.152; Verifikationsbelege einschließlich reserviertem
neuem Nachweis höchstens 91.140 / 262.144 Byte. Sämtliche aktiven
Qualifikationsdateien einschließlich des neutralen Verifikationsrecords
sind enthalten. Letzterer ist Verifikationsbeleg, kein operativer Cueeingang.

Erfolg und Fehler sind alternative Ablagen. Ein gegebenenfalls bereits
vorhandener Record oder Closebeleg verschwindet bei späterem Fehler nicht
aus der Bilanz. Der Istledger zählt seine eigene tatsächliche Dateigröße.
Es bleiben nur 214 Byte Reserve zur konservativen letzten Metadatengrenze;
keine weiteren aktiven Pflichtdateien ohne erneute Bilanz hinzufügen.

`preflight.json` dokumentiert die Rechnung. Diese Anleitung und die statische
Rechnung sind Planungsdokumente außerhalb der aktiven Laufabhängigkeiten;
der Einstieg liest sie nicht. Das operative Manifest und alle von ihm
benötigten Dateien sind vollständig mitgezählt. Ein unvorhergesehen größeres
Fehlerprotokoll bleibt erhalten und wird als Budgetverletzung ausgewiesen,
nicht gekürzt. Die Reserve ist keine Garantie für beliebige externe Fehler.

## Startweg nach separater Einmallauffreigabe

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Dateieinstieg:

```powershell
C:/Python314/python.exe -m reports.run_immediate_visual_once --binding reports/s2oe/immediate-visual-retrieval-binding/manifest.json --authorized-once
```

Der Befehl ist dokumentiert, nicht ausgeführt. `--authorized-once` ist nur
nach ausdrücklicher Freigabe dieses gebundenen Laufs zulässig. Exklusive
Ergebnisablage verhindert Wiederanlauf; Gate wird im Prozess zurückgesetzt.
Keine zweite Verifikation außerhalb des Einstiegs aufrufen.

Aktueller Zustand: startbereit gebunden, **nicht zur Ausführung freigegeben**.
Alle Gates False, keine reale Kontrolle erfolgt.
