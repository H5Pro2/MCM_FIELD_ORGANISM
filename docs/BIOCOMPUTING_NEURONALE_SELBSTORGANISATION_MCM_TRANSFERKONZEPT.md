# Biocomputing und neuronale Selbstorganisation: Transferkonzept fuer MCM

## Status

Dieses Dokument ist ein fachliches Transferkonzept, kein MCM-Befund und keine
Runtimefreigabe. Es ordnet externe Forschung zu lebenden neuronalen Kulturen in
geschlossenen Rueckkopplungsumgebungen ein und leitet daraus methodische
Anforderungen fuer das MCM-Wahrnehmungsfeld ab.

Gesperrt bleiben:

- Nachweis einer vorhandenen MCM-Memory;
- Behauptung von Bewusstsein, Erleben, Feldintelligenz oder KI;
- Gleichsetzung biologischer Neuronen mit MCM-Neuronen;
- Uebernahme biologischer Resultate als direkte Evidenz fuer das Projekt;
- Programmierung eines Zielverhaltens als Ersatz fuer lokale Feldentwicklung.

## Externe Beobachtung

Biocomputing-Arbeiten wie DishBrain koppeln lebende neuronale Kulturen auf
Elektrodenarrays an eine einfache digitale Umwelt. Im Pong-Versuch wurden
Zustaende der Spielwelt in elektrische Stimulation uebersetzt; die gemessene
neuronale Aktivitaet wirkte wiederum auf den Schlaeger zurueck. Der relevante
Punkt fuer MCM ist nicht das Spiel selbst, sondern die geschlossene
Welt-Koerper-Rueckkopplung:

```text
Umweltzustand
-> strukturierte Stimulation
-> neuronale Aktivitaet
-> Wirkung auf die Umwelt
-> veraenderte Folgeeingabe
```

Die Autoren beschreiben, dass neuronale Kulturen in dieser Kopplung ihre
Aktivitaet messbar anpassen koennen. Populaere Formulierungen wie "Neuronen
moegen kein Chaos" sind fuer dieses Projekt zu ungenau. Technisch nuetzlicher
ist die vorsichtige Lesart: Ein lokal dynamisches neuronales Substrat kann in
einer geschlossenen Rueckkopplung Aktivitaetsordnungen hervorbringen, die
Folgeeingaenge strukturierter machen.

## Relevante Prinzipien fuer MCM

### 1. Geschlossene Rueckkopplung statt passiver Eingang

Ein reiner Sensor-zu-Feld-Pfad reicht nicht aus, wenn spaeter eine
hypothetische MCM-Memory untersucht werden soll. Notwendig ist ein Pfad, in dem
Feldzustand oder Substratzustand die spaetere Eingangsbedingung wieder
veraendern koennen.

Fuer MCM bedeutet das:

```text
Rezeptorzustand
-> gemeinsames MCM-Feld
-> lokaler Substratkandidat
-> begrenzte technische Rueckwirkung
-> veraenderte spaetere Rezeptor- oder Feldbedingung
```

Solange dieser Kreis nicht technisch geschlossen und fair gegen Baselines
abgegrenzt ist, bleibt jeder Memory- oder Faehigkeitsbegriff gesperrt.

### 2. Lokale Anpassung vor globaler Zielstruktur

DishBrain ist fuer MCM deshalb interessant, weil die Ordnung nicht als
fertige Symbolregel in das neuronale Substrat geschrieben wird. Das passt zur
MCM-Leitlinie, keine Muster, Bedeutungen oder Zieltopologien vorzuprogrammieren.

Die MCM-Analogie darf nur lauten:

```text
lokale Feldlage + lokale Ressource + Rueckwirkung
-> spaeter messbare Aenderung der Feldaufnahme
```

Nicht zulaessig ist:

```text
Label, Ziel, Reward oder externe Auswertung
-> direktes Schreiben einer Memorystruktur
```

### 3. Encoding und Decoding sind eigenstaendige Forschungsprobleme

Neuere Biocomputing-Arbeiten zeigen, dass die Kopplung zwischen digitaler
Umwelt und biologischem Substrat nicht trivial ist. Welche Signale wie
eingespeist werden und welche Aktivitaet wie gelesen wird, bestimmt wesentlich,
ob eine Anpassung messbar wird.

Fuer MCM folgt daraus:

- Rezeptorzustaende duerfen nicht als Rohdaten in das Feld gelangen.
- Docks muessen getrennt, zeitlich sauber und herkunftserhaltend bleiben.
- Readout darf keine versteckte Zielinterpretation enthalten.
- Baselines muessen dieselbe kausale Vorgeschichte sehen.
- Eine spaetere Rueckwirkung muss technisch begrenzt und separat messbar sein.

### 4. Ordnung ist nicht automatisch Memory

Eine geordnete Folge, ein stabiler Nachhall oder eine bessere Metrik ist noch
keine MCM-Memory. Fuer MCM zaehlt erst eine lokale, ressourcenbegrenzte und
wieder loesbare Wirkung, die spaeter unter gleicher Probe anders kausal wirkt
und nicht durch Fixed Adapter, Leaky-Nachhall, Integrator, Replay oder
vorgegebene Zielstruktur erklaert wird.

## Hypothese fuer die weitere MCM-Forschung

Die vorsichtige Arbeitshypothese lautet:

> Die fuer MCM relevante neuronale Analogie liegt nicht in biologischer
> Nachahmung, sondern in einem lokalen Feld-Substrat-Prinzip: Ein Traeger
> bindet unter strukturierter Rueckkopplung eine endliche Ressource, veraendert
> dadurch spaetere lokale Feldaufnahme, kann abgeschwaecht werden und gibt die
> Ressource wieder frei.

Diese Hypothese bleibt offen. Sie wird nicht als Eigenschaft der aktuellen
Runtime behauptet.

## Eingangs- und rueckkopplungsgetragene Feldordnung

Die untersuchte Ordnung soll nicht ursachenlos oder ohne Einwirkung entstehen.
Sie wird als kausale Feldentwicklung unter fortlaufender Kopplung verstanden:

```text
aeussere Einwirkung
+ aktuelle Feldlage
+ lokaler Substratzustand
+ begrenzte Rueckfuehrung
-> nachfolgende Feldlage
```

Der feldmechanische Nullzustand ist dabei nur Referenz und moeglicher
Relaxationsrand. Rueckkehr zu diesem Rand ist fuer sich noch keine
Musterbildung. Ein technischer Ordnungsbefund erfordert reproduzierbar
unterscheidbare raeumliche oder zeitliche Feldlagen unter kontrollierten
Vorgeschichten.

Nicht vorgegebene Muster oder Mustererweiterungen bleiben moegliche spaetere
Beobachtungen, werden aber weder programmiert noch vorausgesetzt. Eine
uebergeordnete technische Feldlage koennte erst dann untersucht werden, wenn
mehrere lokale Zustaende gemeinsam die Aufnahme einer spaeteren Einwirkung
kausal veraendern. Psychologische Kategorien sind dafuer weder Zustandsnamen
noch Implementierungsziele.

## Anforderungen an einen MCM-Substratkandidaten

Ein naechster Kandidat muss vor jeder Gleichung festlegen:

1. Welche eigene Funktionsprognose er gegen Fixed Adapter, Leaky-Nachhall,
   Integrator, Replay und vorgegebene Zielstruktur besitzt.
2. Welche lokale endliche Ressource gebunden, belastet, abgeschwaecht und
   wieder freigegeben wird.
3. Wie Interferenz durch konkurrierende Folgegeschichte messbar wird.
4. Wie die spaetere Feldaufnahme veraendert wird, ohne Rohdaten,
   Bedeutungslabels oder Zielmuster zu speichern.
5. Wann der Kandidat verworfen wird.
6. Welche Begriffe gesperrt bleiben.

## Methodischer Nutzen fuer MCM

Die Biocomputing-Forschung hilft dem Projekt vor allem als methodischer
Kompass:

- Weltkontakt muss geschlossen und rueckwirkend sein.
- Lokale Dynamik ist wichtiger als eine externe Symbol- oder Rewardstruktur.
- Vergleichbarkeit verlangt identische kausale Vorgeschichte fuer Kandidat und
  Baselines.
- Anpassung muss als technische Zustands- und Funktionsaenderung gemessen
  werden, nicht als grosser Begriff.
- Hypothetische MCM-Memory darf erst aus reproduzierbarer lokaler
  Feld-Substrat-Wirkung entstehen.

## Konsequenz fuer den Forschungszweig

Das MCM-Projekt sollte Biocomputing nicht kopieren und keine biologischen
Eigenschaften behaupten. Der nutzbare Transfer ist abstrakter:

```text
geschlossenes Feld
+ strukturierte Folgeeingabe
+ lokale begrenzte Ressource
+ Rueckwirkung auf spaetere Aufnahme
+ Abschwaechung, Interferenz und Freigabe
= pruefbarer Kandidatenraum fuer hypothetische MCM-Memory
```

Damit wird Biocomputing als externe Orientierung festgehalten, ohne die
technische Evidenzgrenze des Projekts zu verletzen.

Die daraus abgeleitete technische MCM-Leitidee ist gesondert festgehalten in
[MCM-Kohaerenzerhalt unter geschlossener Feldkopplung](MCM_KOHAERENZERHALT_GESCHLOSSENE_FELDKOPPLUNG_KONZEPT.md).

## Quellen

- Brett J. Kagan et al., "In vitro neurons learn and exhibit sentience when
  embodied in a simulated game-world", Neuron, 2022.
  https://www.cell.com/neuron/fulltext/S0896-6273(22)00806-6
- PubMed-Eintrag zu Kagan et al. 2022.
  https://pubmed.ncbi.nlm.nih.gov/36228614/
- Moein Khajehnejad et al., "Biological Neurons Compete with Deep Reinforcement
  Learning in Sample Efficiency in a Simulated Gameworld", 2024.
  https://arxiv.org/abs/2405.16946
- Johnson Zhou et al., "Embodied Neurocomputation: A Framework for Interfacing
  Biological Neural Cultures with Scaled Task-Driven Validation", 2026.
  https://arxiv.org/abs/2605.13315
