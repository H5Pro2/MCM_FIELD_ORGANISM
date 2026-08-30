# S2-GJ: Maskierte visuelle Mustervervollstaendigung

## Auftrag und Aussagegrenze

S2-GJ bindet genau eine private Kontextnutzungsaufgabe:

```text
maskierte visuelle Mustervervollstaendigung
mit ausdruecklich benanntem B_STABLE-Kontext
```

Der Vertrag prueft spaeter, ob ein bereits stabilisierter visueller
`B_STABLE`-Kandidat fehlende Werte einer partiellen Wahrnehmungsprobe
technisch bereitstellen kann. Er fuehrt keine automatische Kontextwahl ein
und behauptet weder eine neue Speichermechanik noch Objektverstaendnis.

S2-GJ ist ausschliesslich statisch. Implementierung, Tests und Ausfuehrung
sind nicht freigegeben.

Technischer Ausgangsstand:

`94b439f570b6d2081e2ac1b67c25fc5da60f3df9`

## Gebundene technische Grundlage

Zulaessige bestehende Bausteine:

1. der bestaetigte private B4-/TSPM-1-Verbund;
2. das qualifizierte S2-GC-Drei-Rollen-Bundle;
3. die qualifizierte S2-GI-A/B-Schattenprojektion;
4. die unveraenderte visuelle Dimension mit 18 reduzierten Werten;
5. read-only Zustands- und Digestpruefungen.

Der spaetere Verbraucher darf weder B4, TSPM-1 noch PPB-1 direkt abfragen.
Er erhaelt nur die aktuelle maskierte Probe und genau ein bereits validiertes
S2-GI-Bundle. Die zu verwendende Rolle wird im Aufruf literal als
`B_STABLE` benannt. Diese Benennung ist keine automatische Auswahl.

## Bildungsvoraussetzung

Vor jeder Kontextprobe muss der jeweilige Kontext aus einem frischen
Speicherzustand tatsaechlich gebildet worden sein. Ein vorgefertigter
Endzustand darf die Bildung nicht ersetzen.

Die spaetere Bildungsgeschichte fuer einen Kontextzustand lautet:

```text
J1, J1, J1, J1, D1, D2, D3, D4, D5, D6, D7, D8, D9
```

Dabei gilt:

- die vier J1-Expositionen erzeugen den stabilen visuellen Slow-Support `3`;
- die neun unterschiedlichen D-Zustaende verdraengen J1 vollstaendig aus
  B4 und lassen die J1-Fast-Spur ablaufen;
- jeder D-Zustand wird nur einmal angeboten und darf keinen stabilen
  Slow-Kandidaten erzeugen;
- final ist J1 nur als visueller `B_STABLE`-Kandidat verfuegbar;
- `A_RECENT` bleibt mit den juengsten D-Zustaenden belegt und wirkt damit als
  ausdrueckliche Interferenzkontrolle;
- Bildung, Verdraengung und Ablauf muessen aus den tatsaechlichen Zustands-
  und Ereignisbelegen hervorgehen.

Die neun visuellen D-Zustaende sind konstante 18-Werte-Vektoren mit den
Werten:

```text
D1=-1.00  D2=-0.75  D3=-0.50  D4=-0.25  D5=0.00
D6= 0.25  D7= 0.50  D8= 0.75  D9=1.00
```

Jeder angegebene Wert belegt alle 18 Positionen des jeweiligen D-Vektors.
Benachbarte D-Zustaende besitzen damit einen normalisierten L1-Abstand von
`0.25`. Die auditive Eingabe bleibt fuer alle Geschichten identisch,
synthetisch und fuer die visuelle Auswertung ungenutzt.

## Literale visuelle Aufgabe

Die 18 Positionen werden nullbasiert nummeriert. Sichtbar sind genau die
geraden Positionen:

```text
VISIBLE = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED  = (1, 3, 5, 7, 9, 11, 13, 15, 17)
```

Die Maske ist damit vorab auf `9/18 = 50 Prozent` gebunden.

### Zielzustand `J1-T`

```text
(1,0, 0,1, 1,0, 0,1, 1,0, 0,1, 1,0, 0,1, 1,0)
```

### Fremdzustand `J1-F`

```text
(1,1, 0,0, 1,1, 0,0, 1,1, 0,0, 1,1, 0,0, 1,1)
```

`J1-T` und `J1-F` sind an allen sichtbaren Positionen identisch und an allen
maskierten Positionen verschieden. Der Verbraucher kann den Fremdkontext
daher nicht aus der partiellen Probe erkennen.

### Sichtbar widerspruechlicher Zustand `J1-C`

```text
(0,0, 0,1, 1,0, 0,1, 1,0, 0,1, 1,0, 0,1, 1,0)
```

`J1-C` widerspricht der Probe bereits an der sichtbaren Position `0`.

### Maskierte Probe

Die Probe enthaelt die Werte von `J1-T` nur an `VISIBLE`. An `MASKED` steht
ein kanonischer Maskenmarker und kein numerischer Ersatzwert. Ihr Digest
bindet:

- Dimension `18`;
- die geordnete Positionsmaske;
- alle neun sichtbaren Werte;
- Rezeptor-, Quellen- und Probendigest;
- keine vollstaendige Zielwahrnehmung.

Der vollstaendige Zielzustand `J1-T` liegt ausschliesslich in einer getrennten
Auswerterfixture. Weder Verbraucher, Kontextbundle noch Baseline erhalten
diese Fixture.

## Kontextgeschichten

Vier getrennte, frische Kontextgeschichten sind vor einer spaeteren
Ausfuehrung zu materialisieren:

| Kontext | Wiederholter Zustand | finaler B-Befund | Zweck |
| --- | --- | --- | --- |
| `K_CORRECT` | `J1-T` | stabiler visueller Kandidat | positive Kontextprobe |
| `K_FOREIGN` | `J1-F` | stabiler visueller Kandidat | ununterscheidbarer Fremdkontext |
| `K_CONFLICT` | `J1-C` | stabiler visueller Kandidat | sichtbarer Widerspruch |
| `K_ABSENT` | keiner | `ABSENT_VALID` | fehlender Kontext |

`K_CORRECT`, `K_FOREIGN` und `K_CONFLICT` verwenden jeweils dieselbe
13-Schritt-Bildungsstruktur. `K_ABSENT` darf keinen stabilen visuellen
Slow-Kandidaten enthalten. Alle Kontexte muessen als validierte
S2-GI-Bundles vorliegen; Fixture-IDs oder Sollrollen duerfen keine
Verbraucherentscheidung beeinflussen.

## Zwei Verbraucherarme und staerkste Baseline

### `CURRENT_PERCEPTION_ONLY`

Dieser Arm erhaelt nur die maskierte Probe.

Er muss ausgeben:

```text
status = INSUFFICIENT_INFORMATION
completed_value_count = 0
```

Die neun sichtbaren Werte bleiben unveraendert. Maskierte Werte werden nicht
erraten, mit Null gefuellt oder aus einer Sollfixture gelesen.

### `CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT`

Dieser Arm erhaelt dieselbe Probe und ein validiertes S2-GI-Bundle. Der
Aufruf benennt literal `B_STABLE`.

Der Verbraucher muss in dieser Reihenfolge:

1. Probe, S2-GI-Bundle, Digests und read-only Zustandsbindung validieren;
2. genau den visuellen stabilen `B_STABLE`-Kandidaten lesen;
3. alle sichtbaren Positionen exakt gegen diesen Kandidaten vergleichen;
4. bei einem sichtbaren Widerspruch ohne Teilvervollstaendigung stoppen;
5. nur die neun maskierten Positionen aus dem Kandidaten uebernehmen;
6. Herkunftsbereich, Kandidaten-, Quellen- und Bundledigest ausgeben;
7. Vor- und Nachzustandsdigests unveraendert nachweisen.

`A_RECENT` darf validiert, aber weder als Ersatzquelle noch zur Rangbildung
verwendet werden.

### `DIRECT_B_STABLE_MASK_FILL`

Die staerkste Engineeringbaseline erhaelt exakt dieselbe Probe und exakt
denselben ausdruecklich benannten B-Kandidaten. Sie fuehrt dieselbe sichtbare
Konsistenzpruefung aus und kopiert bei Erfolg dessen Werte direkt in die
maskierten Positionen.

Die Baseline besitzt dasselbe Eingabe-, Werte-, Validierungs- und
Operationsbudget. Gleichwertigkeit ist vorab als erwartbare technische
Reduktion zugelassen.

## Endliche Fallmatrix

| Fall | Arm | Kontext | Vorab erwarteter technischer Ausgang |
| --- | --- | --- | --- |
| `GJ-01` | Perception only | keiner | unzureichende Information, keine Fuellung |
| `GJ-02` | Plus context | `K_CORRECT` | neun Maskenwerte aus B, Sichtwerte unveraendert |
| `GJ-03` | Direct fill | `K_CORRECT` | identische Rekonstruktion zu `GJ-02` |
| `GJ-04` | Plus context | `K_FOREIGN` | technisch moegliche Fremdvervollstaendigung |
| `GJ-05` | Direct fill | `K_FOREIGN` | identische Fremdvervollstaendigung zu `GJ-04` |
| `GJ-06` | Plus context | `K_ABSENT` | `CONTEXT_ABSENT`, keine Fuellung |
| `GJ-07` | Plus context | `K_CONFLICT` | `CONTEXT_CONFLICT`, keine Teilfuellung |

Der in `K_CORRECT` vorhandene fremde `A_RECENT`-Inhalt prueft zugleich, dass
die benannte B-Rolle nicht durch einen juengeren A-Inhalt ersetzt wird.

## Messgroessen

Der getrennte Auswerter berechnet erst nach dem Verbraucheraufruf:

- `visible_preservation_count` von `9`;
- `completed_mask_count` von `0` oder `9`;
- mittleren absoluten Fehler nur auf `MASKED`;
- mittleren absoluten Fehler ueber alle 18 Positionen;
- Status- und Herkunftskorrektheit;
- Gleichheit der Speicher-, S2-GC- und S2-GI-Vor-/Nachzustandsdigests;
- Operations- und Referenzledger je Arm;
- Gleichheit oder Abweichung zur direkten Baseline.

Die Zielwerte duerfen erst in diesem Auswerter mit dem Ergebnis verbunden
werden. Eine Zielidentitaet darf nicht im Verbraucherresultat erscheinen.

## Erfolgs-, Grenz- und Stoppregeln

Die begrenzte Engineeringfunktion ist nur bestaetigt, wenn gemeinsam gilt:

1. `GJ-01` fuellt keinen maskierten Wert;
2. `GJ-02` fuellt genau neun maskierte Werte korrekt aus `B_STABLE`;
3. alle neun sichtbaren Werte bleiben in jedem auswertbaren Fall bitgleich;
4. `GJ-06` und `GJ-07` erzeugen keine Teilvervollstaendigung;
5. alle Speicher- und Bundlezustaende bleiben read-only unveraendert;
6. Herkunft und B-Bereich sind vollstaendig im Ergebnis gebunden;
7. `GJ-03` und `GJ-02` sind bei gleichem Budget funktional gleichwertig.

`GJ-04` und `GJ-05` duerfen den Fremdkontext nicht kuenstlich als falsch
erkennen. Die erwartbare Fehlvervollstaendigung wird vollstaendig gemessen,
erhaelt aber keinen Erfolgsclaim und falsifiziert die begrenzte Funktion
nicht.

Ein vollstaendiger Erfolg mit gleicher direkter Baseline fuehrt zu:

`S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS`

Die Funktion ist falsifiziert, wenn der korrekte B-Kontext keinen Nutzen
gegenueber `CURRENT_PERCEPTION_ONLY` liefert, sichtbare Werte veraendert,
bei Abwesenheit oder sichtbarem Konflikt teilweise fuellt oder einen
Speicherzustand veraendert.

Methodisch nicht auswertbar sind insbesondere:

- vorgefertigte statt gebildete B-Zustaende;
- Zielwerte oder Falllabels im Verbrauchereingang;
- automatische Kontextwahl;
- fremde Quellen-, Probe-, Zustands- oder Bundledigests;
- nicht identische Eingaben oder Budgets zwischen Kontextarm und Baseline;
- unvollstaendige Einzelbefunde oder Ledger;
- Speicher-, Bundle- oder Feldveraenderung.

Diese Faelle ergeben `S2GJ_NOT_EVALUABLE`, keinen negativen Funktionsbefund.

## Ressourcen- und Read-only-Grenzen

Je Verbraucheraufruf gelten hoechstens:

- eine 18-Werte-Probe mit neun sichtbaren Positionen;
- ein S2-GI-Bundle mit genau zwei Bereichen;
- ein explizit benannter visueller B-Kandidat mit 18 Werten;
- 18 Maskenvalidierungen;
- neun sichtbare Vergleiche;
- hoechstens neun Maskenuebernahmen;
- eine Ausgabe mit hoechstens 18 Werten und den gebundenen Digests;
- keine Historie, Schleife ueber Speicherbaenke oder weitere Kandidatenwahl.

Native Kosten sowie Validierungs-, Vergleichs-, Kopier- und Digestarbeit
werden je Arm getrennt gezaehlt. Die direkte Baseline erhaelt dieselben
Obergrenzen.

## Ausgeschlossene Richtungen

S2-GJ erlaubt nicht:

- Implementierung, Tests oder Ausfuehrung;
- automatische Kontextauswahl oder Kandidatenrangfolge;
- Nutzung von `A_RECENT` zur Vervollstaendigung;
- Lernen, Prototypaktualisierung oder neue Speichermechanik;
- Schwellenanpassung, Semantik oder Objektlabels;
- Rohbildspeicherung;
- API-, Snapshot-, Produktions- oder Feldintegration;
- einen MCM-spezifischen Wirksamkeitsclaim bei Baselinegleichheit.

## Statische Entscheidung

Die Aufgabe ist endlich, materialisierbar und falsifizierbar. Sie prueft
erstmals eine konkrete Nutzung des bereits qualifizierten Zwei-Bereich-
Kontexts. Da die direkte Maskenfuellung denselben Funktionsweg reproduzieren
kann, ist der erwartete Erkenntniswert eine transparente Engineeringfunktion
und keine neue MCM-spezifische Mechanik.

S2-GJ-Abschluss:

`PASS_S2GJ_STATIC_MASKED_VISUAL_COMPLETION_CONTRACT_BOUND`

Eine private Implementierung, neutrale Vertragstests und jede Ausfuehrung
benoetigen eine neue ausdrueckliche Freigabe.
