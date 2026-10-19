# Technische Wiederholungsprüfung bekannter Rasterdaten — vollständiger Abschluss

**COMPLETE. Alle vier gebundenen Kriterien sind in diesem bekannten Raster BELEGT.** Genau ein neuer Lauf über32 Fälle und160 Arme U/M/E/K/P;2048 Quellpositionen,10240 Arm-Aufnahmen plus10240 separat nachgewiesene Referenzfortschreibungen. Kein Abbruch, keine Wiederholung, keine Reparatur während des Laufs. Gesamtdauer einschließlich tatsächlicher Abschlussverwaltung **1426.334740s** unter3600s.

Evidenzstatus: **KNOWN_DATA_TECHNICAL_REPEAT_NOT_UNTOUCHED_EVALUATION**. Keine unberührte Evaluation und keine unabhängige Generalisierung. Der ursprüngliche Raster32-Lauf bleibt geschlossen/global NOT_EVALUABLE; seine Ergebnisse wurden nicht ergänzt, übernommen oder mit dem neuen Lauf verschmolzen.

## Autorisierung, Bindungen und Quellen

Separate operative Datei docs/S2UC_TECHNISCHE_WIEDERHOLUNG_V4_AUTORISIERUNG_20261003.json. Gegenüber der unveränderten Vorlage ausschließlich status=AUTHORIZED_ONCE geändert; time_reserve_demonstrated=false erhalten. Autorisierungs-SHA256 e23c51f67f313e276d86483029d33a90ccb3435d2975bcff311451857c078092.
V4-Bindung SHA256 121cb259d4747949722a332c8f4f9f04e8fdfee05a8c7eb235da7de48513cae2;85 gebundene Code-Dateien, Qualifikationsbelege und Runtime vor dem Start sowie nach dem Ende geprüft. Keine Policy-, Kriterien-, Parameter- oder Ressourcenänderung. Defaults bleiben deaktiviert. Die Einmalfreigabe ist durch das exklusiv beanspruchte Zielverzeichnis verbraucht; keine Fortsetzung.

Alle32 Quellen vollständig neu materialisiert. Manifest SHA256 5316580eec7ef717915bf370af2ba40eae709d1402c851a371a83d25d9ce8ddb; versiegelt 2026-10-03T17:43:09.988080+00:00, erster Policyarmstart 2026-10-03T17:43:09.999989+00:00, jeweils UTC. Alle160 Starts verweisen auf diesen Manifesthash. Quellenhashes, Profile, Masken und feste Reihenfolge vollständig geprüft.32/32 ganze Quellen entsprechen bekannten historischen Profilen; diese Überschneidung wird ausdrücklich dokumentiert und führt zu keiner Fallersetzung. Quellenwerte stammen aus dem neuen versiegelten Lauf.

## Getrennte gebundene Urteile

- Anpassung:48/48 bestanden,24/24 je Dauer und24/24 je Wechselrichtung XY/YX. Mindestwerte39/48 sowie18/24 je Dauer erfüllt.28 erstmalige Wechsel benötigen jeweils das dritte Hauptziel.20 Rückkehrwechsel:12 ab dem zweiten,8 ab dem dritten. Danach bis Phasenende kein Rückfall. Herkunft, vorzielliche Fehlerpaare und Feedback derselben Phase sind in den Belegen geprüft.
- H-Nettonutzen:BELEGT. Gleichgewichtete Fall-MAE von U liegt strikt unter jeder Baseline.
- G-Gesamtnutzen:BELEGT. Gleichgewichtete Fall-MAE von U liegt strikt unter jeder Baseline, einschließlich sämtlicher Anfangskosten und N-Ziele.
- Stabilität/Schadensgrenze:BELEGT nach den vorgegebenen Kriterien. Auf S_w haben U,M,K jeweils MAE0. Schlechtester positiver G-Fallabstand zu einer Baseline ist1/46=0,021739130 gegen K, unter1/32=0,03125. Das bedeutet ausdrücklich nicht Schadensfreiheit.

### Primäre gleichgewichtete Fallmittel

| Maske | U | M | E | K | P |
|---|---:|---:|---:|---:|---:|
| G | 0.410639632 | 0.487231745 | 0.500191611 | 0.474271878 | 0.556020067 |
| H | 0.074013158 | 0.232580742 | 0.259494617 | 0.205666866 | 0.375000000 |
| N | 0.725000000 | 0.725000000 | 0.725000000 | 0.725000000 | 0.725000000 |
| S | 0.026913876 | 0.026913876 | 0.053827751 | 0.000000000 | 0.375000000 |
| S_w | 0.000000000 | 0.000000000 | 0.029166667 | 0.000000000 | 0.375000000 |
| F | 0.250000000 | 0.288690476 | 0.288690476 | 0.288690476 | 0.375000000 |
| A | 0.077008929 | 0.375000000 | 0.375000000 | 0.375000000 | 0.375000000 |

### Ergänzende positionsgewichtete Mittel

| Maske | U | M | E | K | P | Positionen |
|---|---:|---:|---:|---:|---:|---:|
| G | 0.408266129 | 0.486391129 | 0.498487903 | 0.474294355 | 0.556451613 | 992 |
| H | 0.068750000 | 0.230208333 | 0.255208333 | 0.205208333 | 0.375000000 | 480 |
| N | 0.726562500 | 0.726562500 | 0.726562500 | 0.726562500 | 0.726562500 | 512 |
| S | 0.025000000 | 0.025000000 | 0.050000000 | 0.000000000 | 0.375000000 | 60 |
| S_w | 0.000000000 | 0.000000000 | 0.026785714 | 0.000000000 | 0.375000000 | 56 |
| F | 0.250000000 | 0.302083333 | 0.302083333 | 0.302083333 | 0.375000000 | 48 |
| A | 0.062500000 | 0.375000000 | 0.375000000 | 0.375000000 | 0.375000000 | 144 |

G=992 bewertete Ziele,H=480,N=512. Endziele L+1 bleiben zensiert. F/A/S sind diagnostische Teilmengen,keine zusätzlichen Summanden. Das primäre Urteil verwendet Fallmittel; positionsgewichtete Werte ersetzen diese nicht. Auf N sind alle fünf Arme gleich:hier ist kein Vorteil der erfahrungsbasierten Auswahl belegt.

## Vollständige Schäden und Anfangskosten

| Baseline | geschädigte / verbesserte Fälle | geschädigte / verbesserte Ziele | Ziel-Verlustsumme / Gewinnsumme | schlechtester Fallabstand U−Baseline |
|---|---:|---:|---:|---|
| E | 0 / 32 | 0 / 244 | 0.000000 / 89.500000 | D5-YYYY: -0.006410256 |
| K | 5 / 27 | 32 / 212 | 12.000000 / 77.500000 | D3-XXXX: 0.021739130 |
| M | 0 / 28 | 0 / 212 | 0.000000 / 77.500000 | D3-XXXX: 0.000000000 |
| P | 0 / 32 | 0 / 402 | 0.000000 / 147.000000 | D3-XYYY: -0.097826087 |

Alle fünf positiven G-Fallabstände betreffen K:

| Fall | exakter G-Abstand U−K | dezimal |
|---|---:|---:|
| D3-XXXX | 1/46 | 0.021739130 |
| D3-XXXY | 1/92 | 0.010869565 |
| D3-YYYY | 1/92 | 0.010869565 |
| D5-XXXX | 1/78 | 0.012820513 |
| D5-YYYY | 1/156 | 0.006410256 |

Gegen K sind32 Einzelziele schlechter:ausnahmslos Ziel7, an dem U noch kalte Fehlerzellen hat und auf Persistenz zurückfällt.16 X-Anfänge verursachen je0,5 Zusatzfehler,16 Y-Anfänge je0,25; Verlustsumme12. Größter Einzelschaden0,5. Der Grenzwert1/32 gilt für Fallmittel, nicht für Einzelziele. K ist in sämtlichen vier stabilen Fällen im Gesamtmittel besser; der warme Teil S_w gleicht dies nicht rückwirkend aus. Alle weiteren Ziel-/Fallabstände einschließlich Nullen und Gewinne stehen vollständig in all-target-differences.json beziehungsweise aggregate.json.

Erstes Prognoseziel3 bleibt in G/N:U-Fehler0,5 in16 Fällen und0,25 in16 Fällen, identisch zu allen Baselines. An jedem ersten Wechselziel F beträgt der U-Fehler0,25 (Summe12). Am zweiten Hauptziel:36×0,25 und12×0 (Summe9). Ab dem dritten Hauptziel sind alle48 Wechsel fehlerfrei und erfüllen zusätzlich die gebundene Herkunfts-/Warmwahlbedingung; bei Dauer5 gilt dies auch für Ziele4/5. Ein korrektes numerisches Ergebnis allein wurde nicht als Anpassung gewertet. Einzelwechsel mit allen Erstverlusten und Folgefehlern stehen in all-switches.json und phase-costs.json.

## Fehlende, kalte und konkurrierende Kontexte

Auf480 H-Zielen ist die gewünschte Fortsetzung28-mal nicht vorhanden,60-mal nur kalt und392-mal warm vorhanden.244 H-Ziele haben konkurrierende Kontextlabels. U wählt440-mal einen warmen Fehlergewinner;32-mal greift Persistenz wegen ausschließlich kalter Hypothesen,8-mal wegen gleichauf liegender negativer Fehlerdifferenzen. Kein Fall wurde wegen fehlender oder kalter Verfügbarkeit aus H/G oder dem48er-Anpassungsnenner entfernt.

Alle28 fehlenden Sollkontexte liegen am ersten Ziel eines erstmaligen Wechsels. Bei den20 Rückkehrwechseln ist der Sollkontext dort bereits warm vorhanden, aber nicht sofort gewählt; dies ist von bloßer Verfügbarkeit zu unterscheiden. Unter den144 späteren Wechselzielen A sind28 Sollkontexte kalt und116 warm. Auf allen512 N-Zielen fehlt jede berechtigte Kontextfortsetzung; alle Arme fallen dort auf denselben Persistenzfehler zurück. Damit erklärt sich der verbleibende hohe N-Fehler, ohne einen neuen Nutzen zu behaupten.

Jede Entscheidung einschließlich Originalordinalen, lebenden Keys, Fehlerpaaren, früherem Feedback, Auswahlgrund und Verfügbarkeitsklasse steht in den32 *-contexts.json-Dateien. Zusammenfassung samt vollständigen Teilmengen-Kosten in availability-and-costs.json. Stabile/wechselnde Gruppen und beide Dauern sind zusätzlich in aggregate.json vollständig ausgewiesen.

## Zeitwächterchronologie

| Ereignis | UTC | Sekunden seit Start, monoton |
|---|---|---:|
| deadline_established | 2026-10-03T17:43:07.883483+00:00 | 0.000000 |
| worker_end_confirmed | 2026-10-03T18:06:52.290696+00:00 | 1424.395539 |
| closure_admin_started | 2026-10-03T18:06:52.291497+00:00 | 1424.396344 |
| closure_admin_finished | 2026-10-03T18:06:54.229910+00:00 | 1426.334740 |

Workergrenze3540s, Gesamtgrenze3600s; keine abort_requested-/kill_requested-Ereignisse. Worker-Ende bestätigt mit exitcode0 und alive=false. Abschlussverwaltung umfasst tatsächliches Inventar, Abschlussdatei und Hash; Dauer 1.938396s. Der letzte Journalmarker schließt seinen eigenen Schreibvorgang nicht in seine Zeit ein. Rest zur Gesamtgrenze 2173.665260s. Die Nachprüfung dieses Berichts liest nur den bereits geschlossenen Lauf und liegt außerhalb des operativen Zeitfensters; keine nachträgliche Vervollständigung von Ergebnisarmen.

| Exklusive Enginephase | Wall s | Prozess-CPU s |
|---|---:|---:|
| U_replay | 2.762093 | 2.765625 |
| aggregation | 0.013857 | 0.015625 |
| baseline_replay | 1411.703365 | 1410.281250 |
| case_assessment | 6.630205 | 6.671875 |
| export | 0.932490 | 0.812500 |
| manifest | 1.007499 | 0.953125 |
| materialization | 0.016272 | 0.031250 |
| resource_check | 0.000846 | 0.000000 |
| source_hash | 0.309919 | 0.015625 |
| source_read | 0.033766 | 0.000000 |
| source_validation | 0.074404 | 0.109375 |

Enginegesamtzeit 1423.583449s. Alle160 direkten Einzelzeiten sind in chronology.json/phase-times.json erhalten. Der vorherige Plan2709,087488s wurde nicht während des Laufs verändert. Aus dem schnelleren Einzelabschluss wird keine allgemeine Worst-Case-Garantie abgeleitet.

## Ressourcen und gemeinsame Exportbilanz

| Arm | maximaler Zusatzheap Byte | Originalframes | kombiniert | Receipt / UTF8 Byte |
|---|---:|---|---|---|
| E | 2481 | 12 Peak | 13 Peak | 455 / 910 |
| K | 1498 | 12 Peak | 13 Peak | 455 / 910 |
| M | 4420 | 12 Peak | 13 Peak | 455 / 910 |
| P | 1498 | 12 Peak | 13 Peak | 455 / 910 |
| U | 5161 | 12 Bound | 14 Bound | 753 / 1506 |

Alle160 Arme vollständig freigegeben. Unverändert18 Originalframes,2 Ausgabeslots,20 kombiniert,16384 Zusatzheap,16384 Receipt,32768 UTF8; U416 gepackte Bytes. U verwendet im operativen Lauf Originalframe-/Kombinationsbounds; seine exportierten Tracingpeaks0 sind nicht erhoben und bedeuten keinen Nullverbrauch. K/P packed_bytes=416 ist eine historische Exportkonstante, kein Beleg einer aktiven Fehlerbank. Kein Gesamtprozess-RAM-Nachweis aus dem kleinen Policyheap.

Gemeinsamer Deckel64MiB einschließlich gebundener Vorbelastung5462547 Byte, neuem Lauf, Nachauswertung und Berichtsskript.1MiB Abschlussreserve bleibt vorgesehen. Die endgültige bytegenaue Bilanz einschließlich synchronisierter README/Forschungsweg steht in closure.json. Jeder neue JSON-Bericht bleibt unter524288 Byte. Keine alten Dateien oder versiegelten Exporte geändert.

## Nachprüfung und nächste Forschungsentscheidung

Alle32 Einzelbelegprüfungen und die vollständige Aggregation aus den neuen gespeicherten Daten erneut berechnet; semantisch identisch mit den versiegelten Worker-Ausgaben. Alle160 Ressourcen-/Cleanupprüfungen bestanden. Quell-/Manifest-/Startchronologie,10240 Aufnahmen und10240 Referenzfortschreibungen separat abgeglichen. Historischer Rasterlauf367 Dateien und historische Auswertung7 Dateien gegen ihre Abschlussinventare verifiziert. Nachauswertung:0 Replays,0 Quellmaterialisierungen.

**Empfehlung an den Projektleiter:** Den technischen Laufzeit-/Integrationszweig abschließen und den eingefrorenen Mechanismus als innerhalb dieser bekannten Familie belegten Entwicklungsstand behandeln. Als nächsten begrenzten Forschungsauftrag einen vorab festgelegten Transferprüfvertrag für bislang unberührte Wahrnehmungsverläufe formulieren. Dieser muss kalte Anfänge, Kontextausfälle und variable Wechselabstände ausdrücklich enthalten sowie K als starke Vergleichsbasis beibehalten. Erst nach separater Abnahme Quellen erzeugen oder ausführen. Keine weitere Optimierungsserie und keine sofortige Policyänderung aus diesem Abschluss.

Begründung:48/48 Anpassungen und der H/G-Vorteil rechtfertigen den Übergang zur Übertragbarkeitsfrage; die bekannten exakten Hinweis-/Blockmuster beantworten sie nicht. Die32 kalten Anfangsschäden und512 N-Ziele ohne Kontext markieren konkrete Aussagegrenzen. Weder allgemeine Audio-/Video-Generalisation noch Feld-Memory, Clusterbildung oder mehrschrittiges Planen sind damit belegt. Der alte Raster32-Status bleibt unabhängig von diesem Erfolg NOT_EVALUABLE.

## Vollständige Fallübersicht

| Fall | bestandene / vorhandene Wechsel | G-MAE U/M/E/K/P | H-MAE U/M/E/K/P |
|---|---:|---|---|
| D3-XXXX | 0/0 | 0.402174 / 0.402174 / 0.423913 / 0.380435 / 0.619565 | 0.045455 / 0.045455 / 0.090909 / 0.000000 / 0.500000 |
| D3-XXXY | 1/1 | 0.423913 / 0.434783 / 0.456522 / 0.413043 / 0.586957 | 0.090909 / 0.113636 / 0.159091 / 0.068182 / 0.431818 |
| D3-XXYX | 2/2 | 0.434783 / 0.500000 / 0.521739 / 0.478261 / 0.586957 | 0.113636 / 0.250000 / 0.295455 / 0.204545 / 0.431818 |
| D3-XXYY | 1/1 | 0.423913 / 0.467391 / 0.489130 / 0.445652 / 0.554348 | 0.090909 / 0.181818 / 0.227273 / 0.136364 / 0.363636 |
| D3-XYXX | 2/2 | 0.434783 / 0.565217 / 0.586957 / 0.543478 / 0.586957 | 0.113636 / 0.386364 / 0.431818 / 0.340909 / 0.431818 |
| D3-XYXY | 3/3 | 0.445652 / 0.532609 / 0.554348 / 0.510870 / 0.554348 | 0.136364 / 0.318182 / 0.363636 / 0.272727 / 0.363636 |
| D3-XYYX | 2/2 | 0.434783 / 0.532609 / 0.554348 / 0.510870 / 0.554348 | 0.113636 / 0.318182 / 0.363636 / 0.272727 / 0.363636 |
| D3-XYYY | 1/1 | 0.423913 / 0.500000 / 0.521739 / 0.478261 / 0.521739 | 0.090909 / 0.250000 / 0.295455 / 0.204545 / 0.295455 |
| D3-YXXX | 1/1 | 0.402174 / 0.565217 / 0.576087 / 0.554348 / 0.586957 | 0.068182 / 0.409091 / 0.431818 / 0.386364 / 0.454545 |
| D3-YXXY | 2/2 | 0.423913 / 0.532609 / 0.543478 / 0.521739 / 0.554348 | 0.113636 / 0.340909 / 0.363636 / 0.318182 / 0.386364 |
| D3-YXYX | 3/3 | 0.434783 / 0.532609 / 0.543478 / 0.521739 / 0.554348 | 0.136364 / 0.340909 / 0.363636 / 0.318182 / 0.386364 |
| D3-YXYY | 2/2 | 0.423913 / 0.500000 / 0.510870 / 0.489130 / 0.521739 | 0.113636 / 0.272727 / 0.295455 / 0.250000 / 0.318182 |
| D3-YYXX | 1/1 | 0.402174 / 0.500000 / 0.510870 / 0.489130 / 0.554348 | 0.068182 / 0.272727 / 0.295455 / 0.250000 / 0.386364 |
| D3-YYXY | 2/2 | 0.423913 / 0.467391 / 0.478261 / 0.456522 / 0.521739 | 0.113636 / 0.204545 / 0.227273 / 0.181818 / 0.318182 |
| D3-YYYX | 1/1 | 0.402174 / 0.434783 / 0.445652 / 0.423913 / 0.521739 | 0.068182 / 0.136364 / 0.159091 / 0.113636 / 0.318182 |
| D3-YYYY | 0/0 | 0.380435 / 0.380435 / 0.391304 / 0.369565 / 0.489130 | 0.022727 / 0.022727 / 0.045455 / 0.000000 / 0.250000 |
| D5-XXXX | 0/0 | 0.391026 / 0.391026 / 0.403846 / 0.378205 / 0.621795 | 0.026316 / 0.026316 / 0.052632 / 0.000000 / 0.500000 |
| D5-XXXY | 1/1 | 0.403846 / 0.423077 / 0.435897 / 0.410256 / 0.589744 | 0.052632 / 0.092105 / 0.118421 / 0.065789 / 0.434211 |
| D5-XXYX | 2/2 | 0.410256 / 0.487179 / 0.500000 / 0.474359 / 0.589744 | 0.065789 / 0.223684 / 0.250000 / 0.197368 / 0.434211 |
| D5-XXYY | 1/1 | 0.403846 / 0.455128 / 0.467949 / 0.442308 / 0.557692 | 0.052632 / 0.157895 / 0.184211 / 0.131579 / 0.368421 |
| D5-XYXX | 2/2 | 0.410256 / 0.551282 / 0.564103 / 0.538462 / 0.589744 | 0.065789 / 0.355263 / 0.381579 / 0.328947 / 0.434211 |
| D5-XYXY | 3/3 | 0.416667 / 0.519231 / 0.532051 / 0.506410 / 0.557692 | 0.078947 / 0.289474 / 0.315789 / 0.263158 / 0.368421 |
| D5-XYYX | 2/2 | 0.410256 / 0.519231 / 0.532051 / 0.506410 / 0.557692 | 0.065789 / 0.289474 / 0.315789 / 0.263158 / 0.368421 |
| D5-XYYY | 1/1 | 0.403846 / 0.487179 / 0.500000 / 0.474359 / 0.525641 | 0.052632 / 0.223684 / 0.250000 / 0.197368 / 0.302632 |
| D5-YXXX | 1/1 | 0.391026 / 0.564103 / 0.570513 / 0.557692 / 0.589744 | 0.039474 / 0.394737 / 0.407895 / 0.381579 / 0.447368 |
| D5-YXXY | 2/2 | 0.403846 / 0.532051 / 0.538462 / 0.525641 / 0.557692 | 0.065789 / 0.328947 / 0.342105 / 0.315789 / 0.381579 |
| D5-YXYX | 3/3 | 0.410256 / 0.532051 / 0.538462 / 0.525641 / 0.557692 | 0.078947 / 0.328947 / 0.342105 / 0.315789 / 0.381579 |
| D5-YXYY | 2/2 | 0.403846 / 0.500000 / 0.506410 / 0.493590 / 0.525641 | 0.065789 / 0.263158 / 0.276316 / 0.250000 / 0.315789 |
| D5-YYXX | 1/1 | 0.391026 / 0.500000 / 0.506410 / 0.493590 / 0.557692 | 0.039474 / 0.263158 / 0.276316 / 0.250000 / 0.381579 |
| D5-YYXY | 2/2 | 0.403846 / 0.467949 / 0.474359 / 0.461538 / 0.525641 | 0.065789 / 0.197368 / 0.210526 / 0.184211 / 0.315789 |
| D5-YYYX | 1/1 | 0.391026 / 0.435897 / 0.442308 / 0.429487 / 0.525641 | 0.039474 / 0.131579 / 0.144737 / 0.118421 / 0.315789 |
| D5-YYYY | 0/0 | 0.378205 / 0.378205 / 0.384615 / 0.371795 / 0.493590 | 0.013158 / 0.013158 / 0.026316 / 0.000000 / 0.250000 |
