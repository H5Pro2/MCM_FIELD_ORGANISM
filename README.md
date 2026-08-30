# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` entwickelt ein technisches MCM-Wahrnehmungsfeld mit
getrennten Rezeptorpfaden, einer gemeinsamen Feldschicht und einer
MCM-kompatiblen perzeptiven Memory-Architektur.

Das Projekt untersucht klar begrenzte technische Funktionen. Begriffe und
Fähigkeiten werden erst dann verwendet, wenn sie durch einen vorab gebundenen,
reproduzierbaren Befund gestützt sind.

## Aktueller Stand

Der technische Feldkern verarbeitet auditive und visuelle Rezeptorzustände
über getrennte Docks in derselben MCM-Neuronenschicht. Herkunft, Geometrie und
Zeitbindung bleiben nachvollziehbar. Rohbilder und Rohsignale werden nicht im
Feldzustand gespeichert.

Für verdichtete Wahrnehmungszustände bestehen derzeit drei getrennte private
Speichersichten:

- `B4_RECENT`: jüngste Inhalte und ihre tatsächliche Bildungsreihenfolge;
- `TSPM_FAST`: kurzlebige Inhaltsspuren;
- `TSPM_SLOW`: durch Wiederholung stabilisierte auditive und visuelle Inhalte.

Ein atomarer privater Koordinator schreibt B4 und TSPM-1 aus derselben
Wahrnehmungsquelle fort. Read-only Abrufe verändern die Speicherzustände
nicht. Ein begrenzter technischer Funktionslauf hat Kurzfolgen,
wiederholungsabhängige Stabilisierung und kontrolliertes Vergessen für seine
vorab festgelegte synthetische Aufgabe bestätigt.

Die qualifizierte Kontextdarstellung ordnet diese Befunde zwei logischen
Bereichen zu:

```text
A_RECENT
  B4-Inhalt
  B4-Kurzfolge
  interne Fast-Spur

B_STABLE
  stabilisierte auditive und visuelle Slow-Inhalte
```

Diese A/B-Darstellung trifft keine automatische Auswahl und wirkt noch nicht
auf das MCM-Feld zurück.

Der aktuelle Forschungsauftrag ist eine einzelne maskierte visuelle
Kontextaufgabe. Dabei soll geprüft werden, ob ein ausdrücklich benannter
`B_STABLE`-Kandidat fehlende visuelle Werte ergänzen kann, ohne sichtbare
Wahrnehmungswerte oder Speicherzustände zu verändern. Verbraucher, direkte
Baseline und Auswerter sind neutral qualifiziert. Die tatsächlichen
Bildungsgeschichten und der Funktionsvergleich wurden noch nicht ausgeführt.

Der verbindliche Detailstand steht in der
[aktuellen technischen Projektgrenze](docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md).
Die README wird nicht als Forschungsjournal fortgeschrieben.

## Grundarchitektur

![Schaltplan des gemeinsamen MCM-Feldes](docs/bilder/architektur/mcm_field_organism_gemeinsames_feld_schaltplan.png)

```text
Audio-/Video-Rezeptoren
-> neutraler Rezeptorenverteiler
-> modalitätsgebundene MCM-Docks
-> gemeinsame MCM-Neuronenschicht
-> gemeinsamer Feldzustand
```

Die Feldtopologie, Nachbarschaften und technischen Ausbreitungswege sind
vorgegeben. Wahrnehmung liefert Eingaben, aus denen der Feldkern innerhalb
dieser Anatomie Zustände und Flüsse berechnet.

Die perzeptive Memory bleibt vom öffentlichen Feldsnapshot getrennt:

```text
verdichteter Wahrnehmungszustand
-> begrenzte private Speicherbildung
-> read-only Abruf
-> transparente Kontextdarstellung
```

Eine spätere Kontextverwendung oder Feldrückwirkung benötigt jeweils einen
eigenen Funktions- und Falsifikationsvertrag.

## Technische Grenzen

Der aktuelle Stand belegt nicht:

- eine allgemeine oder langfristige MCM-Memory;
- semantisches Verstehen oder Objektverständnis;
- automatische Auswahl eines passenden inneren Kontexts;
- selbstständiges Episoden- oder Sequenzlernen;
- eine MCM-spezifische neue Speicherphysik;
- eine produktive Feldintegration der privaten Memory-Komponenten.

Bekannte Speicherverfahren und einfachere Engineeringbaselines bleiben
zulässige Lösungen. Gleichwertigkeit mit einer einfacheren Architektur ist
kein Forschungsfehler; bei gleichem Funktionsumfang wird die einfachere
Lösung bevorzugt.

Geschlossene Forschungs- und Plattformpfade dürfen nicht durch Umbenennung
oder neue Belegrollen wieder geöffnet werden. Historische Befunde bleiben in
den Fach- und Archivdokumenten erhalten.

## Dokumentation

### Aktueller Entwicklungszweig

- [Aktuelle technische Projektgrenze](docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md)
- [Bestandskonsolidierung nach dem Plattformstopp](docs/BESTANDSKONSOLIDIERUNG_NACH_PLATTFORMSTOPP.md)
- [Bestätigter B4-/TSPM-1-Verbund](docs/S2FZ_UNABHAENGIGER_18_SCHRITT_BESTAETIGUNGSLAUF.md)
- [Qualifizierte A/B-Schattenprojektion](docs/S2GI_PRIVATE_AB_PROJEKTION_UND_EINMALQUALIFIKATION.md)
- [Aktueller S2-GM-Abnahmeaudit](docs/S2GM_STATISCHER_ABNAHMEAUDIT_S2GL.md)

### Architektur und Methodik

- [Gründungs- und Architekturvertrag](docs/GRUENDUNGSVERTRAG.md)
- [Gemeinsames MCM-Feld](docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md)
- [Rezeptorvertrag und Dockgrenze](docs/architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [Gemeinsamer Audio-Video-Feldkontakt](docs/architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md)
- [Hypothetische MCM-Memory-Entwicklungsrichtung](docs/architektur/028_HYPOTHETISCHE_MCM_MEMORY_ENTWICKLUNGSRICHTUNG.md)
- [Weltkontakt, innerer Kontext und Feldrückwirkung](docs/architektur/030_WELTKONTAKT_INNERER_KONTEXT_UND_FELDRUECKWIRKUNG.md)
- [Evidenzgrenze des gemeinsamen MCM-Feldes](docs/EVIDENZGRENZE_GEMEINSAMES_MCM_FELD.md)
- [Offene Forschungsfragen](docs/FORSCHUNGSFRAGEN.md)
- [Historische Architekturstände](docs/architektur/HISTORISCHE_ARCHITEKTURSTAENDE.md)
- [Archiv der Vorarbeiten](docs/archiv/vorarbeiten_bis_forschungsstart/README.md)

Vorarbeiten aus [MINI_DIO](https://github.com/H5Pro2/MINI_DIO) und der
[Mental-Core-Matrix](https://github.com/H5Pro2/Mental-Core-Matrix-MCM) dienen
ausschließlich als Forschungsreferenzen. Sie gelten nicht automatisch als
Evidenz dieses Projekts.
