# 213ZE - G1 Unabhaengige statische Abnahme von 213ZD

## Einordnung

`213ZE` ist eine unabhaengige statische Abnahme, kein Forschungslauf und
keine Ausfuehrungsfreigabe. Eine Laufnummer wird nicht vergeben.

## Forschungsfrage und Auftrag

Schliesst der in `213ZD` neu gebundene Controller die sechs Befunde aus
`213ZC` vollstaendig und bleibt er mit `213X`, `213Z` und `213ZA`
widerspruchsfrei?

Geprueft wurden insbesondere Publikationsausschluss, Audit-Waechter,
`__pycache__`, geschlossener AST-Auswerter, Fehlerkontextorakel, frueher
PE-Abbruch und lexikalische Unterpfadsperre.

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213X_G1_WERKZEUGVALIDIERUNG_VORREGISTRIERUNG.md`;
- `docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json`;
- `docs/forschung/213Z_G1_WERKZEUGVALIDIERUNG_VERTRAGSKORREKTUR.md`;
- `docs/forschung/213ZA_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213Z.md`;
- `docs/forschung/213ZC_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZB.md`;
- `docs/forschung/213ZD_G1_CONTROLLER_STATISCHES_KORREKTURPAKET_213ZC.md`;
- `tests/validate_static_binary_evidence.py`;
- `tools/static_binary_evidence.py`, ausschliesslich statisch gelesen.

Keine externe Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden nur statisches Textlesen, Textsuche, Dateigroesse und
SHA-256. Controller und Werkzeug wurden nicht importiert, geparst oder
ausgefuehrt.

Kontrollierte Bindungen:

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `tests/validate_static_binary_evidence.py` | 33.100 | `18446459E4F3445BDEF7B613DCB604215113BB7DF3A29D89D0B5697360EBC663` |
| `213ZD_G1_CONTROLLER_STATISCHES_KORREKTURPAKET_213ZC.md` | 6.239 | `76A6826CD3878BCAA7F918BB213EC3F0654B23C27C1908EFC1E72B36F2618760` |
| `213ZC_G1_UNABHAENGIGE_STATISCHE_ABNAHME_213ZB.md` | 10.614 | `9724BFD35E891344AA0F658C9FC3C756AD00C8264832CE29CA4813FBA20C798B` |
| `tools/static_binary_evidence.py` | 42.225 | `03162A337473218ADBCAAE577DB1922A3127DD3BCE1AE3B151B0291BDAB4E286` |

## Durchgefuehrte Schritte

1. Bytebindungen kontrolliert.
2. Die sechs Korrekturpfade gegen ihre jeweiligen Akzeptanzbedingungen aus
   `213ZC` verfolgt.
3. Erfolgspfad und gemeinsamen Ausnahmehandler bis zu beiden Rename-Stellen
   verfolgt.
4. Audit-Ereignisse und erlaubte Schreibwurzeln fuer Erfolgs- und Fehlerweg
   getrennt betrachtet.
5. Die zugelassenen AST-Knotentypen und konstruierten Zaehlerdaten verfolgt.
6. Alle fuenf Fehlerkontext-Bindungsfelder je Fall verfolgt.
7. PE-Laufzeitbeobachtung und statische Reihenfolgepruefung auf ihre
   gegenseitige Bindung untersucht.
8. Realpfadgleichheit und separatorgebundene Unterpfadrelation verfolgt.

## Messergebnisse und Gegenbaselines

### Statisch geschlossene Befunde

Fuenf der sechs Befunde aus `213ZC` sind im Grundsatz geschlossen:

1. Nach dem Erfolgs-Rename existiert kein fehlerfaehiger Arbeitsschritt mehr;
   `success_published` sperrt die Fehlerpublikation.
2. Cache-Inventur, `sys.dont_write_bytecode` und ein schreibseitiger
   Audit-Waechter sind implementiert.
3. Die vier Zaehlerfaelle erzeugen die vorregistrierten Datenformen und
   werten die sechs Werkzeugausdruecke ueber einen geschlossenen
   AST-Auswerter aus.
4. Die sieben Fehlerkontextfaelle vergleichen alle vier einzelnen
   Bindungsfelder sowie die geordneten `input_bindings` einschliesslich
   `null`-Zustaenden.
5. Die Realpfadsperre prueft exakte Gleichheit und separatorgebundene
   Unterpfade rein lexikalisch.

Weitere bestaetigte Werte:

- direkte `runpy.run_path`-Stellen: `1`;
- feste Fallzahl: `21`;
- Fallverteilung: `4 + 9 + 7 + 1`;
- keine direkte Werkzeugverwendung von `main`, `collect` oder
  `_verify_binding`;
- keine gesperrten Projekt-, Drittanbieter-, Loader- oder Prozessimporte.

Gegenbaseline war fuer jeden Punkt nicht die blosse Existenz eines Flags,
sondern ein Orakel, das die behauptete Eigenschaft eindeutig beobachtet.

## Abnahmehemmende Restbefunde

### Restbefund 1 - PE-Laufzeitfehler ist nicht an den fruehen AST-Zweig gebunden

Schwere: hoch.

`run_pe_cases` beobachtet bei negativen Faellen nur `exc.code`. Unabhaengig
davon bestaetigt `alignment_precedes_structural_parsing`, dass irgendein
`if` mit der Textkonstante `invalid PE alignment invariants` vor Directory-
und Section-Auswertung liegt. Beide Beobachtungen werden anschliessend nur
boolesch kombiniert.

Damit ist nicht belegt, dass der im konkreten Fixture beobachtete
`UNSUPPORTED_PE_FORMAT` aus diesem fruehen Zweig stammt. Derselbe Fehlercode
kann spaeter in Section-Auswertung oder an anderen PE-Pruefstellen entstehen.
Beim Fall `PE-IMAGEBASE-ZERO` stammt der erwartete fruehe Fehler zudem aus dem
separaten Zweig `zero PE base, alignment, or image size`, den das statische
Orakel ueberhaupt nicht bindet.

Gegenbaseline: Fuer jeden negativen Fall muss die beobachtete Fehleridentitaet
eindeutig einem vor Directory- und Section-Auswertung liegenden Sollzweig
zugeordnet sein. Der Fehlercode allein reicht nicht.

Erforderliche Korrektur: Pro Negativfall den erwarteten exakten Fehlerdetail-
Text beziehungsweise einen eindeutig vorregistrierten Zweigbezeichner
festlegen und diesen sowohl im Laufzeitfehler als auch im AST des jeweils
fruehen `_fail`-Aufrufs pruefen. Fuer den ImageBase-Nullfall und die sechs
uebrigen negativen Alignmentfaelle sind die zwei unterschiedlichen fruehen
Zweige getrennt zu behandeln.

### Restbefund 2 - Fehler-Staging ist waehrend des Erfolgswegs freigegeben

Schwere: mittel.

Der Audit-Waechter wird vor Phase B mit drei erlaubten Schreibwurzeln
installiert: Fixture-Temporaerordner, Erfolg-Staging und Fehler-Staging. Das
Fehler-Staging ist damit bereits waehrend einer spaeter erfolgreichen
Validierung ein erlaubtes Schreibziel. Ein unerwarteter Schreibzugriff dorthin
wuerde nicht blockiert, `unexpected_write_count` bliebe null und das
Erfolgspaket koennte trotzdem publiziert werden, waehrend ein zusaetzlicher
Fehler-Stagingbaum zurueckbleibt.

Dies schwaecht sowohl die Nebenwirkungsgrenze als auch den gegenseitigen
Publikationsausschluss. Das Fehler-Staging darf erst nach Eintritt des
Fehlerpfads beschreibbar werden.

Erforderliche Korrektur: Den Audit-Waechter phasenabhaengig schalten. Im
normalen Validierungsweg duerfen nur Fixture-Temporaerordner und
Erfolg-Staging beschreibbar sein. Erst der Fehlerhandler darf einmalig das
Fehler-Staging fuer das feste Ein-Datei-Paket freigeben; im Erfolgspfad muss
dessen Nichtexistenz vor dem Erfolgs-Rename geprueft werden.

## Grenzen und nicht gepruefte Annahmen

- Die Abnahme ist ausschliesslich statisch.
- Syntax, Audit-Ereignisse, AST-Auswerter und Fixtureverhalten wurden nicht
  ausgefuehrt.
- Keines der 21 Fixtures wurde erzeugt.
- Keiner der 54 Realpfade wurde geoeffnet, aufgeloest, gehasht oder auf
  Existenz geprueft.
- Weitere Laufzeitbefunde duerfen erst nach statischer Restkorrektur, erneuter
  Abnahme und gesonderter Freigabe untersucht werden.
- Aus dieser technischen Abnahme folgt kein G1- oder MCM-Funktionsnachweis.

## Konkrete Schlussfolgerung

`213ZD` schliesst fuenf Befundbereiche im Grundsatz, bleibt aber wegen zweier
abnahmehemmender Restbefunde noch nicht ausfuehrungsreif. Insbesondere ist der
geforderte fruehe PE-Abbruch noch nicht kausal an den beobachteten Fehler
gebunden.

G1 bleibt nicht bestanden, G0 bleibt abhaengig und Huerde G bleibt gesperrt.
Eine Zielabweichung ist nicht erkennbar.

## Vorschlag fuer den naechsten begrenzten Entwicklungsschritt

Als naechstes sollte genau ein statisches Restkorrekturpaket erstellt werden,
das ausschliesslich die beiden Restbefunde dieses Dokuments schliesst und
Controller sowie Korrekturdokument neu bytegenau bindet.

Danach ist erneut genau eine unabhaengige statische Abnahme erforderlich. Bis
dahin bleiben Syntaxpruefung, Tests, Controller- und Werkzeugausfuehrung,
Realpfade, Manifest, Resolver, G2 und Huerde G gesperrt.
