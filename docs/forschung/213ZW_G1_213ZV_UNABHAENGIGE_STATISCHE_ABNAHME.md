# 213ZW - Unabhaengige statische Abnahme von 213ZV

## Einordnung und Laufnummer

`213ZW` ist eine statische Abnahme und kein Forschungslauf. Es wird keine Laufnummer vergeben. Die in `213ZV` vorgeschlagene Metadateninventur wurde nicht ausgefuehrt.

## Forschungsfrage und Auftrag

Zu pruefen war, ob `213ZV` den abgenommenen Werkzeugstand, die 54er-Ausschlussmenge, genau eine spaetere read-only Metadateninventur, frische Ausgabepfade, Ausgabeschema, Abbruchbedingungen, Ausschluesse und Folgeabnahme konsistent bindet.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZV_G1_REALPFAD_INVENTUR_FREIGABEVORSCHLAG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `tools/static_binary_evidence.py`;
- `tests/validate_static_binary_evidence.py`;
- `reports/213ZR_g1_validation_success/syntax_validation.json`;
- `reports/213ZR_g1_validation_success/synthetic_fixture_validation.json`;
- `reports/213ZR_g1_validation_success/validation_report.json`;
- `docs/forschung/213ZU_G1_213ZT_ERGEBNIS_STATISCHE_ABNAHME.md`.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Es wurden ausschliesslich statische Dateilese-, JSON-Parse-, Groessen-, SHA-256-, Textsuch- und Pfadstringpruefungen verwendet. Keiner der 54 in der Ausschlussmenge bezeichneten Realpfade wurde auf Existenz geprueft oder geoeffnet.

## Durchgefuehrte Schritte

1. Groesse und SHA-256 aller von `213ZV` gebundenen Werkzeug- und Validierungsartefakte wurden neu ermittelt.
2. Die Ausschlussmenge wurde als JSON geparst; Anzahl, erwartete Rollenverteilung, leere Pfade und case-insensitive Duplikate wurden geprueft.
3. Syntax- und Fixture-Ergebnisse sowie der zusammenfassende Validierungsbericht wurden strukturiert gelesen.
4. Die Definition der einen spaeteren Handlung, Ausgabepfade, Schemafelder, Abbruchbedingungen, Ausschluesse und Folgeabnahme wurden direkt im Text von `213ZV` geprueft.
5. Nur die beiden vorgesehenen Ausgabe- und Stagingpfade wurden auf Frische geprueft. Dies sind keine Realpfade der 54er-Ausschlussmenge.

## Messergebnisse und Gegenbaselines

### Bindungen

| Artefakt | Bytes | SHA-256 | Ergebnis |
|---|---:|---|---|
| `213ZV_G1_REALPFAD_INVENTUR_FREIGABEVORSCHLAG.md` | 8538 | `245743D80ECF4B2D71E815CB92C5823C0DE847B992F6DCEF181E2131C91173E6` | konsistent |
| `213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` | konsistent |
| `tools/static_binary_evidence.py` | 42225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` | konsistent |
| `tests/validate_static_binary_evidence.py` | 34044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | konsistent |
| `syntax_validation.json` | 779 | `8A80EF10B8DB9BAC8F11347E152AA4DA52C7123E8F6B4CFD0BE01DD91087CEEA` | konsistent |
| `synthetic_fixture_validation.json` | 24053 | `F0FBE63F23D0DF137D91F01C29084CE0238CFF661927F1723D6137E617C03DC9` | konsistent |
| `validation_report.json` | 2184 | `EFBB12DAE271DB46D406613A0C99CE5C76DDA57ECC7F820B1D105A62A1AEC65A` | konsistent |
| `213ZU_G1_213ZT_ERGEBNIS_STATISCHE_ABNAHME.md` | 6318 | `017A679B2414F8BB4E52090A84E49736160C533B4861FA7C12996F28D1AFB916` | konsistent |

### Struktur und Grenzen

- Ausschlussmenge: exakt `54` Eintraege.
- Rollenverteilung: `1` CPython-Binaerrolle und `53` native Kandidatenrollen.
- Leere Pfadstrings: `0`.
- Case-insensitive Pfadduplikate: `0`.
- Syntaxparse: bestanden; Werkzeugmodul nicht ausgefuehrt; kein Bytecode erzeugt.
- Synthetische Fixtures: `21/21` bestanden, `0` fehlgeschlagen.
- Validierung: ein Controllerprozess, Erfolgspublikation `1`, Fehlerpublikation `0`.
- Validierungsausschluesse: Realziel geoeffnet `false`, Projektkontrolldatei geoeffnet `false`, Manifest erzeugt `false`, Resolver ausgefuehrt `false`, G2 beruehrt `false`.
- Finaler Inventurpfad bei Abnahme vorhanden: nein.
- Stagingpfad bei Abnahme vorhanden: nein.
- Realpfadzugriffe in `213ZW`: `0/54`.

Die Gegenbaseline bleibt damit der statische Zustand ohne Realpfadbefund. Die `21/21` synthetischen Fixtures sind nur Werkzeugbaseline und keine Evidenz ueber die 54 Ziele.

## Einzelhandlung, Schema und Abbruchbedingungen

`213ZV` beantragt eindeutig genau eine spaetere Handlung: eine einmalige read-only Metadateninventur der 54 gebundenen Pfade. Zulaessig sind nur Existenzstatus, Objekttyp und gegebenenfalls Dateigroesse. Inhaltslesen, Inhalts-Hashing, Werkzeug- oder Controllerstart, rekursive Suche und Pfaderweiterung sind ausgeschlossen.

Die finale JSON-Ausgabe und ihr Stagingpfad sind kanonisch, als Pfadstrings mit UTF-8-Laenge und SHA-256 gebunden und frisch. Das Ausgabeschema verlangt exakt 54 geordnete Ergebnisse, konsistente Zaehler sowie ausdrueckliche Ausschlussflags. Partielle Erfolgspublikation und Wiederholungsversuch sind nicht vorgesehen.

Die Abbruchbedingungen decken Bindungsabweichungen, falsche Anzahl, leere oder doppelte Pfade, vorbestehende Ausgaben, Umfangserweiterung, Zugriff ausserhalb der Liste, Inhaltszugriff, Werkzeugstart, Manifest, Resolver, G2, Huerde G, uneindeutige Metadaten und Schemaabweichung ab. Eine erneute unabhaengige statische Abnahme nach einer spaeter separat freigegebenen Inventur ist festgelegt.

## Grenzen und nicht gepruefte Annahmen

Nicht geprueft wurden Existenz, Typ, Groesse oder Inhalt der 54 Realziele. Es wurde kein Manifest erzeugt, kein Resolver ausgefuehrt, G2 nicht beruehrt und Huerde G nicht bearbeitet. Die Metadateninventur selbst ist durch den Auftrag zu `213ZW` nicht freigegeben.

Es folgt keine Aussage zu G1-Binaerevidenz, Memory, Feldorganisation, Semantik oder KI.

## Konkrete Schlussfolgerung

`213ZV` besteht die unabhaengige statische Abnahme. Alle geforderten Bindungen und Grenzen sind konsistent, die eine spaetere Handlung ist eindeutig, und beide vorgesehenen Ausgabepfade sind frisch. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer die naechste begrenzte Forschung und Entwicklung

Als naechster Schritt sollte genau die in `213ZV` definierte einmalige read-only Metadateninventur separat zur Ausfuehrung freigegeben werden. Vor dem ersten Realpfadzugriff sind alle Bindungen und die Frische beider Ausgabepfade erneut zu pruefen. Manifest, Resolver, G2 und Huerde G bleiben ausgeschlossen.
