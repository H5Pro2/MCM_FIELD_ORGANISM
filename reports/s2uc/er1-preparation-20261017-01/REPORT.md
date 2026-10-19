# ER1: geprÃ¼ftes Implementierungs- und Neutralpaket

2026-10-17. Status: **NEUTRALPAKET_GEPRUEFT_ZUR_ABNAHME**.
Fortsetzung Workflow `8d1b85cf-cad9-45fd-b0a6-90e43bb95067`; keine Doppelbeauftragung.
Der Konzeptvertrag ist angenommen. Dieser Bericht beansprucht weder Paketabnahme
noch Forschungsfreigabe. AusschlieÃŸlich MCM_FIELD_ORGANISM.

## Ergebnis und Mechanismus

E verwendet unverÃ¤ndert FactorRecencyArm und MultiErrorAdapter. F fÃ¼hrt dieselben
hÃ¶chstens zwei Beobachtungsendmarken und dieselbe vollstÃ¤ndige BestÃ¤tigungsregel;
nur remove/append der Retained-Reihenfolge entfÃ¤llt. F hat einen eigenen exakt
geprÃ¼ften Adapterkonstruktor. U-Auswahl, Feedback, Promotion und Zulassung sind
unverÃ¤ndert geerbte Methoden; Test 08 prÃ¼ft ihre FunktionsidentitÃ¤t. CR1, K1 und A1
werden in keinem ER1-Arm aktiviert. Historische Policydateien wurden nicht geÃ¤ndert.

16/16 fokussierte Tests bestanden. Drei archivierte neutrale FÃ¤lle: 32, 32 und
44 Frames. Je Fall zwei frische Messarme und zwei frische Capture-Arme, zusammen
12 Arme. Alle ReferenzprÃ¼fungen, ArchivprÃ¼fungen und Cleanups bestÃ¤tigt.

Der kurze Regressionseingang A-A-D-D-A-Z-Z liefert zwei getrennte Zeugen:

- A stammt aus Originalordinalen 1â€“4, D aus 9â€“12. Vor der ersten Umordnung
  bei Frame 20 sind die unmaskierten gemeinsamen ZustÃ¤nde gleich. Beide Arme
  fÃ¼hren fÃ¼r A dieselbe aktualisierte Endmarke 20.
- Bei Z-Promotion an Frame 28 verdrÃ¤ngt E die neuere D-Spur 9â€“12; F verdrÃ¤ngt
  A 1â€“4. Ein vollstÃ¤ndiger ungleicher Zwischenblock liegt zwischen A-BestÃ¤tigung
  und spÃ¤terer Wiederverwendung.
- Im A-Anschluss wÃ¤hlt E an Ziel 31 Original 1â€“4, Offset 0, mit vorherigem
  tatsÃ¤chlich Ã¼bernommenem Feedback. MAE E=0, F=0.25.
- Im D-Anschluss wÃ¤hlt F an Ziel 31 Original 9â€“12, Offset 0, mit vorherigem
  tatsÃ¤chlich Ã¼bernommenem Feedback. MAE E=0.25, F=0. Dieser Zeuge belegt
  ausdrÃ¼cklich den Preis verlorener neuerer Erfahrung.
- Im lÃ¤ngeren Fall unterscheiden sich spÃ¤tere BestÃ¤tigungen und Aufnahmen.
  F nimmt A erneut mit Originalen 29â€“32 auf und promoviert diese an Frame 36.
  Wertegleichheit wird nicht als Fortleben der alten Originale 1â€“4 gezÃ¤hlt.

Das sind technische neutrale Zeugen, kein neuer Forschungsbefund und kein
Nettonutzennachweis. Der bereits bekannte FIFO-Grundmechanismus wird nicht als
neue Entdeckung ausgegeben.

## UnabhÃ¤ngige Referenzen und Kostenbelege

`_s2uc_er1_stock_reference.py` ist eine eigene, von Produktionsarmen unabhÃ¤ngige
Bestandsfortschreibung. `_s2uc_er1_reference.py` fÃ¼hrt je Arm eigene Fehlerzellen,
Tickets, Promotionen, Originale, U-Auswahl und Feedback. Jeder Wahrnehmungs- und
Feedbackschritt wird geprÃ¼ft. Nach der ersten Umordnung werden echte Unterschiede
zugelassen; keine Bankbytes oder Bestandsdaten werden wegmaskiert.

`_s2uc_er1_archive.py` prÃ¼ft Capture-Anker und vollstÃ¤ndigen kanonischen Hash sowie
unabhÃ¤ngig rekonstruierte BestÃ¤nde, Endmarken, Fehlerzellen, Matches, Berechtigungen,
Fehlerwerte vor Auswahl, gewÃ¤hlte Herkunft, Ausgabe und Feedback. GroÃŸe interne
Ereignisfolgen werden fÃ¼r IntegritÃ¤t stromweise gelesen; die fachliche PrÃ¼fung
behÃ¤lt nur ihre benÃ¶tigte Zustandsprojektion. VollstÃ¤ndige Rohbelege bleiben im Archiv.

`_s2uc_er1_observer.py` protokolliert alle vollstÃ¤ndigen EingangsblÃ¶cke, Vor-/Nachbestand,
Aufnahme, BestÃ¤tigung, Ersetzung, Promotion, Opfer, Originalalter und letzte
Wiederbeobachtung. Pro beobachtetem Ziel stehen lebende berechtigte Originale,
Offset, frÃ¼here lebende Feedbackziele, WÃ¤rme, tatsÃ¤chliche Auswahl, Ausgabe und MAE
zur VerfÃ¼gung. E\F und F\E sowie Gewinn, Schaden und Gleichheit werden symmetrisch
gefÃ¼hrt. Ereignis-, Originallinien- und Zielanzahlen sind getrennt. Beobachterdaten
werden nie als Policy-Eingabe verwendet. Die Geschichte ist durch Fallarchiv,
Scope `comparison/stream` und Originalordinaltupel eindeutig zugeordnet.

Archivierte Belege:

- Fall 1: [Archiv](neutral/case-01.gz), [Capture-Anker](neutral/case-01-capture.json), [KostenÃ¼bersicht](neutral/case-01-observer.json); 32 Frames; 10732 gzip-Bytes.
- Fall 2: [Archiv](neutral/case-02.gz), [Capture-Anker](neutral/case-02-capture.json), [KostenÃ¼bersicht](neutral/case-02-observer.json); 32 Frames; 10716 gzip-Bytes.
- Fall 3: [Archiv](neutral/case-03.gz), [Capture-Anker](neutral/case-03-capture.json), [KostenÃ¼bersicht](neutral/case-03-observer.json); 44 Frames; 13193 gzip-Bytes.

## Quellen und Statistik

Alle 32 neutralen Quellen werden mit getrennten Cue-/Outcome-SHA256-StrÃ¶men,
Rejection Sampling, festen Orientierungen und festem Wechsel nach Block 128
unabhÃ¤ngig rekonstruiert, einschlieÃŸlich aller 1024 48-dimensionalen Frames und
32-KiB-Quellenlimit. AusschlieÃŸlich `MCM-ER1/neutral/v1`; keine Forschungsquelle
materialisiert. Diese Generatortests sind keine vollstÃ¤ndigen PolicyfÃ¤lle.

Synthetische Statistik benutzt Eâˆ’F Ã¼ber exakt 511 Ziele je Geschichte,
32 gleichgewichtete Geschichten und 16.352 Zielpaare. Fehlende Ziele/Geschichten,
falsche Orientierung, ungÃ¼ltige Fehler und falsche Bootstrapmatrix werden verworfen.
Die unverÃ¤nderte 10.000-fache, 16+16-stratifizierte Indexmatrix wird nur als Indexmatrix
Ã¼bernommen (SHA `0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`).
Keine historischen Fehlerwerte gehen ein.

EigenstÃ¤ndige Referenzsummation und gewichtete Bootstraprekonstruktion bestÃ¤tigen
exakte rationale Mittel und Perzentile. GeprÃ¼ft sind negative, positive, nullberÃ¼hrende,
nullÃ¼berschreitende und degenerierte Intervalle, ferner falsche Intervallreihenfolge.
Ein nichtkonstantes synthetisches Beispiel liefert 3/8176 mit vollstÃ¤ndigem Nenner.
PrÃ¤-/Post-, Q-/S- und Orientierungsgruppen sind deskriptiv. Leere Gruppen haben
Anzahl 0 und Mittel null/undefiniert, keinen kÃ¼nstlichen Nullfehler.

## Ressourcen und Fehlerabschluss

Die endgÃ¼ltigen Messwerte stehen vollstÃ¤ndig in [neutral/worker.json](neutral/worker.json)
und [neutral/supervisor.json](neutral/supervisor.json). Maxima Ã¼ber die endgÃ¼ltigen
neutralen FÃ¤lle, sofern nicht anders angegeben:

| GrÃ¶ÃŸe | Beobachtet | Vertragsgrenze |
|---|---:|---:|
| ZusÃ¤tzlicher Policyheap | 5104 | 16384 |
| Originalframes, konservative Obergrenze | 16 | 18 |
| Frames plus Ausgaben, Obergrenze | 18 | 20 |
| Ausgabeslots | 2 | 2 |
| Receiptbytes | 608 | 16384 |
| Transienter UTF8, Obergrenze | 1216 | 32768 |
| Windows-Jobpeak aller endgÃ¼ltigen TeilprÃ¼fungen | 78168064 | 536870912 |
| gzip je Archiv | 13193 | 524288 |
| Encoded je Archiv | 71235 | 4194304 |
| Codec-Dictionary | 65039 | 4194304 |
| GrÃ¶ÃŸter einzelner Record | 15147 | 262144 |
| Knoten | 1463 | 65536 |
| Kanten | 8444 | 262144 |
| Indizes | 1447 | 65536 |
| Collections | 13 | 16 |

Die Bank bleibt 416 Bytes, die Endmarkenzahl hÃ¶chstens zwei. Maximaler separat
gezÃ¤hlter Beobachterheap: 185711 Bytes; Pythonpeak fÃ¼r
Capture plus ArchivprÃ¼fung: 10836770 Bytes.
Die gesamte Beobachter-JSON-Menge ist kein Einzelrecord: fÃ¼nf zusÃ¤tzliche
Sequenzen halten insgesamt 13 Collections und erzwingen das Einzelrecordlimit.
Die Felder original_frames_peak/combined_peak aus dem nicht aktivierten Tracer
sind **keine Nullmessung**; maÃŸgeblich sind die ausdrÃ¼cklich gemessenen konservativen
Obergrenzen und die Boundary-ZÃ¤hlung. Der Zusatzheap ist keine Gesamtprozessangabe.

Jeder getrennte Einstieg reserviert den Terminalslot vor Workerstart, prÃ¼ft den
Windows-Job und begrenzt ihn auf zwei Prozesse/512 MiB. 54.000 Sekunden Workerfrist
und 57.600 Sekunden Gesamtfrist bleiben unverÃ¤ndert. Die endgÃ¼ltigen drei
Qualifikationsaufrufe beanspruchten zusammen 93.412 Sekunden;
das ist keine Forschungsseriendauer. Einfallstore fÃ¼r Forschung werden vor
Dateianlage abgelehnt (Test 16). Zielordner sind exklusiv.

[write_failure/worker.json](write_failure/worker.json) belegt den absichtlich
injizierten Schreibfehler INJECTED_WRITE. Erwarteter Fehler erkannt, alle vier
angelegten Arme geschlossen, Bank geleert, Codec freigegeben, keine Partialdatei.
[write_failure/terminal.json](write_failure/terminal.json) und der Supervisor
bestÃ¤tigen Workerende und sauberen Abschluss. Tests und neutrale AusfÃ¼hrung haben
jeweils eigene Terminal- und Supervisorbelege.

Eine frÃ¼he EntwicklungsausfÃ¼hrung Ã¼berschritt wegen redundanter unkomprimierter
Beobachterexporte die Administrationsgrenze. Sie wurde nicht als Erfolg ausgegeben.
Die vollstÃ¤ndigen Daten liegen jetzt ausschlieÃŸlich im begrenzten Archiv;
Zusatzdateien enthalten nur KostenÃ¼bersichten. Entwicklungsversuche sind unverÃ¤ndert
unter `../er1-development-attempt-01`, `-02`, `-03-tests` und `-04` erhalten.
Die letzte erneute Qualifikation prÃ¼ft den korrigierten Export und die abschlieÃŸende
Archivimplementierung. Diese Verzeichnisse sind keine Forschungsserien.

Die abschließende Inventur liegt für die gesamte endgültige Vorbereitung unter
256 KiB (Grenze 8 MiB), einschließlich aller erhaltenen Entwicklungsversuche unter
3 MiB. Administrations-, Closure-, Archiv- und Exportbudgets sind eingehalten.
Die bei der Messung erfassten temporären Codecdateien bleiben innerhalb 64 MiB;
keine Partialdatei ist nach Abschluss vorhanden. Es gibt keine Forschungsquellendatei.

## Test-IDs und Dateien

[tests/tests.log](tests/tests.log) und [tests/worker.json](tests/worker.json):

- `tests.test_s2uc_er1.ER1Policy.test_01_retention_warm_origin_and_newer_loss`
- `tests.test_s2uc_er1.ER1Policy.test_02_equal_until_reorder_unmasked_and_equal_marks`
- `tests.test_s2uc_er1.ER1Policy.test_03_readmission_is_new_origin_and_downstream_cost`
- `tests.test_s2uc_er1.ER1Policy.test_04_corrupt_stock_and_feedback_fail_closed`
- `tests.test_s2uc_er1.ER1Policy.test_05_policy_resource_limits`
- `tests.test_s2uc_er1.ER1Policy.test_06_long_policy_and_invalid_mode_rejected`
- `tests.test_s2uc_er1.ER1Policy.test_07_archives_independent_and_tamper`
- `tests.test_s2uc_er1.ER1Policy.test_08_same_u_methods`
- `tests.test_s2uc_er1.ER1Policy.test_13_invalid_entry_initialization`
- `tests.test_s2uc_er1.ER1Policy.test_14_equal_selection_on_identical_stocks`
- `tests.test_s2uc_er1.ER1Policy.test_16_research_entry_denied_before_mutation`
- `tests.test_s2uc_er1.ER1SourceStats.test_09_all_neutral_sources_independent`
- `tests.test_s2uc_er1.ER1SourceStats.test_10_full_denominator_and_independent_bootstrap`
- `tests.test_s2uc_er1.ER1SourceStats.test_11_decisions_and_empty_groups`
- `tests.test_s2uc_er1.ER1SourceStats.test_12_missing_targets_cases_orientation_invalid`
- `tests.test_s2uc_er1.ER1SourceStats.test_15_signed_synthetic_complete_aggregates`

Neue Implementierungs-/Testdateien:

- `tests/test_s2uc_er1.py`
- `tools/_s2uc_er1.py`
- `tools/_s2uc_er1_archive.py`
- `tools/_s2uc_er1_engine.py`
- `tools/_s2uc_er1_observer.py`
- `tools/_s2uc_er1_reference.py`
- `tools/_s2uc_er1_source.py`
- `tools/_s2uc_er1_stats.py`
- `tools/_s2uc_er1_stock_reference.py`
- `tools/s2uc_er1_prepare.py`

## Aussagegrenzen und nÃ¤chster Schritt

Keine Forschungsquelle, kein vollstÃ¤ndiger 1024-Frame-Policyfall, keine
Forschungsberechtigung, keine Forschungsserie und keine endgÃ¼ltige Vorstartbindung
wurden erzeugt. Kurze FÃ¤lle belegen keine vollstÃ¤ndige Serienlaufzeit oder garantierte
ArchivgrÃ¶ÃŸe fÃ¼r 1024 Frames. Kein allgemeiner Lern-, Transfer-, Feld-Memory- oder
Nettonutzennachweis. Die neue PrÃ¼fung Ã¼bernimmt Altbelege nur fÃ¼r unverÃ¤nderte
Codec-/Windows-/Terminalkomponenten; ihre neue ER1-Einbindung wurde separat geprÃ¼ft.

Empfehlung an den Projektleiter: Dieses abgegrenzte Implementierungs-/Neutralpaket
anhand der genannten Belege abnehmen. Danach den gesonderten gebundenen
Forschungsvorbereitungsschritt freigeben. Der vorgesehene spÃ¤tere Aufruf lautet
`C:/Python314/python.exe -m tools.s2uc_er1_prepare research` aus dem Projektworkspace.
Er ist derzeit ausdrÃ¼cklich gesperrt; die aktuelle Einstiegsversion erlaubt nur
neutrale Qualifikation. Der Forschungszweig benÃ¶tigt vor AusfÃ¼hrung seine eigene
geprÃ¼fte Aktivierung, endgÃ¼ltige Vorstartbindung, ein exklusives Ziel und eine
separate Einmallauffreigabe. Dieser Bericht erteilt keine dieser Freigaben.

`delivery-manifest.json` ist eine PrÃ¼fsummenliste der Ãœbergabe, keine
Forschungsvorstartbindung und keine Autorisierung.
