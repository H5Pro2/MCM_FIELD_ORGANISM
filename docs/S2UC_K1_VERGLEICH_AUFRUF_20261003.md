# K1: vorbereitete Aufrufspezifikation und Startgrenze

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Interpreter: `C:\Python314\python.exe`, Python 3.14.4, ohne Optimierung.

Der vorhandene, ausführbare Integritätsaufruf lautet:

```powershell
& C:\Python314\python.exe -m tools.s2uc_k1_check_package
```

Dieser liest ausschließlich Codebindungen und Belege. Er erzeugt keine Quellen,
startet keine Policy und verbraucht keine Einmallauffreigabe.

Für den Vergleich ist folgende Aufrufspezifikation vorbereitet. Sie ist bewusst
kein als lauffähig ausgegebener Shellbefehl: Ein qualifizierter 24-Fälle-Executor
existiert noch nicht. Der frühere T1-Executor ist kein U/K1-Executor.

| Parameter | Fester Wert |
| --- | --- |
| Implementierungsbindung | S2UC_K1_IMPLEMENTIERUNGSBINDUNG_20261003.json, SHA256 aus Abschlussversiegelung |
| Varianten | U: candidate_policy=disabled; K1: candidate_hold_one_block_v1; identische vorhandene Multi-Fehlerpolicy |
| Fallmenge | Alle 16 gespeicherten T1-Fälle in Vertragsreihenfolge plus F1–F8 unverändert gemäß Konzeptvertrag |
| Eingaben | 16 × 80 + 8 × 64 = 1.792 Positionen |
| Ausführung | 48 frische Arme; 3.584 Aufnahmen und 3.584 eigene Referenzfortschreibungen |
| Bewertete Ziele | T1:624; F:248; gesamt872 je Variante; letzte Prognosen zensiert |
| Zeit | 3.600 s gesamt, 3.540 s Worker, 60 s Abschluss |
| Export | 64 MiB einschließlich 1 MiB Abschlussreserve; Vorbereitung 8 MiB |
| Autorisierung | Neue, exakt gebundene Einmalfreigabe; derzeit nicht vorhanden |
| Ergebnis | Vier getrennte Urteile: Technik, Mechanismus, Gesamtnutzen, Schaden |

Die vollständigen symbolischen Fallfolgen, Zielmasken und Entscheidungsregeln
stehen unverändert im K1-Konzeptvertrag. Keine F-Quellen wurden materialisiert.

Vor einem ausführbaren Vergleichsaufruf fehlen: der konkrete Executor samt
vollständigem Auswerter, gebundene Quellen/Masken, Ressourcen- und Zeitplanung
für dieses Paket, neutrale Qualifikation seines Start-/Fehlerabschlusses und
eine neue Einmalautorisierung. Diese Aufrufspezifikation erteilt keine Freigabe.
Der nächste begrenzte Entwicklerauftrag sollte genau diese technische
Vergleichsvorbereitung abdecken, ohne Vergleichsausführung. Die K1-Regel bleibt
dabei eingefroren; die bereits gültigen K01–K10-Prüfungen werden nicht wiederholt.
