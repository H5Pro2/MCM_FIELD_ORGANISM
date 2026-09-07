# S2-NH: statische Rezeptorkontaktgrenze bei e02

Lesender Befund vom 2026-09-07 zum unveraenderten
[Abbruchbeleg](s2nh-runtime-comparison-20260907-01/recording.json).
Keine neue Lauf-ID, Payloadregeneration, Rezeptoranalyse, Tests,
Nachberechnung, Codekorrektur oder erneute Verifikation.

**Ergebnis:** Unter dem gebundenen Aufrufpfad ist die Ausnahme auf die
Werte-Normalformpruefung des Rezeptorkontakts eingrenzbar. Ein konkreter
Wert groesser als 1 ist damit weiterhin nicht gemessen oder belegt:
derselbe Fehlerzweig weist auch nichtendliche Werte ab.

## Aufrufpfad und belegter Fortschritt

`Materializer.run_once` erzeugt genau einen fortgefuehrten HearingPath:
`push -> RollingLogSpectralReceptor.push -> LogSpectralReceptor.analyze
-> AuditoryReceptorState -> from_auditory_receptor_state
-> ReceptorContactFrame.__post_init__`.

Der [Materialisierer](../../tools/_s2nh_private_runtime_binding.py), Zeilen
178-190, setzt `audio_windows=2` und `audio_snapshots=11` erst nach den zehn
erfolgreich zurueckgekehrten e02-Hops. Genau diese Zaehler, insgesamt
20 Hops, `completed_events=1`, `visual_frames=1`, Quelle `nh-a01` und
Phase `RECEPTOR_ANALYSIS` stehen im historischen Beleg.
Die folgende Endpointpruefung haette `S2NHRuntimeError`, nicht
`ReceptorContractError`, erzeugt. In diesem Audiopfad bleibt als Aufruf
mit der aufgezeichneten Ausnahmeklasse die Kontaktbildung in Zeile 190.
Das ist Kontrollflussableitung aus Code und vorhandenem Fortschritt,
kein neuer Trace und keine Wiederholung.

## Vollstaendige Fehlerbedingungen an dieser Grenze

Der [Kontaktvertrag](../../mcm_field_organism/receptor_contract.py),
Zeilen 21-90 und 197-210, verlangt in Pruefreihenfolge:

| Ausloeser fuer ReceptorContractError | Einordnung fuer e02 |
| --- | --- |
| modality_id, geometry_id, snapshot_id oder clock_id kein String bzw. nicht `^[a-z][a-z0-9_.-]*$` | Ausgeschlossen im gebundenen Pfad: `auditory`, unveraenderte Profilgeometrie, `auditory.receptor.10`, `audio.sample`. Die gemeinsamen Identitaeten passierten bereits e01. |
| Start/Ende bool oder nicht int, Start negativ, Ende nicht strikt groesser als Start | Ausgeschlossen: fortgefuehrte ganzzahlige Zaehler; versiegeltes e02-Fenster 4800..9600, Snapshotindex 10. |
| Traegerfolge leer oder doppelte Traeger | Ausgeschlossen: dieselben 48 Kanal-IDs desselben Rezeptorobjekts wie bei e01; keine Neuerzeugung oder Mutation zwischen den Ereignissen. |
| Einzelne carrier_id verletzt technische Identifierform | Ausgeschlossen durch dieselbe unveraenderte, bei e01 akzeptierte Kanalfolge. |
| Umwandlung der Werte mit `float(...)` wirft TypeError/ValueError | Ausgeschlossen im vorliegenden Erzeugungspfad: analyze gibt bereits ein Tupel von Python-float-Werten zurueck; HearingPath reicht es unveraendert weiter. |
| Wertetupel leer | Ausgeschlossen durch 48 Filterbankzeilen und die zeilenweise Ausgabe. |
| Mindestens ein Wert nicht endlich ODER `abs(value) > 1.0` | Verbleibender kombinierter Fehlerzweig; welcher Teil zutraf, Bandindex, Wert und Ausmass fehlen. |
| Anzahl Werte ungleich Anzahl Traeger | Ausgeschlossen: Werte und Traeger stammen aus derselben unveraenderten 48-Band-Konfiguration. Diese Pruefung folgt erst nach der Werte-Normalform. |

Der Kontaktvertrag verlangt nicht allgemein 48 Dimensionen, sondern
Gleichheit von Werte- und Traegerzahl. Die konkrete 48 stammt aus dem
gebundenen Profil. Er prueft auch nicht die Kontinuitaet zu einem vorherigen
Frame; er validiert hier nur das einzelne positive Zeitintervall.

Weitere gleichnamige Ausnahmen liegen ausserhalb der erreichten Grenze:
`CommonFieldTime` prueft ebenfalls Identifier und ganzzahlige positive
Intervalle, wird aber erst in `RECEPTOR_BINDING` erzeugt (Zeilen 198-202).
Dockmap-Paarform, eindeutige Carrier/Neuronen sowie Modalitaets-, Geometrie-
und Carrier-Mengenabgleich werden bei diesem Kontaktbau nicht aufgerufen.
`OrganismTimedReceptorFrame` besitzt dagegen `ReceptorTimeAlignmentError`.
Die NH-eigene strengere Pruefung `0 <= v <= 1` folgt erst in Zeile 201 und
wuerde `S2NHRuntimeError/RECEPTOR_NORMALFORM_INVALID` liefern. Sie ist nicht
die aufgezeichnete Ausnahme. Auch ein nur negativer endlicher Wert mit
Betrag hoechstens 1 wuerde diesen frueheren Kontaktfehler nicht erklaeren.

## Garantierte Ausgabeform versus erforderliche Normalform

[LogSpectralReceptor](../../mcm_field_organism/log_spectral_receptor.py),
Zeilen 81-90, 95-132 und 157-166: Eingangstyp, Dimension, Endlichkeit und
PCM-Betrag hoechstens 1 werden validiert. Die Ausgabe ist ein Float-Tupel
aus `sqrt(sum(square(weights * spectrum), axis=1))`; die Spektralbetraege
werden zuvor mit `2/window_gain` skaliert. Das ist eine Filterbank-RSS,
keine ausdrueckliche Begrenzung oder Ausgangspruefung auf hoechstens 1.
Auch Endlichkeit der Ausgabe wird nicht eigens geprueft.
[BroadbandHearingPath](../../mcm_field_organism/broadband_hearing_path.py),
Zeilen 106-128, ergaenzt Zeit/Identitaet und Zero/Energy-Status, aber keine
Ausgangsnormalisierung. AuditoryReceptorState hat keinen eigenen Validator.

**Statisch nachgewiesen** ist somit die fehlende Ausgangsgarantie fuer den
engeren Kontaktvertrag und, unter dem unveraenderten Codepfad, die
Lokalisierung auf dessen kombinierten Normalformtest. Nicht nachgewiesen
ist ein bestimmter numerischer Grenzverstoss. Die
[versiegelte Quellenwurzel](s2nh-source-preseal-20260906-01/execution-plan.json)
bindet 48 Baender, 4800 Samples, 480er Hops und das passende e02-Fenster.
Gueltige PCM-Amplituden und bestandene Payloadhashpruefung implizieren
keine gueltigen Spektralenergien. Der unveraenderte NH-Plan nennt diese
fehlende Garantie bereits; der fruehere MT-Befund ist kein NH-Messbeleg.

## Genau fehlende Information und Grenze

Zur eindeutigen numerischen Diagnose fehlt fuer den tatsaechlich
uebergebenen e02-Zustand, Snapshot 10/Fenster 4800..9600, die erste verletzte
Teilbedingung (`nicht endlich` oder `Betrag > 1`) samt Bandindex und
unveraendertem Floatwert bzw. NaN/Inf-Kennzeichnung. Der generische Code
`NH_TECHNICAL_ERROR` enthaelt das nicht. Selbst der Fehlertext aus Zeile 43
wuerde beide Alternativen zusammenfassen. `source_receipts=[]` und
`materialization=null` enthalten keine rekonstruierbaren e02-Werte.
Band, Ausmass und ein eventueller Korrekturfaktor bleiben unbestimmt.

Keine neue Diagnoseinfrastruktur oder Messung wurde vorbereitet.
Historischer Lauf weiterhin **NOT_EVALUABLE**, beide Gates False;
S2-NG und bisherige Funktionsbefunde unveraendert. Nur dieses Dokument
wird versioniert, keine historischen Belege oder fremden Aenderungen.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung ueber den
minimalen fehlenden e02-Wertebeleg weiter; ohne neue Freigabe keine Messung,
Korrektur oder erneute NH-Ausfuehrung.
