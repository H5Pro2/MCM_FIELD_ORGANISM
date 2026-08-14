# Lauf 153: Isoliertes OpenCV-Fokus- und Tastatur-Prüfwerkzeug

## Forschungsfrage und Auftrag

Kann die bestehende OpenCV-Tastatureingabe der Aufbauabnahme ohne Kamera, Effektor, Rezeptor oder Feldruntime isoliert geprüft werden, ohne aus einer Taste automatisch eine Aufbauentscheidung abzuleiten?

Freigegeben war eine eng begrenzte technische Erweiterung für diese isolierte Prüfung sowie eine synthetische Absicherung der Key-Mapping-Logik.

## Verwendete Quellen

- aktueller Übergabeeingang mit Prüfergebnis und Folgeauftrag zu Lauf 152
- `docs/forschung/046_PHYSISCHER_FELD_WELT_FELD_AUFBAUVERTRAG_LAUF_124.md`
- `docs/forschung/052_REALE_AUFBAUABNAHME_NO_DECISION_LAUF_152.md`
- `tools/run_physical_setup_acceptance.py`
- `tests/test_physical_setup_acceptance_tool.py`

Externe Webquellen und Medien wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu:

- `tools/run_opencv_keyboard_focus_probe.py`
- `tests/test_opencv_keyboard_focus_probe_tool.py`

Als Referenz gelesen:

- `tools/run_physical_setup_acceptance.py`
- `tests/test_physical_setup_acceptance_tool.py`

Verwendete OpenCV-Schnittstellen des neuen Werkzeugs sind `namedWindow`, `imshow`, `waitKey`, `getWindowProperty` und `destroyAllWindows`. Es gibt keinen Kameraaufruf und keinen Import der Projektlaufzeit.

## Durchgeführte Schritte

1. Bestehende Zuordnung von `A`, `R` und `Esc` in der Aufbauabnahme untersucht.
2. Ein eigenständiges, auf 15 Sekunden begrenztes Diagnosewerkzeug erstellt.
3. Neutrale Ereignisse definiert: `KEY_A_RECEIVED`, `KEY_R_RECEIVED`, `KEY_ESCAPE_RECEIVED` und `NO_KEY_RECEIVED`.
4. Automatische Aufbauannahme und -ablehnung ausdrücklich nicht übernommen.
5. Vertrags- und Mappingtests für das neue Werkzeug ergänzt.
6. Neue und bestehende fokussierte Tests gemeinsam ausgeführt.

Ein reales OpenCV-Fenster wurde in Lauf 153 nicht geöffnet. Es gab keinen Kamera- oder Hardwarezugriff.

## Messergebnisse und Gegenbaselines

Testaufruf:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_opencv_keyboard_focus_probe_tool.py tests\test_physical_setup_acceptance_tool.py
```

Ergebnis:

```text
8 passed in 0.78s
```

Synthetisch bestätigt:

- `A`/`a` -> `KEY_A_RECEIVED`
- `R`/`r` -> `KEY_R_RECEIVED`
- `Esc` -> `KEY_ESCAPE_RECEIVED`
- andere Taste -> `NO_KEY_RECEIVED`
- Zeitlimit muss positiv sein; Standard ist 15 Sekunden.
- kein `VideoCapture` oder `OpenCVVideoFrameSource`
- keine Ausgaben `HUMAN_ACCEPTED` oder `HUMAN_REJECTED`
- kein Import von `mcm_field_organism`

Gegenbaseline ist die bestehende Aufbauabnahme: Dort werden dieselben drei Tasten als menschliche Aufbauentscheidung interpretiert und gleichzeitig Kameraframes gelesen. Das neue Werkzeug isoliert dagegen ausschließlich den Empfang der Taste.

## Grenzen und nicht geprüfte Annahmen

Beobachtet ist nur die korrekte synthetische Vertragslogik. Nicht geprüft ist, ob das OpenCV-Fenster im konkreten Desktop-Kontext sichtbar wird, Fokus erhält und eine reale Taste empfängt. `getWindowProperty(..., WND_PROP_VISIBLE)` prüft Sichtbarkeit, nicht zuverlässig den Betriebssystemfokus.

Das Werkzeug belegt keine Ursache der früheren `NO_DECISION`-Ergebnisse. Es prüft keine Kamera, keine physischen Aufbaukriterien und keine Feld-Welt-Feld-Wirkung. MCM-Feldzeit, Memory, Organisation, Semantik und Topologie bleiben unberührt und nicht nachgewiesen. `E0`, `E1`, `B0` und `B1` bleiben gesperrt. Keine Zielabweichung ist erkennbar.

## Konkrete Schlussfolgerung

Eine eng abgegrenzte Schnittstelle für die isolierte reale Fokus-/Tastaturprüfung ist implementiert und synthetisch abgesichert. Sie erzeugt aus Tastendrücken keine Aufbauentscheidung. Die tatsächliche Eingabeübertragung im Desktop-Kontext ist noch offen.

## Vorschlag für den nächsten begrenzten Forschungslauf

Einmalige interaktive Ausführung von `tools/run_opencv_keyboard_focus_probe.py` im lokalen Desktop-Kontext. Die Person fokussiert das neutrale Fenster und drückt genau eine der Tasten `A`, `R` oder `Esc`. Zu erfassen sind ausschließlich Ereignis, Laufzeit und Anzahl der `waitKey`-Iterationen. Keine Kamera, keine Bildanalyse, keine Speicherung und keine Feldkomponente. Erst nach erfolgreichem realem Tastaturempfang wäre eine gesondert freigegebene Aufbauabnahme technisch sinnvoll.
