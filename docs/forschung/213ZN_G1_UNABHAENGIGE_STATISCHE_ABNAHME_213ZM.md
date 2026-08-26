# 213ZN - Unabhaengige statische Abnahme von 213ZM

## Einordnung

`213ZN` ist eine statische Abnahme und kein Forschungslauf. Geprueft wurde ausschliesslich die Zweischluesselkorrektur aus `213ZM` gegen die alte und neue Controllerbindung, den Fruehstopp aus `213ZL` und das gebundene Ausschlussartefakt.

Es erfolgten keine Syntaxpruefung, kein Test, keine Controller- oder Werkzeugausfuehrung, kein Wiederholungsversuch und kein Zugriff auf einen der 54 Realpfade.

## Forschungsfrage und Auftrag

Enthaelt die neue Controllerbindung exakt die zwei freigegebenen Aenderungen von Bindestrich- zu Unterstrichschluesseln in `expected_counts`, waehrend die Rollenwerte mit Bindestrichen und alle uebrigen Controllerbytes unveraendert bleiben?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang,
- `docs/forschung/213ZL_G1_KONTROLLIERTE_WERKZEUGVALIDIERUNG.md`,
- `docs/forschung/213ZM_G1_CONTROLLER_EXPECTED_COUNTS_SCHLUESSELKORREKTUR.md`,
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`,
- `tests/validate_static_binary_evidence.py`.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

| Rolle | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| Neue Controllerbindung | `tests/validate_static_binary_evidence.py` | 34.044 | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` |
| Korrekturdokument | `docs/forschung/213ZM_G1_CONTROLLER_EXPECTED_COUNTS_SCHLUESSELKORREKTUR.md` | 5.439 | `01EE9932886DBF5E077E0736C4E006DA9831AA3CA80A32E7B7865379FE1B0329` |
| Ausschlussartefakt | `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json` | 6.253 | `52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF` |

Als statische Schnittstellen wurden Rohbyte-Lesen, UTF-8-Dekodierung, Textsuche, rein speicherinterner Ruecktausch der zwei Literale, Dateigroesse und SHA-256 verwendet. Es wurde keine Datei fuer den Ruecktausch erzeugt und keine Python-Laufzeitschnittstelle aufgerufen.

## Durchgefuehrte Schritte

1. Groesse und SHA-256 der neuen Controllerdatei wurden neu bestimmt.
2. Vorkommen der zwei neuen und zwei alten `counts.get`-Ausdruecke wurden gezaehlt.
3. Die Zeilen mit `expected_counts`-Zugriffen und Rollenwerten wurden statisch gelesen.
4. Im Speicher wurden ausschliesslich
   `counts.get("cpython_binary")` und
   `counts.get("native_candidate")`
   auf ihre alten Bindestrichformen zurueckgetauscht.
5. Groesse und SHA-256 dieser rekonstruierten Bytefolge wurden mit der alten Controllerbindung verglichen.

Der speicherinterne Ruecktausch ist keine Syntaxpruefung und keine Controllerausfuehrung. Er dient ausschliesslich dem bytegenauen Nachweis des Aenderungsumfangs.

## Messergebnisse und Gegenbaselines

| Pruefpunkt | Soll | Beobachtet | Ergebnis |
|---|---|---|---|
| Neue Controllergroesse | 34.044 Bytes | 34.044 Bytes | bestanden |
| Neue Controller-SHA-256 | `433B...A88D` | `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` | bestanden |
| `counts.get("cpython_binary")` | genau 1 | 1 | bestanden |
| `counts.get("native_candidate")` | genau 1 | 1 | bestanden |
| `counts.get("cpython-binary")` | 0 | 0 | bestanden |
| `counts.get("native-candidate")` | 0 | 0 | bestanden |
| Rollenwert `cpython-binary` | unveraendert | Zeilen 131 und 141 | bestanden |
| Rollenwert `native-candidate` | unveraendert | Zeilen 131 und 141 | bestanden |
| Rekonstruierte alte Groesse | 34.044 Bytes | 34.044 Bytes | bestanden |
| Rekonstruierte alte SHA-256 | alte Bindung `76CF...E784` | `76CF80B8C62EB73DC9702ED54F364D513B171BC7BF3B61642D83C14EE497E784` | bestanden |
| Syntax/Test/Ausfuehrung | 0 | 0 | bestanden |

Der exakte Rueckgewinn der alten Bytebindung nach Ruecktausch nur dieser zwei Stringliterale weist nach, dass zwischen alter und neuer Controllerbindung keine weitere Byteaenderung vorliegt.

Gegenbaseline sind die zwei alten Bindestrichzugriffe, die in `213ZL` den Stopp `EXCLUSION_BINDING_MISMATCH` ausloesten. Sie kommen in der neuen Controllerbindung nicht mehr vor. Die weiterhin korrekten Rollenwerte mit Bindestrichen wurden nicht als Fehler behandelt und blieben erhalten.

Gesamtergebnis: **Zweischluesselkorrektur statisch bestanden; exakt zwei Stringliterale geaendert, keine sonstige Controllererweiterung**.

## Grenzen und nicht gepruefte Annahmen

- Die Python-Syntax wurde nicht geprueft.
- Die korrigierte Ausschlusspruefung wurde nicht ausgefuehrt.
- Syntaxanalyse und 21 synthetische Faelle besitzen weiterhin kein bestandenes Laufresultat.
- Der fruehere Fehlerordner bleibt belegt und darf nicht wiederverwendet oder entfernt werden.
- Fuer einen spaeteren Versuch existiert noch keine neue Ausfuehrungsvorregistrierung und keine neue CLI-Bindung.
- Die 54 Realpfade wurden nicht geoeffnet oder auf Existenz geprueft.
- Es erfolgte keine Manifest-, Resolver-, G2- oder Huerde-G-Arbeit.
- Aus dieser statischen Abnahme folgt kein G1- oder MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

Die neue Controllerbindung schliesst den in `213ZL` beobachteten Zweischluesselfehler statisch und bleibt exakt auf die freigegebene Aenderung begrenzt. Die Abnahme der Korrektur ist bestanden.

Dies ist keine Wiederholungs- oder Ausfuehrungsfreigabe. G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt. Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes sollte genau eine neue statische Ausfuehrungsvorregistrierung erstellt werden. Sie muss die neue Controllerbindung `433B6EA8695B6C7B6FCC2C583C7125606B00567900802F2871DA305932D1A88D` und einen vollstaendig neuen Satz bisher nicht verwendeter Temp-, Erfolgs-, Fehler- und abgeleiteter Stagingpfade binden. Der alte Fehlerordner und alle Zielnamen aus `213ZH` bis `213ZL` bleiben unberuehrt.

Danach ist erneut eine unabhaengige statische Abnahme erforderlich. Wiederholung, Syntaxpruefung, Tests, Controller- oder Werkzeugausfuehrung, Zugriff auf die 54 Realpfade, Manifest-, Resolver-, G2- und Huerde-G-Arbeit bleiben bis zu einer gesonderten Freigabe gesperrt.
