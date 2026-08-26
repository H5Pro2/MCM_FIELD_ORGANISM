# S1-UL: ACM-1H statischer Zweigabschluss und Konsolidierungsaudit

## Zweck und Grenze

S1-UL schliesst den ACM-1H-Forschungszweig nach dem Ergebnis von S1-UK
statisch ab. Der Audit fuehrt keine Gleichung, keinen Parameter, keinen Code,
keinen Test und keinen Feldpfad aus. Er waehlt auch keinen neuen Kandidaten.

Verbindliche Grundlage ist das versiegelte S1-UK-Ergebnis
`EXPLAINED_BY_BASELINE`: CGR-1 reproduziert die vermittelte ACM-1H-Feldwirkung
fuer beide G/O-Zustaende und alle sechs Konfigurationen exakt.

## Fachliche Einordnung

ACM-1H besitzt gegen ACM-OFF und den vorzeichenblinden E1-Kantengain eine
technische G/O-Unterscheidung. Diese Unterscheidung ist jedoch nicht
eigenstaendig, weil eine breitere gekoppelte Gainbaseline dieselben
Kantenraten, Feldfolgezustaende und privaten Folgezustaende erzeugt.

Damit ist ACM-1H:

- eine transparente private Engineeringdarstellung eines gekoppelten Gains;
- ein geeignetes Regression- und Reduktionsbeispiel;
- kein eigenstaendiger Forschungskandidat fuer eine neue Feldfunktion;
- keine Grundlage fuer eine weitergehende Funktionsbehauptung.

CGR-1 bleibt ausschliesslich die erklaerende Reduktionsbaseline. Aus seiner
exakten Reproduktion entsteht keine neue produktive Feldmechanik.

## Erhaltener technischer Bestand

| Bestandteil | Verbindliche Rolle |
|---|---|
| `_acm1h_reference.py` | privater reiner Referenzkern und Reduktionsfixture |
| `_acm1h_field_runtime.py` | privater atomarer Integrations- und Regressionstraeger |
| `_acm1h_s1uk_matrix.py` | versiegelte private Vergleichsinfrastruktur; keine erneute Matrixausfuehrung |
| drei fokussierte Testdateien | technische Vertrags- und Regressionspruefung |
| S1-UK-Ergebnisartefakt | unveraenderlicher Nachweis des abgeschlossenen Vergleichs |
| S1-UC bis S1-UL | vollstaendige methodische Herleitung und Zweiggrenze |

Keiner dieser Bestandteile wird in Paketroot, `current_api`, produktiven
Feldsnapshot oder reale Laufpfade uebernommen.

## Gestoppte Fortsetzungen

Folgende Arbeiten werden fuer den ACM-1H-Zweig beendet:

- weitere ACM-1H-Parameterauswahl oder Parameteroptimierung;
- weitere ACM-1H-Matrix-, Feld- oder Rezeptorlaeufe;
- Erweiterung der Vier-Knoten-Pruefgeometrie auf eine 2D-Topologie;
- oeffentliche Runtime-, API- oder Snapshotintegration;
- Behandlung von ACM-1H als eigenstaendige neue Feldfunktion;
- Umbenennung der CGR-1-Erklaerung in einen positiven ACM-1H-Befund.

Eine Wiederaufnahme waere nur fachlich zulaessig, wenn vor jeder
Implementierung eine neue Gegenprognose vorliegt, die nicht durch CGR-1 oder
eine gleich starke bekannte Baseline rekonstruierbar ist. Der abgeschlossene
G/O-Vergleich selbst darf dafuer nicht erneut verwendet werden.

## Wirkung auf den primaeren Feldkern

Der primaere MCM-Feldkern bleibt unveraendert. S1-UK und S1-UL liefern keine
neue oeffentliche Feldfunktion. Technisch gewonnen wurden dagegen:

- ein geprueftes Muster fuer private atomare Feld-/Zustandspaare;
- eine faire Trennung von Zustandsintervention und gemeinsamem Probevorzustand;
- eine explizite Reduktionspruefung gegen eine staerkere Baseline;
- eine belastbare Stoppregel fuer baseline-reduzierbare Engineeringmodule.

Diese Punkte sind methodische Infrastruktur und kein Funktionsbefund des
Feldkerns.

## Abschlussentscheidung

Der ACM-1H-Zweig ist geschlossen und konsolidiert. Sein Code bleibt privat
und regressionsgesichert erhalten. Es folgt keine weitere ACM-1H-Ausfuehrung
und keine funktionale Aufwertung.

## Naechster fachlicher Schritt

Als genau ein Anschluss ist S1-UM zulaessig: ein statischer
Rueckkehr- und Lueckenaudit des primaeren MCM-Wahrnehmungsfeldes nach dem
ACM-1H-Zweig.

S1-UM darf nur pruefen, welche technisch offene Feldkernfrage nach Abzug der
geschlossenen Zweige noch eine eigene vorab formulierbare und gegen bekannte
Baselines nicht reduzierte Gegenprognose besitzt. Es darf keine neue
Kandidatenmechanik, Gleichung, Parameter, Implementierung oder Ausfuehrung
enthalten. Falls keine solche Frage uebrig bleibt, ist die Forschung zu
pausieren und nur die bestehende Feldarchitektur zu konsolidieren.
