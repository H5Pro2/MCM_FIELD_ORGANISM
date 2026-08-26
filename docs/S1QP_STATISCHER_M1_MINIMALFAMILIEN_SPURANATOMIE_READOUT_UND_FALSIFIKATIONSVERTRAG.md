# S1-QP: Statischer M1-Minimalfamilien-, Spuranatomie-, Readout- und Falsifikationsvertrag

## Status und Umfang

S1-QP bindet nach dem S1-QO-Bestandsaudit genau eine kleinste endliche
M1-Mehrzeitskalenfamilie. Der Vertrag legt Komponentenrollen, Zustand,
Einzelspurkern, lokalen Readout, Feldrollen und Falsifikationsgrenzen fest.

S1-QP registriert noch keine konkreten Zeitwerte, implementiert keine
Bankhuelle und fuehrt keinen Test oder Feldlauf aus. Der vorhandene W7-N-Kern,
M5_DIRECT, A1 und der primaere Feldkern bleiben unveraendert.

Vertragsentscheidung:

```text
M1_TWO_PARALLEL_INDEPENDENT_W7N_LEAK_TRACES_SELECTED
FAST_AND_SLOW_ORDERED_ROLES_WITH_DISTINCT_FIXED_TIME_CONSTANTS_BOUND
POINTWISE_EQUAL_MEAN_READOUT_SELECTED
A1_FAST_PROPOSAL_ONCE_REPLACE_S_AND_PRESERVE_H_BOUND
EXACT_TIME_VALUES_AND_IMPLEMENTATION_REMAIN_UNBOUND
NO_RUNTIME_NO_TEST_NO_FIELD_EXECUTION
```

## Auswahl der kleinsten Familie

M1 besteht aus genau zwei Spurrollen:

```text
M1_TRACE_ORDER = (FAST, SLOW)
```

Eine einzelne Spur waere funktional M5_DIRECT beziehungsweise einer
Einspur-Leaky-Baseline zuzuordnen. Mehr als zwei Spuren wuerden ohne eigene
zusaetzliche Gegenprognose nur Freiheitsgrade hinzufuegen. Zwei Spuren sind
daher die kleinste Familie, die gleichzeitig unterschiedliche feste
Nachwirkungsanteile tragen kann.

Die Rollen `FAST` und `SLOW` sind technische Konfigurationsrollen. Sie sind
keine Ereignis-, Arm-, Rezeptor-, Bedeutungs- oder Ergebnislabels.

## Ausgewaehlter Einzelspurkern

Beide Rollen verwenden ausschliesslich den vorhandenen reinen Kern:

```text
w7n_capacity_function_baselines.advance_w7n_local_baseline
model_id = leak
equation_contract = dz_i/dt=(S_i-z_i)/tau;R_i=0
```

Die bestehende W7-N-Gleichung wird nicht kopiert oder veraendert. Beide
Spuren sehen pro Intervall denselben vollstaendigen A1-S-Evidencevektor und
dieselbe Intervalldauer.

Unterschiedlich sein duerfen ausschliesslich:

- die technische Spezifikationsidentitaet;
- `time_constant_seconds`;
- der daraus folgende private Spurzustand.

Verbindlich gilt:

```text
0 < tau_FAST < tau_SLOW
```

Konkrete Werte werden in S1-QP nicht gewaehlt. Solange beide Werte nicht
statisch vorregistriert sind, ist M1 nicht implementierbar oder ausfuehrbar.

Die vorhandene einzelne W7-M-`LEAK`-Spezifikation darf nicht zweimal unter
verschiedenen Rollennamen ausgefuehrt werden. Gleiche Zeitwerte wuerden die
Familie auf eine Einspurrolle reduzieren.

## Spezifikationsgrenze

Eine spaetere private M1-Registrierung muss genau zwei
`W7MBaselineSpec`-Objekte enthalten:

| Rolle | `model_id` | persistente Skalare | Parameter | Runtimeflag |
|---|---|---:|---|---|
| FAST | `leak` | 1 pro Ort | nur `time_constant_seconds` | `False` |
| SLOW | `leak` | 1 pro Ort | nur `time_constant_seconds` | `False` |

Beide Spezifikationen muessen denselben vorhandenen Gleichungsvertrag
verwenden. SAT, NORM, epsilon, Gewichte, Kapazitaet, Kanten- oder
Substratparameter sind unzulaessig.

Die Spezifikationsdigests werden gemeinsam und geordnet in einer privaten
M1-Konfigurationsidentitaet gebunden. Ein Spezifikationswechsel waehrend
einer Geschichte oder zwischen Armen macht den gesamten M1-Arm ungueltig.

## Vollstaendige Spuranatomie

Der private M1-Zustand besteht genau aus:

```text
M1ParallelLeakBankState
    FAST -> W7NLocalBaselineState(model_id=leak, latent[N])
    SLOW -> W7NLocalBaselineState(model_id=leak, latent[N])
```

Dabei ist `N` die vollstaendige kanonische Feldknotenanzahl. Beide
Latentvektoren muessen dieselbe Knotenreihenfolge wie das Feld besitzen.

Zum Zustand gehoeren nicht:

- A1-S, H, Perzeption oder Rezeptorrohdaten;
- ein vorheriger Mittelwert oder finales Feld-S;
- globale Nenner oder geometrieweite Skalierungswerte;
- M-, Edge-, Ressourcen-, Entwicklungs- oder Kandidatenzustand;
- Puffer, Replayfolge, Zeitreihe oder Ereigniszaehler;
- Arm-, Pfad-, Ziel-, Probe- oder Ergebnislabels.

Der Frischzustand enthaelt fuer beide Rollen unabhaengige Nullvektoren. Die
beiden Rollen duerfen weder dasselbe Zustandsobjekt aliasieren noch eine
gemeinsame veraenderliche Ablage verwenden.

Nach jedem gueltigen Intervall werden beide vollstaendigen Folgezustaende
atomar und in der festen Ordnung `(FAST, SLOW)` getragen. Ein Teilzustand ist
kein zulaessiges Ergebnis.

## Parallele Fortschreibungsordnung

Die logische M1-Ordnung lautet:

```text
Feldvorzustand und Intervall
    -> genau ein kandidatenfreier A1-Fast-Vorschlag
    -> Evidence = vollstaendiges A1-S
    -> FAST_next = W7N_LEAK(FAST_pre, Evidence, Intervall)
    -> SLOW_next = W7N_LEAK(SLOW_pre, Evidence, Intervall)
    -> punktweiser fester M1-Readout
    -> finales S aus M1-Readout
    -> finales H unveraendert aus A1
```

Die textuelle Reihenfolge der beiden reinen W7-N-Aufrufe erzeugt keine
kausale Kopplung. Beide lesen ausschliesslich ihren jeweiligen Vorzustand und
dieselbe unveraenderte Evidence. Keine Spur darf den Vor- oder Folgezustand
der anderen lesen.

A1 wird genau einmal fortgeschrieben. Das finale Feld besitzt genau eine
Feldzeitfortschreibung.

## Gebundener lokaler Readout

Fuer jeden kanonischen Feldort `i` gilt nach vollstaendiger Fortschreibung:

```text
M1_output_i = (FAST_output_i + SLOW_output_i) / 2
```

Da W7-N `LEAK` seinen Zustand direkt ausgibt, ist dies zugleich der
gleichgewichtete Mittelwert beider Folgezustandskoordinaten.

Dieser Readout ist ausgewaehlt, weil er:

- keine anpassbaren Gewichte einfuehrt;
- beide Spurrollen symmetrisch und mit nicht verschwindendem Anteil bindet;
- unter Vertauschung der beiden Zahlen wertgleich bleibt;
- fuer Eingaben und Spurwerte im Bereich `[-1, 1]` denselben Bereich erhaelt;
- lokal und ortsseparabel bleibt;
- keinen globalen Nenner, keine Kante und keine Ressourcenrolle liest.

Gesperrt sind Summe ohne feste Bereichserhaltung, gewichtete Fits, Maximum,
Minimum, Produktausgabe, nichtlineare Gates, Clipping als neue Wirkung,
globale Normalisierung und eine Auswahl je Arm oder Checkpoint.

## S- und H-Feldrollen

M1 verwendet dieselbe azyklische `REPLACE_S`-Grenze wie M5_DIRECT:

- finales S stammt vollstaendig aus dem gebundenen M1-Mittelwert;
- finales H bleibt bitgleich zum einmaligen A1-Vorschlag;
- Perzeption, Docks, Neuronenidentitaeten und Geometrie bleiben unveraendert;
- der M1-Output wirkt erst als Feldvorzustand des naechsten Intervalls weiter;
- es gibt keine zweite aktuelle A1-Fortschreibung und keinen algebraischen
  Rueckkopplungskreis.

Der private modellneutrale A1/`REPLACE_S`-Hilfskern aus S1-QN waere spaeter
strukturell wiederverwendbar. S1-QP autorisiert diese Implementierung noch
nicht.

## Eigenstaendige Falsifikationsprognose

Fuer eine vorregistrierte einpolige lokale Exposition mit anschliessendem
identischem Nullkontakt-Gap sagt M1 strukturell voraus:

```text
Der lokale M1-Readout enthaelt gleichzeitig einen schnelleren und einen
langsameren positiven Abschwaechungsanteil. Der relative Einfluss der
schnelleren Spur nimmt ueber das Gap staerker ab als der der langsameren
Spur.
```

Eine einzelne feste W7-N-`LEAK`- beziehungsweise M5_DIRECT-Spur besitzt nur
einen solchen Abschwaechungsanteil. Der spaetere Vergleich muss deshalb
mindestens fruehe, mittlere und spaete Gap-Positionen gemeinsam binden. Ein
einzelner Messpunkt kann M1 nicht gegen eine Einspurrolle identifizieren.

Dies ist eine Gegenprognose, kein vorhandener Befund. Ob der spaetere
Feldverlauf sie benoetigt, ist offen.

## Abgrenzung gegen A1, B3 und M5_DIRECT

### A1

A1 traegt die bestehende einzelne schnelle Nachwirkung in H. M1 traegt zwei
private passive Spuren fuer finales S und darf H nicht veraendern. Erklaert
A1 allein das vollstaendige Profil, ist M1 nicht erforderlich.

### B3

Jede vorhandene B3-Rolle bleibt eine konkrete Einspur- oder M/F3-gebundene
Baseline. M1 darf keine M-, Kanten- oder Substratrolle uebernehmen. Eine
nachtraegliche Kombination separat passender B3-Arme ist kein M1-Vergleich.

### M5_DIRECT

M5_DIRECT verwendet genau einen registrierten W7-N-`LEAK`-Zustand und dessen
direkten Output. M1 verwendet zwei gleichzeitig getragene Zustaende und den
festen Mittelwert. Kann M5_DIRECT mit einem vorab registrierten Parametersatz
das vollstaendige Profil reproduzieren, ist die M1-Mehrspurrolle fuer diesen
Vergleich geschlossen.

M5_DIRECT wird nicht veraendert und darf keine zweite Spur aufnehmen.

## Weitere Nichtduplizierungsgrenzen

- Gegen Fixed Adapter bleibt M1 dynamisch abschwaechend statt statisch.
- Gegen Integrator besitzen beide M1-Spuren endliche positive Zeitrollen
  statt nicht abschwaechender Akkumulation.
- Gegen NORM bleibt der M1-Readout ortsseparabel und ohne entfernte
  Zustandslast.
- Gegen M2 speichert M1 keine Eingabefolge und waehlt keinen frueheren
  Zeitpunkt aus.
- Gegen M4 existieren keine Bindungs-, Blockierungs- oder Freigaberollen und
  keine gemeinsame Erhaltungsbilanz.

## Verwerfungsbedingungen

M1 wird als separate Ausfuehrungsrolle verworfen oder bleibt gesperrt, wenn:

- nicht genau zwei Spurrollen verwendet werden;
- `tau_FAST` und `tau_SLOW` gleich, vertauscht, nicht positiv oder nicht
  vorregistriert sind;
- eine Spur eine andere Evidence, Geometrie oder Intervalldauer sieht;
- eine Spur den Zustand oder Output der anderen liest;
- nur eine Spur einen nicht verschwindenden Readoutbeitrag besitzt;
- Readoutgewichte, Spurzahl oder Zeitwerte nach Ergebnissicht wechseln;
- Mittelwert, S-Ersetzung oder H-Identitaet nicht exakt eingehalten werden;
- eine Einspurbaseline das vollstaendige Profil nach der spaeter gebundenen
  Aequivalenzregel reproduziert;
- eine Abgrenzung nur an einem Checkpoint gelingt;
- geschlossene Kandidaten-, Ressourcen-, NORM-, Delay- oder Replayrollen
  hinzukommen;
- ein Fehler einen Teilzustand oder ein Teilfeld veroeffentlicht.

## Noch offene Bindungen

Vor jeder Implementierung fehlen:

- genau zwei konkrete positive Zeitwerte mit `tau_FAST < tau_SLOW`;
- ihre Herleitung ohne Ergebnissicht aus der bestehenden Zeit- und
  Gap-Anatomie;
- zwei eindeutige private Spezifikationsidentitaeten und Digests;
- die statische Identifizierbarkeitspruefung der fruehen, mittleren und
  spaeten Gap-Positionen;
- ein Zustands-, Kompositor-, Receipt-, Fehlercode- und Testbudgetvertrag.

Solange diese Bindungen fehlen, ist M1 weder implementierbar noch
ausfuehrbar. Die offene Luecke ist kein positives Residuum.

## Paketstatus

Nach S1-QP gilt:

```text
M1_MINIMAL_TWO_TRACE_FAMILY_BOUND
W7N_LEAK_SELECTED_AS_THE_ONLY_TRACE_KERNEL
EQUAL_LOCAL_MEAN_AND_REPLACE_S_FIELD_ROLE_BOUND
TIME_VALUES_CONFIGURATION_DIGESTS_AND_IMPLEMENTATION_UNBOUND
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

## Aussagegrenze

S1-QP bindet eine technische Gegenbaseline. Der Vertrag bestaetigt keine
Mehrzeitskalenwirkung im Feld, keinen Kandidaten und keinen Befund zu einer
hypothetischen MCM-Memory. Er erweitert weder den primaeren Feldkern noch eine
aktive Runtime.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QQ - statischer M1-Zeitrollenregistrierungs- und
        Gap-Identifizierbarkeitsvertrag
```

S1-QQ soll aus der bereits gebundenen technischen Intervall- und Gap-Anatomie
genau zwei konkrete Zeitwerte und mindestens drei gemeinsame Gap-Positionen
vorregistrieren. Die Auswahl muss vor jeder M1-Ausfuehrung erfolgen und darf
keine Kandidaten- oder Ergebniswerte lesen. Sind zwei Zeitrollen auf der
vorhandenen Zeitachse nicht identifizierbar, wird M1 gestoppt. Keine
Implementierung, Testausfuehrung oder Ergebnisentscheidung.
