# S1-II: Statischer lokaler DTS-1 A-B-A-Interferenzvertrag

## Status

S1-II bindet ausschliesslich die kleinste lokale Interferenzpruefung fuer
`A-B-A` gegen `A-Pause-A`. Es wird keine Gleichung eingefuehrt, kein
Fixturewert gewaehlt, kein Harness implementiert und kein Schritt ausgefuehrt.

Entscheidung:

```text
DTS1_LOCAL_ABA_VERSUS_A_GAP_A_INTERFERENCE_CONTRACT_BOUND
```

Vertragsdigest:

```text
888c5bfcb525f44439f85f6e9b4664616013552c72ed86e8cd3bb141ddd8a60f
```

## Quellen

Der Vertrag bindet:

- S1-HH mit Digest
  `5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388`;
- den bestandenen S1-IH-Abschwaechungsaudit mit Receipt
  `2fd24fd7ccdee690ea5610440e2d76f85e6a5ca0b8bc4b9045ff7c12a34d0c36`.

S1-IH ist nur eine technische Voraussetzung. Sein PASS belegt noch keine
Interferenz.

## Lokale Geometrie

Gebunden ist eine offene Dreiknotenlinie mit den vorhandenen Kanten A und B.
Beide Kanten teilen genau den mittleren Endpunkt und damit genau ein endliches
lokales Kapazitaetsledger. Die beiden aeusseren Endpunkte bleiben getrennt.

Neue Kanten, Ressourcentransport, globaler Zuteiler oder ein verborgenes
gemeinsames Zustandsobjekt sind ausgeschlossen.

## Folgenpaar

Beide Arme beginnen aus derselben vollstaendigen Anatomie mit demselben
positiven A-Kontakt. Das mittlere Intervall besitzt in beiden Armen dieselbe
Dauer, dieselben Raten und dieselben Ereignisgrenzen:

- `A-B-A`: Nur B erhaelt im mittleren Intervall positive Beteiligung.
- `A-Pause-A`: Beide Kanten erhalten im mittleren Intervall Beteiligung null.

Danach folgt in beiden Armen dieselbe positive A-Probe. Nur vollstaendige
gueltige Anatomien werden weitergetragen. Armname, Folgenindex, Ergebnis oder
Zukunftszustand duerfen keinen Vorschlag steuern.

Die finale A-Ressourcenabbildung wird vollstaendig uebernommen, bevor ein
getrennter gemeinsamer S/H-Feldreadout beginnt. Dessen Ressourcenpoststate
wird verworfen und gelangt nicht in die Folge.

## Direkte Gegenprognose

Ein spaeterer PASS muss gemeinsam und vorab gerichtet zeigen:

1. B bindet im mittleren `A-B-A`-Intervall eine strikt positive Menge.
2. Vor der finalen A-Probe ist am gemeinsamen Endpunkt im `A-B-A`-Arm strikt
   weniger freie Ressource vorhanden als im Pausenarm.
3. Die akzeptierte finale A-Bindung ist im `A-B-A`-Arm strikt kleiner.
4. Ein gemeinsamer S/H-Readout aus den uebernommenen Endanatomien besitzt die
   vorregistrierte Feldrichtung und eine Nichtnullmarge.
5. Diese Feldtrennung bleibt bei angeglichenem oder abgetragenem H oberhalb
   einer vorregistrierten Float64-Grenze.

Direktes gemeinsames Freiledger, finale A-Bindung und Feldreadout muessen alle
bestehen. Keine Messrolle darf eine andere ersetzen.

## Kontrollen

1. Zwei wertidentische `A-B-A`-Folgen sind vollstaendig bitgenau.
2. B-Beteiligung null ist bei gleicher Mitteldauer bitgenau der Pausenarm.
3. A0 liefert im gemeinsamen Readout bitgenau den neutralen Feldpfad.
4. Ein vor der Folge fixierter Adapter liefert zwischen den Armen denselben
   gemeinsamen Feldreadout.
5. Die gerichtete Feldtrennung bleibt bei wertidentischem oder abgetragenem H.
6. Beteiligung null in der finalen A-Probe liefert in beiden Armen exakt null
   akzeptierte A-Bindung.

## Gegenbaselines

| Baseline | Gebundene Gegenprognose |
| --- | --- |
| Fixed Adapter / Frozen-E1 | Ein vor der Folge fixierter Adapter besitzt keine gemeinsame freie Ressource und liefert im identischen Readout dieselbe Kopplung. |
| Leaky / Integrator | Identische S/H-Readoutvorgaenger entfernen getragenen Feldzustand; das direkte gemeinsame Ressourcenledger bleibt davon getrennt. |
| dynamisches zweistufiges E1 | Gemeinsame Konkurrenz allein ist nicht unterscheidend. S1-IB frei gegen refraktaer und S1-IE bleiben gemeinsam erforderlich. |
| F3 / CONST-V | Ohne endliches gemeinsames Endpunktledger fehlt die direkte B-Verdraengung der finalen A-Zulassung. |
| schneller Nachhall | H-Angleichung oder -Abtragung sperrt schnellen Nachhall als Quelle der Feldtrennung. |

Keine Baseline darf Folgenindex, Armname, verborgenes Ressourcenledger oder
einen separaten Armfit erhalten.

## PASS und STOPP

Ein spaeterer PASS verlangt atomar beide Arme, alle sechs Kontrollen, alle
drei direkten Ressourcenrichtungen, die vorregistrierte Feldrichtung,
H-Kontrolle sowie gueltige Anatomien, Bilanzen, Feldbereiche und
Kopplungsordnung.

STOPP gilt bei ungleicher Ausgangsanatomie, ungleichen A-Kontakten oder
Mitteldauern, fehlender gemeinsamer Endpunktkapazitaet, fehlender positiver
B-Bindung, fehlendem gemeinsamen Freidefizit, nicht kleinerer finaler
A-Bindung, scheiternder Feld- oder H-Richtung, Kontrollfehler,
Bilanzverletzung, Baselineerweiterung, Nachwahl, Retry, Teiloutput oder nicht
registrierter Ausfuehrung.

## Aussagegrenze

S1-II bindet nur Funktion, Messung und Falsifikation. Interferenz wurde noch
nicht ausgefuehrt oder nachgewiesen. Insbesondere bleiben Freigabe,
Wiederbeanspruchung, Materialeignung und Nichtreduzierbarkeit gegen
dynamisches zweistufiges E1 offen. Weitergehende Claims sind gesperrt.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1ii_interference_contract.py
tests/test_dynamic_substrate_s1ii_interference_contract.py
```

Neun Tests pruefen Quellenbindung, Geometrie, Folgenpaar, direkte
Messrichtungen, sechs Kontrollen, alle Gegenbaselinegruppen, atomare
STOPP-Regeln, Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IJ darf ausschliesslich ein endliches synthetisches Fixture und einen
Ausfuehrungsvertrag fuer S1-II binden. Vor jeder Implementierung muessen
Kapazitaeten, Startanatomie, A-/B-Beteiligungen, Dauern, Raten, gemeinsame
S/H-Prueffelder, analytische Ressourcen- und Feldrichtungen,
Rundungsgrenze, Fallmatrix und maximales technisches Aufrufbudget feststehen.
Noch keine Implementierung, Runtime oder Ausfuehrung.
