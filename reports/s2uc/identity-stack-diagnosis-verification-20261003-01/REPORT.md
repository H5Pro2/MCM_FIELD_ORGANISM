# N2/M: begrenzte2×2-Diagnose abgeschlossen (2026-10-03)

Genau vier Replays mit je80 Positionen in gebundener Reihenfolge,320 Aufnahmen und320 Referenzfortschreibungen. Keine Warmups,zusätzlichen Kombinationen oder Zeitwiederholungen. Numerisch identische N2-Quelle,derselbe qualifizierte Frame-Visitor und aktiver Trace. Keine operative Optimierung und keine Rasterausführung.

## Isolierte Replayzeiten

| ID | Aufruf | Werteidentität | Wall s | Prozess-CPU s | Quellenaufbereitung ms | Export ms | Heappeak Byte |
|---|---|---|---:|---:|---:|---:|---:|
| A | direct | shared | 19.023107 | 19.015625 | 1.5710 | 3.6282 | 4316 |
| B | direct | json | 23.906571 | 23.812500 | 2.7375 | 4.0475 | 2860 |
| C | integrated | json | 25.304780 | 25.281250 | 2.9243 | 14.8665 | 2724 |
| D | integrated | shared | 21.679324 | 21.687500 | 1.7802 | 12.9961 | 2724 |

A:direkt/geteilt;B:direkt/JSON;C:integriert/JSON;D:integriert/geteilt. Der identische Timer sitzt unmittelbar um die originale baseline.replay-Funktion. Profil-Digest,Quellenaufbereitung und Export liegen außerhalb. Die Replayzeit enthält Referenzfortschreibung,interne Fachbelegerzeugung und sämtliche aktiven Beobachter einschließlich Zähler. Export A/B umfasst einen Ergebnisexport,C/D acht Hüllenexporte;die Spalte ist deshalb keine paarweise Datenträgerbenchmark. Separate Hüllenphasen und Quellen-CPU-Zeiten stehen in den Rohmessungen. CPU-Ticks kleiner Quellenphasen können auf dieser Plattform0 oder15,625 ms sein.

## Gezählte Arbeit

| Zähler | A | B | C | D |
|---|---:|---:|---:|---:|
| trace_events | 172135 | 172135 | 172135 | 172135 |
| stack_frames_checked | 1112367 | 1112367 | 1796817 | 1796817 |
| filename_checks | 1284502 | 1284502 | 1968952 | 1968952 |
| sample_visits | 76050 | 76050 | 76050 | 76050 |
| sample_value_slots | 3650400 | 3650400 | 3650400 | 3650400 |
| sample_float_identity_sum | 76050 | 3650400 | 3650400 | 76050 |
| unique_float_visits | 165973 | 3744788 | 3744788 | 165973 |
| frame_leaf_hits | 729704 | 729704 | 729704 | 729704 |
| visit_attempts | 12091237 | 12091237 | 12091237 | 12091237 |
| unique_object_visits | 4753373 | 8332188 | 8332188 | 4753373 |

Traceereignisse zählen alle an den Basisvisitor dispatchten Ereignisse. Stack-/Dateinamenprüfungen beziehen sich auf diesen Basisvisitor,inklusive seiner Eingangsfilterprüfung;die abgeleiteten Beobachter bleiben aktiv,werden aber nicht einzeln gezählt. unique_float_visits summiert nach dem jeweiligen seen-Filter noch neue Float-Identitäten je Tracecallback;es ist KEINE gleichzeitige Objektzahl. sample_float_identity_sum summiert getrennt die unterschiedlichen Float-Identitäten innerhalb jedes besuchten Samples.
Alle vier Kombinationen haben172135 Traceereignisse,76050 Samplebesuche und729704 Frame-Blattfalltreffer. Der qualifizierte Blattfall ist somit in allen Kombinationen gleich häufig wirksam. JSON erhöht die samplelokale Identitätssumme um3574350=47×76050 und die insgesamt besuchten noch nicht gesehenen Floats um3578815. Die Differenz4465 betrifft weitere Float-Wurzeln/Aliase außerhalb der samplelokalen Kardinalität;deren einzelnen Pfade wurden nicht separat protokolliert.
Die integrierte Hülle erhöht Stack- und Dateinamenprüfungen jeweils um684450=9×76050. Dieser Mehrbedarf ist bei beiden Wertedarstellungen exakt gleich. Umgekehrt sind die Float-/Objekt-/Sample-/Blattfallzähler für dieselbe Wertedarstellung in beiden Hüllen identisch. Die beiden Arbeitsunterschiede sind damit getrennt belegt.

## Faktoreffekte und Wechselwirkung

| Kontrast | Wall-Differenz s | CPU-Differenz s |
|---|---:|---:|
| identity_direct | 4.883464 | 4.796875 |
| identity_integrated | 3.625457 | 3.593750 |
| stack_shared | 2.656216 | 2.671875 |
| stack_json | 1.398209 | 1.468750 |
| identity_average | 4.254460 | 4.195312 |
| stack_average | 2.027213 | 2.070312 |
| interaction | -1.258007 | -1.203125 |

Identitätseffekt: B−A beziehungsweise C−D. Stackeffekt: D−A beziehungsweise C−B. Wechselwirkung: C−D−B+A. Die durchschnittlichen Effekte sind nur arithmetische Kontraste dieser vier Einzelmessungen,keine populationsbezogenen Schätzungen. Die negativen Wechselwirkungen (Wall−1,258007 s,CPU−1,203125 s) verbieten eine einfache additive Zeitgarantie. Die Arbeitszähler trennen die Faktoren,die gemessene Laufzeit ist trotzdem nicht exakt additiv.

## Gleichheit,Ressourcen und Grenzen

Alle vollständigen Fachbelege sind kanonisch gleich. Sämtliche Ressourcenmeterfelder stimmen exakt überein;kein Feld wurde nachträglich ausgeschlossen. Die vollständigen resources-Objekte wurden zusätzlich verglichen und sind wegen additional_python_peak nicht identisch: A4316,B2860,C2724,D2724 Byte. Alle übrigen Ressourcenfelder gleich. Die Abweichung wird erhalten,nicht normalisiert. Sie folgt weder allein der Wertedarstellung noch allein dem Stackfaktor;erstmalige Allokationen/Allocatorzustand sind mögliche,aber nicht separat gemessene Ursachen. Keine Warmups oder Wiederholungen zur Glättung.
Meter:Framepeak12,Slots2,kombiniert13,transiente Frameobergrenze12,Receipt454 Byte und UTF8-Obergrenze908 Byte. Zusatzheap maximal4316 unter16384 Byte. Alle Zustände,EMA und Ausgabeslots freigegeben;zensiertes Endziel81 in allen Armen. Die Diagnosezähler sind zusätzlicher Beobachteraufwand außerhalb der Policy-Heapprobe;dies ist keine neue operative Ressourcenqualifikation oder Gesamtprozess-RAM-Messung.
Zähleraufwand ist nicht null und nicht separat zeitlich abgezogen: Dict-Inkremente bei Besuchern und Blattfällen sowie eine temporäre ID-Menge pro Sample. Derselbe Zählercode läuft überall,aber sein Aufwand wächst selbst mit den gezählten Besuchen. Deshalb enthalten die4,25 s durchschnittlichen Identitätsmehrkosten auch Zählerkosten. Es gibt bewusst keinen fünften Lauf ohne Zähler. Feste Reihenfolge,keine Wiederholungen und kein Hostlastprofil;CPU-nahe Wallzeiten schließen Host-/Cache-/Frequenzeinflüsse nicht aus. Keine Aussage,dass die früheren42,06 s damit sekundengenau rekonstruiert seien.

## Abgrenzung der integrierten Diagnose

Verwendet werden V2.execute und dessen eingefrorener Engine-Bytecode mit derselben checked/active/MagicMock-Aufrufkette. Nur der Umfang ist auf einen N2/M-Arm reduziert;Manifestanzahlprüfung2→1. Fall-/Aggregationsprüfung erhält diagnostische Platzhalter,weil dies keine vollständige32-Fall-Auswertung ist. Sie liegt außerhalb der isolierten Replayzeit. Die vorab vorbereiteten Objekte werden beim Quelleneinlesen zurückgegeben,damit der geteilte Faktor erhalten bleibt;die exportierten Quellen sind numerisch identisch. Diese Änderungen sind im vorab gebundenen Diagnosecode enthalten.
Die Basisvisitor-Zähler werden ausschließlich im Speicher eingefügt. Der AST-Abgleich entfernt die markierten Zähleranweisungen und verlangt exakte Gleichheit zum qualifizierten Tracekörper. D2X01_COUNTER_AST_AND_SYNTHETIC_SNAPSHOT bestätigt zusätzlich die Zähler auf einem einzelnen synthetischen Snapshot ohne Replay. Historische Policy-/Hüllendateien und Bindungen sind unverändert.

## Genau ein minimaler Änderungsvorschlag – nicht umgesetzt

Den bestehenden geprüften Blattfall um einen ebenso strikt geprüften PerceptionSample-Blattfall ergänzen. Nur exakter PerceptionSample-Typ,exaktes tuple mit48 echten floats,sowie exakt skalare profile/owner/stream-Strings und index/start_sample/end_sample-Integer dürfen den rekursiven Abstieg überspringen. Der seen-Eintrag bleibt;Unterklassen,mutable/custom Payloads oder unklare Feldtypen laufen vollständig durch den bisherigen Visitor. Keine Wertededuplizierung,kein Cache,keine Änderung der Quelle,Policy oder Traceereignisse.
Begründung:76050 Samplebesuche führen bei JSON nachweislich zu Millionen zusätzlicher terminaler Float-Prüfungen,obwohl der Frame-Blattfall bereits gleich oft greift. Der Vorschlag beseitigt genau diesen semantisch unnötigen Abstieg bei bewiesen skalaren Samplefeldern. Stackoptimierung wird nicht zusätzlich vorgeschlagen. Notwendige spätere Abnahme:gleiche erreichbare Frame-IDs,Slots,transiente Maxima,Budgetfehler und Fachbelege;Fallbacktests mit in Feldern verborgenen Frames,Unterklassen und mutablen Werten;neutrale Zeit-/Speicherqualifikation mit aktivem Trace. Eine konkrete Einsparung oder die Einhaltung einer vollständigen Rasterstunde ist damit noch nicht bewiesen.

Gesamtdiagnose bis Abschlusszeitstempel:90.940278 s bei900 s Grenze. Dateiinventar und Hashes aller Unterordner in export-inventory.json. Kein Rastermaterialisieren,keine Rasterausführung und keine neue Rasterautorisierung. Raster32 bleibt geschlossen/global NOT_EVALUABLE. Nächste Entscheidung beim Projektleiter:genau diesen Sample-Blattfall samt begrenzter Qualifikation freigeben oder ändern.
