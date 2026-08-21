# S1-PZ: Statischer modellneutraler Expositionsrollenvertrag fuer den S1-PX-Lebenszyklus

## Status und Umfang

S1-PZ bindet ausschliesslich die Rollen, Kausalordnung und
Informationsgrenzen der spaeter erforderlichen Expositionen. Der Vertrag
waehlt keine konkrete Geometrie, keine Werte, Dauern, Ticks, Digests,
Toleranzen oder Fixture.

S1-PZ enthaelt insbesondere:

- keinen Kandidaten und keine Zustandsanatomie;
- keine Gleichung und keine Parameter;
- keine Baselinekonfiguration;
- keine Runtime- oder Feldkernaenderung;
- keinen Test und keinen Feldlauf;
- keine Ergebnis- oder Funktionsentscheidung.

Verbindliche Entscheidung:

```text
MODEL_NEUTRAL_S1PX_LIFECYCLE_EXPOSURE_ROLES_BOUND
NORMAL_HISTORY_CARRY_AND_READOUT_ALIGNMENT_SEPARATED
NO_VALUES_NO_FIXTURE_NO_CANDIDATE_NO_EXECUTION
```

## Modellneutrale Ortsrollen

Eine spaetere endliche Geometrie muss drei unterscheidbare Expositionsorte
bereitstellen:

| Rolle | Bedeutung | Informationsgrenze |
|---|---|---|
| `A_FOCAL` | fokale Geschichte und spaetere fokale Probe | kein Ziel- oder Ergebnislabel im Modellaufruf |
| `B_LOCAL` | von A verschiedene lokale Konkurrenzgeschichte mit gemeinsamem lokalen Umfeld | keine Kandidatenressource als Eingabewert |
| `C_REMOTE` | geometrisch und exogen belastungsangepasste, aber nichtlokale Kontrollgeschichte | kein Zugriff auf einen privaten A/B-Zustand |

`A_FOCAL` und `B_LOCAL` muessen in der spaeter registrierten Geometrie eine
klar definierte lokale Nachbarschaft teilen. `C_REMOTE` muss dieselbe
exogene Form und Belastung wie B tragen koennen, darf aber diese lokale
Nachbarschaft nicht teilen.

Diese Rollen beschreiben nur Geometrie und Exposition. Sie behaupten weder,
dass eine Ressource existiert, noch wo ein spaeterer Kandidat liegen muss.

## Modellneutrale Ereignisrollen

S1-PZ bindet folgende Ereignisklassen ohne konkrete Payloads:

- `HISTORY_A`: normale fokale Weltgeschichte an A;
- `HISTORY_B_LOCAL`: normale konkurrierende Weltgeschichte an B;
- `HISTORY_C_REMOTE`: zu B belastungsangepasste Kontrollgeschichte an C;
- `GAP_ZERO_CONTACT`: normale kontaktfreie Feldfortsetzung ohne privaten
  Recoveryschalter;
- `PROBE_A`: in allen zu vergleichenden Armen wertidentische spaetere
  A-Probe;
- `PROBE_B`: in allen Wiederverwendungsarmen wertidentische spaetere B-Probe;
- `ALIGN_READOUT_SH`: zeitloser gemeinsamer Angleichungsschritt unmittelbar
  vor einer Probe;
- `OBSERVE`: passiver Checkpoint ohne Rueckwirkung auf ein Modell.

Ein Ereignis traegt spaeter ausschliesslich Feld-, Rezeptor-, Geometrie- und
Zeitdaten. Profilname, Armname, Ereignisrolle, Ordinal, erwartete Richtung,
Checkpoint, Referenzwert und spaeteres Ergebnis bleiben im Orchestrator.

## Normale Feldfortsetzung und Angleichungsgrenze

Innerhalb einer Bildung, Konkurrenz, Gap-, Freigabe- oder
Wiederverwendungsgeschichte wird der vollstaendige Feldzustand normal und in
kausaler Reihenfolge getragen. S und H duerfen dabei nicht vor jedem
Geschichtsintervall auf vorgegebene Rollenwerte gesetzt werden.

`ALIGN_READOUT_SH` ist nur unmittelbar vor einem vergleichenden Readout
zulaessig. Der Schritt:

- gleicht aktuellen Rezeptorkontakt, S und H zwischen den zu vergleichenden
  Armen an;
- verbraucht keine Feldzeit;
- fuehrt keine Modellgleichung aus;
- erzeugt keinen privaten Zustandswechsel;
- erhaelt jeden vollstaendigen modelleigenen Zustand bitgenau;
- darf nicht von Arm, Modell, Ergebnis oder spaeterem Zustand abhaengen.

Damit wird die schnelle aktuelle Feldlage als Erklaerung kontrolliert, ohne
die vorherige normale Feldgeschichte durch wiederholte Klemmschritte zu
ersetzen.

## Gemeinsame Start- und Konfigurationsregel

Jeder Arm startet aus einem unabhaengig rekonstruierten, digestgleichen
Frischzustand derselben spaeteren Registrierung. Ein Zustand darf nicht aus
dem Endzustand eines anderen Arms uebernommen werden.

Fuer jedes Modell gilt ueber alle Expositionsfamilien:

- eine unveraenderte Modellklasse;
- eine unveraenderte Konfigurationsquelle;
- ein unveraenderter Konfigurationsdigest;
- dieselbe Geometrie- und Zeitinterpretation;
- keine armweise Initialisierung ausser dem gemeinsam registrierten
  Frischzustand;
- kein Retry, Reset, Fit oder Parameterwechsel nach einem Zwischenresultat.

## Expositionsfamilie F: Endogene Bildung und spaetere Wirkung

Die Bildungsfamilie besitzt drei getrennte Arme:

```text
F_A: HISTORY_A        -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
F_C: HISTORY_C_REMOTE -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
F_G: GAP_ZERO_CONTACT -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
```

`HISTORY_A` und `HISTORY_C_REMOTE` muessen spaeter in exogener Gesamtlast und
Zeit vergleichbar registriert werden. `F_G` kontrolliert den reinen
Zeitverlauf ohne Kontaktlast.

Die Familie trennt:

- fokale Geschichte von gleichem spaeterem Eingang;
- fokale Geschichte von nichtlokaler, belastungsangepasster Geschichte;
- beide Kontaktgeschichten von einer reinen Gap-Geschichte;
- verbleibende private Wirkung von aktuellem S, H und Rezeptorkontakt.

Eine Differenz zwischen `F_A` und `F_G` allein reicht nicht. Sie muss auch
gegen `F_C` und alle Pflichtbaselines bestehen.

## Expositionsfamilie T: Wiederholung und Abschwaechung

Die Wiederholungsfamilie verwendet mehrere unabhaengige Arme mit geordneten
Praefixen derselben A-Geschichte:

```text
T_EARLY:   kurzer registrierter HISTORY_A-Praefix
           -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE

T_LATER:   laengerer registrierter HISTORY_A-Praefix
           -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
```

`T_EARLY` muss ein echter Praefix von `T_LATER` sein. Spaetere Werte und
Anzahl der Wiederholungen bleiben offen. Die Probe ist nicht Teil des
Bildungspraefixes und in beiden Armen identisch.

Die Familie bindet nur die Beobachtungsrichtung. Ein fester leaky Zerfall,
Sattigung oder Clamp darf spaeter nicht als eigene Abschwaechungsfunktion
umgedeutet werden.

## Expositionsfamilie I: Lokale Interferenz

Alle Interferenzarme tragen denselben A-Bildungspraefix. Nur der mittlere
Abschnitt unterscheidet sich:

```text
I_LOCAL:  HISTORY_A -> HISTORY_B_LOCAL -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
I_REMOTE: HISTORY_A -> HISTORY_C_REMOTE -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
I_GAP:    HISTORY_A -> GAP_ZERO_CONTACT -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
```

`HISTORY_B_LOCAL` und `HISTORY_C_REMOTE` muessen spaeter exogene Last, Form
und Dauer gemeinsam kontrollieren. `I_GAP` muss dieselbe mittlere Zeitgrenze
ohne Kontakt tragen.

Die notwendige Interferenzprognose ist dreifach:

- `I_LOCAL` gegen `I_REMOTE` trennt lokale Konkurrenz von gleicher
  nichtlokaler Last;
- `I_LOCAL` gegen `I_GAP` trennt Konkurrenz von reinem Zeitverlauf;
- `I_REMOTE` gegen `I_GAP` quantifiziert jede ortsunabhaengige Lastwirkung.

Kein einzelner dieser Kontraste darf isoliert als S1-PX-Funktion bewertet
werden.

## Expositionsfamilie C: Endliche lokale Kapazitaet

Die Kapazitaetsfamilie verwendet dieselben drei mittleren Rollen wie I,
bindet aber zusaetzliche passive Checkpoints vor und nach dem mittleren
Abschnitt:

```text
gemeinsamer HISTORY_A-Praefix
-> OBSERVE_PRE_COMPETITION
-> B_LOCAL | C_REMOTE | GAP_ZERO_CONTACT
-> OBSERVE_POST_COMPETITION
-> ALIGN_READOUT_SH
-> PROBE_A
-> OBSERVE_READOUT
```

Die Exposition selbst enthaelt keine Ressourcenmenge. Ein spaeterer Kandidat
muss seine vollstaendige lokale Bilanz an den Checkpoints separat und passiv
offenlegen. Baselines erhalten diese Bilanz nicht als Eingabe.

Kapazitaet ist nur dann lokal exponiert, wenn B und C gleich belastet sind,
aber allein B das registrierte lokale Umfeld von A teilt.

## Expositionsfamilie R: Funktionsverlust und Freigabe

Die Freigabefamilie verwendet normale kontaktfreie Feldfortsetzung. Sie
enthaelt keinen Recovery-on/off-Schalter:

```text
R_EARLY: HISTORY_A -> GAP_EARLY
         -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE

R_LATE:  HISTORY_A -> GAP_LATE
         -> ALIGN_READOUT_SH -> PROBE_A -> OBSERVE
```

`GAP_EARLY` und `GAP_LATE` sind geordnete Praefixrollen derselben spaeter zu
registrierenden Nullkontaktfortsetzung. Ihre konkreten Dauern bleiben offen.

Freigabe darf erst angenommen werden, wenn der alte A-Effekt im spaeteren
`R_LATE`-Readout funktionslos ist und eine direkte spaetere Bilanz denselben
lokalen Zustandsraum als wieder nutzbar ausweist. Reiner Zeitablauf,
Nullsetzen oder ein Neustart reicht nicht.

## Expositionsfamilie U: Andere Wiederverwendung

Wiederverwendung wird in getrennten Frischreplikaten mit identischer
B-Geschichte geprueft:

```text
U_RELEASED:
HISTORY_A -> GAP_LATE -> HISTORY_B_LOCAL
-> ALIGN_READOUT_SH -> PROBE_B -> OBSERVE

U_EARLY:
HISTORY_A -> GAP_EARLY -> HISTORY_B_LOCAL
-> ALIGN_READOUT_SH -> PROBE_B -> OBSERVE

U_FRESH_B:
zeitangepasste Frischkontrolle -> HISTORY_B_LOCAL
-> ALIGN_READOUT_SH -> PROBE_B -> OBSERVE
```

`HISTORY_B_LOCAL` und `PROBE_B` sind in allen drei Armen identisch. Ein
spaeterer Kandidat muss zeigen, dass B nach vollstaendiger A-Freigabe wieder
lokale Wirkung bilden kann und dass dies nicht nur aus einem staerkeren
aktuellen B-Eingang folgt.

`U_RELEASED` darf nur gemeinsam mit dem A-Funktionsverlust aus `R_LATE` und
der direkten Kapazitaetsbilanz bewertet werden.

## Ablations- und Nullpfadrollen

Die gemeinsame Exposition muss spaeter zwei private Kontrollrollen zulassen:

- `CANDIDATE_ABLATION_AT_READOUT`: derselbe vollstaendige Geschichtspraefix
  und dieselbe S/H-Angleichung, aber die spaetere Kandidatenrueckwirkung ist
  fuer genau den Readout ausgeschaltet;
- `CANDIDATE_DISABLED_FULL_PATH`: der Kandidat ist ab Frischzustand ueber die
  gesamte Exposition ausgeschaltet.

Diese Rollen sind keine Felder der gemeinsamen Expositionshuelle und bleiben
fuer Baselines unerreichbar. Ihre konkrete technische Bedeutung kann erst
ein spaeterer Kandidatenvertrag festlegen.

Der Vollpfad muss spaeter den bestehenden Feldkern-Nullpfad bitgenau
erhalten. Die Readoutablation muss eine beobachtete Differenz beseitigen,
ohne Eingang, S/H-Vorzustand oder Baselinekonfiguration zu veraendern.

## Faire Baselineexposition

Jede zustandsbehaftete Baseline erhaelt exakt dieselben F-, T-, I-, C-, R-
und U-Geschichten wie ein spaeterer Kandidat. Sie traegt ihren eigenen
vollstaendigen Zustand ueber jedes Geschichtspraefix und durch jeden Gap.

Unzulaessig sind:

- nur der letzte Readout statt der vorangegangenen Geschichte;
- andere Gap- oder Kontaktgrenzen fuer eine Baseline;
- armweise Parameter oder verschiedene Frischzustaende;
- Kandidatenressource, Kandidatenbilanz oder Ablationsrolle als
  Baselineeingabe;
- Ergebnislabels, Zielrichtung, Referenzvektor oder Zukunftszustand;
- Wiederverwendung alter Profile ohne formal identische Kausalgeschichte.

Ist eine Baselineoberflaeche mit einer Pflichtgeschichte nicht kompatibel,
wird der Gesamtvergleich gestoppt. Die Baseline darf nicht still entfallen.

## Fail-Closed-Regeln

S1-PZ gilt als verletzt, wenn spaeter mindestens eine der folgenden
Bedingungen eintritt:

- A, B und C sind geometrisch oder exogen nicht eindeutig getrennt;
- B und C koennen nicht belastungs- und zeitangepasst registriert werden;
- S oder H wird waehrend einer normalen Geschichte wiederholt geklemmt;
- `ALIGN_READOUT_SH` veraendert einen privaten Modellzustand;
- Arme starten nicht aus unabhaengigen gleichen Frischzustaenden;
- ein Modell erhaelt Arm-, Rollen-, Ziel-, Ergebnis- oder Checkpointwissen;
- ein Recoveryschalter ersetzt die normale Freigabegeschichte;
- ein alter Ergebnisvektor oder DTS-/G2-Sidecar wird als neue Exposition
  uebernommen;
- eine Pflichtbaseline sieht eine andere relevante Geschichte;
- ein Teilarm wird nach einem Zwischenresultat veraendert oder repariert.

## Aussagegrenze

S1-PZ bindet nur die faire Expositionslogik. Der Vertrag zeigt keine
endogene Disposition, Abschwaechung, Interferenz, Kapazitaet, Freigabe,
Wiederverwendung oder hypothetische MCM-Memory-Funktion. Der primaere
MCM-Wahrnehmungsfeldkern und alle geschlossenen Zweige bleiben unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-QA - statischer Beobachtungs-, Bilanz- und
        Lebenszyklus-Comparatorrollenvertrag
```

S1-QA soll ausschliesslich festlegen, welche passiven Beobachtungen,
Bilanzrollen, Kontraste, Ablationsgates und atomaren Entscheidungsstufen fuer
F, T, I, C, R und U erforderlich sind. Es darf keinen Kandidaten, keine
Zustandsanatomie, Gleichung, Parameter, konkreten Wert, Toleranz, Fixture,
Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung enthalten.
