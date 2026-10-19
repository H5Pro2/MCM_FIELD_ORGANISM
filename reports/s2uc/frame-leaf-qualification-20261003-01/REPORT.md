# Frame-Blattfall V1: neutrale Qualifikation (2026-10-03)

Separat versionierter Patch: ausschließlich geprüfter Frame-Blattfall. Historischer Beobachter, Policies, Grenzen und Exporte unverändert. Neuer Visitor nur im qualifizierten Vergleich aktiviert; Raster32 bleibt geschlossen.

V01–V08 bestanden; konkrete IDs und neutrale Einzelbelege in tests.json und test-facts.json. Acht vollständige kanonische Fachvergleiche und acht Vergleiche sämtlicher meter-Felder gleich. Entscheidungen/Receipts, Fehlerupdates, Bestände, Zustandshashes, Endziel81, EMA-Löschung und terminale Freigabe eingeschlossen.

16 Replays ×80 Positionen =1280 Aufnahmen +1280 Referenzfortschreibungen. N1 je Arm OLD/NEW, N2 NEW/OLD; beide mit aktivem Originaltrace, keine Warmups oder Zeitwiederholungen. Keine Diagnose-Timerhooks in Policy oder Visitor.

| Quelle/Arm | OLD s | NEW s | OLD/NEW | Entlastung |
|---|---:|---:|---:|---:|
| N1/M | 13.942576 | 10.897546 | 1.279 | 21.84% |
| N1/E | 13.991355 | 10.683822 | 1.310 | 23.64% |
| N1/K | 13.382992 | 9.969323 | 1.342 | 25.51% |
| N1/P | 13.599338 | 10.111891 | 1.345 | 25.64% |
| N2/M | 21.419311 | 14.628340 | 1.464 | 31.70% |
| N2/E | 21.415805 | 14.967013 | 1.431 | 30.11% |
| N2/K | 21.059977 | 14.159261 | 1.487 | 32.77% |
| N2/P | 20.686180 | 13.840664 | 1.495 | 33.09% |

Summe OLD 139.497534 s; NEW 99.257859 s; Entlastung 28.85%. Beobachtete Einzelpaare, kein statistischer Populationstest und keine Garantie einer Raster32-Gesamtlaufzeit.

Zusätzlicher Python-Heappeak maximal 4548 Byte (Grenze16384). Metermaxima: `{"combined_peak": 13, "frame_peak": 12, "match_metadata_peak": 2, "output_python_bytes_peak": 3645, "output_slots_peak": 2, "receipt_bytes_peak": 454, "receipt_python_bytes_peak": 495, "receipt_transient_utf8_bytes_peak": 908, "samples": 76050, "scalar_pair_comparisons": 0, "temporary_numeric_vectors_peak": 0, "transient_reference_frames_peak": 12}`. Originale Trace- und Admission-Bounds bleiben vollständig aktiv. Gepackter EMA-Bound416 Byte ist ein Exportlimit, nicht für jeden Arm tatsächlicher Besitz. Freigegebene Ausgaben und terminales Cleanup in allen16 Replays. Isolierte Visitorallokationen stehen getrennt in V08; sie sind keine Gesamtprozess-RAM-Messung.

V01 prüft per AST, dass am alten Tracekörper nur der Blattfall ergänzt wurde. V02/V03 prüfen gleiche erreichbare Frame-ID-Mengen, Aliase/Zyklen,18/19-Grenze, Slots und20er-Kombination. V04 prüft Unterklassen, mutable Payloads und fremde Feldtypen einschließlich darin verborgener Frames. V05 verwendet sechs echte Hypothesen einer neutralen Vorbelegung. V06 vergleicht Promotion, Verdrängung und vier Publikationsunterbrechungen samt Fehlerbereinigung und transienten Peaks. V07 prüft unveränderte Frame-, Fremdvektor- und Metadatenfehler. V08 prüft isolierte Allokation und das Fehlen persistenten Caches.

Der kurze Pfad prüft jedes Mal exakten Frame-Typ, exakt tuple mit48 echten floats und ausschließlich skalare Bindungsfelder. Unterklassen und unklare/mutable Werte bleiben im alten Visitor. Frame-ID wird vor dem Rücksprung gezählt. Kein Cache, keine deaktivierten Traceereignisse, keine geänderten Policyentscheidungen oder Budgetgrenzen.

Neue Bindung umfasst Patch, Tests, Runner und Plan sowie71 historische Codebindungen und gespeicherte Altartefakte. Prüfung vor/nach Matrix. Zeitwächterereignisse in matrix-lifecycle.json; Bestätigung nach join ist kein genauer Todeszeitpunkt, Abschlussphase dort nur prototypische Serialisierung. Die operative Ausführungsvorbereitung muss später Deadline, Abbruchanforderung, Workerbestätigung und gesamte Abschlussverwaltung getrennt protokollieren.

Nächster Schritt zur Entscheidung des Projektleiters: qualifizierten Beobachterstand für eine separate technische Ausführungsvorbereitung übernehmen und deren Zeitbudget sowie vollständige Zeitwächterprotokollierung prüfen. Dieser Abschluss startet keinen Evaluationslauf und vervollständigt Raster32 nicht. Keine weitere Optimierung implementiert.
