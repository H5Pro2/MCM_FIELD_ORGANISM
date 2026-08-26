# S1-BT: E1 atomarer gekoppelter S/H-Schrittvertrag

## Status

Statischer Kopplungs- und Zeitordnungsvertrag. Noch keine Implementierung,
kein Snapshot-Schema, kein `current_api`-Export und kein Memory-, Lern-,
Organismus- oder KI-Befund.

## Ziel

Ein neuer isolierter opt-in Schritt soll den vorhandenen schnellen S/H-Pfad
und E1 kausal koppeln, ohne eine simultane Gleichungsschleife oder eine von
Aufrufzahlen abhaengige Wirkung einzufuehren.

## Getrenntes Modul

Die spaetere Implementierung liegt in:

```text
mcm_field_organism/e1_coupled_fast_field.py
```

Der bestehende neutrale P0-Pfad
`advance_neutral_fast_shared_field(...)` bleibt unveraendert und direkt
verfuegbar.

## Eingangsgrenze

```text
advance_e1_coupled_fast_shared_field(
    field,
    e1_state,
    distribution,
    step_time,
    substrate_config,
    afterimage_config,
    dissipation_config=None,
    *,
    backreaction_enabled,
) -> E1CoupledFastFieldStepResult
```

Der erste Korridor verwendet nur den bereits vorhandenen synchronen
`ReceptorDistribution`-/`MCMFieldStepTime`-Pfad. Der transiente asynchrone
AV-Pfad wird nicht erweitert, bevor dieser kleine synchrone Vertrag besteht.

## Ergebnisgrenze

```text
E1CoupledFastFieldStepResult
    field
    e1_state
    applied_adapter
```

`applied_adapter` ist das unveraenderliche
`E1WeightedFieldAdapterResult`, das tatsaechlich den Feldgenerator des
Intervalls gebildet hat. Es ist ein technischer Schrittbeleg, kein
persistierter Zustand und keine Wahrnehmungsrolle.

## Atomare Zeitordnung

Fuer einen Eingabestand `(S_t,H_t,b_t)` und das explizite Intervall `dt`
gilt genau diese symmetrische Reihenfolge:

```text
1. Anfangsgrenze validieren
2. b_(t+1/2) = E1_advance(S_t, b_t, dt/2)
3. r_(t+1/2) = E1_adapter(b_(t+1/2), backreaction_enabled)
4. (S_(t+1), H_(t+1)) exakt ueber dt mit r_(t+1/2) entwickeln
5. b_(t+1) = E1_advance(S_(t+1), b_(t+1/2), dt/2)
6. Feld, E1-Endzustand und angewendeten Adapter atomar ausgeben
```

Jeder Teil liest nur einen abgeschlossenen Vorzustand. Kein Teil liest seinen
eigenen noch nicht berechneten Endwert. Damit ist der Schritt deterministisch
und frei von algebraischer Zirkularitaet.

## Warum zwei halbe E1-Schritte

Ein ausschliesslich vor- oder nachgelagerter voller E1-Schritt wuerde die
Anfangs- oder Endfeldlage systematisch bevorzugen. Die symmetrische
Komposition bindet E1 an beide abgeschlossenen Intervallgrenzen und verwendet
den resultierenden Mittelzustand fuer die Feldfortsetzung.

Dies ist eine numerische Kopplungsentscheidung, keine Behauptung ueber
biologische oder natuerliche Zeit.

## Aufbau des gekoppelten Feldgenerators

Der interne Teil stammt ausschliesslich aus:

```text
G_internal = build_e1_weighted_diffusion_generator(
    field.layer,
    applied_adapter,
)
```

Danach werden die vorhandenen Rezeptorgrenzen mit der unveraenderten Basisrate
`r_0 = 1/response_time_seconds` addiert:

```text
fuer jeden gemappten Rezeptorkontakt an i:
    G[i,i] -= r_0
    boundary[i] += r_0 * contact_i
```

Eine optionale bereits vorhandene Felddissipation bleibt unveraendert. H wird
weiterhin gemeinsam aus der exakt integrierten S-Trajektorie berechnet und
nicht nachtraeglich nur aus dem S-Endwert aktualisiert.

## Bereichs- und Symmetriegrenze

Die internen E1-Raten sind symmetrisch und nichtnegativ. Rezeptorraten und
Dissipation bleiben nichtnegativ. Der gemeinsame lineare S-Generator behaelt
damit die vorhandene diffusive Vorzeichenstruktur.

Die bestehende spektrale S/H-Integration wird unveraendert auf den neu
gebildeten symmetrischen Generator angewendet. Nichtendliche Werte oder ein
Verlassen des normierten Feldbereichs fuehren zum Fehler und nicht zu einer
neuen E1-spezifischen Korrekturregel.

## Drei sauber getrennte Arme

### P0: bestehender neutraler Pfad

```text
advance_neutral_fast_shared_field(...)
```

Kein E1-Zustand wird angelegt oder entwickelt.

### A0: E1 entwickelt, Rueckwirkung aus

```text
advance_e1_coupled_fast_shared_field(
    ...,
    backreaction_enabled=False,
)
```

E1 darf sich aus denselben Feldlagen entwickeln. Der S/H-Schritt muss jedoch
exakt die neutrale interne Basisrate verwenden.

### A1: E1 entwickelt, Rueckwirkung an

```text
advance_e1_coupled_fast_shared_field(
    ...,
    backreaction_enabled=True,
)
```

Der E1-Mittelzustand gewichtet die interne Feldleitung desselben Intervalls.

`backreaction_enabled` ist nur ein festes Versuchsarmmerkmal. Es darf nicht
waehrend eines Schritts oder aufgrund eines Feldwertes umgeschaltet werden.

## Exakte P0-/A0-Feldidentitaet

Bei identischem Eingabefeld, Weltkontakt, Zeitvertrag und S/H-Konfiguration
muss gelten:

```text
field_result(P0) == field_result(A0)
```

Das gilt unabhaengig davon, wie `b_t` verteilt ist. Nur der zusaetzliche
E1-Endzustand von A0 besitzt keine P0-Entsprechung.

Diese Identitaet ist die wichtigste technische Nullkontrolle vor jeder
aktiven Rueckwirkungspruefung.

## Aktive Ein-Schritt-Kausalitaet

Bei `gamma > 0`, nichtuniformem E1-Mittelzustand und einer nichtuniformen
S-Lage darf A1 von A0 abweichen. Die Abweichung muss verschwinden, wenn:

```text
backreaction_enabled = False
oder gamma = 0
oder b_(t+1/2) = 0 auf allen Kanten
```

Eine numerische Abweichung belegt nur die implementierte technische
Kausalwirkung des Adapters.

## Zustandsentwicklung in den Vergleichsarmen

A0 und A1 beginnen einen Schritt mit identischem `b_t`. Nach dem
unterschiedlichen Feldschritt kann ihr zweiter halber E1-Schritt verschiedene
Endzustaende erzeugen, weil `S_(t+1)` verschieden sein kann. Das ist eine
erwartete Folge der geschlossenen technischen Kopplung und kein Fehler.

Fuer einen spaeteren isolierten Probevergleich muss deshalb ein gemeinsamer
E1-Zustand vor der Probe geklont und waehrend der Probe wahlweise eingefroren
werden. Diese Probeintervention ist nicht Teil der ersten Runtimefunktion.

## Validierung und Fehleratomaritaet

Vor der ersten Rechnung werden gemeinsam validiert:

- `SharedMCMField` und vollstaendige E1-Geometriebindung;
- `ReceptorDistribution` und passender `MCMFieldStepTime`;
- S/H-, Nachhall- und optionale Dissipationskonfiguration;
- echter Boolescher Wert fuer `backreaction_enabled`;
- positiver expliziter Intervallumfang.

Bei jedem Fehler wird weder ein Teilfeld noch ein E1-Teilzustand ausgegeben.
Alle Eingabeobjekte bleiben unveraendert.

## Kein impliziter Ausbau

S1-BT erlaubt noch nicht:

- transiente asynchrone E1-Kopplung;
- Snapshot/Restore von E1;
- Export ueber `__init__` oder `current_api`;
- Aktivierung in Browser-, Audio-, Video- oder anderen Consumern;
- automatische Wiederholungs- oder Memoryauswertung;
- Parameteroptimierung anhand eines gewuenschten Ergebnisses.

## Pflichtpruefungen der spaeteren Implementierung

1. exakte P0-/A0-Feldidentitaet bei beliebigem gueltigem `b_t`;
2. aktive A1-Abweichung nur bei wirksamer nichtuniformer Kopplung;
3. exakte A0-/A1-Identitaet fuer `gamma = 0`;
4. korrekte Verwendung des E1-Mittelzustands als angewendeter Adapter;
5. zwei halbe E1-Schritte entsprechen bei festem S und ohne Feldwirkung dem
   erwarteten verfeinerten E1-Verlauf;
6. Unveraenderlichkeit aller Eingaben;
7. Feld- und E1-Geometrie bleiben identisch gebunden;
8. normierter S/H-Bereich und endliche Werte;
9. Verfeinerungsvergleich `dt`, `dt/2`, `dt/4`;
10. bestehender neutraler und `current_api`-Testverbund bleibt unveraendert.

## Aussagegrenze

Ein bestandener atomarer Schritt wuerde erstmals eine technische
geschlossene E1-Feldkopplung zeigen. E2 waere damit noch nicht erreicht, denn
es fehlt weiterhin die kontrollierte spaetere identische Probe nach
angeglichenem S/H. Memory, Praegung oder Rekonstruktion werden nicht
behauptet.

## Bester naechster Schritt

S1-BU hat den synchronen atomaren E1/S/H-Schritt in einem neuen isolierten
Modul implementiert und gegen P0, A0 und A1 fokussiert abgenommen. Als
naechstes bindet S1-BV den eingefrorenen identischen Probevertrag fuer die
strengere E2-Kausalpruefung. Der transiente AV-Pfad bleibt unveraendert.
