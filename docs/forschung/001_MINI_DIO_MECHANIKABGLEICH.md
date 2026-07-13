# MINI_DIO-Mechanikabgleich

## 1. Zweck und Grenze

Dieser Abgleich rekonstruiert die tatsächlichen Laufzeitpfade des
Vorgängerprojekts MINI_DIO. Er übernimmt weder Code noch Evidenz. Der gelesene
Quellstand befindet sich im lokalen Repository `C:\Users\TV\Desktop\MINI_DIO`
und wurde ausschließlich read-only untersucht.

Berichtsnamen und Selbstbeschreibungen gelten nicht als Mechaniknachweis. Für
die Einordnung sind die Aufrufpfade in `run_mini.py` und die tatsächlich
gelesenen Zustände maßgeblich.

## 2. Rekonstruierter aktiver Hauptpfad

```text
Chartdaten
-> build_senses*()
-> fest gewichtete rezeptorische Mischgrößen
-> mcm_coherence / mcm_tension / mcm_asymmetry
-> MiniMCMField.step()
-> dio-Syntaxvektor und Hashsymbol
-> SemanticMemory.action_diagnostics()
-> choose_action()
-> WAIT / LONG / SHORT
-> Marktauswertung und Reward
-> SemanticMemory.learn()
-> MiniMCMField.learn()
```

Dieser Pfad ist aktiv handlungs- und lernwirksam. Die spätere passive
Forschungslandschaft darf davon nicht mit dem aktiven Kern verwechselt werden.

## 3. Komponentenkarte

| Komponente | Tatsächliche Rolle | Einordnung für das neue Projekt |
|---|---|---|
| `mini_world.py` | Chartwelt und fest gewichtete Übersetzung von Sehen/Hören in eine gemeinsame `mcm_feldwirkung` | Nicht übernehmen |
| `mcm_neuron.py` | Aktives Feld mit 12 Trägern, festen sinusförmigen Startgewichten, Nachhall, serieller Nachbarweitergabe und Reward-Lernen | Nicht übernehmen |
| `dio_syntax.py` | Fester Merkmalsvektor, 17-stufige Quantisierung und deterministisches Hashsymbol | Nicht als interne Syntax übernehmen |
| `semantic_memory.py` Kern | Persistente Symbol-/Aktionsstatistik; liefert `action_bias` und `readiness` an die Handlungsauswahl | Nicht übernehmen |
| `action_selection.py` | Mischt Feldscore und Memorydiagnose, bevorzugt anschließend das Maximum | Nicht übernehmen |
| Marktaktion und Reward | `WAIT`, `LONG`, `SHORT`, Zukunftsauswertung und belohnungsgetriebene Anpassung | Vollständig ausschließen |
| `MiniTemporalTracker` | Zusätzliche Familienzeitspur; im untersuchten Pfad als passiv markiert | Nur historische Diagnosequelle |
| `PassiveEpisodeTracker` | Externe Episodenbildung und Speicherung | Nur historische Diagnosequelle |
| passive Topologie-, Rollen-, Nachbarschafts-, Sleep- und Bedeutungsdaten | Observerseitige Klassifikation und persistente Forschungsprotokolle | Nicht in die Runtime übertragen |

## 4. Zentrale forensische Befunde

### 4.1 Keine getrennten sensorischen MCM-Felder

`_build_receptor_senses()` erzeugt aus visuellen und auditiven Chartgrößen
feste Mischwerte wie `visual_sharpness`, `auditory_softening`,
`contact_alignment`, `field_intake_pressure` und daraus unmittelbar:

```text
mcm_coherence
mcm_tension
mcm_asymmetry
```

Mehrere Formeln enthalten bereits beide Modalitäten. Der taktile
`direct_contact_pressure` ist in der Chartwelt konstant null. Das alte System
besitzt daher weder ein eigenständiges visuelles, auditives und taktiles MCM
noch einen späteren gemeinsamen MCM-Strang. Die gewünschte neue Architektur
kann daraus nicht durch Umbenennung entstehen.

### 4.2 Das alte MCM ist stark vorstrukturiert

Jedes `MCMNeuron` erhält genau drei bereits fusionierte Feldmerkmale. Seine
Eingangs- und Aktionsgewichte werden deterministisch über Sinusfunktionen
initialisiert. Feste Koeffizienten bestimmen Nachbareinfluss, Nachhall und
Lernrate.

Die Träger werden seriell aktualisiert:

```text
Neuron 0 -> Neuron 1 -> ... -> Neuron 11
```

Jeder Träger liest die soeben berechnete Aktivität seines Vorgängers. Damit
kann technische Iterationsreihenfolge die Feldlage verändern. Das verletzt die
neue Forderung nach einem gemeinsamen vorherigen Zustandsschnappschuss.

### 4.3 Reward formt Feld und Handlung

Nach jeder Aktion werden sowohl `SemanticMemory.learn()` als auch
`MiniMCMField.learn()` mit dem Marktreward aufgerufen. Das Feld ist daher nicht
nur passiver Wahrnehmungsträger. Seine Eingangs- und Aktionsgewichte werden
zielgerichtet durch Handelserfolg verändert.

### 4.4 `dio_*` ist externe Symbolisierung

`make_syntax_vector()` wählt neun Entwicklermerkmale. `make_syntax_symbol()`
quantisiert jedes Merkmal in feste Bänder und hasht die Folge zu `dio_*`.

Das Symbol entsteht somit durch eine vorgegebene Beobachterfunktion. Es ist
keine aus dem Feld gewachsene Syntax. Weil `SemanticMemory` das Symbol liest
und daraus Aktionsbias sowie Handlungsbereitschaft liefert, ist diese
Symbolisierung im Hauptpfad funktional aktiv.

### 4.5 Passive Speicherung bleibt extern

Viele spätere Strukturen heißen ausdrücklich `passive_*`. Sie speichern
Episoden, Topologien, Nachbarschaften, Rollen, Reflexions- oder
Sleep-Auswertungen in der JSON-basierten `SemanticMemory`. Die untersuchten
Methoden dokumentieren, dass diese Daten nicht von `action_diagnostics()` oder
`choose_action()` gelesen werden.

Sie sind wertvolle Forschungsprotokolle, aber keine organisch entstandene
innere Organisationsgeschichte. Ihre Begriffe dürfen deshalb nicht als
Runtime-Zustände in das neue Projekt übertragen werden.

## 5. Übernahme- und Ausschlussentscheidung

### Als Forschungsprinzip übernehmen

- Rezeptoren sind eine wirkungsvolle und prüfpflichtige Weltgrenze.
- Nachhall kann unmittelbare Feldgeschichte tragen.
- Passive Beobachtung muss von aktiver Mechanik getrennt sein.
- Wiederkehrende Feldlagen können offline beschrieben werden, ohne sie sofort
  als Bedeutung auszugeben.
- Nullprüfungen, Gegenwelten und Reproduzierbarkeit bleiben methodisch wertvoll.

### Nicht als Mechanik übernehmen

- Chartwelt und Handelsaktionen
- fest gewichtete multimodale Vorfusion
- drei vorgefertigte globale Feldmerkmale als alleiniger MCM-Eingang
- sinusförmige Träger- und Aktionsgewichte
- serielle In-place-Feldausbreitung
- Reward-Lernen
- Syntax-Hash als innere Bezeichnung
- semantische Aktionsmemory
- Observerklassen als Runtime-Rollen
- externe Episoden-, Topologie- oder Sleep-Speicher als Nervensubstrat

### Nur als offene Hypothese erneut prüfen

- sensorspezifischer Nachhall
- lokale Überlagerung in einem MCM-Feld
- gemeinsame multimodale Feldwirkung
- langsame lokale Organisationsgeschichte
- mögliche spätere Muster-, Kontext- oder Syntaxbefunde

## 6. Evidenzübertragung

Im neuen Projekt beginnen alle Komponenten bei E0. Frühere Befunde können
Forschungsfragen und Baselines begründen, aber keine Evidenzstufe übertragen.
Erst eine isolierte Reproduktion innerhalb der neuen Zustandsgrenzen kann E1
oder E2 begründen.

## 7. Ergebnis

MINI_DIO belegt, dass Rezeptorformeln und Zustandsübersetzung die beobachtete
Feldwirkung stark prägen. Es belegt nicht die neue Architektur aus getrennten
sensorischen MCM-Feldern und einem gemeinsamen MCM-Strang.

Der Neustart ist deshalb keine Erweiterung des alten aktiven Kerns. Er ist eine
neue, enger kontrollierte Architektur, die nur methodische Erfahrungen aus dem
Vorgängerprojekt übernimmt.

## 8. Bester nächster Schritt

Aus diesem Abgleich folgt keine Runtime-Freigabe. Als Nächstes muss ein passiver
Prüfplan zeigen, ob die beiden neuen Schnittstellenverträge vollständig,
reihenfolgeneutral und ohne versteckte semantische Fusion ausführbar sind.
