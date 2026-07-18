# Transiente Neuronenantriebsrolle

## Status

Verbindlicher technischer Antriebsvertrag auf `E0 / CONTRACT_ONLY`.

Dieser Vertrag bindet die bereits lokal getrennte Rezeptorfolge optional an
`MCMNeuronDrive`. Er legt keine Leserfunktion fest und erzeugt aus sich heraus
keine Änderung von Aktivierung, Nachhall, Topologie oder Memory.

## Antriebsrollen

Ein expliziter Neuronenübergang kann damit vier voneinander getrennte Rollen
erhalten:

```text
abgeschlossener eigener Vorzustand
+ lokale Vorfeldwahrnehmung
+ gemessene Vorschlagsdauer
+ optionaler eigener transienter Dockverlauf
-> explizite Transition
```

Der transiente Verlauf ersetzt weder `receptor_contact` noch
`MCMFieldPerception`. Er ist zusätzliche, flüchtige Information über die
innerhalb derselben Vorschlagsspanne abgeschlossenen lokalen Rezeptorzustände.

## Atomare Lokalität

Wenn ein Feldvorschlag die transiente Rolle verwendet, muss er für jedes
angedockte Neuron genau einen lokalen Eingabevertrag liefern. Ein Neuron ohne
Dock erhält keine transiente Rezeptoreingabe.

```text
vollständiger Dockumfang: erforderlich
teilweise Übergabe:       abgewiesen
fremdes Dock-Neuron:      abgewiesen
abweichende Feldzeit:     abgewiesen
```

Eine leere lokale Kontaktfolge bleibt eine gültige und ausdrückliche
Abwesenheit. Sie wird nicht als Nullkontakt, Halten oder fehlender Datensatz
umgedeutet.

## Keine eingebaute Wirkung

`MCMNeuronDrive.transient_receptor_input` stellt nur Information bereit. Die
Neuronenschicht:

- wählt keinen Kontakt aus,
- bildet keinen Mittelwert und keine Gewichtung,
- koppelt die Folge nicht an Aktivierung oder Nachhall,
- erzeugt keinen Feldtakt pro Rezeptorabschluss,
- speichert die Folge nicht im Folgezustand,
- verändert bestehende Transitionen nicht.

Eine Transition, die diese Rolle ignoriert, erzeugt exakt denselben
Neuronenzustand wie ohne transiente Eingabe. Eine spätere Wirkung darf nur über
eine gesondert begründete und geprüfte Transition entstehen.

## Zustandsgrenze

Die Eingabe existiert ausschließlich während des atomaren Aufrufs einer
Transition. Sie wird nicht Teil von:

- `MCMNeuron`,
- `MCMFieldPerception`,
- Layer- oder Feld-Digest,
- Snapshot oder organischem Memory.

## Freigabegrenze

```text
lokale optionale Drive-Rolle: technisch getragen
atomare Dockabdeckung:        technisch getragen
bestehende Wirkungsgleichheit: regressionsgesichert
SharedMCMField-Übergabe:      optional und atomar getragen
Live-Runtime-Anbindung:       nicht freigegeben
Zeitleser oder Verdichtung:   nicht freigegeben
Feldwirkung oder Memory:      nicht freigegeben
```

Die anschließende Feldgrenze ist im Vertrag
[Atomare transiente Feldübergabe](035_ATOMARE_TRANSIENTE_FELDUEBERGABE.md)
geregelt. Sie verbindet einen vollständigen `TransientNeuronInputSet` mit der
gemeinsamen Neuronenschicht, ohne eine Live-Quelle oder Interpretation der
lokalen Folge festzulegen.
