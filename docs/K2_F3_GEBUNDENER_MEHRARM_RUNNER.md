# K2/F3: gebundener Mehrarm-Runner

Stand: 2026-08-06

Status:

- technischer Mehrarm-Runner implementiert;
- gleiche Rezeptorereignisse fuer alle Arme konstruktiv erzwungen;
- noch kein oeffentlicher AV-Forschungslauf ausgefuehrt;
- keine Memory-, Organisations-, Topologie-, Semantik- oder KI-Behauptung.

## 1. Implementierung

Modul:

```text
mcm_field_organism/mcm_f3_causal_runner.py
```

Oeffentliche API:

```text
MCMF3CausalArmRun
MCMF3CausalComparison
MCMF3CausalRunnerError
run_mcm_f3_causal_comparison
mcm_f3_causal_runner_public_roles
```

## 2. Gebundene Arme

Der Runner erzeugt aus einem substratfreien Ausgangsfeld und einem festen
aktiven Arm genau diese Reihenfolge:

```text
p0.exact
p1.n
p1.2n
p1.4n
b.eta-null
b.kappa-null
b.kappa-inverted
```

`eta-null` uebernimmt `lambda_sm` und `kappa` unveraendert von P1 und setzt
nur `eta = 0`. `kappa-null` uebernimmt `lambda_sm` und `eta` unveraendert und
setzt nur `kappa = 0`. Beide Ablationen verwenden die hoechste
Verfeinerungsstufe 4n. `kappa-inverted` uebernimmt `lambda_sm` und `eta`,
invertiert ausschliesslich das vorab gebundene Vorzeichen von `kappa` und
verwendet ebenfalls 4n.

## 3. Eine gemeinsame Ereignisursache

Die Rezeptorzeitfolgen werden genau einmal validiert und genau einmal in den
gemeinsamen `ReceptorProposalHandoff` ueberfuehrt. Fuer jeden Batch werden
Docktrajektorie und lokale Neuroneneingaben einmal gebildet. Dasselbe
unveraenderliche Eingabeobjekt wird danach an alle Arme gegeben.

Der Runner lehnt ab:

- doppelte oder widerspruechliche Quellenfenster;
- Ereignisse ausserhalb des gemeinsamen Horizonts;
- nicht genau einmal zugeordnete Ereignisse;
- ein Ausgangsfeld mit bereits vorhandenem Substrat;
- einen nicht aktiven P1-Referenzarm.

## 4. Ergebnisgrenze

Jeder Arm liefert:

- das vollstaendige aktuelle Schema-2-Feld;
- die feste Verfeinerung;
- technische Diagnosen je Proposal-Batch.

Diagnosen bleiben ausserhalb des Snapshots. Rohmedien, Rezeptorfolgen und
Handoff-Historien werden nicht im Feld gespeichert.

## 5. Technische Tests

Die fokussierte Runner-Suite bestaetigt:

- alle sieben Arme genau einmal und in fester Reihenfolge;
- denselben vollstaendigen Handoff fuer alle Arme;
- P0-Gleichheit zum bestehenden neutralen Asynchronrunner;
- digestgleiche Wiederholung aller Endzustaende und Diagnosen;
- geordnete P1-Verfeinerung n, 2n, 4n;
- getrennte eta-null-Wirkung;
- gleichfoermiges M im kappa-null-Arm;
- getrennte Wirkung der zwingenden kappa-Vorzeicheninversion;
- M-Gesamtmasse und Nichtnegativitaet in allen Armen;
- Ausschluss der Diagnosen aus Schema 2;
- Abbruch bei doppeltem Quellenfenster.

```text
6 Tests bestanden
7 Untertests bestanden
```

Diese Tests verwenden kontrollierte technische Rezeptorereignisse und sind
kein AV-Forschungslauf.

## 6. Noch offene Laufbindung

Vor dem ersten realen kontrollierten AV-Kausallauf muessen feststehen:

- eine bereits technisch validierte AV-Quelle und exakt abgegrenzte
  Zeitintervalle;
- unveraenderte Rezeptorreduktion und gemeinsame Ereignisfolge;
- P1-Parameter vor Einsicht in F3-Ergebnisse;
- feste Feld-, H-, Dissipations- und Proposal-Zeitparameter;
- technische Abbruchgrenzen;
- ein Berichtsschema, das Messung, Interpretation, Hypothese und Nichtnachweis
  trennt.

Der erste Lauf darf nur pruefen:

```text
M-Transport gegen p0 und kappa-null
eta-abhaengige S-Rueckwirkung
Zeitverfeinerungsstabilitaet n/2n/4n
```

Er darf weder Memory noch Praegung behaupten.
