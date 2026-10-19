# S2-SP-Ausführungsbindung

Auftragskennung: `S2SP-SHIFT-HINT-20260919-01`  
Geplante Lauf-ID: `s2sp-shift-hint-real-20260919-01`

## Gegenstand und Grenze

Der Lauf prüft ausschließlich private, read-only Hinweise auf eine sichtbare
Teilstruktur bei einem festen horizontalen Versatz von einer vollständigen
Zelle (`-1`, `0`, `+1`). Es erfolgt keine Memory-, Feld- oder
Hypothesenverarbeitung. Ein einzelner Hinweis bedeutet nur, dass die zehn
vollständig sichtbaren Zellen über den gesamten zulässigen Überlappungsbereich
gleich sind. Er bedeutet keine Identität einer gesamten Wahrnehmung und keine
öffentliche Zulassung.

Der historische Exaktvergleich der ersten 32 sichtbaren Werte bleibt getrennt
und unverändert. Die zwei unvollständigen Werte der elften Zelle sowie alle
verdeckt liegenden Werte sind nicht Teil der Versatzprüfung.

## Gebundene Quellen und Bedingungen

Die Quelle wird als reines 12-zelliges RGB-Rezept in der obersten Rasterzeile
erzeugt. Jeder Rezeptoraufruf erhält ein eigenes Frame mit `1920 x 1080` RGB-
Werten; nach der Analyse wird dieses Frame verworfen. Rohframes werden nicht
gespeichert.

| Technische Quelle | Gebundene Rolle nur für die Auswertung |
| --- | --- |
| `source-001` | Referenz |
| `source-002` | Verschiebung um eine Zelle |
| `source-003` | fremde Innenabweichung |
| `source-004` | Randabweichung außerhalb des Versatzüberlapps |
| `source-005` | widersprüchliche Innenabweichung |
| `source-006` | uniforme Reihe |

Die fünf vorgebundenen Vergleiche sind: gleiche Position, einzelne
Verschiebung gegen Referenz und Fremdquelle, Randmehrdeutigkeit gegen zwei
Kandidaten, widersprüchliche Quelle gegen Referenz und uniforme
Offsetmehrdeutigkeit. Rollen werden nicht an den Vergleichskern übergeben.

## Qualifikation

Ein neutraler Aufruf wurde bereits einmal ausgeführt: `6/6` bestanden.
Ausgeführt wurde ausschließlich
`python -m unittest tests.test_s2sp_private_shift_hint -v`.

Das Inventar prüft eindeutigen Versatz ohne Exakttreffer, fremde
Innenabweichung, Kandidaten- und Offsetmehrdeutigkeit, Abschottung unvollständiger
und verdeckter Werte sowie fail-closed Eingabeformen. Es wiederholt keine
historischen Testserie.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2sp_private_shift_hint.py` | `cc16661dc16f75e5e59e077a739c7b7a608168d68aafe1cdb31071f04532ed36` |
| `tests/test_s2sp_private_shift_hint.py` | `d509c721fa77e430ca5a316f6ccf440558a3ad6a573d2503f1aeb4e3178538c7` |
| `reports/run_s2sp_shift_hint_once.py` | `fffe6461e45603a07fd5342d994fb8e2e32ef950d70c534fe152b0e0ccf41511` |
| `docs/S2SP_STATISCHER_PLAN_POSITIONSVARIATION_DURCH_MEMORY_UND_ABRUF.md` | `cb891e6045d773077d5b7073089cf7ec1f3c4c8e88a8bc2f77bc038d1192fa2e` |

## Ressourcenbindung

- sechs direkte visuelle Rezeptoranalysen;
- 1.728 gespeicherte Rezeptorwerte;
- fünf Vergleichsbedingungen;
- null Memory- und Feldkontakte;
- höchstens ein vollständiges RGB-Frame von 6.220.800 Byte im Arbeitsspeicher;
- keine Rohframeablage;
- `record.json` maximal 131.072 Byte, Verifikation 16.384 Byte, Auswertung
  16.384 Byte, Bilanz 8.192 Byte, Bericht 8.192 Byte;
- veröffentlichte Laufartefakte zusammen maximal 196.608 Byte.

Die unabhängige Verifikation rechnet die drei Offsetüberlappungen unmittelbar
aus den gespeicherten Werten neu und ruft den produktiven Vergleichskern nicht
erneut auf.
