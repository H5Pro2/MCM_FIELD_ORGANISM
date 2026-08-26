# 213ZM - Controllerkorrektur der expected_counts-Schluessel

## Einordnung

`213ZM` ist ein statisches Controllerkorrekturpaket und kein Forschungslauf. Es korrigiert ausschliesslich die zwei durch den kontrollierten Fruehstopp in `213ZL` identifizierten Schluesselzugriffe in `verify_exclusion`.

Es erfolgten keine Syntaxpruefung, kein Test, keine Controller- oder Werkzeugausfuehrung, kein Wiederholungsversuch und kein Zugriff auf einen der 54 Realpfade.

## Forschungsfrage und Auftrag

Kann der Controller exakt an die im gebundenen Ausschlussartefakt definierten `expected_counts`-Schluessel angepasst werden, ohne Rollenbezeichner, Ausschlusslogik oder andere Controllerteile zu veraendern?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213ZL_G1_KONTROLLIERTE_WERKZEUGVALIDIERUNG.md`,
- `reports/213ZH_g1_validation_error/validation_error.json`,
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`,
- `tests/validate_static_binary_evidence.py`.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

| Rolle | Pfad | Bindung vor Korrektur | Bindung nach Korrektur |
|---|---|---|---|
| Controller | `tests/validate_static_binary_evidence.py` | 34.044 Bytes; SHA-256 `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` | 34.044 Bytes; SHA-256 `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` |
| Ausschlussartefakt | `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | unveraendert | 6.253 Bytes; SHA-256 `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |
| Fehlerartefakt | `reports/213ZH_g1_validation_error/validation_error.json` | 2.024 Bytes; SHA-256 `3D053843BD60CC1F5094D11ADE2F6B1D0B5FC2E1A3778B0324E76B6DFF07939B` | unveraendert |

Verwendet wurden ausschliesslich statisches Textlesen, `apply_patch`, Dateigroesse, SHA-256 und Textsuche. Keine Python-Laufzeitschnittstelle wurde aufgerufen.

## Durchgefuehrte Schritte

In `verify_exclusion` wurde genau eine Quellzeile mit genau zwei Stringliteralen geaendert:

```text
counts.get("cpython-binary")  -> counts.get("cpython_binary")
counts.get("native-candidate") -> counts.get("native_candidate")
```

Der dritte Zugriff `counts.get("total")` blieb unveraendert. Alle anderen Controllerzeilen blieben unveraendert.

Die Rollenbezeichner der Eintragsliste bleiben absichtlich:

- `cpython-binary`,
- `native-candidate`.

Diese Rollenwerte sind von den Schluesseln im Objekt `expected_counts` zu unterscheiden. Das gebundene Artefakt verwendet Unterstriche fuer die Zaehlschluessel und Bindestriche fuer die Rollenwerte.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Soll | Beobachtet | Ergebnis |
|---|---|---|---|
| Geaenderte `expected_counts`-Literale | 2 | 2 | bestanden |
| `cpython_binary`-Zugriff | vorhanden | Zeile 125 | bestanden |
| `native_candidate`-Zugriff | vorhanden | Zeile 125 | bestanden |
| `total`-Zugriff | unveraendert | Zeile 125 | bestanden |
| Rollenliterale mit Bindestrich | unveraendert | Zeilen 131 und 141 | bestanden |
| Dateigroesse | 34.044 Bytes | 34.044 Bytes | bestanden |
| Neue SHA-256-Bindung | eindeutig | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | bestanden |
| Syntax/Test/Ausfuehrung | 0 | 0 | bestanden |

Gegenbaseline ist die alte Controllerbindung mit den zwei Bindestrichzugriffen, die in `213ZL` beobachtet zum Stopp `EXCLUSION_BINDING_MISMATCH` fuehrte. Diese beiden Zugriffe sind in der neuen Bindung nicht mehr vorhanden. Die Rollenbezeichner mit Bindestrichen sind keine Gegenbaseline und wurden nicht veraendert.

## Grenzen und nicht gepruefte Annahmen

- Die Python-Syntax wurde nicht geprueft.
- Die Ausschlusspruefung wurde nicht erneut ausgefuehrt.
- Syntaxanalyse und 21 synthetische Faelle besitzen weiterhin kein bestandenes Laufresultat.
- Die neue Controllerbindung ist noch nicht unabhaengig statisch abgenommen.
- Der belegte Fehlerordner aus `213ZL` darf nicht wiederverwendet oder entfernt werden.
- Fuer jeden spaeteren Versuch sind vollstaendig neue Temp-, Erfolgs-, Fehler- und abgeleitete Stagingpfade erforderlich.
- Die 54 Realpfade wurden nicht geoeffnet oder auf Existenz geprueft.
- Es erfolgte keine Manifest-, Resolver-, G2- oder Huerde-G-Arbeit.
- Aus der Korrektur folgt kein G1- oder MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

Die zwei freigegebenen `expected_counts`-Schluesselzugriffe wurden exakt korrigiert und der Controller neu bytegebunden. Es wurde keine weitere Controllerlogik veraendert und keine Validierung wiederholt.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes ist genau eine unabhaengige statische Abnahme der neuen Controllerbindung gegen `213ZL` und das gebundene Ausschlussartefakt vorzunehmen. Zu pruefen sind ausschliesslich die beiden Unterstrichschluessel, die unveraenderten Rollenliterale, die neue Bytebindung und das Ausbleiben weiterer Quelltextaenderungen.

Erst nach dieser Abnahme darf eine neue statische Ausfuehrungsvorregistrierung mit vollstaendig neuen, bisher nicht verwendeten Temp-, Erfolgs-, Fehler- und Stagingpfaden vorgeschlagen werden. Wiederholung, Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Zugriff auf die 54 Realpfade, Manifest-, Resolver-, G2- und Huerde-G-Arbeit bleiben bis dahin gesperrt.
