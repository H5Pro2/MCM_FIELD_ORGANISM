# W7-AM: Vertrag fuer den additiven R1/R2/R4-Aufloesungscontainer

## Entscheidung

`ADDITIVE_CAP_R1_R2_R4_RESOLUTION_CONTAINER_CONTRACT_BOUND`

W7-AM bindet statisch den kleinsten zulaessigen Container fuer drei
voneinander getrennte CAP-Aufloesungsketten. Bestehende W7-AE-, W7-AG- und
W7-AK-Schemata und Digests bleiben unveraendert. Es wurde keine
Verfeinerung ausgefuehrt und kein Messwert verglichen.

## 1. Aufloesungsinventar

Der Container besitzt genau drei geordnete Rollen:

```text
R1 -> refinement = 1
R2 -> refinement = 2
R4 -> refinement = 4
```

Andere Faktoren sind in dieser W7-Linie verboten. Die Rollen bezeichnen nur
die Anzahl numerischer SSPRK-Substeps relativ zur Basisschrittzahl. Sie sind
kein Feldzustand, keine Weltphase und keine Organismuszeit.

## 2. Unveraenderliche gemeinsame Bindungen

Alle drei Rollen verwenden exakt dieselben:

- W7-M-Matrix, Regionen und homogenes CAP-Anfangsfeld;
- W7-K-Gleichung und Kapazitaetsvertrag;
- W7-W-Autorisierung und W7-Y-Siebenpfadplan;
- Quellen-, Segment-, Checkpoint- und Probeintervalle;
- Rezeptorereignisse, Neuronenreihenfolge, Uhr und Tickrate;
- Parameter `lambda_sm = 1.0`, `kappa = 0.5`, `eta = 1.0`;
- Fast-Field-Parameter und fehlende Dissipation;
- W7-P-Messdefinitionen;
- W7-AI-P0-Gesamtreferenzdigest
  `8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5`.

Nur der technische Integrationsfaktor darf sich unterscheiden.

## 3. Drei unabhaengige CAP-Ketten

Jede Aufloesung beginnt aus einer eigenen tiefen Kopie des gleichen
W7-M-Anfangsfeldes. Getrennt materialisiert werden je Rolle:

- sieben CAP-Hauptpfade;
- 32 CAP-Hauptproduktionen;
- 35 technische CAP-Probeaeste;
- 35 getrennte angeglichene CAP-Messaeste;
- 3.185 S/H/M-Messsamples;
- 35 CAP/P0-Rohpaare mit 3.185 S/H-Residualsamples.

R2 und R4 duerfen weder R1 noch einander fortsetzen. Kein Zustand, Feld,
Substrat, Continuation Binding oder Sampleobjekt wird zwischen
Aufloesungen geteilt.

## 4. R1-Kompatibilitaetsrolle

R1 ist keine neue Modellvariante. Der explizit mit `refinement = 1`
durchgeleitete Pfad muss bitgleich reproduzieren:

- W7-AE-Gesamtdigest
  `b70a4b4563bb73d50685d1a8475376f0b00377d72369c030027f44f2725af013`;
- W7-AG-Gesamtdigest
  `898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8`;
- W7-AK-Gesamtdigest
  `ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3`.

Jede Abweichung ist ein technischer Stopp. Die kanonischen R1-Objekte duerfen
nicht durch einen neuen Containerdigest ersetzt werden; der Container
referenziert sie additiv.

## 5. Private Refinementdurchleitung

Eine spaetere Implementierung darf nur private optionale Keywordrollen
ergaenzen:

```text
W7-AE _produce(..., _refinement=1)
W7-AE consume(..., _refinement=1)
W7-AG compose(..., _refinement=1)
```

Die Defaultwirkung bleibt exakt R1. Vor jedem Runtimeaufruf wird der Faktor
auf die Menge `{1, 2, 4}` begrenzt und unveraendert an die vorhandene CAP-
Transientruntime gereicht.

Oeffentliche Funktionsnamen, Positionsargumente und Exporte bleiben
unveraendert.

## 6. Additive Integrationszeugen

Die W7-AE-Produktion speichert derzeit nur reduzierte
`MCMCapacityLimitedRuntimeDiagnostics`. Diese enthalten nicht den
Integrationsfaktor oder die SSPRK-Substepzahl. Bestehende Ergebnisschemata
duerfen deshalb nicht erweitert werden.

Stattdessen entsteht pro CAP-Produktion ein externer unveraenderlicher
Integrationszeuge mit mindestens:

- Aufloesungsrolle und `refinement`;
- Pfad, Segmentdigest und Intervall;
- bestehendem W7-AE-Produktionsdigest;
- `method_id = "ssprk33"`;
- `substep_count`;
- `safe_step_seconds` und `maximum_step_seconds`;
- kanonischem Zeugendigest.

Je Aufloesung muessen genau 67 W7-AE-Zeugen vorliegen: 32 fuer Haupt- und 35
fuer technische Probeproduktionen.

## 7. Additive Messzeugen

Jeder der 35 W7-AG-Messaeste erhaelt einen getrennten Messzeugen. Er bindet:

- Aufloesungsrolle und `refinement`;
- W7-Y-Checkpointdigest;
- W7-AG-Messresultatdigest;
- zugehoerigen W7-AE-CAP-Checkpointdigest;
- Integrationsdiagnostik der Messproduktion;
- unveraenderte geordnete Sampleticks;
- kanonischen Messzeugendigest.

Damit liegen je Aufloesung insgesamt 102 Zeugen vor. Zeugen sind passive
Metadaten und werden nicht in Feld, Substrat oder Fortsetzung
zurueckgeschrieben.

## 8. Aufloesungsgebundene CAP/P0-Paare

R1 verwendet die bestehenden W7-AK-Paare. R2 und R4 erzeugen additive
Paarcontainer nach exakt denselben W7-AJ-Residualdefinitionen.

Jeder R2/R4-Paarcontainer bindet:

- seine Aufloesungsrolle;
- den zugehoerigen CAP-Messuebergabedigest;
- denselben unveraenderten W7-AI-P0-Digest;
- genau 35 Paarresultate in W7-Y-Reihenfolge;
- `evaluated = false`;
- einen eigenen aufloesungsgebundenen Digest.

W7-AK selbst und seine hart gebundenen kanonischen Eingangsdigests werden
nicht geaendert. Seine private Paarbildungslogik darf nur dann wiederverwendet
werden, wenn W7-AK-Ergebnisobjekte und Digests bitgleich bleiben.

## 9. Aufloesungsresultat

Ein `CAPResolutionResult` bindet mindestens:

- Rollenkennung R1, R2 oder R4;
- `refinement`;
- W7-M-, W7-W- und W7-Y-Digests;
- W7-AE-Gesamtergebnisdigest;
- 67 geordnete Produktionszeugendigests;
- W7-AG-Gesamtmessdigest;
- 35 geordnete Messzeugendigests;
- aufloesungsgebundenen CAP/P0-Paarcontainerdigest;
- gemeinsamen W7-AI-P0-Digest;
- Invarianten- und Reihenfolgegegenkontrolldigests;
- `evaluated = false`;
- kanonischen Aufloesungsresultatdigest.

## 10. Gesamtcontainer

Der globale Container bindet genau R1, R2 und R4 in dieser Reihenfolge. Er
enthaelt:

- drei Aufloesungsresultatdigests;
- einen R1-Kompatibilitaetsdigest;
- einen Anfangszustandstrennungsdigest;
- einen gemeinsamen Quellen- und Plandigest;
- den einmaligen W7-AI-P0-Digest;
- `convergence_compared = false`;
- `effect_floor_ready = false`;
- einen kanonischen Gesamtcontainerdigest.

Er enthaelt keine R1/R2-, R2/R4- oder Pfaddistanzen.

## 11. P0-Wiederverwendung

W7-AI wird vor dem Container genau einmal materialisiert. Alle drei
Aufloesungsrollen referenzieren dasselbe unveraenderliche P0-Ergebnisobjekt
und denselben Digest.

Erlaubt ist das Lesen derselben P0-Samples. Verboten sind:

- drei P0-Neuausfuehrungen;
- nominale P0-R1/R2/R4-Kopien;
- eine P0-Refinementkennung;
- Veraenderung oder Rueckschreibung in P0.

## 12. Pflichtgegenkontrollen

Die Implementierung muss mindestens pruefen:

1. **R1-Bitgleichheit:** alle drei Digests aus Abschnitt 4 stimmen exakt.
2. **Aufloesungszeuge:** jeder der 306 Zeugen bindet den erwarteten Faktor.
3. **Substepordnung:** fuer dasselbe Segment gilt
   `substeps_R1 < substeps_R2 < substeps_R4`.
4. **Starttrennung:** R1/R2/R4 starten wertgleich, aber mit getrennten
   Feld-, Layer-, Dock-, Substrat- und Bindingobjekten.
5. **Tickgleichheit:** alle Haupt-, Probe- und Messintervalle sowie alle
   Sampleticks sind aufloesungsuebergreifend identisch.
6. **Quellgleichheit:** Segment-, Quell-, Plan- und Autorisierungsdigests
   bleiben gleich.
7. **Invarianten:** Gesamtmasse, Ortskapazitaet und Geometrie bleiben je
   Aufloesung geschlossen.
8. **Determinismus:** Wiederholung derselben Aufloesung liefert denselben
   Aufloesungsdigest.
9. **Rollenreihenfolge:** kanonische und umgekehrte Verarbeitung aendert kein
   rollenbezogenes Resultat.
10. **P0-Einmaligkeit:** alle Rollen referenzieren dasselbe P0-Objekt und
    denselben Digest.
11. **Eingangspassivitaet:** kanonische W7-AE/AG/AI/AK-Digests bleiben
    unveraendert.

## 13. Noch gesperrte Konvergenzauswertung

Der Container materialisiert nur die drei Aufloesungen. Weiterhin gesperrt
sind:

- R1/R2- und R2/R4-Distanzen;
- Monotonie- oder Konvergenzentscheidungen;
- `epsilon_num` und `effect_floor`;
- Pfad- und Lebenszyklusprofile;
- regionale M-Freisetzungs- oder Beanspruchungsentscheidungen;
- Neutralisierungs-, Transplantations- oder weitere Modellarme;
- Forschungsaussagen jeder Art.

Diese Auswertung benoetigt einen weiteren statischen Vertrag.

## 14. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein bestehendes W7-AE/AG/AK-Schema oder ein kanonischer Digest wechselt;
- ein Zeuge nicht die tatsaechliche Basisdiagnostik der Produktion bindet;
- R2 oder R4 aus einer anderen Aufloesung fortgesetzt wird;
- Zeugen als Feldzustand persistiert werden;
- SSPRK-Substeps neue Mess- oder Rezeptorticks erzeugen;
- P0 mehrfach ausgefuehrt oder kuenstlich verfeinert wird;
- eine Aufloesung andere Quellen, Parameter oder Gleichungen erhaelt;
- Konvergenzabstaende oder Schwellen bereits berechnet werden;
- ein Browser, Runner, Report oder Forschungslauf gestartet wird.

## 15. Aussagegrenze

W7-AM ist ein statischer Containervertrag. Es wurde keine R2- oder R4-Kette
ausgefuehrt und keine Konvergenz gemessen. Daraus folgen keine Feldfunktion,
Ressourcenfreisetzung, Wiederverwendung, Memory, Feldzeit, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## 16. Verwendete Quellen

- `docs/W7AL_AUDIT_DURCHGAENGIGER_2N_4N_VERFEINERUNGSPFAD.md`
- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `mcm_field_organism/mcm_f3_runtime.py`
- `mcm_field_organism/capacity_limited_mcm_f3_runtime.py`
- `mcm_field_organism/w7ae_cap_seven_path_consumer.py`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`
- `mcm_field_organism/w7ai_p0_zero_start_measurement_reference.py`
- `mcm_field_organism/w7ak_cap_p0_raw_contrast_compositor.py`

## 17. Naechster Schritt

W7-AN darf den privaten Refinementdurchlass, die additiven Produktions- und
Messzeugen sowie den R1/R2/R4-Gesamtcontainer mit Vertragstests
implementieren. Noch keine Konvergenzdistanz, Schwellenberechnung,
Auswertung, kein Browser, Report oder Forschungslauf.
