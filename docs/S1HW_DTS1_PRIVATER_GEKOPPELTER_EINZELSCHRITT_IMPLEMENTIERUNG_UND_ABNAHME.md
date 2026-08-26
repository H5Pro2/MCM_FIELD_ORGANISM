# S1-HW: DTS-1 gekoppelter Einzelschritt - Implementierung und Abnahme

## Status

Der in S1-HV gebundene private erste DTS-1/S/H-Einzelschritt ist technisch
implementiert und gegen die 20 vorregistrierten Matrixklassen geprueft.
Keine Runtimeanbindung, keine Materialparameterauswahl und keine
Forschungs-/Feldprobe.

Entscheidung:

```text
DTS1_PRIVATE_COUPLED_STEP_IMPLEMENTED_TECHNICALLY_ACCEPTED
```

Diese Entscheidung bestaetigt nur die technische Implementierung des
geschlossenen Vorzustands- und Paarcommitvertrags.

## Technische Feldzeitkorrektur

S1-HV hatte zunaechst die algebraische Nullzeitidentitaet aus S1-HU als
aufrufbaren Wrapperzweig beschrieben. Der bestehende technische Typ
`MCMFieldStepTime` fordert jedoch bereits konstruktiv:

```text
end_tick > start_tick
```

Ein Nullintervall kann den Wrapper daher nicht erreichen. S1-HV wurde
fail-closed praezisiert: Der gekoppelte Einstieg akzeptiert ausschliesslich
einen vorhandenen positiven, exakt zur Distribution passenden Feldzeitschritt.
Die Nullzeitidentitaet bleibt eine mathematische Grenze der reinen
Abbildungen. Es wurde kein zweiter Zeittyp und kein unaufrufbarer Sonderpfad
eingefuehrt.

Der korrigierte S1-HV-Vertragsdigest lautet:

```text
440ecb022f7684f5938f8df584c5dff8c5abbd4a92bdfdffb83cb4ee89216327
```

## Private Implementierung

Das neue Modul

```text
mcm_field_organism.dynamic_substrate_dts1_coupled_step
```

stellt genau den privaten Einstieg
`advance_dts1_coupled_fast_shared_field(...)` und den unveraenderlichen
Ergebniscontainer `DTS1CoupledFastFieldStepResult` bereit. Weder Paketwurzel
noch `current_api` wurden erweitert.

## Geschlossener Vorzustandsablauf

Ein Aufruf:

1. prueft Typen, Geometrie, Distribution, Feldzeit, Konfigurationen und den
   strikten Ablationsschalter;
2. bildet das vollstaendige kanonische `p_n`-Ledger nur aus `S_n` mit S1-HK;
3. liest den aktiven oder ablatierten Adapter nur aus `A_n` mit S1-HT;
4. berechnet `A_next` nur aus `A_n`, `p_n`, Zeit und Raten mit S1-HP;
5. bildet den Feldvorschlag aus `L_n`, Distribution und dem aus `A_n`
   gelesenen Adapter;
6. erzeugt erst danach einen vollstaendigen Ergebniscontainer.

`A_next` wird nie vom aktuellen Feldvorschlag gelesen. Der Feldvorschlag
liest nie `A_next`. Scheitert der Ressourcenvorschlag, wird kein Feldpfad
aufgerufen. Scheitert der Feldvorschlag, wird kein Paar ausgegeben.

## Neutraler und aktiver Feldpfad

Wenn der Ablationsarm A0 aktiv ist oder im A1-Vorzustand alle gebundenen
Leitungsressourcen null sind, delegiert der Wrapper direkt an
`advance_neutral_fast_shared_field`. Dadurch bleiben P0, A0 und der erste
Nullbindungs-A1-Feldvorschlag bitgenau identisch.

Bei aktiver Nichtnullbindung ersetzt nur der interne symmetrische
Kantengenerator die neutrale interne Diffusion. Der vollstaendige aktive
Generator lautet technisch:

```text
G_active = G_DTS1 + (G_neutral_mit_Rezeptorrand - G_neutral_intern)
```

Damit bleiben diagonale Rezeptorsenke, Rezeptorquelle, S/H-Spektralintegrator,
Nachhallzeit, optionale Leckrate und Feldbereichspruefung unveraendert. Dieser
Randterm wurde in der Implementierungspruefung ausdruecklich kontrolliert.

## Ergebnisgrenze

Ein erfolgreicher Aufruf liefert genau:

- das vollstaendige neue Feld;
- die vollstaendige neue DTS-1-Anatomie;
- die positive explizite Intervalllaenge;
- das aus `S_n` verwendete Beteiligungsledger;
- das passive S1-HP-Transferledger;
- den aus `A_n` angewandten S1-HT-Adapter.

Alle Eingaben bleiben unveraendert. Ledgers und Diagnosewerte sind passiv.

## Technische Matrixabnahme

Alle 20 S1-HV-Klassen sind umgesetzt und bestanden:

- positive bestehende Feldzeit und exakte Distribution-Zeitidentitaet;
- vollstaendige gemeinsame Geometrie und Digestidentitaet;
- kanonische Beteiligung ausschliesslich aus `S_n`;
- direkte Gleichheit zu S1-HP und S1-HT;
- bitgenaue P0/A0- und Nullbindungs-A1-Feldidentitaet;
- Ein-Subschritt-Kausalitaet in beide Richtungen;
- aktiver Generator mit unveraendertem Rezeptorrand;
- unveraenderte H-, Leck-, Bereichs- und Zeitsemantik;
- Unveraenderlichkeit, Determinismus und Deklarationsreihenfolge;
- getrennte Ressourcen- und Feldfehler ohne Paarausgabe;
- messbare Paarreste und schrumpfende Leserzeit unter `n,2n,4n`;
- kein Midpoint-, impliziter, adaptiver oder partieller Commitpfad;
- keine Runtime-, I/O-, Snapshot- oder oeffentliche API-Anbindung.

Die Testwerte sind synthetische Algebra- und Grenzfixtures. Technische
Matrixaufrufe sind keine Forschungsprobe. Der Receipt haelt deshalb
`research_field_steps_executed=0` und
`research_execution_permitted=False` fest.

## Pruefstand

```text
30 fokussierte S1-HV/S1-HW-Tests bestanden
169 relevante Tests bestanden
11 Subtests bestanden
0 Forschungsfeldschritte
```

Receipt-Digest:

```text
841ab118529a92d99ce84b41a77dcc0697b10c7ddfde4b879651c151767ec262
```

## Aussagegrenze

S1-HW belegt keine gekoppelte Konvergenz, keine robuste Baseline-Trennung und
keine der in S1-HH geforderten Funktionen. Abschwaechung, Interferenz,
Kapazitaetsfreigabe und Wiederbeanspruchung bleiben ungeprueft. Ebenso bleiben
absolute Materialraten und jede Forschungsruntime offen.

## Bester naechster Schritt

S1-HX bindet vor jeder weiteren Ausfuehrung nur einen endlichen synthetischen
Kopplungs-Verfeinerungs- und Kausalitaetsaudit mit identischen physischen
Eingaben fuer `n,2n,4n`, vollstaendigem Feld-/Anatomierest und explizitem
STOPP-Kriterium. Noch keine Materialparameter, Runtimeintegration oder
Forschungsprobe.
