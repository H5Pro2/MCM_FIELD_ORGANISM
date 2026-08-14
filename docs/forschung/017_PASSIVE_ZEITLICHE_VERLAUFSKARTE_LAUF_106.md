# Technischer Stand: passive zeitliche Verlaufskarte zu Lauf 106

## Freigegebener Umfang

Der Wahrnehmungszweig von Lauf 106 wurde ausschließlich um einen passiven
Observer ergänzt. Die bestehende Feldruntime, ihre Zustandsrollen und ihre
Parameter bleiben unverändert.

Der Observer verarbeitet:

- dieselbe auf 35.000 ms begrenzte Bildfolge;
- dieselben 280 Rezeptorintervalle zu je 125 ms;
- die exakte unabhängige Wiederholung;
- die statische Bildbaseline aus Lauf 106.

Der Runner akzeptiert den Lauf nur, wenn der reduzierte Digest exakt

```text
f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
```

entspricht.

## Äußere Zeitabschnitte

Die Standardgrenzen werden vor jeder Feldbeobachtung ausschließlich als
äußere Millisekundenwerte festgelegt:

```text
0, 5000, 10000, 15000, 20000, 25000, 30000, 35000
```

Andere Grenzen sind nur zulässig, wenn sie lückenlos bei null beginnen, den
gesamten Lauf abdecken und auf den festen 125-ms-Intervallen liegen. Eine
Auswahl anhand von Rezeptor- oder Feldwerten ist technisch nicht möglich.

## Ausgegebenes Beobachterartefakt

Für jedes der 280 Intervalle enthält die JSON-Verlaufskarte:

- aktuelle lokale Rezeptorprojektion;
- lokale Aktivierung nach dem Intervall;
- lokalen schnellen Nachhall nach dem Intervall;
- euklidische Änderung der Projektion;
- euklidische Änderung der Aktivierung;
- ungeschwelltes Skalarprodukt aus aktueller Projektion und vorherigem
  Nachhall.

Diese letzten drei Größen quantifizieren Bildung, gleichzeitige Überlagerung
und Ablösung nur als technische Verlaufsmaße. Sie erkennen keine Segmente und
tragen keine Memory-, Verdichtungs-, Bedeutungs- oder Topologierolle.

Für jeden äußerlich festgelegten Abschnitt werden ausschließlich Summen der
drei ungeschwellten Intervallmaße ausgegeben. Vollständige lokale Karten
bleiben für reale Bildfolge und statische Baseline getrennt erhalten.

Die vollständige Erklärungsbaseline ist im Artefakt explizit auf folgende
bestehende Mechanik begrenzt:

```text
aktuelle Rezeptorprojektion
+ feste symmetrische Diffusion
+ schneller Nachhall
```

Zur vollständigen Nachrechnung enthält das Artefakt außerdem die feste
Vierernachbarschaft, die unveränderte Feldantwortzeit `1,0 s` und die
unveränderte Nachhallzeitkonstante `0,5 s`.

Die reale Sequenz und ihre exakte Wiederholung sowie beide statischen
Wiederholungen werden unabhängig intervallweise abgespielt. Der maximale
absolute Wiederholungsrest wird jeweils ausgewiesen. Es gibt keine adaptive
Schwelle und keine Auswahl oder Umdeutung einzelner Übergänge.

## Organismusgrenze

Die Verlaufskarte ist ein Observerartefakt. Sie wird weder an Rezeptoren noch
an Dock, Neuronenschicht, Feldsnapshot oder Effektor zurückgegeben. Rohbilder
werden weiterhin unmittelbar auf Rezeptorwerte reduziert und nicht im
Artefakt gespeichert. Es wurden keine Runtimevariable, Persistenz,
Verdichtung, Segmenterkennung oder Memorymechanik ergänzt.

Automatische Kamera-Rückführung und ein geschlossener
Feld-Welt-Feld-Dauerlauf bleiben gesperrt.

## Technische Prüfung

Implementiert wurden:

- `mcm_field_organism/public_visual_temporal_map.py`;
- `tools/run_public_visual_temporal_map.py`;
- `tests/test_public_visual_temporal_map.py`.

Die Python-Quellen wurden erfolgreich kompiliert. `git diff --check` meldet
keine Fehler. Die numerischen Tests und der reale 280-Intervall-Lauf konnten
in diesem Codex-Lauf nicht ausgeführt werden, weil im Workspace weder die
Originalvideodatei noch eine Python-Umgebung mit der Projektabhängigkeit
`numpy` vorhanden war. Deshalb liegt noch kein abnahmefähiger numerischer
Befund und kein Verlaufskarten-Digest vor.

Der nächste technische Schritt ist ausschließlich die Ausführung des Runners
mit der bereits in Lauf 106 verwendeten Originaldatei in einer Umgebung mit
`requirements-video.txt`. Erst das digestgeprüfte JSON darf als Verlaufskarte
ausgewertet werden.

## Aussagegrenze

Aus der späteren Verlaufskarte darf nur bestimmt werden, welche Übergänge
durch aktuelle Rezeptorwerte, feste Diffusion und schnellen Nachhall
vollständig reproduziert werden. Die Karte selbst ist kein Memory-,
Verdichtungs- oder Topologiebefund.

## Tatsächlich verwendete Workspace-Quellen

- `README.md`;
- `PRIO_UMSETZUNGSPLAN.md`;
- `docs/EVIDENZGRENZE_GEMEINSAMES_MCM_FELD.md`;
- `docs/forschung/016_OEFFENTLICHE_VISUELLE_AUSSENWELT_WAHRNEHMUNGSBEFUND.md`;
- `docs/architektur/104_TECHNISCHER_VERTRAG_VISUELLE_MCM_EFFEKTORFLAECHE.md`;
- `docs/architektur/105_KAUSALVERTRAG_GETRENNTE_VISUELLE_WELTWIRKUNG.md`;
- bestehende Implementierung und Tests des öffentlichen visuellen Weltlaufs,
  der asynchronen Feldruntime und des neutralen lokalen Feldsubstrats.

Es wurden keine projektfremden Wissensquellen verwendet.
