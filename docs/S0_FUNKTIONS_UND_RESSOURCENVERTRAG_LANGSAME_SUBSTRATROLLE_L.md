# S0: Funktions- und Ressourcenvertrag der langsamen Substratrolle L

Stand: 2026-08-07

Status: `S0_CONTRACT_BOUND`

## Zweck

Dieser Vertrag bestimmt den kleinsten zulaessigen technischen Traeger, an dem
eine spaetere substratvermittelte Feldwirkung ueberhaupt untersucht werden
kann. Er programmiert weder Praegung noch Memory, Feldzeitverdichtung,
Cluster, Rekonstruktion oder Abstraktion.

S0 schliesst die Luecke zwischen der vorhandenen schnellen MCM-Feldmechanik
und einer noch fehlenden langsameren Entwicklungsrolle. Eine konkrete
Naturgleichung wird erst in S1 ausgewaehlt.

## 1. Ein gemeinsamer Feldzustand

Der vollstaendige lokale Zustand am bestehenden Feldort `i` besitzt kuenftig
drei funktional getrennte Rollen:

```text
S_i = schnelle aktuelle MCM-Aktivierung
H_i = vorhandener schneller MCM-Nachhall
L_i = langsame lokale Entwicklungsdisposition
```

Verbindlich gilt:

- `S`, `H` und `L` gehoeren zu demselben gemeinsamen MCM-Feld;
- `L` verwendet genau die bestehenden Feldorte und deren feste Geometrie;
- `L` ist keine zweite Neuronenschicht, Runtime oder Datenbank;
- `L` besitzt keinen direkten Rezeptor-, Medien- oder Observerzugriff;
- Weltkontakt erreicht `L` ausschliesslich durch die normale lokale
  S-Feldentwicklung;
- `L` wirkt innerhalb derselben atomaren Feldtransition auf `S` zurueck.

## 2. Abgrenzung von der vorhandenen Substratmasse M

Die bestehende `MCMSubstrateState`-Rolle `M` ist eine nichtnegative,
global massenerhaltende und ko-lokalisierte technische Materialmenge. Ihre
bisher untersuchten aktiven Arme sind keine freigegebene Memory-Physik.

Deshalb gilt fuer S1:

```text
M != L
```

- `M` bleibt historische Anatomie, Kontrollarm und moegliche spaetere
  Ressourcenquelle;
- `L` wird nicht als Umbenennung von `mass` implementiert;
- die aktive M-Kopplung bleibt unveraendert geschlossen;
- eine spaetere Kopplung `M <-> L` benoetigt einen eigenen Vertrag.

Damit kann ein technischer Erfolg von L nicht nachtraeglich als Befund der
alten M-Masse ausgegeben werden.

## 3. Kleinster Darstellungsraum

S1 beginnt mit genau einem zusaetzlichen reellen Skalar `L_i` je vorhandenem
Feldort. Das ist eine minimale technische Darstellung und keine Behauptung,
dass ein Skalar fuer den spaeteren Memory-Lebenszyklus ausreicht.

Verbindliche Darstellungsgrenzen:

```text
L_i in [-1, 1]
neutraler Zustand: L_i = 0
gleiche Einheit und gleiche Regel an allen gleichartigen Feldorten
keine zusaetzlichen L-Kanten
keine L-eigenen IDs ausser der Ko-Lokalisierung zum Feldort
```

Das Vorzeichen bezeichnet nur die Richtung eines lokalen konstitutiven
Beitrags relativ zur vorzeichenbehafteten schnellen Feldlage. Es bezeichnet
keine positive oder negative Bedeutung.

Die normierte Skala ist eine Rechen- und Ressourcenbegrenzung. Die Grenzwerte
duerfen nicht als `frei`, `belegt`, `gelernt` oder `vergessen` interpretiert
werden.

## 4. Zulaessige lokale Ursachen

Eine S1-Naturform darf fuer Ort `i` nur lesen:

1. den vollstaendig abgeschlossenen Vorzustand `(S_i, H_i, L_i)`;
2. die bereits fuer S vorhandenen lokalen Nachbarwerte und Sample-Offsets;
3. den gegenwaertigen lokalen S-Antrieb nach normaler Rezeptorreduktion;
4. die reale Dauer `dt` des atomaren Organismusschritts;
5. global festgelegte, inhaltsfreie Naturparameter.

Fuer die erste S1-Scheibe bleibt `H` serialisierter Gesamtzustand, ist aber
keine Schreibsteuerung fuer `L`. Eine H-zu-L-Kopplung wuerde schnellen
Nachhall und langsames Substrat vor dem ersten Trennnachweis vermischen.

Verboten sind insbesondere:

- Rohpixel, Audiosamples oder vollstaendige Rezeptorsequenzen in `L`;
- Dock-, Quellen-, Modalitaets-, Objekt-, Episoden- oder Partneridentitaeten;
- Wiederholungszahl, Versuchszweig, Probe, Ergebnis oder Gegenhistorie;
- globale Mittelwerte, Rangfolgen, Cluster oder Aehnlichkeitsmetriken;
- Labels, Reward, Loss, Zielantworten oder Sollzustaende.

## 5. Atomare Kopplungsordnung S nach L nach S

Alle Rollen lesen denselben abgeschlossenen Vorzustand:

```text
(S_t, H_t, L_t, lokaler Weltkontakt_t, dt)
-> gemeinsamer Vorschlag (S_t+1, H_t+1, L_t+1)
-> atomare Uebernahme
```

`S -> L -> S` bezeichnet zwei Kausalrichtungen, keine sequentielle
Berechnung innerhalb desselben Schritts. `L_t+1` darf nicht sofort wieder als
Ursache von `S_t+1` gelesen werden.

### S nach L

Die lokale schnelle Feldlage darf eine kontinuierliche konstitutive Wirkung
auf `L` ausueben. Die konkrete Wirkungsform ist in S0 nicht festgelegt. Sie
darf weder Aktivitaet als Wichtigkeit deuten noch Wiederholung erkennen.

### L nach S

Der abgeschlossene L-Vorzustand muss einen lokalen inneren Beitrag zur
schnellen Feldtransition leisten koennen. Ein nachgeschalteter Leserwert,
Gain auf Rezeptoren oder Observerbericht erfuellt diese Richtung nicht.

### Nullgrenze

Bei neutralem `L`, deaktivierter L-Kopplung und identischem Vorzustand muss
die heutige schnelle Runtime bitgleich beziehungsweise innerhalb ihrer
bereits gebundenen numerischen Toleranz entstehen.

## 6. Ressourcen- und Bilanzgrenze

S0 fuehrt keine behauptete biologische Energie ein. Es bindet eine technische
Wirkungsbilanz, damit L keine unbegrenzte versteckte Quelle wird.

Pro atomarem Schritt muessen getrennt beobachtbar sein:

```text
W = Wirkung des vorhandenen Welt- und S-Feldpfads
X = interner Austausch zwischen S und L
D = lokale Dissipation oder Begrenzungswirkung
```

Verbindliche Bedingungen:

1. `L_i` bleibt fuer jeden endlichen gueltigen Vorzustand endlich und in
   `[-1, 1]`;
2. interne S-L-Wirkung wird als Austausch und nicht als zweite Welteingabe
   bilanziert;
3. Nullzustand ohne Weltwirkung und ohne S-L-Differenz bleibt exakt neutral;
4. die numerische Begrenzung darf keine inhaltliche Reset- oder Loeschphase
   ausloesen;
5. globale Renormierung ueber alle Feldorte ist als Organismusfunktion
   verboten;
6. Parameter und Zustandsbudget bleiben in Kandidat und Baselines gleich.

Ob S1 eine dissipative, austauschende oder anders begrenzte Naturform nutzt,
wird mit der konkreten Gleichung entschieden. S0 erlaubt keine unerklaerte
Eigenanregung.

## 7. Zeitskala

`L` besitzt keine eigene Uhr und keinen Wiederholungszaehler.

```text
technische Zeitbasis = dieselbe reale Organismusdauer dt wie fuer S
langsame Rolle       = geringere lokale Zustandsaenderung unter derselben
                       endlichen Wechselwirkung
relative Feldzeit    = spaeterer Beobachtungsbegriff, kein S1-Parameter
```

Die S1-Gleichung muss unter einer technisch aequivalenten Teilung desselben
Zeitintervalls konvergieren. Aufrufzahl oder Segmentierung duerfen keine
eigene Organismuswirkung erzeugen.

## 8. Pflichtbaselines

Vor einem S2-Versuch werden bei gleichem lokalen Zustands-, Parameter-,
Praezisions- und Zeitbudget mindestens gebunden:

1. `B0`: heutiger schneller MCM-Pfad ohne L;
2. `B1`: eine einzelne lineare Leaky-Spur von S;
3. `B2`: lineare reziproke Zweizustandskopplung S-L;
4. `B3`: begrenzter Integrator ohne reziproke Feldwirkung;
5. `B4`: statischer beziehungsweise zustandsabhaengiger Gain mit gleicher
   Zahl freier Parameter;
6. `B5`: Ablation der L-nach-S-Wirkung bei identischer L-Entwicklung.

Eine S1-Mechanik darf technisch mit einer Baseline identisch sein. Sie ist
dann ein Referenzsubstrat, aber kein eigenstaendiger Entwicklungskandidat.
Das verhindert, dass die notwendige Implementierung erneut durch eine
pauschale Rekurrenzkritik blockiert wird.

## 9. Technische S1-Abnahme

S1 ist nur technisch bestanden, wenn:

- Nullinvarianz und exakter schneller Nullpfad bestehen;
- alle L-Werte endlich und begrenzt bleiben;
- nur erlaubte lokale Vorzustaende gelesen werden;
- Berechnungsreihenfolge keinen Feldort bevorzugt;
- technische Zeitteilung denselben Grenzverlauf liefert;
- Observer an oder aus keinen Zustandsunterschied erzeugt;
- Snapshot und Wiederaufnahme bitgleich fortsetzen;
- L-Tausch und L-Neutralisierung als externe Testinterventionen moeglich sind;
- keine Rohdaten, versteckten Identitaeten oder Auswertungswerte persistieren;
- die Austausch- und Begrenzungsbilanz geschlossen berichtet wird.

Keiner dieser Punkte ist ein Memory-Befund.

## 10. Sofortige Verwerfung

Die konkrete S1-Mechanik wird verworfen, wenn mindestens eines gilt:

- L liest Weltinformation ausserhalb des normalen S-Pfads;
- eine neue L-Schicht, Routinglogik oder Datenbank entsteht;
- der Observer veraendert Bildung oder Wirkung;
- eine spezielle Schreib-, Abruf-, Konsolidierungs- oder Loeschphase noetig
  ist;
- die Wirkung haengt von Tickzahl, Segmentierung oder Versuchsnamen ab;
- Grenzen werden nur durch ereignisabhaengigen Reset eingehalten;
- L wirkt nur als nachgeschalteter Messwert oder fester Rezeptorgain;
- neutralisiertes L veraendert weiterhin den schnellen Nullpfad;
- der Zustand kann Rohmedien oder feste Inhalte rekonstruieren, weil diese
  direkt gespeichert wurden.

## 11. Aussagegrenze

Der S0-Vertrag belegt nur, dass ein sauberer technischer Entwicklungsraum fuer
eine langsamere lokale Feldkomponente definiert ist. Er belegt keine
Praegung, kein Memory, keine Feldzeitverdichtung, keine Organisation, keine
Semantik, kein Erleben und keine KI.

## Entscheidung

```text
S0 Funktionsrolle:                  gebunden
S0 lokaler Darstellungsraum:        gebunden
S0 Ressourcen- und Bilanzgrenze:    gebunden
S0 Pflichtbaselines:                gebunden
S0 technische Verwerfungskriterien: gebunden
konkrete S1-Naturgleichung:          nachfolgend in S1-A gebunden
Runtime-Aenderung:                   nachfolgend in S1-B opt-in implementiert
Forschungslauf:                      nein
```

## Bester naechster Schritt

S1-A ist mit der
[kapazitaetsgewichteten reziproken S-L-Akkommodation](S1A_NATURGLEICHUNG_KAPAZITAETSGEWICHTETE_REZIPROKE_AKKOMMODATION.md)
gebunden, S1-B ist technisch implementiert, S2-A/S2-B sind vorregistriert und
der S2-C-Kern ist umgesetzt. S2-C2 bis S2-C8 binden Einzelbatch, r1.a/c1.a,
S/H-Angleichung, Probe P, N8, Observer, Einpaardistanzen und D_pair(1).
S2-C9 bis S2-C16 binden A/B-Pfade, Container, `D_world_pair(8)` und die
kanonische End-to-End-Komposition. Der S2-Zwischenentscheid stoppt weitere
Referenzerweiterung ohne konkreten Kandidaten. Der statische S1-C-Vertrag
eines minimalen nichtlinearen lokalen und reversiblen Substratkandidaten ist
inzwischen gebunden, waehlt aber noch
keine Gleichung. S1-D reduziert die gepruefte MCM-spezifische Annahme auf
eine zustandsabhaengige Relaxationsbaseline und stoppt ihre Implementierung.
S1-E begruendet keine zweite lokale Variable und bestimmt
verteilte kausale Nichtseparierbarkeit als offene Feldanforderung. Der
statische S1-F-Zulassungsvertrag ist inzwischen gebunden und oeffnet keinen
geschlossenen Traegerzweig. Der S1-G-Richtungsentscheid ist inzwischen
gebunden: Feldwahrnehmung bleibt
technisch aktiv, Substratimplementierung pausiert. Als naechstes folgt W1-A
mit dem technischen Wahrnehmungspfad-Bestandsaudit. Noch kein
S2-Praegungsversuch.
