# K2/F3 Scheibe C: SSPRK-Runtimevertrag

Stand: 2026-08-06

Status:

- ereignisausgerichtete gekoppelte S/H/M-Runtime implementiert;
- P0-Exaktpfad und aktive SSPRK(3,3)-Pfadtrennung implementiert;
- technische Invarianten-, Verfeinerungs- und Restoretests bestanden;
- noch kein AV-Forschungslauf und kein Memory-Nachweis.

## 1. Implementierter Umfang

Modul:

```text
mcm_field_organism/mcm_f3_runtime.py
```

Oeffentliche API:

```text
MCMF3AdvanceDiagnostics
MCMF3AdvanceResult
MCMF3RuntimeError
activate_mcm_f3_field
advance_mcm_f3_shared_field
advance_mcm_f3_shared_field_transient
mcm_f3_runtime_public_roles
```

`activate_mcm_f3_field` haengt die gleichfoermige aktive M-Initialreferenz an
ein bestehendes gemeinsames Feld. Der allgemeine `SharedMCMField.advance`-Pfad
bleibt fuer aktive Substrate gesperrt. Aktive Fortentwicklung ist nur ueber
die dedizierte F3-Runtime moeglich.

## 2. P0-Bypass

Bei `lambda_sm_per_second == 0` ruft die Runtime direkt die bestehenden
exakten S/H-Funktionen auf:

```text
advance_neutral_fast_shared_field
advance_neutral_fast_shared_field_transient
```

SSPRK wird in P0 nicht betreten. Der vollstaendige historische
Fast-State-Projektionsdigest bleibt identisch und M bleibt unveraendert.

## 3. Aktive gemeinsame Rechte-Seite

Jede SSPRK-Stufe bildet einen einzigen Zustandsvektor:

```text
Y = (S, H, M)
```

Die Stufenfunktion verwendet:

- die bestehende lokale S-Ausbreitung und Weltgrenze;
- das bestehende H-Tracking und die bestehende Dissipation;
- unveraendert die in Scheibe B gepruefte C/R-Funktion.

Innerhalb einer Stufe werden C und R aus demselben S/M-Zustand gebildet. M
wird weder normalisiert noch geclippt.

## 4. SSPRK(3,3)

Implementiert ist die vorregistrierte Shu-Osher-Form:

```text
Y1 = Y0 + h F(Y0)
Y2 = 3/4 Y0 + 1/4 (Y1 + h F(Y1))
Y3 = 1/3 Y0 + 2/3 (Y2 + h F(Y2))
```

Die Schrittgrenze wird aus maximalem Feldgrad, S-Antwortrate, H-Zeitkonstante,
Dissipation, `lambda_sm` und `eta` berechnet. Die feste Sicherheitsmarge ist
0.5. Jedes vorhandene Ereignisintervall wird mit

```text
n = ceil(T / h_safe) * refinement
h = T / n
```

vollstaendig ausgefuellt. `refinement` ist ein technischer Vergleichsarm und
kein Organismusparameter.

## 5. Ereignisvertrag

Im transienten Pfad wird nur zwischen vorhandenen Rezeptorereignissen
integriert. Ein punktfoermiger Kontakt:

- aktualisiert S nach dem bestehenden lokalen Rezeptorvertrag;
- veraendert H am Sprung nicht direkt;
- veraendert M am Sprung nicht direkt;
- kann erst in der anschliessenden kontinuierlichen Feldzeit M-Transport
  ausloesen.

Gleichzeitige Kontakte verwenden denselben unveraenderten S-Vorzustand.

## 6. Invariantendiagnose

Nach jeder vollstaendigen SSPRK-Stufe werden nur lesende Diagnosen gebildet:

- Subschrittzahl und maximale Schrittweite;
- maximaler Gesamtmassenfehler;
- kleinster M-Wert;
- maximale absolute S- und H-Auslenkung.

Nichtendliche Werte, negative M-Werte, S/H-Intervallverletzungen oder ein
Gesamtmassenfehler ueber `1e-12` brechen den technischen Schritt ab. Es gibt
keine Zustandskorrektur.

Diagnosen sind Bestandteil des Rueckgabewerts, aber nicht des Feldzustands,
Snapshots oder Restores.

## 7. Technische Tests

Die fokussierten Scheibe-C-Tests bestaetigen:

- exakten kontinuierlichen P0-Bypass;
- exakten transienten P0-Bypass;
- aktive Massenerhaltung, M-Positivitaet und S/H-Intervalle;
- kausale Trennung durch `eta = 0`;
- geordnete Abnahme der Differenz fuer `n`, `2n` und `4n`;
- digestgleiche aktive Fortsetzung nach Schema-2-Restore;
- harte Sperre des allgemeinen aktiven Advancepfads;
- keinen direkten M-Sprung durch ein Rezeptorereignis;
- spaeteren M-Transport erst nach weiterer Feldzeit;
- Ausschluss der Diagnosen aus Schema 2;
- Ablehnung ungueltiger Verfeinerungswerte.

Fokussierte Runtimepruefung:

```text
10 Tests bestanden
3 Untertests bestanden
```

Die gesamte betroffene Feldregression wird nach Abschlussdokumentation erneut
ausgefuehrt. Technische Tests erhalten keine Laufnummer.

## 8. Nicht nachgewiesen

Scheibe C weist nur nach, dass der aktive mathematische Kandidat technisch
fortschreibbar und falsifizierbar ist. Nicht nachgewiesen sind:

- Wirkung unter einer kontrollierten realen AV-Rezeptorfolge;
- zeitverfeinerungsstabile kausale Wirkung in einem Forschungsarm;
- Praegung, Verdichtung, Loesung oder Vergessen;
- MCM-Memory, Organisation, Topologie, Semantik oder KI.

## 9. Naechste Grenze

Vor einem Forschungsbefund ist ein eigener gebundener F3-Laufvertrag fuer
eine bereits kontrollierte AV-Rezeptorfolge erforderlich. P0, P1,
`eta = 0`, `kappa = 0` sowie `n/2n/4n` muessen dieselben Rezeptorereignisse
erhalten. Der erste Lauf darf nur M-Transport, eta-abhaengige S-Rueckwirkung
und Zeitverfeinerungsstabilitaet untersuchen.
