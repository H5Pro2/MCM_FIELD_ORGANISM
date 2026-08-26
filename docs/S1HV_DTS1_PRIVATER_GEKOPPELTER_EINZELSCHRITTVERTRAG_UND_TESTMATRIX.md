# S1-HV: DTS-1 privater gekoppelter Einzelschrittvertrag

## Status

S1-HV bindet die spaetere private Implementierung genau eines atomaren
DTS-1/S/H-Einzelschritts und seine technische Testmatrix. Es wird noch kein
gekoppelter Schritt implementiert. Keine Materialratenwerte, keine
Runtimeintegration und kein Feldlauf.

Entscheidung:

```text
DTS1_PRIVATE_COUPLED_STEP_CONTRACT_AND_TEST_MATRIX_BOUND
```

## Private Modulgrenze

Die spaetere Implementierung darf nur in

```text
mcm_field_organism.dynamic_substrate_dts1_coupled_step
```

liegen. Sie definiert `DTS1CoupledStepError(ValueError)` und genau einen
gekoppelten Einstieg:

```text
advance_dts1_coupled_fast_shared_field(
    field,
    anatomy,
    distribution,
    step_time,
    substrate_config,
    afterimage_config,
    dts1_rates,
    dissipation_config=None,
    *,
    backreaction_enabled,
) -> DTS1CoupledFastFieldStepResult
```

Das Modul bleibt ausserhalb von Paketexport, `current_api`, Runtime, Runner,
Snapshot, Restore sowie Audio-, Video- und Browserpfaden.

## Abgeschlossener Eingabezustand

`field` liefert den unveraenderlichen abgeschlossenen Zustand `L_n` mit
`S_n` und `H_n`. `anatomy` liefert `A_n`. Beide muessen exakt dasselbe
vollstaendige Knoten- und Kanteninventar besitzen. `distribution` und
`step_time` beschreiben genau ein gemeinsames geschlossenes Kontaktintervall.

Die bestehenden Feldkonfigurationen werden unveraendert uebergeben.
`dts1_rates` ist ein expliziter `DTS1StepRates`-Wert. S1-HV waehlt keine
Zahlen. `backreaction_enabled` ist ein zwingender echter boolescher A0/A1-
Schalter ohne Default.

## Verbindliche Kopplungsphasen

1. Alle Typen, Geometrien, Zeiten, Konfigurationen und den Schalter pruefen.
2. Nur den bestehenden positiven, zur Distribution passenden Feldzeitschritt
   zulassen.
3. Die Intervalllaenge mit dem bestehenden neutralen Zeithelfer bestimmen.
4. Fuer jede Anatomiekante `p_n` nur aus `S_n` mit S1-HK bilden.
5. Adapter und `G_n` nur aus `A_n` mit S1-HT bilden.
6. `A_next` nur aus `A_n`, `p_n`, Intervall und Raten mit S1-HP bilden.
7. A0 und aktive Nullbelegung direkt an den bestehenden neutralen
   Schnellfeldschritt delegieren.
8. Nur bei aktiver Nichtnullbelegung `L_next` mit `G_n`, aber unveraenderter
   neutraler Rand-, S/H-, Leck- und Bereichslogik bilden.
9. Beide vollstaendigen Proposals und passiven Ledgers validieren.
10. Genau einen neuen Ergebniscontainer als einzigen atomaren Paarcommit
    erzeugen.

Kein Proposal darf den Endzustand des anderen lesen. Neu gebundene Ressource
wirkt daher fruehestens im Folgeschritt auf das Feld; neue Feldwerte wirken
fruehestens dort auf das Beteiligungsledger.

## Exakter neutraler Pfad

P0 bleibt der vorhandene `advance_neutral_fast_shared_field`-Aufruf ausserhalb
des neuen Moduls. P0 konstruiert weder Beteiligung noch Ressourcenvorschlag.

A0 entwickelt `A_next`, muss den Feldteil jedoch genau einmal direkt an den
bestehenden neutralen Schnellfeldschritt delegieren. Eine numerische Kopie
dieses Pfads ist nicht zulaessig. Damit muss A0 bei identischen Feldeingaben
wert- und bitidentisch zu P0 sein.

Auch A1 mit `b_e=0` auf allen Kanten muss fuer seinen ersten Feldvorschlag
denselben direkten neutralen Aufruf verwenden. A0 und A1 erzeugen aus
demselben Vorzustand immer dasselbe `A_next`, weil der Ressourcenvorschlag den
Ablationsschalter nicht liest.

## Atomare Ausgabe

`DTS1CoupledFastFieldStepResult` enthaelt nur:

- das vollstaendige `L_next`;
- die vollstaendige `A_next`-Anatomie;
- die validierte explizite Intervalllaenge;
- das vollstaendige kanonische `p_n`-Ledger;
- das vollstaendige passive S1-HP-Transferledger;
- den vollstaendigen aus `A_n` gelesenen S1-HT-Adapter.

Diagnosen duerfen keine Rechnung steuern. Scheitert Ressourcen- oder
Feldproposal, entsteht kein Ergebniscontainer und damit kein Teilcommit.
Eingaben bleiben unveraendert; Callback-, Observer- und Teilausgaben sind
verboten.

## Technische Testmatrix

| ID | Verpflichtender Nachweis |
|---|---|
| T01 | positiver Feldzeitschritt ist zwingend; Nullzeit ist nicht darstellbar |
| T02 | vollstaendige gemeinsame Layer-/Anatomiegeometrie und Digestidentitaet |
| T03 | `p_n` ist vollstaendig, kanonisch und liest nur `S_n` |
| T04 | `A_next` entspricht dem direkten S1-HP-Aufruf |
| T05 | Adapter entspricht dem direkten S1-HT-Leser aus `A_n` |
| T06 | A0-Feld ist bitgenau der direkte neutrale Schnellfeldschritt |
| T07 | A0 und A1 liefern im selben Schritt identische Ressourcenergebnisse |
| T08 | A1 mit Nullbindung ist im Feld bitgenau A0 und P0 |
| T09 | neue Bindung beeinflusst nicht den aktuellen Feldvorschlag |
| T10 | neue Feldwerte beeinflussen nicht den aktuellen Ressourcenvorschlag |
| T11 | aktive Nichtnullbindung nutzt S1-HT-Generator und neutrale Randlogik |
| T12 | H-, Leck-, Bereichs- und Zeitsemantik bleiben unveraendert |
| T13 | Eingaben bleiben unveraendert; Wiederholung ist deterministisch |
| T14 | Ressourcenfehler liefert weder Feld- noch Paarausgabe |
| T15 | Feldfehler liefert weder Anatomie- noch Paarausgabe |
| T16 | ungueltige Typen, Kontrolle, Zeit, Konfiguration oder Geometrie brechen ab |
| T17 | Knoten- und Kantendeklarationsreihenfolge aendert keinen Wertausgang |
| T18 | Paarrest und Leserlatenz sind unter `n,2n,4n` messbar |
| T19 | kein Midpoint-, impliziter, adaptiver oder partieller Commitpfad |
| T20 | keine Runtime, I/O, Snapshots, oeffentliche API, Werte oder Feldlaeufe |

T18 verlangt in der Implementierungsstufe nur, dass die spaeteren
Verfeinerungsgroessen unverfaelscht messbar sind. Eine bestandene Konvergenz
oder ein Funktionsbefund wird noch nicht behauptet.

Die S1-HU-Nullzeitidentitaet bleibt eine algebraische Grenze der reinen
Abbildungen. `MCMFieldStepTime` fordert bereits konstruktiv `end_tick >
start_tick`; der gekoppelte Wrapper erfindet deshalb weder einen zweiten
Zeittyp noch einen unaufrufbaren Nullzeitzweig.

## Aussagegrenze

S1-HV bindet nur eine implementierbare erste Kopplungsgrenze. Auch eine
spaetere bestandene technische Matrix belegt weder gekoppelte Stabilitaet noch
Abschwaechung, Interferenz, Kapazitaetsfreigabe oder eine Trennung von
Gegenbaselines.

## Bester naechster Schritt

S1-HW darf nach dem naechsten `ok weiter` genau das private gekoppelte
Einzelschrittmodul und die 20 technischen Matrixfaelle implementieren. Noch
keine Materialparameterauswahl, Runtimeintegration, Verfeinerungsausfuehrung
oder Forschungs-/Feldprobe.
