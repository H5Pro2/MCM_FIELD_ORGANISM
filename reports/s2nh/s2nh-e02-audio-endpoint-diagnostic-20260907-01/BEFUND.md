# S2-NH: einmalige Audioendpunkt-Diagnose e02

## Auftrag und Aussagegrenze

- Diagnose-ID: `s2nh-e02-audio-endpoint-diagnostic-20260907-01`.
- Ausgangscommit: `06d6eb9c817dfe30b1bfb2033afe541f54c6bec4`.
- Genau eine neue diagnostische Reproduktion, kein NH-Hauptlauf.
- Status: `DIAGNOSIS_COMPLETE`.
- Befund: `CONTACT_NORMALFORM_VIOLATION_REPRODUCED`.
- Der historische NH-Lauf bleibt unveraendert `NOT_EVALUABLE`. Seine nicht
  aufgezeichneten e02-Werte werden nicht nachtraeglich ersetzt. Die folgenden
  Werte stammen ausschliesslich aus dieser neuen Reproduktion.

## Einmalige Ausfuehrung

Arbeitsverzeichnis: `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.

```powershell
& C:/Python314/python.exe -m reports.s2nh.diagnose_e02_audio_once
& C:/Python314/python.exe -m reports.s2nh.verify_e02_audio_diagnostic
```

Beide Aufrufe genau einmal, beide Exit-Code `0`. Keine Tests, Wiederholung
oder vorgeschaltete Rezeptoranalyse. Der separate Verifikator importiert nur
die Standardbibliothek und erzeugt weder PCM noch Rezeptorzustaende.

| Umfang | Tatsaechlich |
| --- | ---: |
| PCM-Payloads erzeugt und vor Verarbeitung hashgeprueft | 2 / 2 |
| Audiofenster, ein frischer fortgefuehrter HearingPath | 2 |
| Hopaufrufe / abgeschlossene Hops | 20 / 20 |
| Rollende Rezeptorabschluesse | 11 |
| Aufgezeichnete Endpunkte / Werte | 2 / 96 |
| Video-, Rezeptorkontakt-, Memory-, Feld-, Kontext-, Runtimeaufrufe | jeweils 0 |
| Read-only-Belegpruefungen | 1 |

Nur `nh-a00` (e01) und `nh-a01` (e02) wurden aus den unveraenderten versiegelten
Rezepten erzeugt. Float32-Rechenfolge und bestehender Eingangsparameter blieben
unveraendert. Hoechstens ein PCM-Payload gleichzeitig; nach Verarbeitung
freigegeben, keine Rohdatenablage. Kein neues Skalieren, Clipping oder Normalisieren.

## Gemessene Endpunkte vor Kontaktbildung

| Endpunkt | Native Uhr / Samplefenster | Snapshot | Nicht endlich | abs(value) > 1 |
| --- | --- | ---: | --- | --- |
| e01 | `audio.sample`, `[0,4800)` | 0 | keine, 48/48 endlich | keine |
| e02 | `audio.sample`, `[4800,9600)` | 10 | keine, 48/48 endlich | genau Bandindex 30 |

Der e02-Endpunkt ist an die gemeinsame Zeit `[190000000,200000000)` und die
Felduhr-Metadaten `s2nh-transfer-field-clock` gebunden. Keine Felduhrfunktion
wurde aufgerufen; native Samplezeit und gemeinsame Zeit bleiben getrennt.

Einziger verletzender Wert, Bandindex **0-basiert**:

- Bandindex: `30`.
- Carrier: `auditory.log_hz.2141.176418`.
- Unveraenderter Binary64-Wert: `1.0062227733397906`.
- Exakte Hexdarstellung: `0x1.0197d0cffc1d4p+0`.
- Binary64-Bits, Big-Endian: `3ff0197d0cffc1d4`.
- `is_finite = true`, `abs_gt_one = true`.

Alle 48 e02-Werte sind einzeln mit Bandindex, Carrier, Wert, Hexdarstellung,
Bits und beiden getrennten Praedikaten gespeichert. NaN/Inf sind in der
Diagnoseform explizit typisiert; solche Werte traten hier nicht auf. Der Beleg
enthaelt keine nichtstandardisierten JSON-Zahlen.

Damit ist in dieser Reproduktion die Teilbedingung `abs(value) > 1`
nachgewiesen, nicht die Teilbedingung fehlender Endlichkeit. Der
`ReceptorContactFrame` wurde absichtlich nicht konstruiert: Gemessen wurde
unmittelbar davor. Es wurde weder eine Exception erneut ausgeloest noch eine
Korrektur aus dem Wert abgeleitet.

## Bindungen und lesende Pruefung

- Ausfuehrungsplandigest: `47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4`.
- e01-Payload-SHA-256: `89197158e5ccb608e933156157fbcaaf124ee10ba92cfd007d56e2e8801bfb89`.
- e02-Payload-SHA-256: `6e73faa09d0302e2a499b12174036e2658acdde3f44b16b6ec51281c49b728cc`.
- Ergebnisdigest: `bd0f535fbdbb40e3bcef430affa37f17c0e21b727a19cf2659495ba692ecef31`.
- Ergebnisdatei-SHA-256: `1dcc60b438f198d6d8f8eae98c3792b966ddbe79ce63e046d23aed383ba7d3f8`.
- Verifikationsdigest: `5a560b31573a09f88bfa0e04e5311af88ec4b7344ffa64b173b71043d3434eca`.
- `evidence_valid = true`, `read_only = true`, `file_unchanged = true`.
- 111 Datei-SHA-256-Bindungen vor/nach identisch, einschliesslich Quellenplan,
  qualifiziertem Code, Diagnosecode und historischem NH-Ergebnis.
- Python-, Generator-, NumPy-, Profil- und Konfigurationsidentitaet stimmen
  mit der versiegelten Bindung ueberein und sind im Ergebnis enthalten.
- Beide Hauptgate-Deklarationen bleiben `False`; die Hauptlaufmodule wurden
  nicht importiert. Es gab keine Gateumschaltung.
- Ergebnisgroesse: 55.569 Byte bei vorab begrenzten 131.072 Byte.

Der Verifikator pruefte Bindungen, Fortschritt, Endpunktform, native Zeiten,
Binary64-Kodierung und die beiden Praedikate nur aus dem gespeicherten Beleg.
Keine Rezeptorwiederholung und keine erneute historische Verifikation.

## Abschluss

Dieser Diagnoseauftrag ist abgeschlossen. S2-NH bleibt `NOT_EVALUABLE`;
S2-NG und fruehere Funktionsbefunde bleiben unveraendert. Keine Aussage zu
Abrufselektivitaet oder Transferleistung wird daraus gewonnen.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zur
Rezeptor-/Kontaktgrenze auf Grundlage dieses neuen e02-Wertebelegs weiter.
Keine Korpuskorrektur und kein weiterer Lauf sind damit freigegeben.
