# S1-TR: Statischer Nachabnahme-, Infrastruktur- und Kandidatenzulassungsaudit

## Auftrag und Grenze

S1-TR trennt die mit S1-TQ technisch abgenommene Kandidatenhuelle von einer
noch nicht vorhandenen Kandidatenmechanik. Der Audit waehlt keinen Kandidaten,
bindet keine Gleichung, Parameter oder Werte, aendert keinen Code und fuehrt
keinen Test oder Feldlauf aus.

## Abgenommene technische Infrastruktur

| Bereich | Abgesicherter Stand | Grenze |
|---|---|---|
| primaerer Feldkern | kontrollierte Rezeptor-, Dock-, S/H-, Snapshot- und Fortsetzungskette | keine neue Substratfunktion |
| Expositionsachse | 17 F/T/I/C/R/U-Plaene und 40 Feldcheckpoints | keine Kandidatenprognose |
| Baselineatlas | 14 Profile, 322 Kontraste und 91 Profilpaare | unveraenderte Referenz, kein Kandidatenbefund |
| Kandidatenhuelle | 17 Plaene, 40 Checkpoints, 127 Intervalle und 320 Feldkomponenten | passives Strukturschema |
| interne Belegrollen | Zustand, Bilanz, Ablation, Nullpfad, Release und Reuse | Rollenbeleg ohne fachliche Kandidatenanatomie |
| Fail-Closed-Validator | 32 priorisierte Fehlerklassen ohne Teilresultat | keine Funktionsentscheidung |
| synthetische Abnahme | 24 von 24 Methoden im einzigen S1-TQ-Lauf bestanden | nur technische Schemaevidenz |

Die neue Huelle wird weder durch `current_api` noch durch Root-Lazy-Exports
angeboten und von keinem anderen Produktionsmodul importiert. Sie ist damit
korrekt als getrennte Forschungsinfrastruktur vorhanden, nicht als aktive
Feldfunktion.

## Verbindlich geschlossene Kandidatenquellen

Folgende Bestaende liefern keine neue Zulassung:

| Bestand | Entscheidung |
|---|---|
| Frozen-E1 und Fixed-Adapter-Varianten | geschlossen oder Gegenbaseline |
| F3, CONST-V, Leaky und Integrator | Gegenbaselines, keine neue Kandidatenrolle |
| DTS-1/T1 mit `free -> bound -> blocked -> free` | technische Dreirollenbaseline |
| Capacity-Clamp | erklaert statische Free/Blocked-Kapazitaetswirkung |
| G2/D3 | Kandidatenzweig mit S1-PP beendet; Infrastruktur bleibt erhalten |
| Replay und Retentionsarme | Referenzbaselines ohne neue lokale Ursache |
| allgemeine Koharenz-, Ordnungs- oder Biocomputing-Analogie | Forschungsanregung, aber keine operative Gegenprognose |

Umbenennung, neue Parametrisierung oder Kombination dieser geschlossenen
Rollen oeffnet keinen neuen Kandidatenzweig.

## Noch fehlende kandidatenspezifische Vorregistrierungen

Vor einer spaeteren Kandidatenimplementierung fehlen weiterhin gemeinsam:

1. **Eigene Funktionsprognose:** ein vorab benanntes Feldereignis, das nicht
   aus Fixed Adapter, Leaky, Integrator, F3/CONST-V, schnellem H, Replay,
   Retention, DTS-1/T1, Capacity-Clamp oder G2/D3 rekonstruierbar ist.
2. **Endogene Erreichbarkeit:** der unterschiedliche innere Zustand muss nur
   aus normaler Rezeptor- und Feldgeschichte entstehen, ohne Armziel, Label,
   Ergebniszugriff, Reset oder Sidecar.
3. **Eigenstaendige Anatomie:** lokale Zustands- und Ressourcenrollen duerfen
   nicht nur `free/bound/blocked` oder `bound_unconfigured/bound_configured`
   umbenennen.
4. **Konjugierte Kopplung:** Feld-zu-Traeger und Traeger-zu-Feld muessen aus
   derselben lokalen Wechselwirkung folgen.
5. **Endliche Bilanz:** Rollenachse, lokale Reichweite, Kapazitaet, erlaubte
   Zu-/Abfluesse, Dissipation, Restregel und ungueltige Zustaende muessen vor
   jeder Dynamik feststehen.
6. **Falsifikationsintervention:** bei angeglichenem S/H und identischer Probe
   muss genau die kandidateninterne Ursache isolierbar veraendert werden.
7. **Lebenszyklusprognose:** Bildung, spaetere Wirkung, Abschwaechung,
   Interferenz, Freigabe und erneute Beanspruchung muessen durch einen
   Parametersatz gemeinsam vorhergesagt werden.
8. **Faire Gegenbaselines:** alle zustandsbehafteten Baselines muessen dieselbe
   A/B/Gap-Vorgeschichte und dieselben zulaessigen Interventionen erhalten.
9. **Producer- und Comparatorgrenze:** erst nach 1 bis 8 duerfen ein realer
   Huellenproducer und ein passiver Kandidat-gegen-Atlas-Comparator gebunden
   werden.

Die technisch abgenommene Huelle kann diese Belege spaeter tragen und
validieren. Sie kann die fehlende fachliche Ursache nicht selbst erzeugen.

## Zulassungsentscheidung

Kein offener Projektbestand erfuellt derzeit Punkt 1 und Punkt 3 gemeinsam.
Insbesondere ist keine nicht-DTS-reduzierbare und nicht-Clamp-reduzierbare
Gegenprognose vorregistriert. Eine Kandidatenmechanik waehrend dieses Audits
zu erfinden oder einen geschlossenen Zweig umzubenennen waere methodisch
ungueltig.

Damit wird kein neuer Kandidatenzweig geoeffnet. Die Forschungsrichtung fuer
eine spaetere technische MCM-Memory bleibt als Entwicklungsrichtung offen,
aber an dieser Stelle pausiert, bis eine eigenstaendige falsifizierbare
Gegenprognose fachlich vorliegt.

## Verbindliche Entscheidung

```text
S1_TR_CANDIDATE_ENVELOPE_ACCEPTED_AS_INACTIVE_RESEARCH_INFRASTRUCTURE
NO_ADMISSIBLE_NON_DTS_NON_CLAMP_COUNTERPREDICTION_PRESENT
CANDIDATE_RESEARCH_BRANCH_PAUSED_WITHOUT_REOPENING_CLOSED_BRANCHES
PRIMARY_MCM_FIELD_CORE_REMAINS_ACTIVE_AND_UNCHANGED
```

## Genau ein naechster Schritt

Der einzige zulaessige Anschluss ist S1-TS als statischer Konsolidierungs-
und Driftgrenzenvertrag. Er soll:

- Produktions- und Testdigest der Kandidatenhuelle einfrieren;
- die Rolle `INACTIVE_RESEARCH_INFRASTRUCTURE` binden;
- fehlende Root- und `current_api`-Exporte als gewollte Grenze festhalten;
- Importe aus aktivem Feldkern, Runnern und Comparatoren verbieten;
- die neun vorstehenden Zulassungsvoraussetzungen als Wiedereroeffnungstor
  dokumentieren.

S1-TS darf noch keine Inventardatei aendern, keinen Export ergaenzen, keine
Kandidatenmechanik auswaehlen und keinen Test ausfuehren.
