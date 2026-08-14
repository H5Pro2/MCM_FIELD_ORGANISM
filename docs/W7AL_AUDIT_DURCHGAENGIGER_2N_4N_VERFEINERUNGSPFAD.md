# W7-AL: Audit des durchgaengigen 2n/4n-Verfeinerungspfads

## Entscheidung

`RUNTIME_REFINEMENT_EXISTS_FULL_W7_PATH_NOT_YET_BOUND`

W7-AL prueft statisch, ob die in W7-L geforderten Aufloesungen n, 2n und 4n
bereits vom CAP-Hauptpfad bis zur CAP/P0-Paarung durchgaengig materialisiert
werden koennen. Es wurde keine Runtime geaendert, keine Verfeinerung
ausgefuehrt und kein Messwert berechnet.

## 1. Ergebnis in Kurzform

Die technische CAP-Basisruntime besitzt einen funktionierenden
`refinement`-Parameter. Der aktuelle W7-AE/AG/AK-Verbrauch bindet jedoch nur
den Standardwert `1`. Ein vollstaendiger 2n/4n-Pfad existiert deshalb noch
nicht.

P0 verwendet eine analytische exakte Fast-Field-Fortschreibung und benoetigt
keine numerische 2n/4n-Neuausfuehrung. Dieselbe W7-AI-P0-Referenz darf als
gemeinsame aufloesungsunabhaengige Gegenbaseline dienen.

## 2. Vorhandene Runtimefaehigkeit

`advance_capacity_limited_mcm_f3_shared_field_transient` nimmt bereits
`refinement: int = 1` an und reicht den Wert an
`advance_mcm_f3_shared_field_transient` weiter.

Die Basisruntime:

- lehnt boolesche, nichtganzzahlige und nichtpositive Werte ab;
- multipliziert die fuer ein Intervall bestimmte Basisschrittzahl mit dem
  Verfeinerungsfaktor;
- bindet den Faktor in `MCMF3IntegrationDiagnostics`;
- fuehrt bei aktiver CAP-Kopplung SSPRK33-Stufen mit unveraenderter Gleichung
  und unveraenderten Parametern aus;
- beobachtet weiterhin nur echte Rezeptorabschlussgrenzen und den
  Segmentendtick;
- besitzt technische Einzeltests fuer `refinement = 1, 2, 4`.

Damit fehlt keine neue Integrationsmethode. Es fehlt die aufloesungsgebundene
Durchleitung durch die W7-Verbraucher.

## 3. Lokalisierte Durchleitungsluecken

### 3.1 W7-AE

Die private Funktion `_produce` ruft die CAP-Transientruntime ohne
`refinement` auf. Dadurch gilt immer der Standardwert `1`.

Die sieben Hauptketten und 35 technischen Probeaeste werden nur in dieser
Aufloesung erzeugt. Pfad-, Checkpoint-, Produktions- und Gesamtergebnisse
besitzen keine explizite Aufloesungsrolle.

### 3.2 W7-AG

Die 35 CAP-Messkopien rufen dieselbe W7-AE-Funktion ebenfalls ohne
Verfeinerungsfaktor auf. Ihre Samples tragen echte Ticks, aber keine
Aufloesungskennung. Der W7-AG-Gesamtdigest bindet daher nur n.

### 3.3 W7-AK

Der Rohkontrastkompositor bindet absichtlich die kanonischen W7-AG- und
W7-AI-Gesamtdigests. Er besitzt keine Aufloesungsdimension und darf keine
alternativen CAP-Ergebnisse unter denselben Rollen annehmen.

Diese harte Bindung ist korrekt fuer W7-AK und darf nicht geloest werden.
Verfeinerung benoetigt additive neue Ergebnisrollen.

## 4. P0-Rolle

W7-R und W7-AI verwenden den neutralen Fast-Field-Pfad. Seine S/H-
Fortschreibung zwischen Ereignissen erfolgt analytisch ueber die
Eigenzerlegung des linearen Generators und nicht ueber SSPRK-Substeps.

Deshalb gilt:

- W7-AI wird nicht fuer n, 2n und 4n dreifach ausgefuehrt;
- derselbe P0-Gesamtdigest und dieselben 35 P0-Samplefolgen werden fuer jede
  CAP-Aufloesung wiederverwendet;
- P0 erhaelt keine kuenstliche `refinement`-Eigenschaft;
- eine nominelle P0-2n/4n-Kopie waere nur ein Duplikat und keine numerische
  Gegenkontrolle.

## 5. Erforderliche additive Aufloesungsketten

Eine spaetere Implementierung muss drei voneinander unabhaengige CAP-Ketten
erzeugen:

```text
CAP-R1: frisches W7-M-Anfangsfeld -> alle Hauptpfade -> CAP-Messungen
CAP-R2: frisches W7-M-Anfangsfeld -> alle Hauptpfade -> CAP-Messungen
CAP-R4: frisches W7-M-Anfangsfeld -> alle Hauptpfade -> CAP-Messungen
```

Dabei bezeichnet R1/R2/R4 ausschliesslich den SSPRK-Verfeinerungsfaktor.
Quellen, Ereignisse, Weltzeit, Organismusticks, Gleichung, Parameter,
Geometrie, Kapazitaet und Checkpoints bleiben identisch.

Keine Aufloesung darf den Endzustand einer anderen Aufloesung fortsetzen.
Alle drei starten aus getrennten tiefen Kopien desselben homogenen
W7-M-Anfangsfeldes.

## 6. Kleinste zulaessige Schnittstellenerweiterung

Die bestehende kanonische n-Kette muss unveraendert bleiben. Additiv noetig
sind:

1. eine private, auf `{1, 2, 4}` begrenzte Refinementdurchleitung in der
   W7-AE-Produktion;
2. eine explizite aeussere Aufloesungsrolle fuer getrennte W7-AE-
   Siebenpfadergebnisse;
3. dieselbe private Durchleitung und aeussere Rolle fuer W7-AG-Messungen;
4. ein neuer aufloesungsgebundener CAP/P0-Paarkompositor, der dieselbe
   W7-AI-P0-Referenz liest;
5. neue Digests, die `refinement`, den zugehoerigen CAP-Eingangsdigest und
   die unveraenderte P0-Referenz explizit binden.

Die Paketwurzel und `current_api` erhalten keine neuen Exporte.

## 7. Beobachtungs- und Paarungsinvarianz

SSPRK-Substeps duerfen keine zusaetzlichen Messsamples erzeugen. Fuer jede
Rolle muessen R1, R2, R4 und P0 dieselbe geordnete Folge tatsaechlicher
Rezeptorabschlussgrenzen besitzen.

Vergleichbar bleiben ausschliesslich S und H am selben Tick und Feldort.
M darf nur zwischen CAP-Aufloesungen verglichen werden, niemals gegen P0.

## 8. Verfeinerungsabstaende

Nach einer spaeteren Materialisierung duerfen zunaechst nur rohe
Konvergenzabstaende gebildet werden:

```text
D_CAP_R1_R2(role)
D_CAP_R2_R4(role)
D_RAW_R1_R2(role)
D_RAW_R2_R4(role)
```

`D_CAP` vergleicht sampleweise CAP-S/H-Trajektorien zweier Aufloesungen.
`D_RAW` vergleicht die daraus entstandenen CAP/P0-Residualtrajektorien.

Eine erwartete Verkleinerung von R1/R2 nach R2/R4 ist eine technische
Konvergenzkontrolle, aber noch kein Funktionsbefund.

## 9. Grenze des numerischen Bodens

W7-L definiert:

```text
epsilon_num = max aller gebundenen entscheidenden 2n/4n-Linf-Abstaende
effect_floor = 10 * epsilon_num
```

Die verfeinerten CAP/P0-Rohabstaende sind dafuer notwendig, aber nicht
allein hinreichend. Spaetere Funktionsentscheidungen verwenden auch
Pfadkontraste, regionale M-Rollen und Interventionen. Solange deren
entscheidende 2n/4n-Abstaende fehlen, darf hoechstens ein lokaler technischer
Rohkontrastboden dokumentiert werden, nicht der globale `effect_floor` aus
W7-L.

## 10. Pflichtgegenkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- R1 reproduziert bitgleich die bestehenden W7-AE-, W7-AG- und W7-AK-
  Digests;
- R2 und R4 besitzen explizit andere Aufloesungsdigests;
- jede Aufloesung ist deterministisch und rollenreihenfolgeunabhaengig;
- alle Aufloesungen starten aus getrennten, wertgleichen Anfangsfeldern;
- Quellen-, Plan-, Geometrie-, Parameter- und P0-Digests bleiben gleich;
- Sampleticks und Vektorgeometrie sind ueber R1/R2/R4/P0 identisch;
- Gesamtmasse und lokale Kapazitaet bleiben in jeder Aufloesung erhalten;
- die bestehenden n-Ergebnisobjekte und Digests bleiben unveraendert;
- keine Aufloesung oder Messung schreibt in eine andere zurueck.

## 11. Harte Stopplinien

Die Verfeinerung muss stoppen, wenn:

- `refinement` als Runtimezustand oder Feldparameter verwendet wird;
- andere Werte als 1, 2 und 4 in die W7-Verfeinerungsmatrix gelangen;
- Quellen, Gleichungen oder Modellparameter zwischen Aufloesungen wechseln;
- R2 oder R4 aus einem R1-Endzustand startet;
- SSPRK-Substeps als neue Rezeptorereignisse oder Feldzeit ausgegeben werden;
- P0 kuenstlich numerisch verfeinert oder mehrfach ausgefuehrt wird;
- der bestehende W7-AK-Digest ueberschrieben wird;
- nur Endwerte statt sampleweiser Trajektorien verglichen werden;
- aus den Rohkontrastabstaenden bereits der globale `effect_floor` abgeleitet
  wird;
- eine Auswertung, Intervention, ein Browser, Report oder Forschungslauf
  gestartet wird.

## 12. Aussagegrenze

W7-AL ist ein statischer technischer Audit. Er zeigt eine vorhandene
Runtimefaehigkeit und eine fehlende Durchleitung, aber keine numerische
Konvergenz. Daraus folgen keine Feldfunktion, Ressourcenfreisetzung,
Wiederverwendung, Memory, Feldzeit, Organisation, Topologie, Semantik,
Selbstregulation oder KI.

## 13. Verwendete Quellen

- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7K_IMPLEMENTIERUNG_KAPAZITAETSBEGRENZTER_SHAREDMCMFIELD_ADAPTER.md`
- `docs/W7AK_IMPLEMENTIERUNG_CAP_P0_ROHKONTRASTKOMPOSITOR.md`
- `mcm_field_organism/mcm_f3_runtime.py`
- `mcm_field_organism/capacity_limited_mcm_f3_runtime.py`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/w7ae_cap_seven_path_consumer.py`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`
- `mcm_field_organism/w7ai_p0_zero_start_measurement_reference.py`
- `mcm_field_organism/w7ak_cap_p0_raw_contrast_compositor.py`
- `tests/test_capacity_limited_mcm_f3_runtime.py`

## 14. Naechster Schritt

W7-AM soll vor jeder Implementierung statisch den additiven
Aufloesungscontainer, seine R1-Kompatibilitaetsbindung, R2/R4-Digests,
P0-Wiederverwendung und Vertragstests festlegen. Noch keine Codeaenderung,
Verfeinerungsausfuehrung, Schwellenberechnung, Auswertung, kein Browser,
Report oder Forschungslauf.
