# S2-OA: Quellen-/Haupteinstiegsanschluss neutral qualifiziert

Lauf-ID `s2oa-main-binding-qualification-20260910-01`.
Genau ein Testaufruf: **14/14 bestanden**, Exit-Code 0,
`S2OA_MAIN_BINDING_QUALIFIED`. Kein Retry, keine Wiederholung der alten 20 Tests.

[Vorregistrierung](preregistration.json), [Testprotokoll](stderr.txt),
[Ergebnis](result.json), [Vollhuellenpruefung](reports/s2oa/s2oa-continuous-runtime-20260910-01/verification.json).
Ergebnisdigest:
`9014fff8ef1394feb6808cb9fdedec645a1afae7476317232b9dae71ffd61c27`.
Quellhashinventar vor/nach identisch:
`03303b65607aa3d5dfcc7899bc7ca4e33135baf9e6efd6f5b929f289dea0c2aa`.

## Anschluss und Beobachtung

Neuer expliziter OA-Modus in `tools/_s2oa_private_main_binding.py`:
`run_main_once(run_id)`, genau 28/20/2/6, eine Runtimeinstanz.
`tools/_s2oa_private_main_verification.py` bindet `verify_once(out)` und
das danach gesperrt/freigegeben auswertende `evaluate_once(out)` an.
Die bisherigen NEUTRAL-Limits, Module, Adapter, Regeln und Memorykerne
bleiben bytegleich. Neue Version separat durch diese Qualifikation gebunden.

Historische Versiegelung und korrigierte administrative Referenzen wurden
read-only geladen und geprueft. Im neutralen Ladecheck wurde nur die noch
nicht existierende neue Qualifikationsantwort durch ihre Vorregistrierung
vertreten; der reale Einstieg verlangt das bestandene Resultat mit Hashkette.

Die vollstaendige Funktionsfixture verwendet andere, synthetische Nullquellen
und eine andere Reihenfolge, nicht die reale OA-Geschichte. Tatsaechlich:
22 direkte Audioanalysen, 26 visuelle Analysen, 22 NJ-Projektionen;
28 Ereignisse, 20 Formationen, acht read-only Hinweise, 8.544 Feldkontakte
und 16 Scanbelege in **einer** fortgesetzten Runtime. Alle Vorkommen wurden
separat analysiert. Keine OA-Payloads und keine Hauptlaufbehauptung.

Native Zeiten, unterschiedliche Modalitaetsfenster, explizite OA-Felduhr,
Hash vor Analyse und NJ vor Audiokontakt sind abgesichert. CLOSED nach
Ereignis 28; close veraendert weder Memory- noch Feldwerte.
Die unabhaengige Vollpruefung erreicht 20 Formationspruefungen,
105 Zustandsvalidierungen, 6.384 Fast-Rangterme, 6.048 PPB-Auswahlterme,
13.440 Updatekomponenten, 480 Generationspositionen und 4.048 Scanvergleiche.

Die getrennte neutrale Auswertung meldet absichtlich **FALSIFIED** fuer
unpassende Sollinventare/Erwartungen. Gueltige Enthaltungen bleiben technisch
verifizierbar. Dies ist kein fachlicher OA-Befund.

## Vollstaendige Bytebilanz

| Belegklasse | Anzahl | Einzelbytes | Summe / Reserve |
| --- | ---: | ---: | ---: |
| NJ | 22 | 511..573 | 12.482 / 22.528 |
| Formation | 20 | 1.090..1.102 | 21.932 / 30.720 |
| Generation | 20 | 563..590 | 11.623 / 30.720 |

Gesamtbelegdatei: 811.926 Byte. Einschliesslich aller zugeordneten externen
Referenzen: 1.023.706/4.194.304 Byte. Metadaten dieser Kombination:
56.013/65.536 Byte. Gemeinsame Zusatzhuelle: 213.745/262.144 Byte, darin
162.321 historische Quellenbytes plus 5.387 Byte neutrale Quellen-/
Evaluationsbindung und saemtliche oben genannten Zusatzbelege.

Die groessere Qualifikationsablage einschliesslich Fehlerfixtures,
Pruefbelegen und Protokollen ist im Ergebnis separat bilanziert:
Metadatenobergrenze 59.625/65.536 Byte; Gesamtobergrenze
1.482.960/4.194.304 Byte; Verifikationsbelege zusammen
37.587/262.144 Byte. Getrennte neutrale Auswertung: 95.020/262.144 Byte.
Diese Zahlen betreffen die gebundenen Belegklassen vor diesem narrativen
Abschlussbericht, keine Prozessspeichermessung oder Laufzeitgarantie.
Auch mit diesem Bericht als zusaetzlicher Metadatenbelegung bleiben
hoechstens 65.000 Metadatenbyte und 1.489.000 Gesamtbyte belegt;
der historische Qualifikationsbeleg wird dafuer nicht veraendert.

Die volle kuenftige OA-Reservierung bleibt 246.289/262.144 Byte.
Istbelegung ist keine Grenzerhoehung. Historische Budgetabweichung bleibt
unveraendert dokumentiert. Ein abgewiesener Schreibkonflikt hinterliess
absichtlich eine separate Zwei-Byte-Pendingdatei; auch sie ist mitgezaehlt.

## Fehler und verbleibende Freigabe

Drei isolierte Fehlerfixtures pruefen den neuen Einstieg: BINDINGS vor
Materialisierung (0 Ereignisse), FORMATION mit MEMORY_BRANCH_FAILED bei
Ereignis 2, CUE mit PRIMARY_SCAN_FAILED bei Ereignis 1. Fortschritt und
Snapshots bleiben gebunden; Feldfortschreibung ist unabhaengig, Runtimes
geschlossen, keine fachliche Teilauswertung. Die letzten beiden Fixtures
verwenden nur neutrale bereits gebundene Testeingaben, keine erneute
Materialisierung und keine neuen realen Erfahrungen.

Die alte 20/20-Qualifikation traegt weiterhin die spezifischen Ersetzungs-
und Generationstests. Die neue 14/14 prueft den dazugekommenen Hauptpfad.
Offline-NJ-Pruefung bleibt Herkunfts-/Projektionsbindung, kein Rohspektren-
oder Halbierungsreplay. Feldreceipts sind kein numerischer Feldreplay.

Gates False, reale OA-Ausfuehrung weiterhin gesperrt. ME/MI gesperrt,
Prognosezweig ruhend. Historische Belege und fremde Aenderungen unveraendert.

RUECKMELDUNG ERFORDERLICH: separate Entscheidung ueber den einmaligen realen
OA-Hauptlauf; die neutrale Qualifikation ersetzt diese Freigabe nicht.

WEITER: Am besten geht es jetzt mit der Analystenpruefung der Anschluss-
qualifikation und der separaten OA-Hauptlaufentscheidung weiter.
