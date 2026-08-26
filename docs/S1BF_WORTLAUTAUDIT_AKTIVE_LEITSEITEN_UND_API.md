# S1-BF: Wortlautaudit der aktiven Leitseiten und API

## Status

Dokumentations- und Docstringkorrektur. Keine Runtimeaenderung, keine neue
Mechanik, kein Forschungslauf und kein Memory-, Substrat- oder KI-Befund.

## Auftrag

Die aktiven Projekteinstiege und Docstrings wurden auf missverstaendliche
Gleichsetzungen folgender Rollen geprueft:

```text
Snapshot / Restore
schneller Nachhall H
NeutralLocalFieldSubstrateConfig
C_i-, F3- und S1B-Referenzpfade
MCM-Memory als offene Zielhypothese
```

Historische Forschungsdokumente und abgeschlossene Einzelbefunde wurden nicht
umgeschrieben.

## Gefundene Probleme

1. Der Bauplan erlaubte im Eingangstext noch die sofortige Spezifikation und
   Implementierung neuer Substratphysik. Das widersprach dem spaeteren
   Negativentscheid S1-AY.
2. Haupt-README, Prioritaetsplan und Dokumentationsuebersicht verwiesen zwar
   auf den aktuellen Forschungsweg, stellten den spaeteren Stopp und die
   aktive AV-Engineeringlinie aber nicht vor ihre langen historischen
   Chronologien.
3. Der Modulname `neutral_local_field_substrate` konnte ohne Erklaerung als
   bereits vorhandenes Memorysubstrat gelesen werden.
4. Der `current_api`-Docstring erklaerte die Bedeutung seiner getrennten
   Referenzmanifeste nicht.

## Korrektur

Die aktiven Einstiege verwenden nun einheitlich folgende Begrenzung:

```text
Snapshot / Restore = technische Runtime-Serialisierung
H                  = schnelle passive Spur
neutrale Config    = technische S/H-Feldantwort
C_i / F3 / S1B     = getrennte technische Referenzpfade
MCM-Memory         = nicht implementiert und nicht nachgewiesen
Substratneubau     = bis zu einem S1-AW-konformen Naturprinzip gestoppt
aktive Linie       = kontrolliertes AV-Feld-Engineering
```

Der historische Python-Name bleibt aus Kompatibilitaetsgruenden bestehen.
Sein Modul- und Konfigurationsdocstring schliessen eine Memorylesart jetzt
explizit aus.

## Geaenderte aktive Einstiege

- `README.md`
- `BAUPLAN_UND_ANWEISUNG.md`
- `PRIO_UMSETZUNGSPLAN.md`
- `docs/README.md`
- `mcm_field_organism/current_api.py`
- `mcm_field_organism/neutral_local_field_substrate.py`

## Aussagegrenze

Die Korrektur aendert keine wissenschaftliche Hypothese und wertet keinen
technischen Zustand um. Sie synchronisiert nur den sichtbaren aktuellen
Projektwortlaut mit den bereits getroffenen Entscheidungen S1-AV bis S1-BE.

## Bester naechster Schritt

Die aktive Architektur ist jetzt technisch und sprachlich getrennt. Als
naechstes sollte keine weitere reine Bereinigung folgen. Der naechste
sinnvolle Engineeringanschluss ist eine kompakte, geraeteneutrale
Zustandsbeschreibung des aktiven AV-Pfads fuer externe Verbraucher, erzeugt
direkt aus den bestehenden Manifest- und Snapshotvertraegen.

