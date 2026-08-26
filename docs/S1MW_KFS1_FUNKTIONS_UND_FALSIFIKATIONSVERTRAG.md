# S1-MW KFS-1 Funktions- und Falsifikationsvertrag

## Status

S1-MW ist ein statischer Funktions- und Falsifikationsvertrag fuer `KFS-1`.
Der Schritt bindet keine Gleichung, keine Parameter, keine Runtime, keinen
Feldlauf, keine Matrixpublikation und kein Urteil.

`KFS-1` bleibt ein Kandidatenraum:

```text
lokales ressourcenbegrenztes Feld-Substrat
mit Kohaerenzbelastung und spaeterer Aufnahmeaenderung
```

## Zweck

S1-MW legt fest, welche eigene technische Funktion `KFS-1` spaeter zeigen
muesste, damit der Kandidat nicht sofort auf Fixed Adapter, Leaky-Nachhall,
Integrator, Replay, globale Normalisierung oder Readout-Artefakte reduziert
wird.

Die Funktion ist nicht Memory. Sie ist nur die Mindestbedingung, ab der eine
hypothetische MCM-Memory-Entwicklungsrichtung ueberhaupt weiter pruefbar
waere.

## Funktionsprognose

`KFS-1` muss spaeter eine lokale Feldaufnahmeaenderung tragen, die aus
vorheriger lokaler Feldspannung und Ressourcenbelastung entsteht.

Vorlaeufige technische Prognose:

```text
A-Kontakt belastet lokale Ressource
-> spaetere A-Probe wird lokal anders aufgenommen
-> B-Konkurrenz stoert diese Aufnahmeaenderung gerichtet
-> Loesungsphase schwaecht die gebundene Wirkung
-> freigegebene Ressource kann anders wiedergebunden werden
```

Diese Prognose ist nur gueltig, wenn alle Rollen lokal, endlich und
vorregistriert messbar sind.

## Mindestrollen

### 1. Stoerungsaufnahme

Ein Kontakt muss eine lokale Feldspannung oder Feldabweichung erzeugen, die
vorab benannt ist. Die Stoerung darf nicht aus Bedeutung, Zielerfolg, Reward
oder nachtraeglicher Auswertung entstehen.

### 2. Ressourcenbelastung

Die Stoerung muss eine endliche lokale Ressource belasten. Die Ressource muss
als freie, gebundene und blockierte oder refraktaere Rolle bilanziert werden.

### 3. Spaetaufnahme

Eine spaetere Probe muss auf derselben lokalen Feldgeometrie anders aufgenommen
werden als ohne vorherige Belastung. Diese Aenderung muss im Feldreadout
sichtbar sein, darf aber nicht durch den Readout erzeugt werden.

### 4. Abschwaechung

Eine definierte Loesungs- oder veraenderte Folgegeschichte muss die gebundene
Wirkung reduzieren. Abschwaechung ist nur gueltig, wenn die Ressourcenbilanz
gleichzeitig konsistent bleibt.

### 5. Interferenz

Eine konkurrierende B-Geschichte muss die spaetere A-Aufnahme gerichtet
veraendern. Interferenz darf keine globale Ueberschreibung und kein
nachtraeglicher Klassifikator sein.

### 6. Freigabe

Gebundene oder blockierte Ressource muss wieder in eine freie Rolle uebergehen
koennen. Ohne Freigabe entsteht nur permanente Struktur.

### 7. Wiederbindung

Freigegebene Ressource muss durch eine andere Folgegeschichte neu beansprucht
werden koennen. Ohne Wiederbindung bleibt Freigabe funktional leer.

## Gegenbaselines

`KFS-1` muss spaeter mindestens gegen folgende Baselines antreten:

| Baseline | Muss scheitern, wenn KFS-1 eigenstaendig sein soll |
|---|---|
| Fixed Adapter | darf die spaetere Aufnahmeaenderung nicht aus einem vorab fixierten Operator erklaeren |
| Leaky-Nachhall | darf die Spaetaufnahme nicht als schnelle passive Persistenz erklaeren |
| Integrator/Saettigung | darf Belastung nicht als blosse Akkumulation ohne Loesung erklaeren |
| Replay/Puffer | darf keine gespeicherte Folge erneut ausgeben |
| globale Normalisierung | darf Kohaerenz nicht ohne lokale Ressourcenursache erzeugen |
| feste Kantenmatrix | darf die Wirkung nicht als vorgegebene Struktur tragen |
| Readout-Klassifikator | darf die Differenz nicht erst in der Auswertung erzeugen |
| F3/CONST-V | darf dieselbe Feldwirkung ohne KFS-1-Ressourcenledger nicht reproduzieren |

Zustandsbehaftete Baselines muessen dieselbe relevante A/B/Gap-Vorgeschichte
sehen wie KFS-1. Nicht aequivalente Baselineprofile sind gesperrt.

## Messbindung vor Gleichung

Vor jeder Gleichung muessen feststehen:

1. welche lokale S/H-Spannung als Stoerung gilt;
2. welche Ressource pro Kante oder Traeger belastet wird;
3. welche spaetere Probe den Aufnahmeeffekt misst;
4. welche Nullkontakt- oder Gap-Folge die Baseline bildet;
5. welche B-Folge Interferenz erzeugen soll;
6. welche Loesungsfolge Abschwaechung prueft;
7. welche Wiederbindungsfolge eine andere Beanspruchung prueft;
8. welche Digests und Fallrollen den Vergleich reproduzierbar machen.

Keine dieser Rollen darf nach einem Lauf angepasst werden.

## Falsifikationskriterien

`KFS-1` wird verworfen, wenn mindestens eine der folgenden Bedingungen gilt:

- lokale Ressource ist nicht endlich oder nicht bilanziert;
- Spaetaufnahme entsteht ohne gebundene lokale Belastung;
- Fixed Adapter erklaert denselben Unterschied vollstaendig;
- Leaky-Nachhall oder Integrator erklaert denselben Unterschied vollstaendig;
- Replay, Puffer oder Readout erzeugt die scheinbare Wirkung;
- Interferenz bleibt unmessbar;
- Abschwaechung bleibt unmessbar;
- Freigabe oder Wiederbindung fehlt;
- Kandidat und Baselines sehen keine faire Kausalhistorie;
- die Wirkung benoetigt Labels, Reward, Zieltopologie oder Rohdatenzugriff.

## Claim-Sperren

Auch bei spaeter positivem Funktionsbefund bleiben gesperrt:

- vorhandene MCM-Memory;
- Lernen als Projektfaehigkeit;
- Feldintelligenz oder KI;
- Bewusstsein, Erleben, Bedeutung oder Verstehen;
- biologische Gleichsetzung mit echten Neuronen;
- allgemeine Uebertragbarkeit auf offene Weltumgebungen.

Ein positiver spaeterer Befund duerfte nur lauten:

```text
KFS-1 zeigt in der vorregistrierten Testgrenze eine lokale,
ressourcengetragene und baselineabgegrenzte Feldaufnahmeaenderung.
```

## Ergebnis von S1-MW

S1-MW bindet:

- die minimale KFS-1-Funktionsprognose;
- die notwendigen Rollen Stoerung, Belastung, Spaetaufnahme, Abschwaechung,
  Interferenz, Freigabe und Wiederbindung;
- die Baselinepflicht;
- die Messbindung vor jeder Gleichung;
- die Falsifikationskriterien;
- die Claim-Sperren.

S1-MW bindet nicht:

- Gleichung;
- Parameter;
- Zahlenwerte;
- Runtime;
- Feldlauf;
- Fallmatrix;
- Ergebnisentscheidung.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-MX, ausschliesslich als statische Anatomie- und
Messrollenbindung fuer KFS-1. S1-MX darf nur klaeren, welche lokalen Ledger-,
Stoerungs- und Readoutrollen existieren muessen. Gleichung, Parameter,
Runtime und Ausfuehrung bleiben gesperrt.
