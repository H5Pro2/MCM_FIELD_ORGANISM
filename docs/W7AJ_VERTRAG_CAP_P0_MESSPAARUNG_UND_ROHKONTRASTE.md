# W7-AJ: Vertrag fuer CAP/P0-Messpaarung und Rohkontraste

## Entscheidung

`CAP_P0_SAMPLE_ALIGNED_RAW_CONTRAST_CONTRACT_BOUND`

W7-AJ bindet statisch, wie die 35 vorhandenen W7-AG-CAP-Messungen und die
35 vorhandenen W7-AI-P0-Messreferenzen spaeter gepaart und ohne Deutung
voneinander abgezogen werden duerfen. Der Vertrag berechnet noch keinen Wert,
startet keinen Browser oder Forschungslauf und erzeugt keinen Report.

## 1. Forschungsnahe technische Frage

Wie gross ist fuer dieselbe W7-Y-Probe, denselben Pfad, denselben Checkpoint,
dieselben Abschlussgrenzen und dieselbe S/H-Nullausgangslage der rohe
sampleweise S/H-Abstand zwischen CAP und substratfreiem P0?

Der Abstand zeigt zunaechst nur eine technische Abweichung zweier offen
implementierter Modelle. Er ist weder eine Funktionsentscheidung noch ein
Nachweis von Memory, Feldzeit oder Organisation.

## 2. Unveraenderliche Eingangsbindung

Eine spaetere W7-AK-Komposition muss gemeinsam binden:

- W7-Y-Gesamtplan- und 35 Checkpointdigests;
- W7-AG-Gesamtmessuebergabedigest
  `898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8`;
- W7-AI-Gesamtmessreferenzdigest
  `8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5`;
- genau die Pfade `AB`, `AG`, `BA`, `BG`, `UA`, `UB`, `UG`;
- genau die Checkpoints 0 bis 4;
- die unveraenderte Neuronenreihenfolge, Uhr und Tickrate;
- die vorhandenen W7-P-Messdefinitionen.

W7-AG, W7-AI und ihre Eingangsergebnisse bleiben unveraendert. W7-AK darf
keinen Messzweig erneut ausfuehren.

## 3. Eindeutige 35-Paar-Zuordnung

Genau ein CAP-Resultat und genau eine P0-Referenz werden nur dann gepaart,
wenn gemeinsam gilt:

```text
cap.path_id                  = p0.path_id
cap.checkpoint               = p0.checkpoint
cap.plan_checkpoint_digest   = p0.plan_checkpoint_digest
cap.probe_observation_ticks  = p0.probe_observation_ticks
len(cap.samples)             = len(p0.samples)
```

Zusaetzlich muessen an jedem Sampleindex Tick, S-Geometrie und H-Geometrie
uebereinstimmen. Die Rollen werden in kanonischer W7-Y-Reihenfolge gebunden.
Fehlende, doppelte oder ausserhalb dieser Zuordnung liegende Resultate sind
ein technischer Stopp.

## 4. Vergleichbare und nicht vergleichbare Anteile

Vergleichbar sind ausschliesslich:

- S gegen S am gleichen Tick und Feldort;
- H gegen H am gleichen Tick und Feldort;
- die daraus gebildete gemeinsame diskrete S/H-Residualnorm;
- die bereits getrennt berechneten W7-P-S/H-Normen als Auditwerte.

Nicht vergleichbar sind:

- CAP-M gegen einen P0-Wert, da P0 kein M besitzt;
- regionale M- oder Freikapazitaetsledger gegen P0;
- CAP-Zustandsdigests gegen P0-Zustandsdigests als numerische Distanz;
- W7-P-Feldwerte gegen LEAK-, SAT- oder NORM-Observerwerte;
- diskrete Trajektorien-L2-Werte gegen kontinuierliche Zeitintegrale oder
  Feldzeit.

## 5. Primaere sampleweise Rohkontraste

Fuer jedes gepaarte Sample j und jeden Feldort i gelten nur die gerichteten
Rohresiduen:

```text
r_S(j,i) = S_CAP(j,i) - S_P0(j,i)
r_H(j,i) = H_CAP(j,i) - H_P0(j,i)
```

Aus ihnen werden genau drei nichtnegative primaere Abstaende gebildet:

```text
cap_p0_S_linf = max(j,i) abs(r_S(j,i))
cap_p0_H_linf = max(j,i) abs(r_H(j,i))
cap_p0_SH_trajectory_l2 = sqrt(sum(j,i) (r_S(j,i)^2 + r_H(j,i)^2))
```

Die L2-Groesse ist eine diskrete Norm ueber gebundene Samples. Es gibt keine
Zeitgewichtung, Interpolation, Normierung nach Samplezahl oder Umdeutung als
Feldzeit.

## 6. Sekundaere Aggregataudits

Zusaetzlich duerfen genau diese absoluten Differenzen der vorhandenen W7-P-
Skalare gebunden werden:

```text
abs_probe_S_linf_gap
abs_probe_H_linf_gap
abs_probe_SH_trajectory_l2_gap
```

Sie sind keine Ersatzmessung fuer Abschnitt 5. Insbesondere beweist ein
Skalargap von null keine identische Trajektorie. Die primaeren sampleweisen
Abstaende bleiben massgeblich fuer die technische Gleichheitskontrolle.

## 7. Noch nicht anzuwendende Schwellen

W7-L bindet `effect_floor` erst aus entscheidenden 2n/4n-Abstaenden. W7-AG
und W7-AI enthalten derzeit nur die vorhandene n-Aufloesung. Deshalb darf
W7-AK:

- keinen `epsilon_num` oder `effect_floor` berechnen;
- keinen positiven Rohabstand als aufgeloesten Effekt bezeichnen;
- keine relative oder prozentuale Differenz bilden;
- keinen Nenner durch Epsilon retten;
- die Grenzen 0,05 oder 0,50 nicht anwenden;
- keine Rangfolge zwischen Pfaden oder Checkpoints erzeugen.

Werte werden unveraendert als endliche nichtnegative Rohabstaende gebunden.

## 8. Ergebnis- und Digestrollen

Ein Paarresultat muss mindestens enthalten:

- Pfad und Checkpoint;
- gemeinsamen W7-Y-Checkpointdigest;
- CAP- und P0-Messresultatdigest;
- gemeinsame geordnete Beobachtungsticks;
- geordnete Digests der sampleweisen S/H-Residualvektoren;
- die drei primaeren Rohabstaende;
- die drei sekundaeren Aggregataudits;
- Kennzeichen `same_zero_fast_start = true`;
- Kennzeichen `p0_has_substrate = false`;
- Kennzeichen `evaluated = false`;
- einen kanonischen Paarresultatdigest.

Der globale Digest bindet genau 35 Paarresultate, beide unveraenderten
Eingangsgesamtdigests und alle Gegenkontrollen. Er enthaelt keine
Pfadentscheidung, Schwelle oder sprachliche Interpretation.

## 9. Pflichtgegenkontrollen

W7-AK muss mindestens pruefen:

1. **Identitaet:** CAP gegen dieselben CAP-S/H-Samples und P0 gegen dieselben
   P0-S/H-Samples liefert fuer alle drei primaeren Abstaende exakt null.
2. **Operandsymmetrie:** Vertauschen von CAP und P0 aendert die drei
   absoluten Abstaende nicht; gerichtete Residuen wechseln nur ihr Vorzeichen.
3. **Rollenreihenfolge:** kanonische und umgekehrte Verarbeitung liefert je
   Pfad und Checkpoint denselben Paarresultatdigest.
4. **Aggregatrekonstruktion:** die vorhandenen sechs W7-P-Skalare werden aus
   den jeweiligen Samples erneut exakt reproduziert.
5. **Eingangspassivitaet:** W7-AG- und W7-AI-Gesamtdigests bleiben
   unveraendert.
6. **Rollenreinheit:** kein M-, Kapazitaets- oder Observerwert fliesst in die
   S/H-Rohabstaende ein.

## 10. Harte Stopplinien

Die Komposition muss stoppen, wenn:

- Pfad, Checkpoint oder W7-Y-Checkpointdigest nicht uebereinstimmen;
- Sampleanzahl, Tickfolge oder Feldgeometrie differieren;
- CAP oder P0 nicht mit S = H = 0 gestartet ist;
- eine Messung fehlt, doppelt vorkommt oder erneut ausgefuehrt wird;
- M oder freie Kapazitaet kuenstlich auf P0 abgebildet wird;
- nur Aggregatnormen statt sampleweiser Residuen verglichen werden;
- eine Schwelle aus den Rohwerten abgeleitet oder nachgezogen wird;
- Pfade untereinander verglichen oder Lebenszyklusprofile gebildet werden;
- ein Paarresultat in einen Modellzustand zurueckgeschrieben wird;
- ein Browser, Runner, Report oder Forschungslauf gestartet wird.

## 11. Aussagegrenze

W7-AJ ist ausschliesslich ein statischer Paarungs- und Rohkontrastvertrag.
Es wurde kein CAP/P0-Abstand berechnet. Auch eine spaetere W7-AK-
Materialisierung zeigt nur technische Modellabstaende bei n-Aufloesung. Sie
begruendet keine Feldfunktion, Ressourcenfreisetzung, Wiederverwendung,
Memory, Feldzeit, Organisation, Topologie, Semantik, Selbstregulation oder
KI.

## 12. Verwendete Quellen

- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7O_MESSVERTRAG_FELDKAUSALITAET_UND_OBSERVERBASELINES.md`
- `docs/W7P_IMPLEMENTIERUNG_IN_MEMORY_MESSKOMPOSITOR.md`
- `docs/W7AF_VERTRAG_PASSIVE_CAP_MESSUEBERGABE.md`
- `docs/W7AG_IMPLEMENTIERUNG_PASSIVE_CAP_MESSUEBERGABE.md`
- `docs/W7AH_VERTRAG_P0_NULLSTART_MESSREFERENZEN.md`
- `docs/W7AI_IMPLEMENTIERUNG_P0_NULLSTART_MESSREFERENZEN.md`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`
- `mcm_field_organism/w7ai_p0_zero_start_measurement_reference.py`

## 13. Naechster Schritt

W7-AK darf einen reinen In-Memory-Kompositor fuer genau diese 35
sampleausgerichteten CAP/P0-Paare und seine Vertragstests implementieren.
Noch keine Verfeinerung, Schwellenanwendung, Pfad- oder
Lebenszyklusauswertung, Intervention, kein Browser, Report oder
Forschungslauf.
