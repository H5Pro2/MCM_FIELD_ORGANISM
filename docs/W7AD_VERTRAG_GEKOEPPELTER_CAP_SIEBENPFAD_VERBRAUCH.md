# W7-AD: Vertrag fuer gekoppelten CAP-Siebenpfad-Verbrauch

## Entscheidung

`COUPLED_CAP_SEVEN_PATH_CONSUMPTION_CONTRACT_BOUND`

W7-AD bindet statisch den ersten Verbrauch des W7-Y-Siebenpfadplans durch
genau den vorhandenen kapazitaetsbegrenzten CAP-Arm. Der Vertrag fuehrt kein
Segment aus, erzeugt keinen Modellwert und startet keine Matrix.

## 1. Exklusive Modellgrenze

Der spaetere Verbraucher darf ausschliesslich den W7-M-Modellarm `cap`
verwenden:

- aktiver Substratarm `w7m.cap` mit `eta = 1.0`, `kappa = 0.5` und
  `lambda_sm = 1.0`;
- unveraenderlicher W7-K-Runtimevertrag
  `w7k.capacity-limited-shared-mcm-field.v1`;
- `C_site = 2/84`, aus dem unveraenderten W7-M-Adapter;
- Reaktionszeit `1.0`, Nachhallzeitkonstante `0.5`, keine Dissipation und
  zunaechst Refinement `1`;
- genau die Geometrie, Neuronenreihenfolge und Kanteninventarbindung des
  W7-M-Anfangsfeldes.

P0, LEAK, SAT und NORM bleiben unveraenderliche Gegenbaselines. F3, LIN,
CONST-V, MOB, ETA0, KAPPA0, SIGN sowie alle W7-M-Interventionen sind in
diesem ersten Verbraucher gesperrt. Kein Baseline- oder Observerwert darf
CAP initialisieren, veraendern oder fortsetzen.

## 2. Unveraenderliche Eingangsbindung

Vor jeder spaeteren Verarbeitung wird genau einmal gebunden:

- ein frischer W7-M-Adapter und sein Matrix- und Regionsdigest;
- dessen CAP-Anfangsfeld, Runtimevertrag und Konfigurationsdigest;
- eine passende W7-W-Quellenfamilie samt Autorisierungsdigest;
- der unveraenderte W7-Y-Plan und sein Gesamtplandigest;
- der unveraenderte W7-AA-P0-Gesamtverbrauchsdigest;
- der unveraenderte W7-AC-Observer-Gesamtverbrauchsdigest;
- Uhr `organism.mcm_f3_k2b`, Tickrate `1_000_000` und Pfadreihenfolge
  `AB`, `AG`, `BA`, `BG`, `UA`, `UB`, `UG`.

W7-AA und W7-AC werden nur digestgebunden. Der CAP-Verbrauch darf sie nicht
neu ausfuehren und keine ihrer Zustands- oder Messrollen uebernehmen.

## 3. CAP-Startrollen

### 3.1 Kontaktpfade

AB, AG, BA und BG erhalten je eine eigene tiefe Kopie des frischen
W7-M-CAP-Anfangsfeldes bei Tick 0. Das Feld besitzt ein M-Substrat, aber noch
keine abgeschlossene Distribution und deshalb keine Fortsetzungsbindung.

Jede Kopie verarbeitet genau einmal den in W7-Y gebundenen A- oder
B-Praefix bis Tick 4. Das Ergebnis ist ein unteilbares Zustandspaar aus:

1. vollstaendig gekoppeltem `SharedMCMField` mit S, H und M;
2. der vom W7-K-Adapter erzeugten `MCMCapacityLimitedContinuationBinding`.

### 3.2 U-Pfade

UA, UB und UG erhalten je eine eigene tiefe Kopie desselben frischen
W7-M-CAP-Anfangsfeldes, logisch bei Tick 4. Sie verarbeiten davor keine
Rezeptorsequenz. S und H bleiben im unveraenderten Anfangswert, M bleibt
homogen mit derselben Gesamtmasse, Kapazitaet und Kantenbindung.

Da ein initiales Feld laut W7-K keine Fortsetzungsbindung konsumieren darf,
besitzt auch der U-Checkpoint 0 keine kuenstlich erzeugte Bindung. Die erste
Fortsetzung 4 bis 5 wird als Initialadvance auf diesem Feld ausgefuehrt. U
ist weder Nullkontakt noch Gap, Reset oder simuliertes Praefix.

## 4. Hauptfortsetzung

Nach Checkpoint 0 verarbeitet jeder Pfad genau die vier W7-Y-Hauptsegmente:

```text
4-5 -> 5-6 -> 6-7 -> 7-8
```

Fuer Kontaktpfade muss jede Fortsetzung das vollstaendige vorherige
Feldobjekt und exakt dessen Fortsetzungsbindung konsumieren. Fuer U-Pfade
gilt dies ab dem Ergebnis des ersten Initialadvance. Jede neue Runtimeantwort
liefert das alleinige Zustandspaar fuer das naechste Segment desselben
Pfads.

Pfadwechsel, Neubindung aus Metadaten, Bindung an einen anderen Snapshot,
Konfigurationswechsel und Fortsetzung aus P0-, Observer- oder Probeausgaben
sind unzulaessig.

## 5. CAP-Checkpoints

Checkpoint 0 wird nach dem Praefix oder direkt auf dem unveraenderten
U-Anfangsfeld bei Tick 4 gebunden. Checkpoint 1 bis 4 folgen jeweils dem
zugeordneten Hauptsegment bei Tick 5 bis 8.

Ein Checkpointresultat bindet mindestens:

- W7-Y-Pfadplan-, Checkpoint- und Quellsegmentdigest;
- Pfad, Checkpointnummer und Tick;
- Hauptfeldsnapshotdigest;
- vorhandenen Fortsetzungsbindungsdigest oder fuer U/Checkpoint 0 die
  explizite Rolle `initial-no-binding`;
- Runtime-Konfigurationsdigest;
- Substratarm, Gesamtmasse, `C_site` und Kanteninventardigest;
- Digest der objektgetrennten Probeausgangskopie;
- kanonischen CAP-Checkpointdigest.

Der Checkpoint misst oder veraendert das Feld nicht. Regionale W7-M-Ledger
duerfen spaeter nur als passive, getrennte Messrollen erzeugt werden.

## 6. Isolierte CAP-Probeaeste

An jedem der 35 Checkpoints wird der vollstaendige gekoppelte Hauptzustand
tief kopiert. Die Kopie umfasst S, H, M, Substratarm, Kanteninventar,
Zeitgrenzen, letzte Distribution und alle weiteren fortsetzungsrelevanten
Feldteile.

Ist am Checkpoint eine Fortsetzungsbindung vorhanden, wird fuer die Kopie
eine neue wertgleiche Bindung aus ihrem eigenen Snapshotdigest und demselben
Konfigurationsdigest erzeugt. An U/Checkpoint 0 bleibt die Probe ebenfalls
ein initiales Feld ohne Bindung.

Am Kopierpunkt muessen Haupt- und Probezweig digestgleich, aber
objektgetrennt sein. Die Probe verarbeitet ausschliesslich das in W7-Y
gebundene Probesegment und gibt Feld, Bindung, Diagnose oder Messwert nie an
Hauptpfad, andere Probe, P0 oder Observer zurueck.

## 7. Erhaltungs- und Kontinuitaetskontrollen

Vor und nach jedem Haupt- und Probesegment sind mindestens zu pruefen:

- Gesamtmasse M entspricht unveraendert `1.0` innerhalb der bestehenden
  numerischen Toleranz;
- jede lokale Masse liegt zwischen `0` und `C_site`;
- maximaler Kapazitaetsueberschuss bleibt `0.0`;
- Geometrie, Neuronenreihenfolge und Kanteninventardigest bleiben gleich;
- Substratarm und Runtime-Konfigurationsdigest bleiben gleich;
- vorhandene Fortsetzungsbindung passt exakt zum Eingabefeldsnapshot;
- ausgegebene Fortsetzungsbindung passt exakt zum Ausgabefeldsnapshot;
- Segmentstart entspricht dem vorherigen Haupt- oder Probeendtakt;
- Quellen-, Intervall- und W7-W-Autorisierungsbindung stimmen mit W7-Y.

Eine Verletzung stoppt den Verbraucher vor der naechsten Fortsetzung.

## 8. Rueckwirkungsgegenkontrollen

Eine spaetere Implementierung muss mindestens folgende technische
Gegenkontrollen binden:

1. **Haupt-/Probereihenfolge:** An AB/Checkpoint 0 liefern Probe zuerst und
   Hauptsegment zuerst je Rolle dieselben Feld-, Bindungs- und
   Produktionsdigests.
2. **Pfadreihenfolge:** Kanonische und umgekehrte Verarbeitung liefern je
   Pfad denselben CAP-Verbrauchsdigest.
3. **Checkpointpassivitaet:** Checkpoint und Probekopie veraendern weder
   Hauptfeldsnapshot noch Hauptbindung.
4. **Baselinepassivitaet:** W7-AA- und W7-AC-Gesamtdigests bleiben vor und
   nach CAP-Verarbeitung unveraendert.

Diese Kontrollen pruefen nur technische Isolation und Determinismus. Sie
sind kein Feldfunktions- oder Memorybefund.

## 9. Ergebnis- und Digestrollen

Ein spaeteres CAP-Pfadergebnis bindet mindestens:

- W7-Y-Pfadplandigest und CAP-Modellbindung;
- Anfangsfeld- und Anfangsbindungsrolle;
- geordnete Hauptproduktions-, Feld- und Bindungsdigests;
- fuenf Checkpointdigests;
- fuenf Probeproduktions-, Feld- und Bindungsdigests;
- terminalen Hauptfeld- und Bindungsdigest bei Tick 8;
- Erhaltungskontrollen und kanonischen `cap_path_consumption_digest`.

Der globale `cap_seven_path_consumption_digest` bindet die sieben
Pfadergebnisse in W7-Y-Reihenfolge und die Gegenkontrollen. Er enthaelt
keine Pfadrangfolge, Schwellenentscheidung, Interpretation oder
Rueckschreibung.

## 10. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- genau sieben getrennte CAP-Hauptketten;
- vier Kontaktstarts bei Tick 0 und drei unexponierte U-Starts bei Tick 4;
- exakt 32 Hauptproduktionen und 35 objektgetrennte Probeproduktionen;
- tiefe Kopie des vollstaendigen gekoppelten Feldes an jedem Checkpoint;
- korrekte Bindungsabwesenheit nur bei initialen Feldern;
- snapshot- und konfigurationsgenaue Bindung jeder abgeschlossenen Kopie;
- lueckenlose Haupt- und Probezeitordnung bis Tick 8 beziehungsweise 9;
- alle Kontrollen aus Abschnitt 7 und 8;
- deterministische Pfad- und Gesamtverbrauchsdigests;
- unveraenderte W7-M-, W7-W-, W7-Y-, W7-AA- und W7-AC-Digests;
- fehlende Exporte aus Paketwurzel und `current_api`;
- keine Reports, Browserstarts oder Laufmarker.

## 11. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- ein CAP-Feld kein M-Substrat besitzt oder einen anderen Modellarm traegt;
- ein abgeschlossenes Feld ohne passende Fortsetzungsbindung fortgesetzt
  wird;
- U ein Praefix, eine Nullsequenz oder eine kuenstliche Bindung erhaelt;
- Haupt- und Probeast Feldobjekte oder veraenderbare Unterobjekte teilen;
- ein Probeendzustand Hauptpfad oder weitere Probe fortsetzt;
- M neutralisiert, transplantiert, normalisiert oder durch eine Intervention
  ersetzt wird;
- Kapazitaet, Gesamtmasse, Geometrie oder Kanteninventar abweichen;
- P0- oder Observerwerte in CAP einfliessen;
- Pfade gekreuzt, bewertet oder nach Ergebnis veraendert werden;
- ein Report oder Forschungslauf erzeugt wird.

## 12. Aussagegrenze

W7-AD ist ausschliesslich ein statischer Verbrauchsvertrag. Es wurde kein
CAP-Pfad und keine Probe ausgefuehrt. Auch eine spaetere vertragskonforme
Ausfuehrung waere zunaechst nur technische Zustandsevidenz. Daraus folgen
keine Feldfunktion, kein Memory, keine Feldzeit, Organisation, Topologie,
Semantik, Selbstregulation oder KI.

## 13. Verwendete Quellen

- `docs/W7K_IMPLEMENTIERUNG_KAPAZITAETSBEGRENZTER_SHAREDMCMFIELD_ADAPTER.md`
- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md`
- `docs/W7Y_IMPLEMENTIERUNG_NICHTAUSFUEHRENDER_SIEBENPFAD_PLANADAPTER.md`
- `docs/W7AA_IMPLEMENTIERUNG_P0_ONLY_SIEBENPFAD_VERBRAUCHER.md`
- `docs/W7AC_IMPLEMENTIERUNG_OBSERVER_SIEBENPFAD_VERBRAUCHER.md`
- `mcm_field_organism/capacity_limited_mcm_f3_runtime.py`
- `mcm_field_organism/w7m_capacity_function_matrix.py`
- `mcm_field_organism/w7y_seven_path_source_plan.py`

## 14. Naechster Schritt

W7-AE darf einen isolierten CAP-Siebenpfad-Verbraucher und seine
Vertragstests implementieren. Er darf nur den W7-M-CAP-Arm auf dem
unveraenderten W7-Y-Plan im Arbeitsspeicher fortsetzen und W7-AA/W7-AC nur
als unveraenderliche Digestgegenbaselines binden. Keine Intervention,
Pfadbewertung, Browsernutzung, kein Report oder Forschungslauf.
