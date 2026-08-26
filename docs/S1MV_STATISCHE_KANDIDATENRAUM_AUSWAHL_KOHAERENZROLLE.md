# S1-MV Statische Kandidatenraum-Auswahl fuer die Kohaerenzrolle

## Status

S1-MV ist eine statische Auswahl und Eingrenzung des Kandidatenraums nach
S1-MU. Es gibt keine Gleichung, keine Parameter, keine Runtime, keinen
Feldlauf, keine Matrixpublikation und kein Urteil.

Der Schritt waehlt keinen fertigen Mechanismus aus. Er legt nur fest, welcher
minimale Kandidatenraum fachlich weiterverfolgt werden darf und welche
Alternativen fuer die naechste MCM-Memory-Entwicklungsrichtung gesperrt sind.

## Ausgangspunkt

S1-MU bindet Kohaerenz als technischen Messrahmen:

```text
Weltkontakt
-> gemeinsame technische Feldzeit
-> lokale Feldspannung oder Stoerung
-> Belastung einer endlichen lokalen Ressource
-> lokale Umordnung
-> spaetere veraenderte Feldaufnahme
```

S1-MV fragt nur, welche minimale Substratklasse diesen Rahmen prinzipiell
tragen koennte, ohne als Fixed Adapter, Nachhall, Integrator, Replay,
Rewardlogik oder globale Normalisierung zu kollabieren.

## Ausschlussraum

Nicht weiterverfolgt werden fuer die naechste Kandidatenstufe:

| Klasse | Grund fuer Ausschluss |
|---|---|
| Reward- oder Zielwertlogik | schreibt externe Bewertung in die Entwicklung |
| Replay- oder Verlaufspuffer | speichert Geschichte statt lokale Feldwirkung zu tragen |
| feste Kanten- oder Gewichtsmatrix | ist vorgegebene Struktur, keine belastete lokale Ressource |
| globale Normalisierung | erzeugt Ordnung ohne lokale Ursache und ohne Kantenbilanz |
| reiner Leaky-Nachhall | erklaert schnelle Persistenz ohne Ressourcenbindung |
| reiner Integrator | sammelt Werte ohne Freigabe-, Interferenz- und Wiederbindungsrolle |
| Fixed Adapter | erklaert spaetere Wirkung aus einem vor der Probe fixierten Operator |
| Readout-Klassifikator | erzeugt Ordnung nur in der Auswertung, nicht im Feld |

Diese Klassen bleiben als Gegenbaselines oder Negativkontrollen zulaessig, aber
nicht als primaerer Kandidatenraum.

## Gepruefte Kandidatenraeume

### A. Lokales Feldspannungs-Ledger

Ein lokales Feldspannungs-Ledger wuerde pro Kante oder Nachbarschaft eine
begrenzte Belastungsrolle fuehren. Die Belastung entstuende aus lokaler
S/H-Spannung und waere spaeter im Feldreadout sichtbar.

Vorteil:

- direkte Naehe zu vorhandenen S/H-Feldgroessen;
- klare Gegenbaselines gegen Fixed Adapter und Leaky-Nachhall;
- lokale Bilanz pro Kante prinzipiell moeglich.

Schwaeche:

- Gefahr, wieder nur ein Adapter oder Integrator zu werden;
- Freigabe und Wiederbindung sind noch nicht eigenstaendig gebunden;
- Rueckwirkung auf spaetere Feldaufnahme waere noch zu spezifizieren.

### B. Lokales Ressourcen-Kompartiment mit Kopplungsbereitschaft

Ein lokales Ressourcen-Kompartiment wuerde freie, gebundene und blockierte
Anteile pro Kante oder Traeger fuehren. Kontakt belastet die Ressource, eine
spaetere Probe liest die dadurch veraenderte lokale Kopplungsbereitschaft.
Abschwaechung, Interferenz, Freigabe und Wiederbindung muessen im Ledger
unterscheidbar bleiben.

Vorteil:

- passt zu S1-HI bis S1-MU;
- bildet eine klare endliche Ressource;
- trennt Bindung, Stoerung, Interferenz und Freigabe;
- kann gegen Replay, Reward, Leaky, Integrator und Fixed Adapter abgegrenzt
  werden.

Schwaeche:

- noch keine Gleichung und kein Transfergesetz;
- Kohaerenzgewinn muss vorab als eigene Messrolle definiert werden;
- geschlossene Rueckwirkung darf keine versteckte Zielstruktur einfuehren.

### C. Globale Feldordnung mit Kohaerenzwert

Eine globale Feldordnung wuerde einen Gesamtkohaerenzwert berechnen und das
Feld danach ausrichten.

Vorteil:

- leicht messbar.

Schwaeche:

- zu nah an Reward, globaler Normalisierung oder Zieltopologie;
- keine lokale Ressourcenbilanz;
- keine saubere Interferenz- und Freigaberolle;
- widerspricht der lokalen MCM-Ausrichtung.

Diese Klasse wird fuer den naechsten Schritt gesperrt.

## Auswahl

S1-MV waehlt als einzigen weiterverfolgbaren Kandidatenraum:

```text
lokales ressourcenbegrenztes Feld-Substrat mit Kohaerenzbelastung
und spaeterer Aufnahmeaenderung
```

Kurzname fuer die naechste Vertragsstufe:

```text
KFS-1
```

KFS-1 steht fuer `Kohaerenz-Feld-Substrat 1`. Der Name bezeichnet nur einen
Kandidatenraum, keine Gleichung und keine Runtime.

## Mindestrollen von KFS-1

KFS-1 darf in S1-MW nur weiterverfolgt werden, wenn diese Rollen vor jeder
Formel gebunden werden:

1. **Stoerungsaufnahme:** lokale Feldspannung belastet eine endliche Ressource.
2. **Gebundene Wirkung:** ein Teil der Ressource veraendert spaetere lokale
   Feldaufnahme.
3. **Blockierte Phase:** ein Teil der Ressource ist zeitweise nicht direkt
   wieder bindbar.
4. **Abschwaechung:** wiederholte oder veraenderte Folgegeschichte reduziert
   die gebundene Wirkung.
5. **Interferenz:** konkurrierende lokale Geschichte veraendert die spaetere
   Aufnahme messbar.
6. **Freigabe:** gebundene oder blockierte Ressource wird wieder frei.
7. **Wiederbindung:** freie Ressource kann durch andere Folgegeschichte neu
   gebunden werden.

## Messgrenzen

KFS-1 muss spaeter mindestens diese Messflaechen besitzen:

- lokale S/H-Feldspannung vor Bindung;
- Ressourcenbilanz pro Kante oder Traeger;
- spaetere Feldaufnahme unter identischer Probe;
- Stoerungs- oder Kohaerenzkontrast gegen Nullkontakt;
- Abschwaechungskurve;
- Interferenzkontrast;
- Freigabe- und Wiederbindungsnachweis.

Alle Messflaechen muessen vor einem Lauf gebunden werden. Nachtraegliche
Auswahl eines guenstigen Readouts ist unzulaessig.

## Baselinepflicht

KFS-1 muss gegen folgende Baselines vorbereitet werden:

- Fixed Adapter aus identischer Kausalhistorie;
- Leaky-Nachhall;
- Integrator/Saettigung;
- F3/CONST-V;
- Replay- oder Verlaufspuffer;
- globale Normalisierung;
- feste Kantenmatrix;
- Readout-Klassifikator;
- gleiche Feldrechnung ohne Ressourcenledger.

Jede Baseline muss dieselbe relevante A/B/Gap- oder Kontaktgeschichte sehen,
wenn sie zustandsbehaftet ist. Nicht aequivalente Baselineprofile duerfen nicht
uminterpretiert werden.

## Verwerfungsbedingungen

KFS-1 wird vor einer Gleichung verworfen, wenn:

- keine lokale endliche Ressource benannt werden kann;
- Stoerung nur global oder nur semantisch definiert ist;
- Kohaerenzgewinn nur aus einem externen Zielwert entsteht;
- die spaetere Aufnahme durch Fixed Adapter oder Leaky erklaerbar ist;
- Abschwaechung, Interferenz oder Freigabe nicht getrennt messbar sind;
- Rueckwirkung Rohdaten, Labels, Reward oder Zieltopologie in das Feld
  schreibt;
- keine faire Kausalhistorie fuer Kandidat und Baselines herstellbar ist.

## Ergebnis von S1-MV

S1-MV entscheidet:

```text
SELECTED_CANDIDATE_SPACE = KFS-1
KFS-1 = lokales ressourcenbegrenztes Feld-Substrat
        mit Kohaerenzbelastung und spaeterer Aufnahmeaenderung
```

Nicht entschieden sind:

- Gleichung;
- Parameter;
- numerische Schwellen;
- Runtimeform;
- Feldlauf;
- Fallmatrix;
- Memory-Nachweis;
- Systemfaehigkeit.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-MW, ausschliesslich als Funktions- und
Falsifikationsvertrag fuer KFS-1. S1-MW darf noch keine Gleichung, Parameter,
Runtime oder Ausfuehrung freigeben.
