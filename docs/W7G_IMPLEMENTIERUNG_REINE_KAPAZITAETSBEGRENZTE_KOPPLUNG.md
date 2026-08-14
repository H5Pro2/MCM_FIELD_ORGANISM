# W7-G: Implementierung der reinen kapazitaetsbegrenzten Kopplung

Stand: 2026-08-09

Entscheidung: `PURE_CAPACITY_LIMITED_COUPLING_IMPLEMENTED`

Arbeitsart: additive opt-in Referenzimplementierung

Runtimeintegration: nein

Forschungslauf: nein

## Implementierter Umfang

W7-G setzt ausschliesslich die in W7-F gebundene reine Ableitungsfunktion um:

```text
mcm_field_organism/capacity_limited_mcm_f3_coupling.py
```

Das Modul enthaelt:

- `MCMCapacityLimitedCouplingContract` fuer genau eine feste
  `site_capacity`;
- `MCMCapacityLimitedEdgeRate` fuer beide nichtnegativen gerichteten Raten
  einer kanonischen Feldkante;
- `MCMCapacityLimitedCouplingResult` fuer das fluechtige Kantenledger und die
  daraus gebildeten lokalen M-/S-Raten;
- `compute_capacity_limited_mcm_f3_coupling(...)` als reine opt-in Funktion;
- einen eigenen harten Fehlervertrag.

Die Funktion liest genau einen unveraenderten `MCMNeuronLayer`, einen
unveraenderten `MCMSubstrateState` und einen Kapazitaetsvertrag. Sie schreibt
keinen Zustand fort und haelt keine Welt-, Verlaufs- oder Observerdaten.

## Mathematische Bindung im Code

Fuer jede vorhandene kanonische Kante werden die W7-F-Raten direkt aus dem
abgeschlossenen S/M-Vorzustand berechnet:

```text
q_i_to_j = lambda_sm * M_i * (1 - M_j/C_site)
           * (1 + kappa*(S_j-S_i))
```

und spiegelbildlich fuer j nach i. Der resultierende Nettofluss wird mit
entgegengesetztem Vorzeichen an beiden Orten verbucht. Die S-Rueckarbeit
verwendet unveraendert denselben fertigen lokalen M-Ratenvektor.

Die Implementierung prueft vor der Berechnung:

- vollstaendige Identitaet von Feldorten und M-Mengen;
- unveraenderten Geometrie- und Kanten-Digest;
- `M_total/N < site_capacity <= M_total`;
- `M_i <= site_capacity` an jedem Ort;
- nichtnegative gerichtete Feldfaktoren;
- endliche nichtnegative gerichtete Raten.

Es gibt kein Clipping, keine Renormierung und keine Zustandskorrektur.

## Trennung vom aktiven Projektpfad

W7-G hat nicht veraendert:

- `mcm_f3_coupling.py`;
- `mcm_f3_runtime.py`;
- `MCMSubstrateState` und sein Snapshot-Schema;
- `mcm_field_organism.__init__`;
- `mcm_field_organism.current_api`;
- Browser-, Audio-, Video-, Runner- oder Reportpfade.

Das neue Modul ist nur durch direkten expliziten Modulimport erreichbar. Es
gibt keinen neutralen Default und keine implizite Aktivierung.

## Vertragstests

Neu angelegt:

```text
tests/test_capacity_limited_mcm_f3_coupling.py
```

Geprueft werden:

1. exakter Nullarm und Eingabeimmutabilitaet;
2. Zuflussnull bei voller Zielkapazitaet;
3. fehlende Abgabe bei leerer Quelle;
4. exakte Rekonstruktion des bilinearen W7-F-Delta-J-Terms;
5. Gleichheit mit passiver K2/F3-Diffusion bei `kappa = 0`;
6. `eta = 0` entfernt nur die S-Rueckarbeit;
7. kantenweise Gesamtmassenbilanz;
8. Invarianz gegen Deklarationsreihenfolge;
9. harte Ablehnung unzulaessiger Kapazitaetskorridore und Ueberbelegung;
10. keine Aufnahme in `current_api`.

Der fokussierte Standardbibliotheksverbund aus neuer und bestehender
K2/F3-Kopplungssuite ergibt:

```text
python -m unittest \
  tests.test_capacity_limited_mcm_f3_coupling \
  tests.test_mcm_f3_coupling -q

Ran 21 tests in 0.030s
OK
```

Der globale Python-Interpreter enthaelt kein `pytest`; deshalb wurde derselbe
auf `unittest` basierende Verbund direkt ausgefuehrt. Das ist keine
fachliche oder technische Testabweichung.

## Aussagegrenze

W7-G belegt die korrekte reine Ableitungsrechnung und ihre algebraischen
Grenzen. Nicht belegt sind:

- diskrete Invarianz unter einem Zeitschritt;
- Runtime-, Snapshot- oder Restore-Faehigkeit des neuen Pfads;
- Verhalten unter Audio-, Video- oder Browser-Testwelten;
- konkurrierende Verdraengung, funktionale Loesung oder
  Kapazitaetswiederverwendung;
- Verdichtung, Feldzeit, Memory, Organisation, Semantik,
  Selbstregulation oder KI.

## Entscheidung

```text
reine Kopplungsfunktion:            implementiert
gerichtetes Kantenledger:           implementiert
W7-F-Algebra:                       fokussiert bestaetigt
bestehender K2/F3-Pfad:             unveraendert
current_api:                        unveraendert
Runtimeintegration:                 nein
Forschungslauf:                     nein
```

## Bester naechster Schritt

W7-H bindet vor jeder Runtimeaenderung den diskreten Integrationsvertrag. Er
muss eine Forward-Euler-Schrittgrenze fuer `0 <= M_i <= C_site` herleiten,
ihre Vererbung durch SSPRK(3,3) zeigen, P0 und Ereignisgrenzen erhalten sowie
die erforderlichen Diagnosen festlegen. W7-H implementiert noch keine
Runtime und fuehrt keinen Weltlauf aus.
