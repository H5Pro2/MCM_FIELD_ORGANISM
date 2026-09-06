# S2-NF: Auditiver Erhaltungs- und Verlustplan unter Konkurrenz

## Status und Gegenfrage

Nur dieser statische Plan, Quellenstand `8a999d7`. Keine Implementierung,
PCM-Erzeugung, Rezeptoranalyse, Distanzberechnung, Tests oder Memoryausfuehrung.
Keine neue Lauf-ID: Planung ist kein Lauf. Alle Hauptgates bleiben `False`.

S2-NE bleibt unveraendert als bestaetigter begrenzter Transfer abgeschlossen:
vier erhaltene A-Treffer ohne Konkurrenz, vier neue A-Treffer unter Konkurrenz,
ein ermoeglichter B-Abruf und eine verhinderte Fehlzulassung. Das betrifft
Abrufselektivitaet, nicht Lernregel oder Kapazitaet. Die Erhaltung unter
Konkurrenz blieb wegen `D=0` ungeprueft. Historische Belege werden weder
ergaenzt noch neu ausgewertet.

Gegenfrage: Verliert `ALL_BANDS_24` einen zuvor korrekt eindeutigen
historischen Mittelwerttreffer, wenn ein anderer Inhalt wirklich gleichzeitig
in A gespeichert ist? Allgemeine Erhaltung folgt nicht aus der strengeren
Regel: Eine einzelne grosse Differenz kann den Max-Arm ausschliessen, obwohl
der Mittelwert einschliesslich derselben Differenz noch akzeptiert.

## Unveraenderte Mechanik

Beide Arme und ihre unabhaengigen Direktbaselines erhalten denselben echten
Zustand, dieselbe Cuequelle und den vorhandenen Bandplan:

```text
delta_i = abs(candidate[i] - float(cue.values[i])), i = 0..23
Referenz B4/Fast: sum(delta_i in Bandreihenfolge) / 24 <= 0.2
Alternative B4/Fast: max(delta_i in Bandreihenfolge) <= 0.2
Beide Auditory-Slow: sum(delta_i in Bandreihenfolge) / 24 <= 0.02
```

Referenz ist die historische Binary64-Rechenfolge, NICHT `statistics.mean`.
Keine Rundung, Toleranz, Gewichtung, dritte Regel oder Schwellenaenderung.
Vollstaendiger `9/3/8`-Scan; keine Deduplication, Rangfolge oder B-Bevorzugung.
Die vollen 48 Kandidatenwerte dienen unveraendert der internen B4-/Fast-
Gleichheitspruefung. Verdeckte Cuewerte beeinflussen die Anwendbarkeit nicht.
Hypothesen bleiben getrennt, werden weder angewendet noch vervollstaendigt.

## Sieben feste Audiorezepte, fuenf Hinweise

Alle Quellen: Mono `PCM_F32LE`, 48.000 Hz, 4.800 Samples, 19.200 Bytes.
Direkter unveraenderter `LogSpectralReceptor.analyze`, Profil
`48000/4800/480/50/18000/48`. Keine rollende Audiopipeline.

| Neutrale Quellen-ID | Festes Rezept |
| --- | --- |
| nf-a01 | Unveraendertes S2-ND s001 |
| nf-a02 | Unveraendertes logarithmisches Rechteckchirp-Rezept aus S2-LB |
| nf-a03 | Unveraendertes S2-ND s007; bewusste Exaktkopie von nf-a01 |
| nf-a04 | Unveraendertes S2-ND s008 |
| nf-a05 | Unveraendertes S2-ND s009 |
| nf-a06 | Unveraendertes S2-ND s010 |
| nf-a07 | s001-Grundrezept mit der unten festgelegten vierten Partialkomponente |

Die Wiederverwendung ist gezielt und transparent, kein unabhaengiges Korpus.
S2-LB liefert einen bereits vorhandenen breitbandigeren Konkurrenten statt
des in S2-NE benutzten s004. Seine alten Abstaende zu S2-KY sind KEINE
Abstaende zu den jetzigen Quellen und garantieren hier keinen positiven D.
Keine weiteren Konkurrenten werden erprobt oder nachtraeglich ausgewaehlt.

Harmonische Rezepte, Partialfolge links nach rechts, Frequenzen in Hz:

| ID | Frequenzen | Amplituden als rationale Paare | Seed |
| --- | --- | --- | --- |
| nf-a01, nf-a03 | 240, 480, 720 | 8/20, 2/20, 1/20 | s2nd-pcm-001 |
| nf-a04 | 240, 480, 720 | 6/20, 3/40, 3/80 | s2nd-pcm-001 |
| nf-a05 | 247.2, 494.4, 741.6 | 8/20, 2/20, 1/20 | s2nd-pcm-001 |
| nf-a06 | 240, 480, 720 | 6/20, 4/20, 1/20 | s2nd-pcm-001 |
| nf-a07 | 240, 480, 720, 120 | 8/20, 2/20, 1/20, 3/10 | s2nd-pcm-001 |

Frequenzen werden literal als ganzzahlige Millihertz gebunden: insbesondere
nf-a07 `(240000,480000,720000,120000)`. nf-a07 fuegt einen einzelnen
Unterton mit halber Grundfrequenz hinzu, nicht einen aus Filterbankzentren
abgeleiteten Ton. Staerke `3/10` ist jetzt fest; keine Suche an `0.2`.
"Lokal" bezeichnet die Quellpartialaddition, nicht garantiert exakt eine
betroffene Rezeptorposition. Hann-Leckage und Filterbankueberlappung bleiben
real erhalten. Ein moeglicher Verlust ist ausdruecklich ein gueltiges Ergebnis.

Exakte Erzeugungsfolge wie `reports/s2nd/seal_inventory.py::pcm_payload`:
je Partialindex i erste vier SHA-256-Bytes von `seed + ':' + str(i)` als
unsigned Little-Endian u; Phase `(float(u)/4294967296.0)*math.tau`.
Frequenz `float(millihz)/1000.0`, Amplitude `float(zaehler)/float(nenner)`.
Fuer n=0..4799: `t=float(n)/48000.0`, Akkumulator `value=0.0`, dann
in Partialfolge `angle=((math.tau*f)*t)+phase` und
`value=value+a*math.sin(angle)`. Erst danach einmal `struct.pack('<f',value)`.
Auch nf-a07 wird aus dieser Summe gebildet, nicht durch Addition auf schon
gerundete PCM-Samples. Der vorhandene reine Generator unterstuetzt diese
Partialliste; sein historischer Sealer-Einstieg wird nicht ausgefuehrt.

nf-a02 uebernimmt exakt die vorhandene S2-LB-Rechenfolge:

```text
f0=50.0; f1=890.0; duration=0.1; ratio=f1/f0
phase_scale=2.0*math.pi*f0*duration/math.log(ratio)
initial_phase=math.pi/7.0
scale=f32(0.9800000190734863)
t=n/48000.0
phase=initial_phase+phase_scale*(ratio**(t/duration)-1.0)
sample=f32(scale if math.sin(phase)>=0.0 else -scale)
```

`f32` ist pack/unpack `<f`; kein Clipping. Der historische PCM-Hash lautet
`97a11dfcb89615b257d430ab718505b2ec207b8b8684c012ec5bdc6adcea4f5b`.
Nur dieses reine Quellenrezept wird spaeter uebernommen, nicht die alten
S2-LB-Distanzgates, Rollen oder der rollende Materialisierungseinstieg.

Harmonische Amplitudensummen maximal 0.85, Chirpamplitude kleiner 1.
Das ersetzt KEINE Validierung der spaeteren 48 Rezeptorwerte. Quellen-,
Normalform-, Zeit- oder Digestfehler fuehren zu `NOT_EVALUABLE`; kein
Clipping, Nachnormalisieren, Skalieren, Ersatzrezept oder Retry.

## Vorbindung und tatsaechliche Formation

Vor jeder neuen Rezeptoranalyse werden spaeter die sieben Quellenrezepte
und Payloads einmal rezeptorfrei versiegelt, inklusive Exaktkopie ohne
Deduplizierung. Native Siegelzeit fuer Quellenordinal n=1..7:
`s2nf-source-sample-clock`, `[(n-1)*4800,n*4800)`. Dokument-, Generator-,
Python-/Interpreter-/math-Herkunfts-, Profil- und Planbindungen mitfuehren.
Noch nicht erzeugte Payload- oder neue Plandigests werden hier nicht erfunden.

Visuelle Formationsbegleitung unveraendert S2-JX: nf-v01 ist Ordinal 0 (X),
nf-v02 Ordinal 2 (D1), `1920x1080 RGB8`, 288 Blockmittelwerte. Vorhandene
Payload-/Wertbindungen aus `FIXTURES` uebernehmen. Generator und Rezeptoren
bleiben gleich. Keine visuellen Hinweise, Maskenerkennung oder Feldkontakte.

Zwei getrennte frische Memoryzustaende, keine manuell eingesetzten Slots.
Vollstaendig literale technische Ereignisfolge, erst h01, danach h02:

| Ereignis | Art | Audio | Video |
| --- | --- | --- | --- |
| s2nf-h01-e01 | Formation | nf-a01 | nf-v01 |
| s2nf-h01-e02 | Formation | nf-a02 | nf-v02 |
| s2nf-h01-e03 | Teilhinweis | nf-a03 | keines |
| s2nf-h01-e04 | Teilhinweis | nf-a04 | keines |
| s2nf-h01-e05 | Teilhinweis | nf-a05 | keines |
| s2nf-h01-e06 | Teilhinweis | nf-a06 | keines |
| s2nf-h01-e07 | Teilhinweis | nf-a07 | keines |
| s2nf-h02-e01 | Formation | nf-a02 | nf-v02 |
| s2nf-h02-e02 | Teilhinweis | nf-a03 | keines |
| s2nf-h02-e03 | Teilhinweis | nf-a04 | keines |
| s2nf-h02-e04 | Teilhinweis | nf-a05 | keines |
| s2nf-h02-e05 | Teilhinweis | nf-a06 | keines |
| s2nf-h02-e06 | Teilhinweis | nf-a07 | keines |

Je Geschichte beginnt Ereignisordinal j bei 0, inklusive Hinweise.
Native Audiozeit `s2nf-hXX-audio-sample`: `[9600*j,9600*j+4800)`.
Bei Formation Videoindex `6*j+2` auf `video.frame`; gemeinsame Paarzeit
`s2nf-hXX-pair-clock`: Audio `[200000000*j,200000000*j+100000000)`,
Video `[floor((6*j+2)*1000000000/30),200000000*j+100000000)`.
Jeder spaetere Hinweis hat strikt spaetere native Audiozeit. Gleiche
PCM-Bytes zwischen Geschichten bedeuten keine gleiche zeitliche Quelle.
Jedes Ereignis regeneriert spaeter seine Quelle mit Hashpruefung vor Analyze.

Statische Speicherableitung: X/D1 sind bereits visuell ausserhalb der
Fast-Grenze 0.2. Daher werden bei unveraenderter Fast-AND-Regel in h01
zwei getrennte Slots mit Support 1 erzeugt, unabhaengig vom Audioabstand.
B4[0]/Fast[0] enthalten nf-a01, B4[1]/Fast[1] nf-a02. h02 enthaelt nur
nf-a02 in B4[0]/Fast[0]. Alle anderen Slots sind frei; beide Slow-Banken
bleiben leer. Keine Wiederholung, Konsolidierung, Verdraengung oder Ersetzung.
Die unterschiedliche physische Position des Konkurrenten in h02 entsteht
regelkonform durch frische Formation, nicht durch manuelles Verschieben.
B4/Fast derselben Quelle sind wertgleich, aber nicht dedupliziert.
Diese Inventare sind spaeter tatsaechlich zu belegen, nicht einzusetzen.

## Getrennte Bewertung und harte Aussagegrenzen

Nur die Evaluationswurzel kennt: nf-a01 = Ziel, nf-a02 = Konkurrent;
nf-a03 = Exakt, nf-a04 = Pegel, nf-a05 = Frequenz, nf-a06 = spektrale
Umgewichtung, nf-a07 = lokale Partialaddition. Alle fuenf Hinweise werden
als zum Ziel gehoerende Aufgabenvorgaben bewertet. Das ist keine behauptete
akustische Identitaet; insbesondere nf-a07 ist ein gezielter Belastungsfall.

Faelle c01..c05 sind die fuenf h01-Hinweise; c06..c10 die entsprechenden
h02-Kontrollen. In h01 ist nur die aus nf-a01 wirklich gebildete A-Hypothese
korrekt; deren voller Kandidatendigest und 24 vorgeschlagene Werte muessen
dem Formationsbeleg entsprechen. In h02 ist Enthaltung korrekt. Keine
angenommene Regelentscheidung wird technisches Startgate. Auch saemtliche
Mehrdeutigkeiten und nicht erfolgreiche Quellen verbleiben im Datensatz.

Erhaltung ausschliesslich unter vorhandener Konkurrenz in h01:

- N=5 vorgebundene positive Faelle, davon exakt 1, Varianten 4.
- D: korrekt eindeutige Referenz-A-Treffer auf nf-a01 bei belegtem nf-a02.
- R: davon dieselben korrekten Hypothesen im Alternativarm.
- L: jeder nicht korrekt erhaltene D-Fall; stets `D=R+L`.
- Getrennte Tabellen fuer Exakt und jeden der vier Variantentypen sowie
  alle Varianten zusammen. PCM-Bitvariation, volle 48-Werte-Variation und
  tatsaechliche Variation auf den beobachteten 24 Baendern separat ausweisen.
  Verschwundene beziehungsweise nur verdeckte Variation wird nicht als
  bestandene Toleranz im beobachteten Teilhinweis behauptet.

Fuer jeden Verlust einzeln: Fall-/Quellen-ID, B4-/Fast-Treffermengen,
Statistikwerte und betroffene Banddifferenzen, Kandidatendigests und
Entscheidungen beider Arme. Verlust in Enthaltung und falsche Eindeutigkeit
auseinanderhalten. Gewinne und verhinderte Fehlzulassungen separat, niemals
als Saldo gegen L. Fuenf Zielentfernungskontrollen erhalten eigene Nenner;
sie sind keine Erhaltungsfaelle und kein allgemeiner Open-Set-Nachweis.

`D>0,L=0` bestaetigt Erhaltung ausschliesslich auf diesem Teilnenner.
Jedes `L>0` falsifiziert die Erhaltungsprognose fuer die betreffenden Faelle,
auch bei anderen Gewinnen. `D=0` bedeutet **ERHALTUNG_NICHT_GEPRUEFT**,
separat auch fuer Varianten und echte beobachtete Rezeptorvariation.
Eine bestandene Exaktkontrolle ersetzt keinen Variantenbefund.
Bei erneut leerem D keine Ersatzquellensuche oder kleinere Variation.

## Wiederverwendung und endliches Budget

S2-NE `retrieve`, `direct_retrieve`, `verify_arm`, `compare_technical`,
Quellenpaarung und bestehender atomarer Koordinator unveraendert verwenden.
Alle vier Arme pro Fall sehen denselben State/Cue; beide Direktbaselines
scannen unabhaengig. Keine Memoryprobe vor dem Teilhinweis.
Die zehn Hinweise und alle 40 Abrufbelege bleiben vollstaendig read-only.
Die drei Formationen sind bestimmungsgemaess schreibend.

Keine neue Infrastruktur. Spaeter genuegt eine kleine explizite Bindung
dieses Tupels, der Quellen, Zaehler und Evaluationsrelationen an den
vorhandenen Belegweg: ein atomarer Gesamtbeleg, eine unabhaengige read-only
Gesamtpruefung, danach eine getrennte Bewertung. Die historisch fest auf
20/13 und alte Quellen gebundenen S2-NE-Haupteinstiege/Erwartungen duerfen
nicht mit neuen Daten aufgerufen oder durch Monkeypatching umetikettiert
werden. Der vorliegende Auftrag implementiert auch diese kleine Bindung nicht.

| Groesse | Fest / Obergrenze |
| --- | ---: |
| Quellenfenster bei spaeterer rezeptorfreier Vorversiegelung | 7 |
| PCM-Samples / Bytes dieser sieben Fenster | 33.600 / 134.400 |
| Gleichzeitiger PCM-/RGB-Rohpayload maximal | 19.200 / 6.220.800 Byte |
| Frische Geschichten / Formationen / Hinweise | 2 / 3 / 10 |
| Ereignisse | 13 |
| Direkte Audio-/Videoanalysen im spaeteren Funktionslauf | 13 / 3 |
| Erzeugte Rezeptorwerte im Funktionslauf | 13*48 + 3*288 = 1.488 |
| Faelle je Regel / Primaerentscheidungen | 10 / 20 |
| Zusaetzliche Direktbaselineentscheidungen / alle Abrufbelege | 20 / 40 |
| Vollstaendige Slotbesuche | 40*20 = 800 |
| Belegte Scanbeziehungen bei hergeleiteten Inventaren | 120 |
| Banddifferenzen bei hergeleiteten Inventaren | 120*24 = 2.880 |
| Harte Banddifferenzgrenze unabhaengig vom Inventar | 40*480 = 19.200 |
| Interne Gleichheitsvergleiche maximal | 40*48 = 1.920 |
| Abruf-Wertvergleiche maximal | 21.120 |
| Zusaetzliche einmalige Verifikationsreserve maximal | 21.120 |
| Abruf plus Verifikation maximal | 42.240 |
| Logische Abrufoperationen einschliesslich Baselines | 40*14 = 560 |
| Profilabgeleitete Formations-L1-Obergrenze | 3*3.552 = 10.656 |
| Numerischer Memoryzustand je Geschichte maximal | 44.544 Byte |
| Kanonischer Abrufbeleg / atomarer Gesamtbeleg | <32.768 / <=4.194.304 Byte |
| Vollprobe / Feld / Runtime / Hypothesenanwendung | 0 / 0 / 0 / 0 |

120 Beziehungen: fuenf Hinweise mal vier Arme mal vier belegte Slots in
h01 plus fuenf mal vier mal zwei in h02. Leere Slow-Slots werden trotzdem
vollstaendig besucht. Diese inventarabhaengigen Kosten sind keine
Treffer-Erfolgsgates. Typ-/Hashpruefung ist keine weitere Rezeptoranalyse.
Eine gesonderte vorgeschaltete Rezeptormessreihe ist hier nicht vorgesehen.

## Lesend gebundene Ausgangsdateien

Historische Regeln, Profile, Kerne und NE-Module bleiben ueber den
S2-NE-Vertrag und den letzten Qualifikationsbeleg gebunden. Die folgenden
SHA-256 wurden nur von vorhandenen Dateien gelesen, keine PCM-Digests neu erzeugt:

| Datei | SHA-256 |
| --- | --- |
| docs/S2NE_PRIVATER_AUDITIVER_MEMORY_TRANSFER_VERTRAG.md | e14021fc90d2270a4b10af92a9f2ac7f0ca67280c7df969d31b55ebafb74ea6f |
| reports/s2ne/s2ne-real-auditory-transfer-20260906-01/evaluation.json | 9c92c37bdafc1d37d7105ebc1212dbf9cc0732b33c533a3cdb3d1a1301941f65 |
| reports/s2ne/s2ne-run-completion-qualification-20260906-01/result.json | 1a5d795b50e94d2290724e8d0de9e3f9daa94beb4cf55e76a4505e20bfba85e2 |
| reports/s2nd/s2nd-source-panel-preseal-20260906-02/execution-plan.json | 0db1fc0f64a5af76616e7652fcf9b8da3bfb6fef8c9e60fa0870a4e49425df4e |
| reports/s2nd/seal_inventory.py | 9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c |
| docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json | f77f074cb9df6ada1f182c1bdb4abfb5fe233ca923f8a7bd99334c9c13a85d48 |
| tools/_s2lb_d_far_pcm_materialization.py | 5044fbc2d1e755b8bca494b90f1ec6ff13fad40e6d59aca31ae838c568300450 |
| reports/s2kx/s2lb-d-far-pcm-materialization-20260904-01/materialization.json | 1fd9ab971acbdb1bcacd6dde7c69a4ba485edd7056697ed240d00d465a9b05d0 |
| tools/_s2jx_default_live_memory_fixtures.py | 5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936 |

Jetzt nur Dokumentation und Versionierung. Keine Produktumstellung,
Memorymechanik, Systemintegration oder neue Erhaltungsbehauptung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses einzelnen
Erhaltungsplans unter Konkurrenz und danach gegebenenfalls der Freigabe
seiner unveraenderten Quellenbindung weiter; noch keine Ausfuehrung.
