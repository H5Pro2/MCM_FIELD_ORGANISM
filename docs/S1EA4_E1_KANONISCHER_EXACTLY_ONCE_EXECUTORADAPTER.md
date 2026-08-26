# S1-EA4: E1 kanonischer Exactly-once-Executoradapter

## Status

Der kanonische Exactly-once-Executoradapter ist implementiert und gegen
temporaere Spiegelpfade abgenommen. Der Adapter ist technisch gebunden, aber
seine kanonische Ausfuehrung und Persistenz bleiben falsch. Der produktive
Einstieg bricht weiterhin vor jedem Marker ab.

## Implementierung

```text
mcm_field_organism/e1_canonical_refined_chain_executor_adapter.py
tests/test_e1_canonical_refined_chain_executor_adapter.py
```

Normalisierter Implementierungsdigest:

```text
74e5ac4ee337192ecca97263bd68d7e512bfda823c924042b72a3e2d0f902508
```

## Adapterbindung

`prepare_e1_canonical_executor_adapter(...)` bindet:

- den kanonischen JSON-Digest des aktuellen S1-EA3-Preflights;
- den S1-DW-Einmallaufdigest;
- die drei exakten kanonischen Dateinamen;
- die vollstaendige Berichtsfeldreihenfolge;
- `canonical_executor_bound=True`;
- ausschliesslich `mirror_execution_permitted=True`.

Kanonische Ausfuehrung, kanonische Persistenz und automatischer Retry bleiben
falsch.

## Spiegelabnahme

`execute_mirrored_e1_canonical_refined_chain_one_shot(...)` akzeptiert nur
ein bestehendes temporaeres Verzeichnis ausserhalb des kanonischen
Zielordners. Dort verwendet es dieselben Dateinamen und dieselbe
Exactly-once-Politik:

1. exklusive Sperrdatei;
2. exklusiver Versuchsmarker vor Produzentenaufruf;
3. strikte S1-DX-Ergebnisvalidierung;
4. identische geordnete S1-DW-Berichtsfelder;
5. temporaere Datei mit Ruecklesepruefung;
6. exklusive atomare Veroeffentlichung;
7. Entfernung von Versuch und Sperre nur nach Erfolg;
8. Beibehaltung des Versuchsmarkers nach gestartetem Fehler;
9. Sperrung jeder Wiederholung.

Der Spiegelbericht ist eine Persistenzfixture und kein kanonischer
Forschungsbericht.

## Produktive Grenze

`execute_e1_canonical_refined_chain_one_shot(...)` ist vorhanden, lehnt aber
jeden Aufruf bis S1-EA5 ab. Ungueltige Vorstarteingaben erzeugen weder Marker
noch Bericht. Die drei Projektpfade blieben waehrend aller Tests frei.

## Technische Abnahme

```text
5 fokussierte Tests
396 Tests im vollstaendigen E1-Verbund
OK
```

Der S1-DN-Bericht blieb digestidentisch.

## Aussagegrenze

S1-EA4 liefert keine kanonischen Messwerte und keinen Bildungs-, Transfer-,
Memory-, Semantik-, Organisations-, Topologie-, Selbstregulations- oder
KI-Befund.

## Anschluss

S1-EA5 bindet nun alle Vertraege, Implementierungen, Einstiege und freien
Pfade im letzten statischen Gate. Der folgende Schritt waere erstmals der
tatsaechliche kanonische Einmallauf.
