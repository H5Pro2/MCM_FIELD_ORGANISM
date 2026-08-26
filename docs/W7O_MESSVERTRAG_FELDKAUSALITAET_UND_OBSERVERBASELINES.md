# W7-O: Messvertrag fuer Feldkausalitaet und Observerbaselines

## Entscheidung

`CAUSAL_FIELD_AND_OBSERVER_MEASUREMENT_SURFACES_BOUND`

W7-O bindet die Messrollen der in W7-L bis W7-N vorbereiteten Modelle vor
jeder Hauptauswertung. Es gibt zwei getrennte Messflaechen. Ihre absoluten
Werte duerfen nicht miteinander gleichgesetzt werden.

Dieses Dokument ist ein statischer Vertrag. Es implementiert und berechnet
keine Hauptmatrix, startet keinen Browser und erzeugt keinen Forschungsreport.

## 1. Modellklassen

### 1.1 Kausale Feldmodelle

Zur kausalen Feldmessflaeche gehoeren:

- `CAP`
- `P0`
- `LIN`
- `F3`
- `CONST-V`
- `MOB`
- `ETA0`
- `KAPPA0`
- `SIGN`

Nur diese Klasse darf anhand spaeterer, identisch angeregter S/H-Probewirkung
verglichen werden. Eine technische Modellbezeichnung ist kein Funktions- oder
Memorybefund.

### 1.2 Observer-Erklaerungsmodelle

Zur getrennten Observermessflaeche gehoeren:

- `LEAK`
- `SAT`
- `NORM`

Diese Modelle erklaeren hoechstens einen zeitlichen Ausgangsverlauf. Sie sind
keine Organismusfunktion, kein Feldmodell und keine Gegenbaseline fuer eine
M-Ressourcenkausalitaet.

## 2. Gemeinsamer Observer-Treiber

LEAK, SAT und NORM erhalten genau denselben externen P0-S-Treiber aus den in
W7-M eingefrorenen Quellen. Der Treiber wird einmal erzeugt und unveraendert
an alle drei Modelle gegeben.

Der Treiber ist an Rezeptorabschlussgrenzen ausgerichtet. Zwischen zwei
Grenzen gilt der zuletzt vollstaendig abgeschlossene P0-S-Wert linksstetig.
Gleichzeitige Ereignisse werden atomar uebernommen. Zu Beginn eines Intervalls
gilt der dort bereits abgeschlossene P0-S-Wert.

H-, M-, CAP-, Diagnose- oder Observerwerte duerfen den Treiber nicht
veraendern. Es gibt weder Observerrueckwirkung noch Observerpersistenz in eine
spaetere Feldfortsetzung.

## 3. Messflaeche F: kausale Feldwirkung

Jeder Feldarm besitzt die Checkpoints 0 bis 4. Vor einer Probe werden S und H
auf Kopien angeglichen; danach wird dieselbe P-Probe verwendet. Messbar sind:

- `probe_S_linf`
- `probe_H_linf`
- `probe_SH_trajectory_l2`
- `probe_observation_ticks`

Die vorregistrierten Pfadvergleiche lauten:

- `AB` gegen `UB`: alte A-Wirkung unter B
- `AG` gegen `UG`: alte A-Wirkung nach Unterbrechung
- `AB` gegen `AG`: neue B-Wirkung nach A
- `UB` gegen `UG`: neue B-Wirkung nach neutralem Vorlauf
- `BA` gegen `UA`: alte B-Wirkung unter A
- `BG` gegen `UG`: alte B-Wirkung nach Unterbrechung
- `BA` gegen `BG`: neue A-Wirkung nach B
- `UA` gegen `UG`: neue A-Wirkung nach neutralem Vorlauf

Ein Vergleich ist nur oberhalb des vorab gebundenen numerischen Bodens des
jeweiligen Modells entscheidbar.

## 4. Zulaessige Substratmessungen

Nur CAP besitzt ein vollstaendiges M-Feld und darf deshalb messen:

- das gesamte M im Arbeitsspeicher;
- regionale M-Summen und regionale freie Kapazitaet;
- Freisetzung, Beanspruchung und Bilanzrest;
- M-Neutralisierung und M-Transplantation.

F3, CONST-V, MOB und LIN duerfen einen technischen skalaren oder vektoriellen
Zustand fuehren. Dieser Zustand darf nicht als freie Zielkapazitaet bezeichnet
werden. P0 besitzt kein Substrat. LEAK, SAT und NORM besitzen weder M noch eine
Ressourcenrolle.

## 5. Messflaeche E: Observer-Erklaerung

Die drei Observermodelle laufen auf getrennten Zustandskopien und werden nur
vom gemeinsamen P0-S-Treiber angeregt. Ihre Messnamen tragen immer das
Praefix `observer_`:

- `observer_output_linf`
- `observer_output_trajectory_l2`
- `observer_state_linf`
- `observer_ticks`

Diese Werte duerfen nicht als S/H-Probewirkung, Feld- oder
Organismusantwort, M, Kapazitaet oder Interventionskausalitaet ausgegeben
werden. NORM bleibt insbesondere eine rein externe normalisierte Darstellung.

## 6. Einzige Bruecke: dimensionslose Lebenszyklusprofile

Zwischen den beiden Messflaechen duerfen nur dimensionslose Kurven und ihre
Entscheidungsklassen verglichen werden. Fuer die A-B-Richtung gelten pro
Modell und bezogen auf dessen eigenen aufgeloesten Anfangseffekt:

```text
old_b_retention(k) = old_b_effect(k) / old_b_effect(0)
old_g_retention(k) = old_g_effect(k) / old_b_effect(0)
new_b_gain(k)      = new_b_effect(k) / old_b_effect(0)
```

Die B-A-Richtung wird spiegelbildlich gebildet. Ist der Nenner kleiner oder
gleich dem numerischen Boden des jeweiligen Modells, ist das Profil technisch
unentscheidbar. Es wird kein Epsilon eingesetzt, um einen Nenner kuenstlich
entscheidbar zu machen.

Observermodelle koennen damit nur die Form eines zeitlichen Profils erklaeren.
Sie koennen weder Ressourcenbilanz noch M-Interventionskausalitaet erklaeren
oder ersetzen.

## 7. Getrennte Entscheidungen

Jede spaetere Auswertung muss zwei unabhaengige Felder fuehren:

- `field_function_decision`
- `observer_profile_explanation`

Die Observerentscheidung darf nur einen der folgenden Werte annehmen:

- `NOT_RESOLVED`
- `PROFILE_NOT_MATCHED`
- `PROFILE_EXPLAINED_BY_LEAK`
- `PROFILE_EXPLAINED_BY_SAT`
- `PROFILE_EXPLAINED_BY_NORM`

Falls mehrere Observer denselben vorab gebundenen Erklaerungsboden erreichen,
gilt die feste Einfachheitsreihenfolge `LEAK > SAT > NORM`. Sie wird nicht
nach Sichtung der Resultate geaendert.

## 8. Pflichtkontrollen

- W7-M-Quellen-, Regions- und Matrixdigests bleiben unveraendert gebunden.
- Ereignis-, Probe- und Checkpointgrenzen sind fuer alle Arme identisch.
- Wiederholungen mit identischem Eingang muessen deterministisch sein.
- Feldmodelle erhalten den vorregistrierten n/2n/4n-Verfeinerungsboden.
- Lokale Observerkerne verwenden ihre exakte Segmentfortschreibung.
- Alle Modell-, Mess- und Entscheidungsinventare sind endlich und vollstaendig.
- Observer besitzen weder Feedback noch Persistenz.
- Feld- und Observerrollennamen duerfen nicht vermischt werden.

## 9. Harte Stopplinien

Die spaetere Komposition muss stoppen, wenn:

- ein Observerwert als S oder H bezeichnet wird;
- ein modellabhaengiger S-Treiber fuer Observer erzeugt wird;
- ein Nicht-CAP-Modell eine Rolle freier Zielkapazitaet erhaelt;
- absolute Amplituden ueber beide Messflaechen verglichen werden;
- ein unaufgeloester Nenner durch Epsilon ersetzt wird;
- NORM als Organismusfunktion verwendet wird;
- ein Observer eine M-Intervention oder Ressourcenbilanz ersetzt;
- die Einfachheitsreihenfolge erst nach Resultatsichtung festgelegt wird.

## 10. Aussagegrenze

W7-O zeigt nur, dass spaetere Messungen rollenrein komponiert werden koennen.
Es wurde kein Modellpfad ausgefuehrt. Daher folgen weder Funktion, Memory,
Vergessen, Wiederverwendung, Feldzeit, Organisation, Semantik,
Selbstregulation noch KI.

## 11. Verwendete Quellen

- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md`
- `docs/W7N_IMPLEMENTIERUNG_REINER_KAPAZITAETSFUNKTIONS_BASELINEKERNE.md`
- Lauf 194 als eingefrorene Quelle der A/B-/G-/P-Pfade
- `docs/W7F_MATHEMATISCHER_MINIMALVERTRAG_KAPAZITAETSBEGRENZTER_KANTENAUSTAUSCH.md`
- `docs/W7G_IMPLEMENTIERUNG_REINE_KAPAZITAETSBEGRENZTE_KOPPLUNG.md`

## 12. Naechster Schritt

W7-P darf einen reinen In-Memory-Messkompositor implementieren. Er erzeugt
den kanonischen P0-S-Treiber, fuehrt getrennte F- und E-Datensaetze, bildet
nur die hier definierten dimensionslosen Profile und erzwingt die
Rollentrennung. Er darf noch keinen vollstaendigen A/B-Modellpfad, keine
Hauptmatrix, keinen Browser, keinen Report und keinen Forschungslauf starten.
