# MCM-KI

Wahrnehmung, Gedächtnis und erfahrungsbasierte Erwartungen aus Audio und Video.

Das Projekt **MCM_FIELD_ORGANISM** untersucht, wie ein System Wahrnehmungsverläufe
aufnehmen, begrenzte Spuren davon bewahren und diese bei späteren Eindrücken
wieder nutzen kann. Im Mittelpunkt steht die Frage, wann frühere Erfahrung
tatsächlich hilft: beim Wiedererkennen, beim Umgang mit unvollständigen Hinweisen
und bei Erwartungen über den weiteren Verlauf.

Das Repository enthält einen **Forschungsprototyp**, seine experimentellen
Komponenten und die zugehörigen Prüfnachweise. Eine allgemein einsetzbare MCM-KI
ist damit noch nicht erreicht.

## Grundaufbau

```text
Audio und Video
      ↓
Rezeptoren und gemeinsame Wahrnehmungsbindung
      ↓
Getrennte Verarbeitung in Feld und Gedächtnis
      ↓
Vergleich mit gespeicherten Spuren
      ↓
Hypothese oder begründete Enthaltung
```

Feld und Gedächtnis erhalten dieselben kanonischen Wahrnehmungswerte, bleiben
aber technisch getrennt. Der Gedächtniszweig unterscheidet jüngere Inhalte
(`A_RECENT`) und stabilisierte auditive beziehungsweise visuelle Inhalte
(`B_STABLE`). Ein Teilhinweis kann mit gespeicherten Spuren verglichen werden.
Fehlt eine passende oder eindeutige Grundlage, enthält sich das System.

Ein solcher Abruf betrifft gespeicherte Wahrnehmungsmerkmale. Er bedeutet noch
nicht, dass das System ein Objekt, eine Szene oder deren Bedeutung versteht.
Die getrennte Software-Memory ist auch kein Nachweis eines Gedächtnisses,
das sich eigenständig innerhalb des Feldes organisiert.

## Entwicklungsstand

**Stand: 19. Oktober 2026**

Der Grundpfad zur Aufnahme, Speicherung und begrenzten Wiederverwendung von
Wahrnehmung ist implementiert und in abgegrenzten Versuchen geprüft.
Das Speichern und Wiederladen von Zuständen sowie einzelne Abruf- und
Vorhersagefunktionen sind dokumentiert. Ihr Nutzen hängt jedoch von der
jeweiligen Aufgabe und Vergleichsbedingung ab; ein allgemeiner Lernvorteil
ist nicht belegt.

Die jüngste Forschungsreihe untersucht das Wiedererkennen zeitlich verschobener
auditorischer Verläufe. Ihr letzter Versuch **RW1** wurde wegen der Zeitgrenze
technisch abgebrochen. Seine wissenschaftlichen Kriterien konnten nicht
vollständig ausgewertet werden. Daraus folgt weder ein positiver noch ein
negativer Forschungsbefund.

Eine anschließende technische Untersuchung identifizierte wiederholte
Verzeichnisscans als Engpass der Exportverwaltung bei einer festgelegten
künstlichen Schreiblast. Eine getrennte inkrementelle Variante benötigte dafür
rund **58,70 statt 214,27 Sekunden**, einschließlich Initialisierung und
Bestandsabgleich. Die Nutzdateien blieben bytegleich; 22 gezielte Fehlerprüfungen
bestanden. Die Variante ist noch nicht an den vollständigen RW1-Ablauf
angeschlossen. Der Befund belegt deshalb eine technische Verbesserung unter
diesen Testbedingungen, noch keinen zusätzlichen Wahrnehmungs- oder Lernnutzen.

Nachweise: [RW1-Abschlussbericht](reports/s2uc/rw1-research-01/closure/REPORT.txt)
und [Diagnose der Exportverwaltung](reports/s2uc/rw1-budget-diagnosis-20261019-01/REPORT.txt).

## Forschungsrichtung

Langfristig soll das System aus Wahrnehmungsverläufen nutzbare Erfahrung
gewinnen: Zusammenhänge behalten, Erwartungen bilden und Abweichungen erkennen.
Ein weiterer konzeptioneller Schwerpunkt ist **gezielte Aufmerksamkeit**.
Untersucht werden soll, ob ausgewähltes, genaueres Hinsehen oder Hinhören
tragfähigere Verknüpfungen ermöglicht als die bloße Aufnahme größerer Datenmengen.

Verdichtete Erfahrung, flexible Aufmerksamkeit und eine dadurch mögliche
Verringerung des Verarbeitungsaufwands sind Forschungsziele. Sie sind noch keine
nachgewiesenen Eigenschaften des aktuellen Systems. Die Überlegungen dazu stehen
in der [Konzeptnotiz zu Wahrnehmung, Prägung und Aufmerksamkeit](docs/KONZEPTNOTIZ_WAHRNEHMUNGSVERLAEUFE_PRAEGUNG_UND_INNERKONTEXT.md).

## Aufbau des Repositorys

| Verzeichnis | Inhalt |
| --- | --- |
| [`mcm_field_organism/`](mcm_field_organism/) | Komponenten des Feldsystems |
| [`experiments/`](experiments/) | Abgegrenzte experimentelle Implementierungen |
| [`tools/`](tools/) | Forschungswerkzeuge, Adapter und Laufumgebungen |
| [`tests/`](tests/) | Technische Prüfungen |
| [`docs/`](docs/) | Architektur, Konzepte und Versuchsverträge |
| [`reports/`](reports/) | Ergebnisberichte und gespeicherte Prüfnachweise |
| [`analyses/`](analyses/) | Vertiefende Auswertungen |
| [`audits/`](audits/) | Prüfunterlagen |

## Dokumentation und Nutzung

- [Dokumentationsübersicht](docs/README.md): Einstieg in die fachlichen und technischen Unterlagen.
- [Forschungsweg](AKTUELLER_FORSCHUNGSWEG.md): detaillierter Stand, historische Ergebnisse und jeweilige Aussagegrenzen.
- [Betriebsanleitung des privaten Sitzungseinstiegs](docs/BETRIEBSANLEITUNG_PRIVATER_OC_SITZUNGSEINSTIEG.md): Dateieingang, Sitzungsablauf und technische Grenzen.
- [Arbeitsregeln](AGENTS.md): verbindliche Projekt- und Ausführungsregeln.

Die vorhandenen Versuchseinstiege sind an ihre jeweiligen Quellen, Prüfbedingungen
und Ressourcenlimits gebunden. Es gibt noch keinen allgemeinen Startbefehl für
eine frei nutzbare MCM-KI. Historische Laufanleitungen sind keine aktuellen
Ausführungsfreigaben. Die Arbeit erfolgt mit kontrollierten Audio- und
Videoquellen; Kamera und Mikrofon sind nicht als Live-Sensoren aktiv.

Diese README dient als Projektübersicht. Versuchsprotokolle, interne
Arbeitsaufträge und historische Entscheidungen stehen in der verlinkten
Forschungsdokumentation.
