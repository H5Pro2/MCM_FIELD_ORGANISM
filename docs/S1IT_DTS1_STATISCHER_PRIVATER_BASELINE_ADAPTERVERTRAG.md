# S1-IT: Statischer privater DTS-1-Baseline-Adaptervertrag

## Status

S1-IT bindet die privaten Schnittstellen fuer die sechs in S1-IS als statisch
anschliessbar klassifizierten Baseline-Kerne. Der Vertrag definiert Eingaben,
Ausgaben, baselineeigene Zustandsinitialisierung, Zeitplanabbildung und
Fail-Closed-Regeln. Es wurde kein Adapter implementiert und keine
Modellfunktion ausgefuehrt.

Entscheidung:

```text
SIX_PRIVATE_BASELINE_ADAPTER_CONTRACTS_BOUND_NO_IMPLEMENTATION_OR_VALUES
```

Vertragsdigest:

```text
942373dd7605c8b8054c1b188d99fce47145d7894e7521bad81c2b9065facac4
```

## Gemeinsame Schnittstelle

Jeder Adapter erhaelt nur kanonische Knoten und Kanten, den vollstaendigen
S/H-Vorzustand, geordnete Kontakte und Zeitgrenzen sowie Identitaeten bereits
vorhandener Konfigurationsquellen. Ausgabe sind vollstaendige S/H-
Checkpointvektoren, Eingabe-, Konfigurations- und Ausgabedigest sowie
modelleigene Invarianten und numerische Diagnosen.

Erfolg oder Fehler ist atomar. Teilprofile sind unzulaessig. Kontaktwerte,
Reihenfolge, Beginn, Ende, Dauer und Checkpoints bleiben unveraendert. Auch
kontaktfreie Intervalle bleiben explizit und duerfen nicht entfernt werden.

## Rollenspezifische Bindung

- B1 erhaelt nur einen bereinigten gemeinsamen leitenden Zustand vor der
  Armdivergenz. Das originale DTS-1-Anatomieobjekt ist gesperrt. Der daraus
  einmal erzeugte Kantenratenbestand bleibt danach fest.
- B2 startet mit dem gemeinsamen S/H-Zustand und einem baselineeigenen
  neutralen Null-L. Generator und Randvektor muessen exakt zur Geometrie
  passen.
- B3 bis B5 starten mit einem einheitlichen baselineeigenen M-Zustand und
  verwenden ihren unveraenderten Rechner im privaten Slot der vorhandenen
  generischen F3-Runtime.
- B6 verwendet fuer beide Geometrien dieselbe vorhandene eingefrorene W7-M-
  CONST-V-Spezifikation und einen einheitlichen baselineeigenen M-Zustand.

Freie, refraktaere oder transferierte DTS-1-Ressource, Arm- und Fallkennung,
Zielrichtung, Referenzausgabe, Zukunftszustand sowie ergebnisabhaengige Werte
sind fuer alle Adapter verboten. Schon ihre Anwesenheit fuehrt vor dem
Kernelaufruf zum Fehler.

## Noch offene Bindung

S1-IT benennt Konfigurationsquellen nur nach ihrer Rolle. Zahlenwerte,
Konfigurationsdigests, Refinement und Vergleichsschwellen bleiben offen.
Ebenso unbewiesen sind numerische Zulaessigkeit, 28-Komponenten-
Profilrekonstruktion und deterministische Wiederholung.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1it_private_adapter_contract.py
tests/test_dynamic_substrate_s1it_private_adapter_contract.py
```

Zehn Tests pruefen Quellenbindung, sechs getrennte Adapter, vollstaendige
S/H-Schemata, B1-Informationsbarriere, baselineeigene L/M-Initialisierung,
Zeitplanerhaltung, offene Werte und Digests, Fail-Closed-Verhalten,
Ausfuehrungsfreiheit und Manipulationsschutz.

## Bester naechster Schritt

S1-IU darf ausschliesslich einen endlichen statischen Bindungsvertrag fuer
die vorhandenen Konfigurationsquellen, deren exakte Werte und Digests sowie
die Zwei-/Dreiknoten-Adapterfallmatrix festlegen. Noch keine
Adapterimplementierung, Modellausfuehrung, Runtime oder Forschungsprobe.
