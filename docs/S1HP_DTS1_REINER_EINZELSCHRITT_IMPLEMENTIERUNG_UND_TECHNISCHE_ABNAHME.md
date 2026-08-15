# S1-HP: DTS-1 reine Einzelschritt-Implementierung

## Status

Der in S1-HO gebundene private, zustandsfreie DTS-1-Einzelschritt ist
implementiert und gegen die technische Matrix abgenommen. Die Ausfuehrungen
sind ausschliesslich kleine synthetische Algebra- und Grenztests. Es wurde
kein MCM-Feld fortgeschrieben und kein Forschungs- oder Feldlauf ausgefuehrt.

Entscheidung:

```text
DTS1_PURE_STEP_IMPLEMENTED_TECHNICALLY_ACCEPTED
```

## Implementierter Umfang

Das private Modul

```text
mcm_field_organism/dynamic_substrate_dts1_step.py
```

enthaelt:

- `DTS1StepRates` fuer drei explizite globale Raten;
- `DTS1EdgeParticipation` fuer ein vollstaendiges kanonisches `p_e`-Ledger;
- `DTS1EdgeTransfer` fuer Bindung, Umsatz und Erholung je Kante;
- `DTS1StepResult` fuer neue Anatomie, Transferledger und passive Diagnosen;
- `compute_dts1_closed_prestate_step(...)` als einzige Rechenfunktion;
- einen eigenen harten `DTS1StepError`.

Die vorhandenen unveraenderlichen S1-HI-Typen fuer Kapazitaeten,
Kantenressourcen und Anatomie werden direkt wiederverwendet. Freie Ressource
wird weiterhin nur aus dem Kantenledger abgeleitet.

## Rechenweg

Der Schritt validiert zuerst das komplette Kanten- und Beteiligungsinventar.
Danach liest er genau einen abgeschlossenen Anatomiezustand, berechnet die
Intervallanteile mit `-expm1(-k*dt)`, bildet alle Angebote und gemeinsamen
Knotennachfragen und bestimmt erst dann alle lokalen Zulassungsfaktoren.

Bindung, Umsatz und Erholung werden aus demselben Vorzustand berechnet und in
genau einer neuen Anatomie gebucht. Neu entstandene Ressource wird im selben
Schritt nicht erneut verwendet. `math.fsum` wird fuer gemeinsame
Knotennachfragen und bestehende Anatomiebilanzen verwendet.

Es gibt kein Clipping, keine Nachnormierung, keine Zustandsreparatur und keine
Mutation der Eingaben. Ungueltige Eingaben oder Ausgaben brechen vor Rueckgabe
eines Ergebnisses ab.

## Technische Abnahme

Die 17 in S1-HO gebundenen Klassen sind umgesetzt:

- Nullintervall und Nullraten;
- getrennte Nullursachen fuer Bindung, Umsatz und Erholung;
- analytische Einkantenbetraege aller drei Rollenwechsel;
- simultane Konkurrenz an einem gemeinsam genutzten Knoten;
- Unabhaengigkeit von der Deklarationsreihenfolge;
- lokale und globale Ressourcenbilanz;
- keine Wiederverwendung neu erzeugter Ressource;
- Eingabeimmutabilitaet und deterministische Wiederholung;
- Fail-Closed fuer Zahlen, Beteiligungen, Kanten und Anatomie;
- Schrittverfeinerung einer gemischten Rollenfolge;
- Abwesenheit von Feld-, Runtime-, I/O- und oeffentlichen API-Pfaden.

Die dabei verwendeten Zahlen sind synthetische Testfixtures und keine
Materialparameterauswahl. Sie wurden nicht gegen ein Feldprofil angepasst.

## Isolationsgrenze

Nicht veraendert wurden:

```text
mcm_field_organism/__init__.py
mcm_field_organism/current_api.py
SharedMCMField
Snapshot und Restore
Runner, Browser, Audio und Video
```

Das Schrittmodul nimmt kein S/H-Feld entgegen und berechnet keine
Feldrueckwirkung. Die Beteiligungswerte werden explizit als abgeschlossenes
technisches Eingabeledger uebergeben.

## Aussagegrenze

Die Abnahme zeigt nur, dass die in S1-HN gebundene diskrete Algebra isoliert
reproduzierbar, positiv und bilanziert implementiert werden kann. Sie zeigt
keine Abschwaechung, Interferenz, Kapazitaetsfreigabe im MCM-Feld,
Wiederbeanspruchung oder funktionale Ueberlegenheit gegen eine Baseline.

## Bester naechster Schritt

S1-HQ darf nach dem naechsten `ok weiter` ausschliesslich einen statischen
Parameterkorridor- und Dimensionsaudit fuer `k_bind`, `k_turn`, `k_rec` und
das technische Schrittintervall vorbereiten. Noch keine Parameterschaetzung,
keine Feldrueckwirkung, keine Runtimeintegration und kein Forschungs- oder
Feldlauf.
