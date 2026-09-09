# S2-NU: rezeptorfreie Vorversiegelung

## Technischer Abschluss

Lauf-ID: `s2nu-source-preseal-20260909-01`.
Genau ein Vorversiegelungsaufruf nach bestandener neutraler **16/16**-Qualifikation;
anschliessend genau eine unabhaengige read-only Bindungspruefung.
Ergebnis: **S2NU_PRESEAL_VERIFIED**, Exit-Code `0`, kein Retry.

Alle **30/30 Fenster** wurden in versiegelter Reihenfolge erzeugt und gehasht:
sechs Verlaeufe mit je fuenf Fenstern, insgesamt 144.000 Float32-Samples und
576.000 PCM-Bytes. Je Fenster 4.800 Samples bei 48.000 Hz; hoechstens ein
vollstaendiger 19.200-Byte-Payload gleichzeitig, keine Rohpayloadablage.
Die feste Synthesereihenfolge endet mit genau einer Float32-Rundung pro Sample.
Es gab keinen Quellenersatz, keine Skalierung, Optimierung oder Permutationswahl.

## Wurzelbindungen

| Beleg | Kanonischer Inhaltsdigest | Datei-SHA-256 |
| --- | --- | --- |
| [Ausfuehrungsplan](execution-plan.json) | `1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7` | `6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10` |
| [Evaluationsplan](evaluation-plan.json) | `7556d0f0c7807817468f840347ca5d139477fffb18e1b24c67ecbba00d716847` | `5fb011d2057cc56f167912e2a1963e52ba8cacc5bbd2157f0236f0404e419160` |
| [Siegel](seal.json) | `0dea5839d814c50c82a2858fca00632b0cdcbedda6576f28a0031f687f313a13` | `b61bffb93a816730fe2ee00c2d6bbb4a7f2e01414608228aa53c2f90a092621e` |

[Verifikationsdigest](verification.json):
`069b9892cdd9d872f0d861dd570e2a4240e3ac1d99ee1502d77111a8c8f18e68`.
Die drei Dateihashes sind vor und nach der lesenden Pruefung unveraendert.

NU-Plan-SHA-256:
`983057c24442de2c862a423525cb9c43c090caa69088724aefe8d912f9663d0f`.
Generator-Modul-SHA-256:
`8e0fa79f3ce66ce4228f46a52252de5d207c6cee29fefc42f957aa41dc56bce6`.
Generator-AST-Digest:
`5dab98b10580b6719c074cebe8298865c201e96824c5b1c7f60e06f7b21655b0`.
Alle elf gebundenen Dokument-/Quellhashes blieben unveraendert.

CPython 3.14.4, MSC v.1944 AMD64, Binary64 mit 53 Mantissenbits.
`math` ist durch `__spec__.origin == "built-in"` **und** Built-in-Mitgliedschaft
gebunden; keine erfundene Moduldatei. Interpreter- und Python-DLL-Hashes,
Generatoridentitaet sowie NumPy-2.4.4-Dateibindungen stehen im Ausfuehrungsplan.
NumPy wurde nicht importiert. Raw-/Halbprofil wurden nur als Metadaten gebunden:
`5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7` /
`4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f`.

## Fenster und Bytegleichheiten

Alle Quellen `nu-s01-w00` bis `nu-s06-w04` behalten eigene Ordinal-, Fenster-
und Quelldigests. Startindex `((s-1)*24000+k*4800)`, Ende `start+4800`,
nativer Snapshotindex `start//480` nach exakter Teilbarkeitspruefung.
Die s03-Synthesepermutation veraendert nicht die reale Zeitbindung.

Die fuenf beabsichtigten Payloadentsprechungen sind bestaetigt:

| s02-Fenster | s03-Fenster |
| --- | --- |
| w00 | w00 |
| w03 | w01 |
| w01 | w02 |
| w02 | w03 |
| w04 | w04 |

Zusaetzliche Bytegleichheitsgruppen, unveraendert erhalten:

- `s01-w00..w04`, `s05-w00`, `s05-w04`, `s06-w00`, `s06-w01`.
- `s06-w03`, `s06-w04`.

Saemtliche Payloadhashes und Gruppen sind im Siegel erhalten. Keine
Deduplizierung: Auch bytegleiche Fenster behalten unterschiedliche Quellen-/
Zeitbindungen. Das ist Payloadgleichheit, noch kein gemessener Rezeptorbefund.

## Kontrollarme und Aussagegrenze

Die Ausfuehrungswurzel bindet die Messformeln, Bandreihenfolge und drei
Kontrollarmformen. Kategorien und die fuenf strikten Ordnungskriterien
stehen ausschliesslich in der getrennten Evaluationswurzel. Keines wurde
ausgewertet. Gleichstaende bestehen das spaetere strikte Kriterium nicht.

Der ungeordnete Arm darf ausschliesslich `profile_digest` und die fuenf
lexikographisch nach `<48d`-Bytes sortierten Wertevektoren erhalten;
Multiplizitaet bleibt bestehen. Quellen-, Stream-, Zeit-, Ordinal-, Snapshot-,
Zustandsdigest-, Rezept- und Seedfelder sind als funktionale Eingaben verboten.
Ihre externe Belegbindung darf diese Grenze nicht umgehen. Der spaetere
Kontrollarm ist noch nicht implementiert; geprueft ist die geschlossene
Planform einschliesslich neutraler Ablehnung solcher Zusatzfelder.

Die unabhaengige Pruefung bestaetigt gespeicherte Hash-/Wurzelbindungen,
literal nachgepruefte Fenster/Rezepte, Permutation, Profil, Formeln, Budgets
und Kollisionsgruppen. Sie regeneriert keine Payloads und bestaetigt die
PCM-Bytes deshalb nicht durch eine zweite numerische Synthese.

Artefakte: Ausfuehrungsplan 44.937 Byte, Evaluationsplan 1.282 Byte,
Siegel 4.495 Byte, Vorregistrierung 39.282 Byte, Verifikation 2.326 Byte.
Alle Metadaten liegen unter 65.536 Byte je Beleg; die getrennte
Verifikationsgrenze von 262.144 Byte wird eingehalten.

Rezeptor-, NJ-, Banddifferenz-, Ordnungs-, Memory-, Feld-, Kontext- und
Runtimeaufrufe: jeweils **0**. Gates bleiben `False`. NT/ME/MI und historische
Belege sind unveraendert; fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

Offen bleiben Rezeptorgueltigkeit und die Gegenprognose der Verlaufsmessung.
Auch ein spaeterer Erfolg belegt nur Reihenfolgenempfindlichkeit dieser
Kennzahl, keine Quellenfortsetzung, Kategorieerkennung oder sichere Lernbindung.
Naechster Vorschlag an den Analysten: Vorversiegelung lesen und separat ueber
die einmalige Rezeptor-/NJ-Materialisierung entscheiden, noch keine Messauswertung.
