# S2-OA: neutrale Eininstanz-/Generationsqualifikation

## Technischer Abschluss

Lauf-ID: `s2oa-single-runtime-qualification-20260910-01`.
Genau ein Qualifikationsaufruf, 20/20 Tests bestanden, Exit-Code 0,
Status `S2OA_RUNTIME_QUALIFIED`. Kein Retry und keine weitere Testausfuehrung.

- [Vorregistrierung mit Inventar und Quellhashes](preregistration.json)
- [Ergebnis](result.json), [vollstaendiges Testprotokoll](stderr.txt)
- [Neutraler Gesamtbeleg](s2oa-neutral-continuous.json)
- [Unabhaengiger Pruefbeleg](s2oa-neutral-continuous-proof.json)
- [Vorab gebundener Umfang](../RUNTIME_QUALIFIKATIONSBINDUNG.md)

Ergebnisdigest:
`7820b6e4ee1121965067a1f55181f2d3f41218b9739ebf95a7c7cb3cc6efe7c4`.
Quellhashinventar vor/nach dem Test identisch:
`82504fd145c6802b352fab4e55be095385db2491687578890466fd3fc7f20109`.

Der private Anschluss liegt in `tools/_s2oa_private_runtime_binding.py`,
die unabhaengige Pruefung in `tools/_s2oa_private_runtime_verification.py`.
Historische Adapter, Regeln, Profile, Memorykerne und Defaultlimits wurden
nicht geaendert. Die Formationsbelege verwenden eine versionierte verlustfreie
Positionskodierung; vor Ausgabe wird die Rueckwandlung in den vollstaendigen
nativen Transaktionsbeleg auf Gleichheit geprueft.

## Tatsaechlich gepruefte Geschichte

Eine neutrale Hauptfixture verarbeitet ohne Reset 21 Ereignisse:
16 AV-Formationen und fuenf Hinweise. Hinzu kommen drei getrennte kleine
Fehlerfixtures. Insgesamt: 25 Ereignisse, 19 Formationsversuche,
21 NJ-Projektionen, null Rezeptoraufrufe und null Hauptlaufaufrufe.
Synthetische Rohzustandswerte, keine OA-Payloads und keine Quellenproduktion.

Die Hauptfixture erreicht `RECORDING_COMPLETE`, 6.576 Feldkontakte und zehn
Scanbelege einschliesslich Direktbaselines. Fortlaufende Modalitaetsfenster
und `s2oa-continuous-field-clock` sind gebunden. NJ liegt vor der gemeinsamen
Wahrnehmungsbindung. Die fuenf Hinweise sind read-only:

| Ereignis | Technisch gueltiges Ergebnis |
| --- | --- |
| 1 | ABSTAIN_NO_CONTEXT |
| 3 | CONTEXT_CANDIDATE_AVAILABLE |
| 7 | ABSTAIN_INTERNAL_AMBIGUITY |
| 17 | CONTEXT_CANDIDATE_AVAILABLE |
| 21 | ABSTAIN_NO_APPLICABLE_CONTEXT |

Generationen stammen aus den tatsaechlichen Transaktionen, nicht aus
Rollenerwartungen. Der erste visuelle Slow-Slot wird bei e04 erzeugt;
MATCHED bei e05/e06 erhaelt diese Generation und erreicht Support 3.
Weitere Inhalte belegen die restlichen visuellen Slow-Slots. Bei e20 wird
`ppb1.visual.default-live.v1.slot.000` ersetzt: gleiche Slot-ID, neue
Generation, Support 1. Der historische e17-Abruf bleibt als damaliger
Beleg gueltig, ist aber kein aktueller Verfuegbarkeitsbeleg fuer e21.
Der abgelaufene Fast-Eintrag traegt keine aktuelle Generationsbindung.

Die unabhaengige Pruefung kontrolliert 384 Generationspositionen,
16 Formationen, 73 Zustandsvalidierungspassagen, 10.416 Fast-Rangterme,
6.816 PPB-Auswahlterme und 10.752 Updatekomponenten. Scans enthalten
2.848 Vergleichskomponenten. Historische Zustands-, Auswahl- und
Updatebaselines werden ohne erneute Memoryfortschreibung verwendet.

## Fehler- und Abschlussgrenzen

Die unabhaengigen Fehlerfixtures bestaetigen:

- Fehler nach Erzeugung des B4-Kandidaten: keine teilweise Memoryuebernahme,
  Feldkontakt dennoch aufgezeichnet.
- Feldfehler: Feldzustand unveraendert, atomare Memoryformation unabhaengig
  abgeschlossen; Gesamtstatus technisch NOT_EVALUABLE.
- Scanfehler am Hinweis: Feldfortschreibung erfolgt, Memory bleibt read-only;
  unabhaengige Direktbaseline bleibt erreichbar, keine fachliche Auswertung.
- Fehler vor der Ereignisbindung: phasengebundener technischer Abschluss.

Manipulierte Zustands-, Quellen-, Zeit- und Generationsbindungen werden
abgewiesen. Gueltige Enthaltungen bleiben verifizierbar. `close()` beendet
den Lifecycle, ohne gespeicherte Memory- oder Feldwerte zu veraendern.

## Reale Beleggroessen

Alle Zahlen sind Byte kanonischer Artefakte, keine Prozessspeichermessung.
Die folgenden Zusatzbelege sind vollstaendig erzeugt, nicht Platzhalter:

| Klasse | Anzahl | Einzelgroesse | Summe | Unveraenderte Reserve |
| --- | ---: | ---: | ---: | ---: |
| NJ | 17 | 511..573 | 9.679 | 22 x 1.024 = 22.528 |
| Formation | 16 | 1.090..1.102 | 17.524 | 20 x 1.536 = 30.720 |
| Generation | 16 | 563..610 | 9.389 | 20 x 1.536 = 30.720 |

Der neutrale Hauptbeleg belegt 674.165 Byte. Einschliesslich der bestehenden
25.438 Byte administrativen Metadaten und der voll mitgezaehlten 162.321 Byte
historischen Quellenartefakte betraegt seine Gesamtbilanz 861.924 Byte.
Metadaten dieser Belegkombination: 33.922/65.536 Byte.
Tatsaechlich belegte gemeinsame Zusatzhuelle: 198.913/262.144 Byte.

Die volle prospektive Reservierung bleibt davon getrennt und unveraendert:
162.321 + 22.528 + 30.720 + 30.720 = 246.289/262.144 Byte.
Die kleinere neutrale Istbelegung hebt keine Reserve oder spaetere Grenze auf.

Die gesamte Qualifikationshuelle samt zusaetzlicher Vorregistrierung,
Ergebnis, Protokollen und Fehlerfixtures bleibt ebenfalls begrenzt:
Metadatenobergrenze 44.412/65.536 Byte; Pruefbelege zusammen
28.491/262.144 Byte; Gesamtobergrenze 995.008/4.194.304 Byte.
Die archivierten alten Quellenbelege bleiben mit ihrer dokumentierten
historischen Budgetabweichung erhalten, nicht rueckwirkend budgetkonform.

## Aussage- und Anschlussgrenzen

Qualifiziert ist die private Eininstanz-/Generationskomposition an neutralen
realen Datentypen und tatsaechlichen Memorytransaktionen. Kein OA-Funktionsbefund,
kein allgemeiner Dauerbetriebsnachweis und keine auditive Slow-Ersetzungsprobe.

Die Offline-Pruefung bindet NJ-Herkunftsdigests und die tatsaechlich gespeicherte
Projektion. Sie rekonstruiert keine ungespeicherten Rohspektren und rechnet
deren Halbierung nicht unabhaengig nach. Die Feldpruefung kontrolliert
Zeit-, Receipt- und Zustandsbindungen; sie ist kein unabhaengiger numerischer
Replay der Feldtrajektorie.

**Verbleibender konkreter Anschluss:** `SingleRuntime` akzeptiert derzeit
nur `NEUTRAL` mit maximal 21 Ereignissen und 16 Formationen. Der reale,
quellengebundene OA-Materialisierer und der geschlossene 28-Ereignis-
Haupteinstieg sind noch nicht angebunden. Ein realer Hauptlauf ist daher
nicht allein durch Oeffnen eines Gates ausfuehrbar. Dafuer ist eine separat
freigegebene minimale Quellen-/Haupteinstiegsanbindung erforderlich, ohne
historische Grenzen global zu lockern. Diese Restgrenze wird nicht durch
den Qualifikationsstatus verdeckt.

Hauptgate False; keine OA-Payloadverarbeitung und keine reale OA-Geschichte.
ME/MI bleiben gesperrt, Prognosezweig ruht. Keine Hypothesenanwendung.

RUECKMELDUNG ERFORDERLICH: Analystenentscheidung zum verbleibenden geschlossenen
Quellen-/Haupteinstiegsanschluss; noch keine reale Einmallauffreigabe ableiten.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser neutralen
Qualifikation und der Entscheidung ueber den kleinen verbleibenden
OA-Haupteinstiegsanschluss weiter.
