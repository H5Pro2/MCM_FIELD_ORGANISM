# S2-NT: einmalige Rezeptor-/NJ-Materialisierung

Lauf-ID: `s2nt-receptor-nj-materialization-20260908-01`.
Datum: 2026-09-08. Technischer Abschluss:
`RECEPTOR_NJ_MATERIALIZATION_COMPLETE`, Exit-Code `0`.
Anschliessend genau eine unabhaengige read-only Belegpruefung:
`S2NT_MATERIALIZATION_VALID`. Kein Retry, keine zusaetzliche Qualifikation
oder Rezeptorvorpruefung. Kein fachlicher Vergleich.

## Tatsaechlicher Umfang

| Operation / Bestand | Anzahl |
| --- | ---: |
| Regenerierte PCM-Fenster | 14 |
| Vor Analyse gegen das Siegel gepruefte Payloadhashes | 14 |
| Direkte analyze-Aufrufe / Rueckgaben | 14 / 14 |
| Gespeicherte Rohwerte | 672 |
| NJ-Aufrufe / Rueckgaben | 14 / 14 |
| Gespeicherte gerundete Halbwerte | 672 |
| Vollstaendig gebundene Quellenzustaende | 14 |
| Unabhaengig bitgenau gepruefte Halbierungen | 672 |
| Rollende Hops / Kontaktframe-Aufrufe | 0 / 0 |
| Gespeicherte PCM-Payloads | 0 |
| Distanzen / Quellenvektorpaarvergleiche / Ordnungsauswertungen | 0 / 0 / 0 |
| Memory / Feld / Kontext / Runtime | 0 / 0 / 0 / 0 |

Einmalige Quellenfolge `nt-a01` bis `nt-a14`, unveraenderte versiegelte
Rezepte, Gruppen-, Partial- und Phasenreihenfolge. Jeweils ein 4800-Sample-
Fenster bei 48000 Hz; hoechstens ein PCM-Payload von 19200 Byte gleichzeitig.
Nach direkter Analyse werden Payload und darauf verweisende Sampleansicht
freigegeben. Keine Eingangsabschwachung, Normalisierung, Sattigung, Ersatzquelle
oder Aenderung des Faktors `0.5`.

Die Quellenfenster bleiben `[(n-1)*4800,n*4800)` auf `audio.sample`.
Native Snapshotindizes sind unveraendert `0,10,20,...,130`; Ganzzahligkeit,
Nichtnegativitaet und exakte Teilbarkeit des Fensterstarts durch 480 werden
vor der Analyse geprueft. Die direkte `analyze`-Methode liefert Werte, keine
rollende Indexzaehlung. Der daraus gebundene rohe `AuditoryReceptorState`
traegt bereits den nativen Index und das richtige Fenster vor NJ.

## Quellen- und Profilbindung

Vor der Materialisierung wurden die historischen Ausfuehrungs-, Siegel- und
Verifikationswurzeln sowie Quellen-, Generator-, Code- und Umgebungsbindungen
geprueft. Die Evaluationsplandatei wurde nur ueber ihre Bindung erhalten;
ihre Rollen und Ordnungskriterien wurden nicht angewandt.

| Bindung | Digest |
| --- | --- |
| Unveraenderte NT-Ausfuehrungswurzel | 512cab06237f98ca0481f6b16764e30bdd99bb18841f0fb204c5e4700ae8673d |
| Unveraendertes Quellensiegel | ab2f64627d3385592281b6b0b312968bd4ff6397dcc46ec72fafd5779dad676a |
| Historischer Vorversiegelungs-Pruefbeleg | 0b1ed1b7755ddd532d6af0c181a3abe1d8893e7c1fb8d9f3efa7a1a4817b229c |
| Rohprofil | 5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7 |
| Halbprofil | 4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f |
| Aktive Profil-/Traegerbindung | 5a409ab7be103daeacdab56d7b2ae7f37dcaffd5c57472b111276ced9f7c3b73 |

Unveraenderter `LogSpectralReceptor`: Hann-/FFT-/48-Band-Profil,
50..18000 Hz, Fenster 4800, Hopbindung 480. Genau eine
`project_auditory_half_v1`-Projektion je Rohzustand unter
`s2nj.auditory.hann48.output-half.v1`. Die aktive NumPy-Identitaet wurde
gegen die versiegelten Umgebungsdaten geprueft.

Die neue private NT-Anbindung verwendet die vorhandenen reinen
Kanonisierungs-, Hash- und atomaren Ablagehilfen. Vom historischen
NP-Materialisierungsmodul werden nur `read_root`, `binary_digest` und
`atomic_result` wiederverwendet, keine NP-Hauptfunktion oder Korpusbindung
umetikettiert. Historische Dateien und die NT-Vorversiegelung sind unveraendert.
Die neue Anbindung ist separat mit ihren eigenen Quellhashes vorab gebunden.

## Werte und unabhaengige Pruefung

`result.json` speichert pro Quelle vollstaendige originale Rohwerte und
tatsaechlich gerundete Halbwerte, native Fenster, Quellen-/Rezept-/PCM-Digests,
Rohzustands- und NJ-Projektionsdigests, Binary64-Hexdarstellungen und
F64LE-Byte-Digests. Der Aktivitaetsmarker des Rohzustands ist kein erzeugter
Kontaktframe und kein Feldkontakt.

Alle 672 Rohwerte sind endlich und nichtnegativ; alle 672 Halbwerte sind
endlich und liegen in `[0,1]`. Bei allen 14 Quellen sind die gespeicherten
Roh-Subnormal-, Halb-Subnormal- und Unterlaufindexlisten leer. Das ist nur der
Befund dieses Materialisats, keine Aufhebung der historischen S2-NM-Grenze
oder universelle Gleitkommagarantie.

**Numerische Offline-Pruefung:** Form und Wertebereiche, Hexdarstellungen,
Byte-Digests und Marker wurden geprueft. Fuer jede der 672 Komponenten wurde
aus dem gespeicherten Rohwert `x` vorwaerts `x * 0.5` berechnet und seine
Binary64-Bytefolge exakt gegen den gespeicherten Halbwert geprueft.
Keine Toleranz und keine Rekonstruktion `raw = half * 2`.

**Bindungspruefung:** Vollstaendigkeit und Reihenfolge aller Quellen,
native Indizes/Fenster, Profile und Traeger, Rohzustands-/Projektionsdigests,
Code- und Dateihashes, Zaehler, Groessen und Belegunveraenderlichkeit.
Keine erneute PCM-Erzeugung, FFT, Rezeptoranalyse oder NJ-Funktion.
Die Payload-/FFT-Herkunft wird offline durch ihre gespeicherten Bindungen
geprueft, nicht als unabhaengige Wiederholung der Sensorrechnung ausgegeben.
Quellenvektoren wurden auch nicht zur Bestaetigung der Exaktpaare verglichen.

## Ergebnisintegritaet und verbleibende Grenze

| Artefakt | Byte |
| --- | ---: |
| preregistration.json | 9557 |
| result.json | 143872 |
| verification.json | 1100 |

Gesamtbeleg unter 2097152 Byte, Verifikation unter 262144 Byte;
NJ-Einzelbelege innerhalb der gebundenen 16384 Byte.
Resultdigest:
`48a75e2957b1c2e65bc6e63f1a24200b3538fb779406d9abb9f2f2638704647f`.
Datei-SHA-256 vor/nach Verifikation identisch:
`eb7106c6b32300130aa5376623b07f9c6406aed183f10cea810300c17ddf49b0`.
Verifikationsdigest:
`8fe9e748a841a2b0a63e8e4536cdbc92151e6ff828c60310652926b02afeee59`.

Keine technische Abbruchstelle; `failure = null`. Alle gebundenen
Quell-/Code-/Versiegelungshashes vor/nach Materialisierung unveraendert.
Gates abschliessend `False`. Historische Belege, fremde Aenderungen und
Bootstrap bleiben unberuehrt.

Die 25 Distanzpaare, Quellenvektorgleichheiten und 24 Ordnungskriterien sind
weiterhin unausgewertet. Technisch gueltige Werte beweisen keine Trennleistung,
Bestandteilserkennung oder richtige Gesamtzuordnung. S2-NS bleibt geschlossen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses Materialisats
und der separaten Entscheidung ueber den gebundenen diagnostischen Vergleich
weiter; keine weitere Rezeptoranalyse erforderlich.
