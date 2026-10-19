# CR1: Originalrecency ausschließlich bei kalten Hypothesen

2026-10-17. **KONZEPT_ZUR_PRUEFUNG**, keine Implementierungs- oder Forschungsfreigabe. Workflow-Auftrag 91519f9f-6376-4e2f-a05d-998a08797454. CR1 ist eine Konzeptkennung, keine Laufnummer. Ausschließlich Codelektüre und Dokumentation; keine Quellen erzeugt, Archive erneut ausgewertet oder Policies ausgeführt.

## 1 Frage, Motivation und genau eine Variante

Hilft bei fehlender Fehlererfahrung die jüngste berechtigte Originalfortsetzung gegenüber der bisherigen Persistenz, ohne die warme Auswahl zu verändern? Verglichen werden ausschließlich unverändertes U und die Variante C; kein zusätzlicher R-Arm und keine Suche nach Ersatzregeln.

Die Variantenwahl ist ausdrücklich durch die angenommene REV1-Diagnose motiviert: 66 ausschließlich kalte Primärziele hatten für U gegenüber R einen deskriptiven Nettobeitrag von −3,5; Enthaltung ohne negative warme Bewertung dagegen +2,5 und eindeutige Kontextwahl +15. Die insgesamt 201 kalten Auftritte einschließlich gemischter Bestände betrafen Kandidaten ohne frühere Bewertung derselben Originalidentität und desselben Offsets [B1]. Gemischte Bestände werden durch C ausdrücklich nicht verändert.

Diese historischen Daten sind Entwicklungsdaten und begründen die Hypothese, keinen unabhängigen Wirksamkeitsnachweis. Insbesondere wird hier keine historische C-Ausgabe rekonstruiert und kein neuer Effekt aus alten Archiven berechnet. Das REV1-Urteil INCONCLUSIVE bleibt unverändert. Hypothese für frische Daten: Der mittlere Primärfehler von C ist kleiner als der von U. Gegenmöglichkeit: Unbewertete Originale sind nach dem Wechsel unpassend, sodass C schlechter wird.

## 2 Präzise Regel

H ist die im regulären U-Abruf eingefrorene Menge berechtigter Hypothesen: gültige Originalidentität, Faktor genau [1.0], Offset 0 oder 1 mit vorhandenem Nachfolger. Warm bedeutet eine gültige Fehlerzelle für (role,generation,offset); kalt bedeutet ihr Fehlen. EC−EP=0 ist **warm**, nicht kalt. Eine ungültige oder inkonsistente Bank löst weiterhin den bestehenden Fehlerpfad aus und wird nicht als Kaltzustand behandelt [B2].

| Zustand vor Auswahl | Ausgabe von C |
|---|---|
| H leer | Genau U, somit reguläre Persistenz |
| H nicht leer und jede Hypothese kalt | Originalrecency innerhalb H gemäß bestehender R-Regel |
| Mindestens eine warme Hypothese, auch bei zusätzlichen kalten | Genau U |

Im einzigen abweichenden Zweig wählt C den Nachfolger mit größter **Originalordinalzahl**; bei gleicher Ordinalzahl entscheidet das lexikografisch kleinste Tupel (role,generation,offset), retained=0, candidate=1. Ausgegeben werden dessen unveränderte Originalwerte [B3]. Originalrecency bedeutet nicht „letzte beobachtete Fortsetzung“, letzte Rückmeldung oder letzte Promotion.

Außerhalb dieses Zweigs bleiben insbesondere U-Persistenz bei fehlender negativer warmer Bewertung, Enthaltung bei Gleichstand des besten negativen Werts und U-Kontextwahl bei eindeutigem negativem Minimum unverändert. Auch deaktivierter Adapter, unvollständiges Paar, Validierung und Fehlerbehandlung behalten U-Verhalten. C gilt bei jeder regulären Prognose der ganzen Geschichte, nicht nur im Primärfenster und nicht erst nach dem Wechsel. Kein Zugriff auf Fenster, Phase, Zielwert oder künftige Rückmeldung.

Kein zusätzlicher Zähler, Prior, Pseudofeedback, Warmstart, Konfidenzparameter oder Lernzustand. Die sechs Fehlerzellen und 416-Byte-Bank bleiben unverändert. Nur Auswahlmetadaten, Kontext/Persistenz-Ausgabeverweis und entsprechende Protokollbegründung dürfen im kalten Zweig abweichen. Berechtigung, Reihenfolge und Anzahl der eingefrorenen Tickets bleiben gleich. Auswahl und Receipt werden einmal erzeugt; ein zweiter zustandsverändernder U-/R-Receipt-Durchlauf ist nicht Bestandteil dieser Regel.

## 3 Statische Prüfung der gemeinsamen Zustände

**Aufnahme:** `PairContextAdapter.accept_perception` bildet Frames ausschließlich aus `sample.values`. Nach der Receipt-Erzeugung werden exakt diese Wahrnehmungsframes aufgenommen; Receipt oder gewählte Ausgabe gehen nicht in `form` ein [B4]. `MultiErrorAdapter._admit` führt Formation, regulären Segmentabschluss, Promotion und Pruning unabhängig vom gewählten Kontext aus [B2].

**Rückmeldung:** `consume_feedback` berechnet EP aus dem eingefrorenen Persistenzframe und dem tatsächlich folgenden Wahrnehmungsframe. Es iteriert über alle eingefrorenen berechtigten Tickets und berechnet deren EC aus dem jeweiligen Originalnachfolger. `choice` und `reason` werden gelesen, steuern aber weder die Auswahl der zu bewertenden Tickets noch deren Zellinitialisierung oder Aktualisierung. Erste gültige Bewertung und spätere EMA bleiben unverändert; `_promote` überträgt vorhandene Fehlerpaare und `_prune` entfernt regulär nicht mehr lebende Zellen [B2].

**Versuchshülle:** Die ausgewählte Ausgabe dient im bestehenden Executor zur Prognoseprüfung und gemessenen MAE. Die folgende Wahrnehmung stammt weiterhin aus derselben extern festgelegten Framefolge; gemessener Ausgabefehler wird nicht als Zellfeedback eingespeist [B5].

Damit ist im untersuchten Pfad kein vorgesehener Rückkopplungspfad von der geänderten Ausgabe in gemeinsamen Bestand, Tickets oder Fehlerzellen erkennbar. Induktive Erwartung: gleiche Startzustände und Eingaben ergeben gleiche gemeinsame Folgezustände; deshalb können sich spätere Ausgaben außerhalb des kalten Zweigs nicht mittelbar unterscheiden. Dies ist eine statische Begründung, kein bereits ausgeführter Gleichheitsnachweis der noch nicht implementierten Variante. Andere Umgebungen mit Aktionsrückwirkung sind nicht erfasst.

## 4 Frische Quellen und einziger Primärkontrast

Festgelegt werden 32 neue Geschichten r=1…32, 16 je Orientierung, mit je 1024 Frames und zwei frischen Armen C/U. Das REV1-Rezept bleibt vollständig erhalten [B6]: 256 Blöcke (X/Y,P,A/B,S), 48 Komponenten V(x)[j]=x+j/4096, j=0…47; Basen X=1/8, Y=7/8, P=1/2, A=1/4, B=3/4, S=1/16. Je Phase 128 Blöcke mit 64 A/B und 64 X/Y. Ungerades r: X an 48 A- und 16 B-Positionen vor dem Wechsel, danach 16/48; gerades r spiegelbildlich. Einziger Wechsel nach Block 128/Frame 512. Kein Reset, Zusatzsignal oder Aufnahmepräfix.

Einziger neuer Forschungsnamensraum: **MCM-URA1-CR1/source/v1**. Hashschlüssel exakt `MCM-URA1-CR1/source/v1/r={r}/phase={p}/stream={name}/draw={cursor}`. p=0,1; Streams continuation, dependent-A, dependent-B; cursor beginnt je Stream bei 0. Unverändert SHA-256/erste acht Bytes unsigned Big-Endian, Rejection Sampling unter 2^64−(2^64 mod n), absteigendes Fisher-Yates, 4096-Ziehungsgrenze. Erst 64 A/64 B mischen, dann deren aufsteigend gesammelte Positionen getrennt mischen und die festgelegten Anzahlen X zuordnen. Beide Phasen unabhängig mischen und in Reihenfolge verbinden. Keine Kennung wird vorab ausprobiert, ersetzt oder nach ihrem Ergebnis gewählt. Spätere neutrale Tests erhalten ausschließlich **MCM-URA1-CR1/neutral/v1**.

Alle 32 Quellen müssen vor dem ersten Arm unabhängig rekonstruiert, geprüft und gemeinsam versiegelt sein. Keine historischen Quellen, Archive, Effektwerte oder Teilserien werden gepoolt. Die zwei Arme erhalten innerhalb einer Geschichte identische Eingaben; zwischen Geschichten frischer Zustand. Keine alternative Reihenfolge, Wiederholung oder Größenanpassung aufgrund beobachteter Effekte.

Primärfenster ausschließlich Q129–160, also Zielordinalzahlen 515,519,…,639. Für Geschichte r ist D_r das Mittel von MAE48(C,t)−MAE48(U,t) über **alle 32 Fensterziele**. Einziger Primärkontrast D ist das gleichgewichtete Mittel der 32 D_r. Einheit ist die Geschichte, nicht jeder Frame. Geschichten ohne ausschließlich kalte Fensterziele bleiben mit D_r=0 enthalten, sofern die Gleichheitsprüfungen bestehen. Keine Mindestzahl kalter Treffer und kein Ausschluss schädlicher, gemischter oder identischer Ausgaben.

Unveränderte gebundene Bootstrapindexmatrix (10000 Ziehungen, 16+16 Geschichten mit Zurücklegen nach Orientierung), SHA-256 `0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`. Exakte rationale Aggregation gespeicherter binary64-Fehler und nominales zweiseitiges 95%-Perzentilintervall mit h=9999q und linearer Interpolation wie REV1 [B7]. Das Wiederverwenden der festen Indexmatrix übernimmt keine historischen Messwerte.

| Vorab festes Kriterium | Urteil |
|---|---|
| Obere Intervallgrenze <0 | C im definierten Primärvergleich hilfreich |
| Untere Intervallgrenze >0 | C im definierten Primärvergleich nachteilig |
| Intervall enthält oder berührt 0 | Unentschieden, kein Gleichwertigkeitsnachweis |
| Fehlender Fall/Ziel, Referenz- oder Zustandsverletzung | Technisch ungültig; kein Wirksamkeitsurteil aus Teilserie |

Ergänzend, ohne weitere Signifikanztests: Primärfenster nach U-seitigem gemeinsamen Kalt-/Warmstatus, Anzahl berechtigter Hypothesen und Ausgabeidentität; Zahl besser/schlechter/gleich, Gewinn, Schaden und maximaler Einzelzielschaden. Bisherige Fenster Q97–128, Q161–256, Q129–256 und Gesamtmasken bleiben deskriptiv. Keine nachträglichen Fenster oder günstigen Teilgruppen. Nullfälle werden mit Anzahl 0 und nicht definiertem Teilgruppenmittel ausgewiesen, nicht als Erfolg umgedeutet.

## 5 Erforderlicher späterer Prüfplan und Ressourcen

Vor einem Forschungseinstieg ist ein gesondertes Umsetzungspaket erforderlich:

1. Unabhängige C-Referenz und kurze neutrale Handfälle: kein Kontext; eine/mehrere kalte Hypothesen; Originalzeit-Gleichstand; gemischt warme Bestände; warme EC−EP=0 und positive Werte; negativer Bestwert-Gleichstand; eindeutiger Gewinner; ungültige Zustände. Außerhalb des kalten Zweigs müssen C/U-Ausgabe und Entscheidung exakt übereinstimmen. Im kalten Zweig müssen bestehender R-Ordnungsvergleich, Herkunft und Ticket stimmen.
2. Vor Auswahl, nach Rückmeldung und nach jedem Aufnahme-/Promotion-/Pruning-Schritt: identische Originalbestände, Rollen/Generationen, Reihenfolgen, Berechtigungen, Frozen-Nachfolger, Tickets, Persistenzframe, Fehlerzellen, Zähler und Revisionen. Beim Bankvergleich dürfen ausschließlich choice/reason (bestehend Bytes 202:204) normalisiert werden; keine Fehler- oder Identitätsfelder. Ausgabe-/Entscheidungsmetadaten separat prüfen. Erste kalte Nutzung, erste Rückmeldung und anschließende warme Nutzung müssen durchgängig gleiches Feedback zeigen. Gültige Promotion bewahrt Fehlerpaare, echter Ersatz bleibt regulärer Ersatz. Kein Reset am Wechsel [B5].
3. Frische Quelle unabhängig prüfen; Q128/129 und Q160/161, Nenner, Vorzeichen C−U, alle Intervallentscheidungen einschließlich Nullberührung neutral prüfen. Archiv-/Statistikreferenz muss C ausdrücklich verstehen; der bestehende U/R-Executor erlaubt nur U/R und ist nicht durch Umbenennung automatisch qualifiziert [B5,B7].
4. Getrennter Einstieg, neuer exklusiver Zielpfad und eigene Vorstartbindung; bestehende Integritäts-, Dateibilanzierungs-, Terminal- und Cleanup-Nachweise nur für unveränderte Komponenten übernehmen. Geänderte Integration fokussiert prüfen. Historische Dateien und verbrauchte Freigaben unangetastet lassen. Keine große Wiederholungsqualifikation ohne konkreten neuen Bedarf.

Ressourcenrahmen unverändert [B8]: höchstens 32 Geschichten/64 Arme; global 57600 s, Worker 54000 s, Abschlussreserve 3600 s innerhalb der Gesamtfrist; 512 MiB gemeinsamer Job und höchstens zwei Prozesse. Vorbereitung 8 MiB, Quellen gesamt 2 MiB/je 32 KiB, Archive 32 MiB/je gzip 512 KiB, encoded und dictionary je 4 MiB, record 256 KiB; nodes 65536, edges 262144, indices 65536, collections 16. Temporär und Gesamtexport einschließlich Vorbereitung je 64 MiB, Administration 2 MiB, Closure 1 MiB. Die unveränderte Bankgröße ersetzt keinen Nachweis für temporäre und gesamte Prozessressourcen. Keine Laufzeitgarantie aus REV1; Überschreitung führt zum technischen Abschluss ohne Retry, Resume oder Ersatzlauf.

## 6 Nachteile, Aussagegrenzen und Übergabe

Ein unbewertetes Original kann falsch sein. Bei den binären Q-Fortsetzungen kann der Originalfehler 0 oder 1/2 betragen, während Persistenz 1/4 ergibt: C kann einzelne kalte Ziele sowohl verbessern als auch verschlechtern. Neuere verfügbare Originale können seltene oder vor dem Wechsel entstandene Fortsetzungen enthalten. Der Primäreffekt kann durch wenige kalte Ziele klein oder unpräzise sein; das rechtfertigt keine nachträgliche Stichproben- oder Fensterauswahl.

Ein Vorteil wäre ein Befund zur konkreten Ausgabeentscheidung dieser Testfamilie. Da gemeinsame Fehlerzustände und Erfahrungsaufnahme gerade unverändert bleiben sollen, wäre er **kein Nachweis verbesserter Erfahrungsbildung**, neuer Memory-Organisation oder allgemeiner Intelligenz. Der Vergleich isoliert die feste kalte Auswahl, nicht einen allgemeinen Wechselmechanismus. Die Wahl ist post hoc motiviert, der geplante neue Vergleich vorab festgelegt; beides muss im späteren Bericht sichtbar bleiben.

Nächster Schritt: Projektleiter prüft diesen Vertrag und entscheidet über das begrenzte Umsetzungspaket aus Abschnitt 5. Bis dahin bleiben Implementierung, Quellenmaterialisierung, erneute Archivdiagnose und Versuchsstart geschlossen.

## Belegstellen

- B1: [Abgenommene REV1-Diagnose](../reports/s2uc/ura1-rev1-diagnosis-20261016-01/REPORT.md), Entscheidungsgründe und Herkunft kalter Hypothesen; hier ausschließlich vorhandener Bericht gelesen.
- B2: [MultiErrorAdapter](../tools/_s2uc_multi_error.py), `_find`/`_validate_cells`, `_receipt` ab Zeile 103, `consume_feedback` ab 179, `_promote` ab 267 und `_admit` anschließend.
- B3: [OriginalRecencyAdapter](../tools/_s2uc_ura1.py), `_receipt`, insbesondere `found.ordinal` und `selection_key`.
- B4: [PairContextAdapter](../tools/_s2uc_pair_context_adapter.py), `accept_perception` ab 41 und Aufnahme der unveränderten Frames nach `_receipt`.
- B5: [Bestehender Executor](../tools/_s2uc_ura1_v2_engine.py), `common`, `run_arm`, Ausgabemessung und getrennte Wahrnehmungs-/Rückmeldeverarbeitung; [gemeinsamer Archivvergleich](../tools/_s2uc_ura1_v2_fused.py), `finish`.
- B6: [REV1-Quellenrezept](../tools/_s2uc_ura1_rev1_sources.py), `Stream` und `generate`; [angenommener REV1-Vertrag](S2UC_URA1_REV1_TRANSFER_KONZEPTVERTRAG_20261015.md), Abschnitt 2.
- B7: [REV1-Fenster und Statistik](../tools/_s2uc_ura1_rev1_stats.py), `WINDOWS`, `interval`, `aggregate`; [unabhängige Referenz](../tools/_s2uc_ura1_rev1_stats_reference.py).
- B8: [Gebundene Grenzwerte](../tools/_s2uc_ura1_v2_series.py), `LIMITS`; [bestehende Integration](../tools/s2uc_ura1_prepare_rev1.py). Diese Dateien werden durch diesen Konzeptvertrag nicht geändert.
