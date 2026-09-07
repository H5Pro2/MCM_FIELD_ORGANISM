# S2-NP: einmalige Rezeptor-/NJ-Materialisierung

Lauf-ID `s2np-receptor-nj-materialization-20260907-01`, 2026-09-07.
Ausgangsstand `1ad3637`. Genau ein Materialisierungsaufruf und anschliessend
genau eine unabhaengige read-only Belegpruefung, kein Retry oder Vorlauf.

```powershell
& C:/Python314/python.exe -m reports.s2np.materialize_once
```

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.
Exit-Code **0**. Materialisierung `RECEPTOR_NJ_MATERIALIZATION_COMPLETE`,
Belegpruefung `S2NP_MATERIALIZATION_VALID`, `failure = null`.

## Tatsaechlicher Umfang

| Schritt | Abgeschlossen |
| --- | --- |
| NP-Payloadregenerationen in versiegelter Reihenfolge | 12 |
| Payloadhashpruefungen vor jeweiliger Analyse | 12 |
| Direkte LogSpectralReceptor.analyze-Aufrufe / Rueckgaben | 12 / 12 |
| Gespeicherte rohe Rezeptorwerte | 576 |
| project_auditory_half_v1-Aufrufe / Rueckgaben | 12 / 12 |
| Gespeicherte halbierte Werte | 576 |
| Vollstaendige quellengebundene Materialisate | 12 |
| Unabhaengige Belegpruefungen | 1 |

Ein unveraenderter direkter Rezeptor, keine rollende Pipeline. Je Quelle
ein PCM-Fenster mit 19.200 Byte; dessen NumPy-Eingabesicht teilt den
Bytepuffer. Sicht und Payload werden nach der Analyse freigegeben, bevor
die naechste Quelle erzeugt wird. Kein PCM-Rohpayload wird gespeichert.

Die zwoelf Quellen bleiben np-a01..np-a12 mit getrennten Identitaeten und
Zeiten, auch fuer die vorversiegelten Exaktkopien. Keine Erhaltungsauswertung
oder neue Paarpruefung dieser Kopien. Die Fenster liegen auf der gebundenen
Uhr `audio.sample`; Snapshotindices 0,10,...,110 sind direkte Fensterbindungen
auf dem Hopraster, keine behaupteten rollenden Abschlusszaehler.

Der `AuditoryReceptorState` traegt seinen vorhandenen deskriptiven
ACTIVE_ZERO-/ACTIVE_ENERGY-Status fuer NJ. Es wird weder ein normalform-
gebundener `ReceptorContactFrame` noch ein Feld-/Memorykontakt konstruiert.

## Werte und technische Gueltigkeit

`result.json` speichert fuer jede Quelle:

- Quellen-, Rezept- und PCM-Digest sowie den vor Analyse geprueften Hashbezug;
- den tatsaechlichen Rohzustand mit allen 48 Rohwerten, nativen Fenstern,
  Traeger-IDs und eigenem Zustands-/Wertedigest;
- die tatsaechliche NJ-Projektion mit allen 48 gerundeten Werten,
  Original-/Halbprofilidentitaet, Rohzustandsbindung und Projektionsdigest;
- beide Binary64-Hexlisten und die Digests ihrer Little-Endian-Binary64-Bytefolgen;
- getrennte rohe/halbierte Subnormalmarker und NJ-Unterlaufmarker.

Alle gespeicherten Rohwerte sind endlich und nichtnegativ; alle NJ-Werte
sind endlich und in `[0,1]`. Die rohe Spektralausgabe wurde nicht vor NJ auf
`[0,1]` eingeschraenkt. Bei allen zwoelf Quellen sind die gespeicherten
Subnormal- und Unterlaufindexlisten leer. Keine allgemeine Gleitkommagarantie
und keine Aufhebung der historischen S2-NM-Profilgrenze daraus ableiten.

Keine Eingangsskalierung, kein Clipping, keine dynamische Normalisierung
oder Quellenaenderung. Die einzige Ausgangsprojektion war NJ mit festem `0.5`.

## Numerische Pruefung gegen Bindungspruefung

Die separate Pruefung hat **576 vorwaerts gerichtete Binary64-Halbierungen**
aus den gespeicherten Rohwerten unabhaengig nachgerechnet und per Bytevergleich
mit den gespeicherten Ausgangswerten verglichen. Alle stimmen exakt ueberein,
ohne Toleranz oder Rundung zur Ergebnisangleichung. Dazu wurden Endlichkeit,
Wertedomaenen, Hexdarstellungen, Binary64-Digests sowie Subnormal-/Unterlauf-
marker kontrolliert. Der NJ-Projektionsaufruf wurde nicht wiederholt.

Reine Bindungspruefungen betrafen Quellen-/Payloadhashverknuepfungen, native
Zeiten, Profile und Traeger-IDs, Rohzustands-/Projektions-/Gesamtbelegdigests,
Codehashes, Zaehler, erlaubte Formen, Groessen und Zustandsunveraenderlichkeit.
Alle 19 vorab gebundenen Code-/Plan-/Belegdateien blieben unveraendert.

**Nicht unabhaengig neu berechnet:** PCM-Erzeugung/PCM-Hash aus erneut erzeugten
Bytes, FFT-/Filterbankreduktion und Bandgeometrie. Die Pruefung bestaetigt hier
gespeicherte Herkunfts-/Codebindungen, nicht eine zweite Rezeptorausfuehrung.
Insbesondere wurde kein Rohwert aus halbierten Werten zurueckrekonstruiert.

## Beleg- und Profilbindungen

| Bindung | Digest |
| --- | --- |
| Vorversiegelte Ausfuehrungswurzel | bae2b0ef565a5117c28984d40753da39cc1ca82b576e59864c72d57212254664 |
| Vorversiegeltes Siegel | a72aa07c9dc153f29a187470bce76fb918ce8cbbaeb4f2666c700fb719bf307b |
| Rohprofil | 5c6b2b19281a44023497b435a96b1051905af4bbac493cae7e699ea1320392c7 |
| NJ-Halbprofil | 4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f |
| Aktiver Materialisierungsprofilbeleg | 517dad5f5fc1c686aa5322fb42790525589c84c48aeed049243b38038dbc447f |
| Gesamtmaterialisat record_digest | f548fa82983390465854b1c1b4824c2a32f5b73669cb85c01dc0de853151b9f7 |
| result.json Datei-SHA-256 vor/nach Pruefung | 59796211f0203216a9c71c5b1e93a0326ebcc6d947e7c7ad7d4910d97307f430 |
| Separater verification_digest | c2dc1ce3ebf7d2124d315adb090c140b0593b13e40c503f93773a0bbb0860be2 |

`preregistration.json` wurde vor Rezeptorinitialisierung und erster Quelle
geschrieben: 9.122 Byte. `result.json`: 125.094 Byte, atomar ueber eine
exklusive temporaere Datei veroeffentlicht. `verification.json`: 1.084 Byte.
Alle Grenzen eingehalten: Gesamtbeleg hoechstens 2.097.152 Byte, einzelne
NJ-Projektion hoechstens 16.384 Byte, Vorregistrierung/Pruefbeleg jeweils
unter 65.536 Byte. Kein neuer Prozesspeaknachweis.

Neue Aufrufbindung:

| Datei | SHA-256 zum Lauf |
| --- | --- |
| tools/_s2np_private_receptor_materialization.py | bcb7e37e2a3aa4a32eb35b40c60ec4ed7ccb59a298837e5889fa0ff4bff6f7e3 |
| tools/_s2np_private_materialization_verification.py | aafeca07b68d29662b015ff5a9af1c9ff4797542c890ca9cbe9b62aebb47025f |
| reports/s2np/materialize_once.py | ae5dd570df4120928013cf97bfd49ca0f07f50257ffdac4d001776a634076f8e |

CPython-/math-/NumPy-Bindungen wurden vor Analyse gegen die Vorversiegelung
geprueft; der tatsaechlich geladene NumPy-Build ist zusaetzlich aufgezeichnet.
Rezeptor, NJ, Generator und historische Belege wurden nicht geaendert.

## Ausfuehrungsgrenze

Paarabstaende, Maskenvergleiche, Trefferentscheidungen, fachliche Auswertung,
Memory, Feld, Kontext und Runtime: **0 Aufrufe**. Keine Tests oder weitere
Qualifikationsrunde. Kein Gate geoeffnet; Hauptgates bleiben `False`.
Fremde Aenderungen und Bootstrap bleiben unberuehrt und ausgeschlossen.

Die zwoelf technisch gueltigen Vollvektoren stehen als eingefrorene
Rezeptorevidenz bereit. Noch kein Abdeckungs-, Trennungs-, Erhaltungs- oder
Abrufbefund. Auch die Vollsichtdiagnose wurde nicht ausgefuehrt oder freigegeben.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses Materialisats
und der getrennten Freigabe des begrenzten Abdeckungsvergleichs weiter.
