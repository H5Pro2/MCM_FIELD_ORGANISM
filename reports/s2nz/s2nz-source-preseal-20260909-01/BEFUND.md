# S2-NZ: rezeptorfreie Vorversiegelung

ID: `s2nz-source-preseal-20260909-01`.
Nach der separaten [24/24-Quellenqualifikation](../s2nz-source-binding-qualification-20260909-01/BEFUND.md)
genau ein Vorversiegelungsaufruf und anschliessend genau eine unabhaengige
read-only Bindungspruefung: **S2NZ_SOURCES_PRESEALED / S2NZ_PRESEAL_VERIFIED**,
Exit-Code 0. Kein Retry und keine Payloadregeneration zur Verifikation.

## Tatsaechlicher Umfang

30/30 getrennte PCM-Fenster in der versiegelten Reihenfolge s01..s06/k0..k4,
je 4.800 Samples, 48.000 Hz, mono PCM_F32LE. Insgesamt 576.000 erzeugte
PCM-Byte; hoechstens ein vollstaendiges 19.200-Byte-Fenster gleichzeitig.
Jedes Fenster wurde einmal erzeugt, gehasht und freigegeben; keine Rohdatenablage.
15 saubere und 15 gestoerte Fenster; 72.000 feste Sample-Stoerhashes.

Die Reihenfolge ist Synthese -> Pegelmultiplikation -> optionale Stoeraddition
-> einmalige Float32-Rundung. Stoerstaerke 1/1024, die drei vorgegebenen
Stoerseeds und alle Zeitbindungen unveraendert. Kein Clipping, Skalierungswechsel,
Quellenersatz oder Auswahl nach Messergebnissen.

Quellen-, Rezept-, Payload-, native Zeit-, Profil-, Generator-/AST-,
Interpreter- und Codeidentitaeten stehen vollstaendig in der
[Ausfuehrungswurzel](execution-plan.json). CPython 3.14.4/64 Bit,
`math` nachgewiesen built-in; NumPy 2.4.4 nur dateigebunden, nicht importiert.
Der unveraenderte historische Planhash lautet
`aec5a731d455bd05c2c043c7e4224d403f2634e0be046f89fd395ae04aaf9a6c`.

## Saemtliche Bytegleichheiten

Die vier Gruppen aus dem [Siegel](seal.json) bleiben getrennte Quellen
mit jeweils eigener Zeit-/Herkunftsbindung; keine Deduplizierung:

| Quellen | PCM-SHA-256 |
| --- | --- |
| nz-s01-w00, nz-s03-w00, nz-s05-w00 | 006f1f5393275c95a643561db4c02cb5835e47635967e6769ab57e01f446e0fa |
| nz-s05-w03, nz-s05-w04 | 876b0cfee3ba4039b49b4a7d8d1a407d925bc1f23917be69e99fee1af619a236 |
| nz-s03-w02, nz-s05-w02 | bfb93738df197b4bdcab9d926e69e2a1d3a080ae68df6dcb9d1ee9abb923b05e |
| nz-s01-w01, nz-s03-w01, nz-s05-w01 | fb2c45b27ac402d1a8ad52e91dbb8dcc7e4d68ebdbc39df05c1619b4f71eaa24 |

Keine weiteren Payloadhash-Kollisionen. Dies ist keine Aussage ueber
spaetere Rezeptorgleichheit oder prognostischen Nutzen.

## Getrennte Bindungswurzeln

| Beleg | Kanonischer Digest | Dateigroesse Byte |
| --- | --- | ---: |
| execution-plan.json | 7f424a6dbc694b4f8cb20160ce8a294e0d4923137b9f0fcdf83aeb5a48e0d113 | 53.319 |
| evaluation-plan.json | f2ba6dbba0e139e614384e9b33a35bfd011507e57e92366b15e81379f29644bf | 1.441 |
| seal.json | 4341121eb545faa00b5158ded2ca148b8cf153e5295a6565f0e02d9c5521da41 | 6.418 |
| verification.json | a127825ce2e6ecb5d0e8b27bd28a66516f925df2a8b0753b816a2ac49214de9c | 2.158 |

Vorregistrierung 47.805 Byte; alle Plan-/Siegelgrenzen 65.536 Byte und
Pruefbeleggrenze 262.144 Byte eingehalten. Dateihashes der drei Plan-/Siegel-
artefakte sind im [Pruefbeleg](verification.json) vor/nach identisch gebunden.

Beide historischen NX-Freeze-Payloads samt Ergebnis-, Verifikations- und
Profilbindungen wurden read-only importiert. Importdigest unveraendert:
`a897b32ef204947af6e08ef5770e23c921b422da73b06b92d9bf08189c77c07f`.
Keine Lernkettenwiederholung, Koeffizientenberechnung oder Owneroeffnung.

Die [Evaluationswurzel](evaluation-plan.json) bindet Kategorien und saubere/
gestoerte Kontrollpaare separat. 18 Prognosestellen und zwoelf LOCAL-Stellen
sind ausschliesslich Metadaten. Fokus p05/p06/p11/p12 entspricht
s02/k3,k4 und s04/k3,k4: **N=4 fest**, Empfehlungsnenner D daneben;
Enthaltungen entfernen keine Schwerpunktstelle. Keine Ersatzschwelle,
praktische Erfolgskriterien oder Robustheitsbewertung.

## Grenzen

Ziel bleibt auch gestoert der naechste tatsaechlich beobachtete Halbvektor.
Saubere Kontrollfolgen sind keine operative Zusatzinformation und kein
verborgenes Rekonstruktionsziel. Absolute MAE, Gewinne, Verluste und Abdeckung
sind erst nach spaeterer Freigabe getrennt auszuwerten. Feste Historienbefunde
und tatsaechlich ausgegebene Empfehlungen duerfen nicht gleichgesetzt werden.

Die lesende Pruefung rekonstruierte alle 30 Quellen-/Zeitformen und 18
Stellenmetadaten unabhaengig literal. Sie pruefte Digests, Freeze-Herkunft,
Bytegleichheitsgruppen, Planwurzeln, Budgets und Unveraenderlichkeit.
Formelmetadaten nutzen gemeinsame deklarative Bindungen. Sie erzeugte keine
PCM-Bytes und bestaetigt deshalb nicht unabhaengig deren numerische Synthese.
Die Synthesereihenfolge ist neutral qualifiziert; die spaetere funktionale
Zukunftssperre und Prognoserechnung sind noch nicht angebunden/qualifiziert.

**Null Rezeptor-/NJ-, Prognose-, Empfehlungs-, LOCAL-, Fehler-, Lern-,
Memory-, Feld-, Kontext- und Runtimeaufrufe.** Keine Rezeptorgueltigkeit,
Stoerwirkung, Entrauschung oder Funktionsverbesserung nachgewiesen.
Alle Hauptgates False; ME/MI und Systemintegration gesperrt. Historische
Quellen, Profile, Freeze-Belege und NZ-Plan unveraendert; Bootstrap und
fremde Aenderungen ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Bindungsbelege
und der separaten Entscheidung ueber die minimale diagnostische Laufanbindung weiter.
