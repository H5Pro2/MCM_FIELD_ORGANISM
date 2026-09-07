# S2-NL: einmalige neutrale Rangskalenqualifikation

Vor dem Aufruf gebunden, 2026-09-07. Grundlage: S2-NK und die ausdrueckliche
Freigabe des versionierten Kernanschlusses. Keine Hauptlauf-Freigabe.
ID: `s2nl-versioned-rank-scale-qualification-20260907-01`.

Ein Aufruf von `reports/s2nl/qualify_once.py` startet genau einen begrenzten
Unittest-Prozess mit Failfast. Kein separater Testvorlauf, kein Retry.
Vor dessen Start werden das vollstaendige Inventar, die Quellhashes,
Interpreteridentitaet, Kommando und Gates in `preregistration.json` gebunden.

## Testinventar und Umfang

24 neue Testkoerper in `tests/test_s2nl_private_rank_scale.py`:

1. Historische kanonische Fast-Payload und sieben vorhandene Profilbindungen.
2. Festes neues Profil, neue Version, unveraenderte visuelle Bankkonfiguration.
3. Gemischte Profile/Versionen abweisen.
4. Manipulierte Rangregel, Grenze oder Version abweisen.
5. S2-NK-Gegenbeispiel: historisch, naive Halbierung, gebundene Rangumrechnung.
6. Maximum vor Summe.
7. Slot-ID und B4-Formationsalter als bestehende Tie-Breaks.
8. Genau 30 S2-NK-Matchpaare in fuenf Arithmetikpfaden, inklusive direkter
   S2-KZ-/S2-NE-Pruefung der Teilscanstatistiken; keine Toleranz.
9. Drei feste Subnormalpaare, Unterlauf, volle Kandidatengleichheit und Rangwerte.
10. Zwei Vier-Schritt-PPB-Ketten je Skala, insgesamt 16 direkte PPB-Schritte;
    vollstaendige Prototypbits/-digests und Supportfolge.
11. Ein neutraler Null-Rezeptoraufruf; NJ-Projektion und Kontaktbildung ohne
    erneute Skalierung. Weitere synthetische Werte sind explizite Testfixtures.
12. Gemischte Quellen-/Planbindungen abweisen.
13. Je vier neutrale atomare Formationen pro Skala, State-/Owner-/Receiptbindung,
    auditive und visuelle PPB-Prototypen getrennt.
14. Reale Fast-Funktion und Relationspruefung auf synthetischem Mehrslotzustand,
    unabhaengige Rangnachrechnung und Updatepruefung.
15. Native Vollprobe und S2-JW-Beobachter: ausgewaehlte Slotbindung, volle
    Rangzeilen, Zustandsunveraenderlichkeit.
16. Vier neutrale Halbprofilformationen, beide rangfreien S2-NE-Teilscanarme und
    unabhaengige Direktbaselines/Verifikation; Slow-Regel unveraendert halbiert.
17. Gueltige Abwesenheit technisch verifizieren.
18. Vertauschte/veraenderte Rangbelege abweisen.
19. Falsche native Slotwahl abweisen.
20. Gemischten Zustand und falsche Owner-Konfiguration abweisen.
21. Eine neutrale Formation und abgelaufene Quellenzeit pruefen.
22. Voller Drei-Slot-Rangscan, kanonische Ausgabe- und numerische Zustandsgrenze.
23. Gleichstand in nativer Vollprobe und B4-Beobachter, mit unabhaengiger Pruefung.
24. Historische Null-Fast-Payload einschliesslich Digest separat rekonstruieren.

Zusaetzlich genau fuenf unveraenderte historische S2-DH-Testkoerper:
`test_foreign_timed_binding_fails_closed`,
`test_fast_create_update_and_consolidation_are_separate`,
`test_lru_replacement_uses_last_selected_step_then_slot_id`,
`test_atomic_failure_of_second_ppb_step_publishes_nothing`,
`test_read_only_probe_prefers_slow_then_fast_and_changes_no_state`.
Gesamt: **29 Tests**, nicht die gesamten historischen Testsuiten.

## Ressourcen und Aussagen

- Neue Tests: exakt 13 atomare Formationen bei Vollabschluss, 16 direkte
  PPB-Schritte, ein direkter neutraler Rezeptoraufruf; keine RGB-Analyse.
- Historische Teilmenge zusaetzlich, zusammen maximal 40 atomare Versuche.
- Numerischer Memoryzustand maximal 44.544 Byte je Zustand; bestehendes Ledger.
- Direktnachrechnung: maximal 1.008 Fast- bzw. 3.024 B4-L1-Terme pro Scan.
  Rangbeleg maximal 16.384 Byte; AV-Paar maximal 65.536 Byte.
- Teilhinweisarme: bestehende 9/3/8-Scans, maximal 528 Wertvergleiche je Arm,
  Ausgabe strikt unter 32.768 Byte.
- Je Qualifikations-JSON maximal 1.048.576 Byte; Prozesszeit maximal 300 Sekunden.
- NH-Quellen, Feld-, Kontextanwendung und Runtimeaufrufe: null. Alle Hauptgates False.

Numerische Skalenabweichungen werden mit Binary64-Hex und Matchstatus
aufgezeichnet, nicht toleriert oder aus dem Inventar entfernt. Sie sind von
technischen Vertragsverletzungen getrennt. Technische Qualifikation beweist
keine universelle Gleitkommagleichheit oder identische Feldtrajektorien.
Historische Payloads sind unveraendert; neue Semantik ist in versionierter
Profil-/Fast-/Koordinatorbindung enthalten und durch deren Digests in
Zustand, Owner und Receipt transitiv gebunden. Es entsteht kein neuer Recorder.

Bei Fehler: Originalbefund sichern, keine Korrektur oder Wiederholung dieses
Aufrufs. Auch bestandene Qualifikation erlaubt keinen NH-Hauptlauf.
