# W3-A: current_api End-to-End-Consumertest

Stand: 2026-08-09

Entscheidung: `CURRENT_API_CONTROLLED_AV_CONSUMER_PATH_COMPLETE`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-A prueft, ob ein externer technischer Verbraucher den aktuellen
kontrollierten Feldpfad ausschliesslich ueber `mcm_field_organism.current_api`
aufbauen kann:

```text
synthetische kontrollierte Audio-/Videofolgen
-> Audio- und Videorezeptoren
-> kontrollierte Sequenzaufnahme
-> neutrales gemeinsames Feld
-> Snapshot
-> Restore
```

## Importgrenze

Der neue Test `test_current_api_end_to_end_consumer.py` besitzt genau einen
Projektimport:

```python
from mcm_field_organism.current_api import (...)
```

NumPy und Python-Standardbibliothek erzeugen nur kontrollierte Testdaten und
eine threadsichere monotone Testuhr. Es gibt keinen direkten Import eines
internen Projektmoduls und keinen Paket-Root-Import.

## Kontrollierter Pfad

Der Test verwendet:

- zehn synthetische Audioframes fuer 0,2 Sekunden;
- zwei synthetische Videoframes mit 12 x 8 Pixeln;
- einen logarithmischen Audiorezeptor mit vier Baendern;
- einen lokalen 2 x 2-Videogitterrezeptor;
- eine neutrale lokale Feldkonfiguration;
- eine explizite technische Organismusuhr.

Der Pfad erzeugt sechs abgeschlossene auditive und zwei visuelle reduzierte
Rezeptorzustaende. Alle acht Supports werden genau einmal uebergeben. Der
erzeugte Feldsnapshot wird restauriert und behaelt denselben Digest.

Der Test prueft ausserdem, dass weder optionales F3-Substrat noch ein
Entwicklungszustand aktiviert wurde.

## Verifikation

```text
118 passed
350 subtests passed
Python-Kompilierung erfolgreich
8 von 8 Supports zugewiesen
Snapshot-Digest nach Restore identisch
substrate is None
development is None
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- `mcm_field_organism.current_api`;
- W2-J als statisch geschlossene Importgrenze;
- bestehende technische Rezeptor-, Feld- und Snapshotvertraege;
- kontrollierte synthetische Testdaten im neuen Consumertest.

## Aussagegrenze

W3-A belegt nur die technische Vollstaendigkeit der kuratierten Fassade fuer
diesen kontrollierten Pfad. Snapshot/Restore ist Runtime-Serialisierung und
kein MCM-Memory. Der Test belegt kein Lernen, keine Feldzeit, Organisation,
Semantik, Selbstregulation oder KI. Es wurde kein Browser gestartet und keine
Kamera, kein Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197
bleibt unberuehrt.

## Bester naechster Schritt

W3-B erweitert den Fassade-only Consumertest um eine kausale
Fortsetzungspruefung:

1. Ein kontrollierter erster AV-Abschnitt erzeugt ein Feld und einen Snapshot.
2. Derselbe zweite reduzierte Rezeptorabschnitt wird einmal auf dem
   ununterbrochenen Feld und einmal auf dessen restaurierter Kopie fortgesetzt.
3. Beide Endfelder muessen denselben Digest besitzen.
4. Der Test importiert weiterhin ausschliesslich aus `current_api`.
5. F3-Referenzarm, Live-Sensorik und Forschungsclaims bleiben ausgeschlossen.

## Spaeterer Umsetzungsstand W3-B

W3-B ist am 2026-08-09 umgesetzt worden. Derselbe zweite reduzierte
AV-Abschnitt erzeugt auf dem ununterbrochenen Feld und einer restaurierten
Kopie des ersten Snapshots denselben Enddigest. Der aktuelle Verbund besteht
mit `119 passed` und 350 Subtests.
