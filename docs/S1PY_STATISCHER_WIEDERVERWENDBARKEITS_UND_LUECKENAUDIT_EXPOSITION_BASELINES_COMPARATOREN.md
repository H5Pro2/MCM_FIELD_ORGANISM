# S1-PY: Statischer Wiederverwendbarkeits- und Lueckenaudit von Exposition, Baselines und Comparatoren

## Status und Umfang

S1-PY auditiert ausschliesslich den vorhandenen technischen Bestand gegen den
S1-PX-Funktions- und Falsifikationsvertrag. Geprueft werden gemeinsame
Exposition, Modellvorzustaende, Baselineadapter, Orchestrierung,
Vergleichsrollen und geschlossene Kandidateninfrastruktur.

S1-PY fuehrt nicht aus und veraendert keine Runtime. Es wurden keine Fixture,
kein Test und kein Feldlauf gestartet. Es werden weder Kandidat noch
Gleichung, Parameter oder Zustandsanatomie ausgewaehlt.

Auditentscheidung:

```text
PARTIAL_MODEL_NEUTRAL_INFRASTRUCTURE_REUSABLE
S1PX_LIFECYCLE_EXPOSURE_AND_COMPARISON_SURFACE_INCOMPLETE
NEW_MODEL_NEUTRAL_EXPOSURE_ROLE_CONTRACT_REQUIRED
```

## Gepruefter Kernbestand

Der Audit trennt vier Bestandsklassen:

1. allgemeine technische Primitive;
2. modellneutrale, aber auf alte Profile begrenzte Orchestrierung;
3. geschlossene kandidaten- oder baselinegebundene Spezialbausteine;
4. historische Ergebnisse ohne neue operative Wirkung.

Zentrale gepruefte Implementierungen und Vertraege sind:

- S1-IV bis S1-JM fuer gemeinsame A/B/Gap-Exposition, Grenzrollen,
  Intervallhuelle und getrennte Digestrollen;
- `dynamic_substrate_dts1_common_interval_materializer.py` fuer reine
  Intervallmaterialisierung;
- `dynamic_substrate_dts1_private_baseline_adapters.py` fuer B1 bis B6;
- `dynamic_substrate_dts1_one_replica_orchestrator.py` fuer registrierte
  Einzelreplikate und getrennte Frischstarts;
- S1-IP und S1-JZ fuer Komponentenordnung, Informationsgrenzen und atomare
  Ausgabe;
- der bis C17 vorhandene, aber unvollstaendige 24-Fall-Baselinebestand;
- G2/D3-Retentionsbaseline, Capacity-Clamp-Audit und passive
  Checkpointvergleiche;
- `controlled_probe_baseline_comparison.py` als einfacher passiver
  Snapshot-Distanzvergleich.

Das Vorhandensein dieser Dateien aktiviert keinen geschlossenen Kandidaten.

## Direkt wiederverwendbare technische Primitive

Folgende Eigenschaften sind darstellungs- und kandidatenunabhaengig genug,
um in einem spaeteren S1-PX-Pruefstand erneut gebunden zu werden:

| Primitive | Wiederverwendbarer Umfang | Grenze |
|---|---|---|
| gemeinsame S/H-Grenzoperatoren | identische Feldvorzustaende vor einem Intervall oder Readout | konkrete alte A/B/Gap-Werte bleiben alte Fixtures |
| gemeinsame Intervallhuelle | Geometrie, Knotenfolge, Eingabe, Zeit, Reihenfolge und Checkpoint getrennt von Modellwahl | Huelle ist aktuell auf vier alte Profilformen registriert |
| getrennte Digestrollen | gemeinsame Exposition, privater Vorzustand, materialisierte Eingabe und Orchestrierungssteuerung bleiben getrennt | alte Digests duerfen nicht fuer neue Folgen umgedeutet werden |
| reine Materialisierung | kanonische Feld-, Rezeptor-, Zeit- und Geometrieuebergabe ohne Ergebniswissen | konkrete Registry ist DTS-benannt und fixturegebunden |
| private B1-B6-Adapter | Fixed Adapter, S2-Integrator, Local Leaky, Linear Coupled, F3 Full und CONST-V tragen eigenen Zustand | nur diese sechs Rollen und registrierte Geometrien sind abgedeckt |
| Frischstart und Carry | Sequenzen und Refinements starten getrennt; Carry bleibt innerhalb einer Replik | vorhandener Runner ist profil- und fallhart codiert |
| atomare Ausgaben | Fehler unterdruecken Teilresultate; Checkpoints und signed Komponenten sind digestgebunden | noch kein gemeinsamer S1-PX-Lebenszyklusbeleg |
| passiver Snapshotvergleich | S/H- und optionale Substratdistanzen ohne Modellfortschritt | prueft weder Historienaquivalenz noch Freigabe oder Nichtreduzierbarkeit |

Diese Primitive duerfen spaeter ueber neue, explizite Vertraege verwendet
werden. Ihre alten Klassen- oder Profilnamen sind keine fachliche
Kandidatenbindung.

## Nur eingeschraenkt wiederverwendbarer Bestand

### Alte Expositionsprofile

Die Profile P_IE, P_IH, P_IK und P_IN besitzen brauchbare Teilrollen:

| Profil | Brauchbarer Anteil | S1-PX-Luecke |
|---|---|---|
| P_IE | gemeinsame Exposition und getrennte private Intervention | Intervention setzt eine alte DTS-Anatomie extern; keine endogene Bildung |
| P_IH | wiederholte A-Exposition mit drei Checkpoints | nur Abschwaechungsteil; kein gemeinsamer Lebenszyklus |
| P_IK | A-B-A gegen A-Gap-A und gemeinsamer Probevorzustand | B und Gap sind nicht belastungsangepasst; nichtlokale Konkurrenzkontrolle fehlt |
| P_IN | identischer A-Gap-B-Aussenablauf | Unterschied entsteht durch DTS-internen Recovery-Schalter; keine endogene Freigabe |

Die Expositionsformen koennen als Entwurfsmuster dienen. Ihre konkreten
Fixtures, Sidecars und Ergebnisvektoren duerfen nicht in S1-PX uebernommen
werden.

### Sechs bestehende Baselineadapter

B1 bis B6 sind technisch implementiert und informationsisoliert. Sie decken
Fixed Adapter, S2-Integrator, drei F3-Varianten und CONST-V ab. Sie sind
deshalb eine belastbare Basis, aber keine vollstaendige S1-PX-Gegenmenge.

Es fehlen noch modellneutral angebundene Rollen fuer:

- reinen aktuellen Rezeptorkontakt;
- schnellen Nachhall und mehrere feste Zeitskalen als explizite
  Vergleichsarme;
- feste Verzoegerung, statische Rekurrenz und permanentes Gewicht;
- Replay als negative technische Kontrolle;
- globale Normalisierung und Saettigungsintegrator;
- Capacity-Clamp;
- DTS-1/T1 als geschlossene Dreirollenbaseline;
- die zustandsbehaftete Retentionsbaseline;
- G2/D3 ausschliesslich als geschlossene Rekonstruktionskontrolle.

Vorhandene Kerne duerfen fuer diese Rollen nur nach einem neuen statischen
Oberflaechen- und Informationsaudit angebunden werden. Fehlende Rollen duerfen
nicht still ausgelassen werden.

### Bestehende Comparatoren

Der einfache Snapshot-Comparator ist als numerisches Primitiv nutzbar. Der
S1-IP-Profilvergleich und der G2/D3-Checkpoint-Comparator sind dagegen an
bestimmte Vektorlaengen, Profile, Provenienzen und geschlossene Kandidaten
gebunden.

Keiner der vorhandenen Comparatoren kann derzeit gemeinsam pruefen:

- endogene Bildung;
- Wirkung nach Eingangs- und S/H-Angleichung;
- Abschwaechung;
- lokale gegen nichtlokale, belastungsangepasste Interferenz;
- direkte endliche Kapazitaetsbilanz;
- vollstaendige funktionale Freigabe;
- andere Wiederverwendung;
- einen unveraenderten Parametersatz pro Modell ueber alle Rollen.

Ein neuer Comparator darf diese Modelle spaeter nur passiv vergleichen. Er
darf weder Kandidat noch Baseline starten, konfigurieren oder reparieren.

## Nicht als neuer Forschungsnachweis wiederverwendbar

Ausgeschlossen bleiben:

- alle DTS-spezifischen Anatomie- und Recovery-Sidecars;
- direkte Free/Refraktaer- oder G2-C0/C1-Interventionen als endogene Bildung;
- `free -> bound -> blocked -> free` als neuer Kandidatenlebenszyklus;
- alte P_IK- und P_IN-Ergebnisvektoren ohne neue gemeinsame Exposition;
- die Retentionsbaseline als Kandidatenmechanik;
- der Capacity-Clamp-Kontrast als Funktionsresiduum;
- die C01-C17-Falloutputs als Nachweis fuer S1-PX;
- das Abarbeiten der fehlenden C18-C24-Faelle als neuer Forschungsfortschritt.

Der alte 24-Fall-Zweig bleibt unvollstaendiger technischer Referenzbestand.
S1-PY autorisiert weder seine Fortsetzung noch seine Matrixpublikation.

## S1-PX-Abdeckungsmatrix

| S1-PX-Pflichtrolle | Vorhandener Stand | Auditentscheidung |
|---|---|---|
| endogene Bildung | alte Geschichten und externe Sidecars vorhanden | fehlt |
| Eingangs- und S/H-Angleichung | Grenzoperatoren und Probegrenzen vorhanden | technisch wiederverwendbar |
| spaetere S-Fortsetzung | Feldcheckpoints und signed Komponenten vorhanden | technisch wiederverwendbar |
| Abschwaechung | P_IH-Topologie vorhanden | nur als Teilmuster wiederverwendbar |
| spezifische Interferenz | P_IK A-B-A/A-Gap-A vorhanden | belastungsangepasste Ortskontrolle fehlt |
| endliche lokale Kapazitaet | geschlossene Ledger und Clamp vorhanden | keine modellneutrale S1-PX-Expositionsrolle |
| funktionale Freigabe | P_IN-Recoverytoggle und geschlossene Ledger vorhanden | endogene Freigabegeschichte fehlt |
| andere Wiederverwendung | geschlossene DTS-Wiederbeanspruchung vorhanden | nicht kandidatenneutral gebunden |
| Kandidatenablation und Nullpfad | einzelne technische Nullkontrollen vorhanden | gemeinsamer S1-PX-Vertrag fehlt |
| vollstaendige Pflichtbaselines | sechs Adapter plus Spezialbestand vorhanden | mehrere Adapterrollen fehlen |
| gemeinsame Nichtreduzierbarkeit | profilspezifische Comparatoren vorhanden | Lebenszyklus-Comparator fehlt |

Damit ist das vorhandene Geruest substanziell, aber fuer eine faire
S1-PX-Entscheidung nicht vollstaendig.

## Verbindliche Luecken vor jeder Kandidatenwahl

Vor einer Kandidatenanatomie muessen mindestens folgende Luecken statisch
geschlossen werden:

1. eine einzige modellneutrale Rollenfolge fuer Bildung, Angleichung,
   Readout, Abschwaechung, Interferenz, Kapazitaet, Freigabe und andere
   Wiederverwendung;
2. eine lokale Konkurrenzgeschichte, eine gleich belastete nichtlokale
   Kontrolle und eine reine Zeit-/Gap-Kontrolle;
3. normale Feldgeschichte als einzige Bildungs- und Freigabeursache;
4. klare Trennung zwischen gemeinsamer Exposition und spaeterer privater
   Kandidatenanatomie;
5. ein global ueber alle Rollen unveraenderter Konfigurationsdigest pro
   Kandidat oder Baseline;
6. Adapterzulassung fuer alle noch fehlenden Pflichtbaselines;
7. ein passiver gemeinsamer Comparator mit Fail-Closed-Gateordnung;
8. direkte Bilanz-, Ablations-, Nullpfad- und Wiederverwendungsrollen.

S1-PY loest diese Luecken nicht durch neue Mechanik auf.

## Aussagegrenze

Der Audit zeigt, dass ein grosser Teil der technischen Versuchshygiene bereits
vorhanden ist. Er zeigt weder eine hypothetische MCM-Memory-Funktion noch die
Zulaessigkeit eines bestimmten Traegers. Die geschlossenen Kandidaten bleiben
geschlossen, und der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-PZ - statischer modellneutraler Expositionsrollenvertrag fuer den
        vollstaendigen S1-PX-Lebenszyklus
```

S1-PZ soll ausschliesslich Rollen und Kausalordnung der erforderlichen
Geschichten binden: Bildung, S/H-Angleichung, Readout, wiederholte Exposition,
lokale Konkurrenz, gleich belastete nichtlokale Kontrolle, Gap-Kontrolle,
Freigabe und andere Wiederverwendung. Es darf keine konkreten Werte, Dauern,
Digests, Fixture, Kandidatenzustandsrolle, Gleichung, Parameter,
Runtimeaenderung, Testausfuehrung oder Ergebnisentscheidung enthalten.
