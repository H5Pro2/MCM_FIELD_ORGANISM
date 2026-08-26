# 213ZV - G1-Realpfad-Inventur: statischer Freigabevorschlag

## Einordnung und Laufnummer

`213ZV` ist ein rein statischer Freigabevorschlag und kein Forschungslauf. Es wird daher keine Laufnummer vergeben. Mit der Erstellung dieses Dokuments wurden keine der 54 Realpfade abgefragt, kein Zielinhalt geoeffnet und kein Werkzeug ausgefuehrt.

## Forschungsfrage und Auftrag

Kann als naechste einzelne G1-Handlung eine streng read-only ausgefuehrte Metadateninventur der exakt 54 in der gebundenen Ausschlussmenge bezeichneten Realpfade zugelassen werden, ohne Zielinhalte zu lesen und ohne Manifest-, Resolver-, G2- oder Huerde-G-Arbeit vorwegzunehmen?

Beantragt wird exakt eine spaetere Handlung: **eine einmalige Metadateninventur der 54 gebundenen Realpfade**. Dieser Vorschlag selbst autorisiert und startet diese Handlung nicht.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der Freigabe fuer genau einen statischen Vorschlag;
- `docs/forschung/213ZU_G1_213ZT_ERGEBNIS_STATISCHE_ABNAHME.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- die drei abgenommenen Ergebnisdateien unter `reports/213ZR_g1_validation_success/`;
- die statisch gebundenen Dateien `tools/static_binary_evidence.py` und `tests/validate_static_binary_evidence.py`.

Keine externe Quelle wurde verwendet.

## Gebundener Werkzeugstand

Der abgenommene Werkzeugstand wird als Voraussetzung gebunden, aber fuer die beantragte Inventur nicht ausgefuehrt:

| Artefakt | Bytes | SHA-256 |
|---|---:|---|
| `tools/static_binary_evidence.py` | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |
| `tests/validate_static_binary_evidence.py` | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` |
| `reports/213ZR_g1_validation_success/syntax_validation.json` | 779 | `8A80EF10B8DB9BAC8F11347E152AA4DA52C7123E8F6B4CFD0BE01DD91087CEEA` |
| `reports/213ZR_g1_validation_success/synthetic_fixture_validation.json` | 24053 | `F0FBE63F23D0DF137D91F01C29084CE0238CFF661927F1723D6137E617C03DC9` |
| `reports/213ZR_g1_validation_success/validation_report.json` | 2184 | `EFBB12DAE271DB46D406613A0C99CE5C76DDA57ECC7F820B1D105A62A1AEC65A` |
| `docs/forschung/213ZU_G1_213ZT_ERGEBNIS_STATISCHE_ABNAHME.md` | 6318 | `017A679B2414F8BB4E52090A84E49736160C533B4861FA7C12996F28D1AFB916` |

Die Werkzeugvalidierung belegt Syntax und `21/21` synthetische Fixtures. Sie belegt weder Existenz noch Typ oder Inhalt eines Realpfads.

## Eingabe der beantragten Handlung

Einzige fachliche Eingabe ist:

- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`
- Groesse: `6253` Bytes
- SHA-256: `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF`
- erwartete Struktur: `schema`, `source_binding`, `expected_counts`, `entries`
- erwartete Anzahl: exakt `54` Eintraege, bestehend aus einer CPython-Rolle und 53 nativen Rollen

Nur die in `entries` enthaltenen kanonischen Pfadstrings duerfen spaeter als Inventurziele verwendet werden. Eine Erweiterung, Suche, Rekursion oder Ableitung weiterer Pfade ist unzulaessig.

## Exakt beantragte spaetere Handlung

Fuer jeden der 54 Eintraege darf genau einmal ausschliesslich Dateisystemmetadaten abgefragt werden:

- Ordinal und Rolle werden unveraendert aus der Eingabe uebernommen;
- kanonischer Pfadstring wird unveraendert aus der Eingabe uebernommen;
- `exists`: Existenzstatus;
- `item_type`: `file`, `directory`, `other` oder `missing`;
- `size_bytes`: nur fuer eine regulaere Datei, andernfalls `null`.

Nicht erlaubt sind Oeffnen oder Lesen des Zielinhalts, Ziel-Hashing, Signaturpruefung, Parsing, Laden, Ausfuehren, rekursive Verzeichnisabfrage oder das Folgen eines Pfads zu weiteren Zielen. Das validierte Python-Werkzeug und sein Controller bleiben waehrend dieser Handlung unausgefuehrt.

## Ausgaben

Bei vollstaendig erfolgreicher Inventur wird exakt eine finale JSON-Datei atomar ueber den gebundenen Stagingpfad publiziert:

| Zweck | kanonischer Pfad | UTF-8-Bytes | SHA-256 des Pfadstrings | Bestand bei Vorschlagserstellung |
|---|---|---:|---|---|
| final | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZV_g1_realpath_inventory.json` | 91 | `ECD777B801368AFD986906AB4C3C890D15CBF68D0B003E628109FC4D9BF6B2AA` | nein |
| staging | `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZV_g1_realpath_inventory.json.staging` | 100 | `A00F20901FB872365226B9995DF54C45D0A30B04C6BBF0C54A8735B4F628E2BE` | nein |

Die finale JSON-Datei muss mindestens enthalten:

- `schema` und `action: "metadata-only-realpath-inventory"`;
- die vollstaendige Bindung der Eingabedatei;
- `entry_count: 54` und genau 54 geordnete Ergebnisobjekte;
- Zaehler fuer `existing`, `missing`, `files`, `directories` und `other`;
- die Flags `content_opened: false`, `content_hashed: false`, `validated_tool_executed: false`, `manifest_generated: false`, `resolver_run: false`, `g2_touched: false` und `gate_g_touched: false`.

Es gibt keine partielle Erfolgspublikation. Nach Erfolg oder Abbruch darf der Stagingpfad nicht vorhanden sein.

## Abbruchbedingungen

Die spaetere Handlung muss vor dem ersten Realpfadzugriff abbrechen, wenn:

- eine der oben gebundenen Voraussetzungen in Groesse oder SHA-256 abweicht;
- die Eingabe nicht exakt 54 geordnete Eintraege enthaelt;
- Pfade fehlen, leer sind oder als exakte beziehungsweise gross-/kleinschreibungsunabhaengige Duplikate auftreten;
- finaler Ausgabe- oder Stagingpfad bereits vorhanden ist;
- die vorgesehene Ausfuehrung mehr als die eine beantragte Metadateninventur umfasst.

Waehrend der Inventur muss ohne finale Publikation abgebrochen werden, sobald:

- ein Zugriff ausserhalb der exakt 54 gebundenen Pfade versucht wird;
- Zielinhalt geoeffnet, gelesen oder gehasht werden soll;
- das validierte Werkzeug oder der Controller gestartet werden soll;
- Manifest-, Resolver-, G2- oder Huerde-G-Arbeit beginnt;
- ein Metadatenzugriff keinen eindeutigen Ergebnisstatus liefert;
- die Ausgabe nicht exakt dem festgelegten Schema und den 54 Eingabeeintraegen entspricht.

Ein Wiederholungsversuch ist durch diesen Vorschlag nicht beantragt.

## Ausschlussgrenzen und Gegenbaseline

Ausgeschlossen bleiben Projektkontrolldateien ausser der gebundenen Ausschlussmenge, Zielinhalte, Inhalts-Hashes, Manifest-Erzeugung, Resolverlauf, G2 und Huerde G. Ebenso ausgeschlossen sind Kamera, Mikrofon, physische Sensorik und jegliche MCM-Feld- oder Memory-Auswertung.

Gegenbaseline ist der aktuelle Zustand: `54` Pfadbezeichnungen sind statisch gebunden, aber `0/54` Realpfade wurden in `213ZV` abgefragt. Die synthetische Werkzeugbaseline ist `21/21`; sie darf nicht als Realpfadbefund interpretiert werden.

## Erneute unabhaengige Abnahme

Vor jeder Ausfuehrungsfreigabe ist dieser Vorschlag unabhaengig statisch abzunehmen. Nach einer spaeter separat freigegebenen Inventur ist die finale JSON-Datei erneut unabhaengig statisch zu pruefen auf:

- Eingabe-, Ausgabe- und Pfadstringbindungen;
- exakt 54 geordnete Ergebnisse und konsistente Zaehler;
- ausschliesslich die erlaubten Metadatenfelder;
- finale Publikation exakt `1`, partielle Publikation `0`;
- Abwesenheit des Stagingpfads;
- alle Ausschlussflags `false`;
- keine Aussage ueber Zielinhalte, G1-Binaerevidenz oder MCM-Funktionen.

## Messergebnisse und konkrete Schlussfolgerung

**Beobachtet:** Die Ausschlussmenge enthaelt 54 Eintraege. Der gebundene Werkzeugstand ist fuer Syntax und 21 synthetische Fixtures abgenommen. Beide neu gebundenen Ausgabepfade waren bei Vorschlagserstellung nicht vorhanden. In `213ZV` wurden keine Realpfade abgefragt.

**Technische Interpretation:** Eine Metadateninventur ist die kleinste kontrollierbare naechste G1-Stufe, weil sie nur die spaetere Existenz- und Typgrundlage erhebt und weder Binaerinhalte noch Resolverentscheidungen vorwegnimmt.

**Nicht gepruefte Annahme:** Es ist offen, wie viele der 54 Realpfade existieren und regulaere Dateien sind.

**Schlussfolgerung:** Beantragt wird ausschliesslich die einmalige read-only Metadateninventur nach den vorstehenden Bindungen. Daraus folgt kein MCM-Forschungsbefund und keine Aussage zu Memory, Feldorganisation, Semantik oder KI. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer die naechste begrenzte Forschung und Entwicklung

Naechster Schritt ist die unabhaengige statische Abnahme von `213ZV`. Erst nach ausdruecklicher Freigabe darf die hier exakt definierte einzelne Metadateninventur ausgefuehrt werden; Manifest, Resolver, G2 und Huerde G bleiben danach weiterhin gesondert freigabepflichtig.
