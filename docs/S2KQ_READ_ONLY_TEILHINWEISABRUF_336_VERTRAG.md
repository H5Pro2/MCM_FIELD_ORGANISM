# S2-KQ - Read-only Teilhinweisabruf aus der Zwei-Bereich-Memory 336

## Status und Zweck

`S2KQ_STATIC_PARTIAL_CUE_RETRIEVAL_336_CONTRACT_COMPLETE`

S2-KQ bindet genau eine begrenzte visuelle Funktion:

```text
maskierte aktuelle 336-Werte-Wahrnehmung
+ unabhaengiger Maskenbeleg
+ validierter bestehender 336-Werte-Memoryzustand
-> belegte Slots nur auf beobachteten visuellen Positionen pruefen
-> B4 und Fast intern zu A_RECENT aufloesen
-> zwischen A_RECENT und B_STABLE zulassen oder enthalten
-> getrennte Kontext-Hypothese oder Enthaltung
```

Eine vorherige Vollprobe ist verboten. Zielwerte, Sollbereich und
Auswertungserwartung sind vor dem versiegelten Funktionsergebnis nicht
zugaenglich. Die Funktion veraendert weder die aktuelle Wahrnehmung noch
Memory oder Feld.

S2-KQ ist ein statischer Funktions-, Erreichbarkeits- und
Falsifikationsvertrag. Er implementiert und startet nichts. Neue Runner-,
Recorder-, Registry- oder Plattforminfrastruktur ist nicht freigegeben.

Die Slow-Mehrdeutigkeitsgeschichte dieses Vertrags ist durch S2-KR eng
korrigiert und unten bereits in ihrer korrigierten Form wiedergegeben.

## Gebundener Ausgangsstand

Technischer Ausgangsstand ist Commit
`702afbb3689886f907c1002150aca03781d54bb2`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Zwei-Bereich-Zulassung 336 | `tools/_s2kn_private_two_area_context_admission_336.py` | `15ccfa47195887a590b0609fbad9def93c5cd48222254a7a688fb173b14930eb` |
| unabhaengige Zwei-Bereich-Baseline | `tools/_s2kn_private_direct_two_area_admission_baseline.py` | `6071a5390ecf9200f472c0ab4e444e2acf2f1e54f8ac52fca078dbfd6c3d7939` |
| 336-Werte-Findingbinder | `tools/_s2kj_validated_perceptual_finding_336.py` | `920762c4a29d2baf579829fdb896526c5a2901ffd3629d52ab1658b0436a0b6c` |
| bestehender Vollprobenleser | `tools/_s2jw_profiled_memory_read_only.py` | `efd3dad03810811acc3fc124543bf8aa524ad1de4585210f2852f7048dbf93e7` |
| atomarer 336-Werte-Zustand | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| reale S2-JX-Fixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |
| realer S2-KP-Funktionsbeleg | `reports/s2kp/s2kp-real-context-admission-336-20260903-01/result.json` | `dfe691f7da48f4bdc0b8a8340ee2f3c9dad867e528f34071ec00000ac056df82` |

S2-KP bleibt als bestaetigter Befund bestehen. Seine durch Vollproben
ausgewaehlten Kandidaten sind jedoch kein zulaessiger Eingang fuer S2-KQ.
Ein spaeterer S2-KQ-Lauf muss die Memoryzustaende frisch bilden und direkt
deren belegte Slots lesen.

## Aufgabengrenze

Der erste S2-KQ-Umfang ist eine visuelle Teilhinweisaufgabe im unveraenderten
Default-Live-Profil:

- 48 auditive und 288 visuelle Rezeptorwerte bleiben quellen- und
  zustandsgebunden;
- die visuellen Positionen `0..31` sind `OBSERVED`;
- die visuellen Positionen `32..287` sind `MASKED`;
- die Maske ist ein unabhaengiger, vor der Probe gebildeter Beleg;
- die 48 auditiven Werte duerfen in diesem Versuch keinen visuellen
  Kandidaten auswaehlen, bevorzugen oder ausschliessen;
- maskierte Werte duerfen fuer die Kandidatensuche nicht gelesen werden.

S2-KQ erkennt keine Maske automatisch. Eine audiovisuelle Teilhinweissuche
mit modalitaetsgetrennter Evidenz benoetigt einen eigenen spaeteren Vertrag.

## Verbindliche Eingangsrollen

Ein spaeterer reiner Aufruf akzeptiert genau:

1. eine validierte, unveraenderliche `S2JVCompositeStateV1`;
2. eine strikt spaetere `MaskedMemoryCue336V1` mit eigenem Quelldigest,
   Zeitfenster, Profil- und Konfigurationsdigest;
3. einen unabhaengigen `VisualMaskPlan336V1` mit exakt 32 beobachteten und
   256 maskierten Positionen;
4. einen vor dem Scan gebildeten Aufrufdigest.

`MaskedMemoryCue336V1` enthaelt auf beobachteten Positionen echte
Rezeptorwerte und auf maskierten Positionen ausschliesslich den typisierten
Marker `MASKED`. Es enthaelt keine Vollwerte, Zielwerte, Geschichte,
Fallkennung oder erwartete Entscheidung.

Vor dem ersten Slotzugriff muessen Profil, Dimensionen, FIFO-Anatomie,
Fast-Zustand, beide PPB-Banken, Quellenzeit und Zustandsdigest vollstaendig
validiert sein. Beschaedigte oder widerspruechliche Eingaben erzeugen keine
Teilbefunde.

## Direkter Slotbestand

Der Scan darf ausschliesslich den validierten Zustand lesen:

| interne Rolle | maximales Inventar | zulaessige Werte |
| --- | ---: | --- |
| `B4_RECENT` | 9 belegte FIFO-Slots | visueller Anteil der gespeicherten 336 Werte |
| `TSPM_FAST` | 3 belegte Fast-Slots | gespeicherte 288 visuellen Fast-Werte |
| `B_STABLE_VISUAL` | 4 visuelle PPB-Slots | nur stabile Prototypen mit Support mindestens 3 |

Freie Slots sind gueltig abwesend. Instabile visuelle Slow-Slots bleiben
interne Diagnoseevidenz und sind keine `B_STABLE`-Kandidaten. Auditive
Slow-Slots sind fuer diese visuelle Aufgabe kein Kandidateninventar.

Der bestehende `probe_s2jv_composite_read_only` ist fuer S2-KQ unzulaessig:
Er benoetigt eine vollstaendige 336-Werte-Probe und waehlt innerhalb einer
Bank einen rangierten Treffer. S2-KQ muss dagegen jeden belegten Slot
direkt pruefen und die Trefferanzahl erhalten.

## Beobachtete Gleichheit

Ein Slot ist `OBSERVED_MATCH`, wenn jede der 32 beobachteten Positionen mit
dem dort gebundenen Rezeptorwert uebereinstimmt. Eine einzige belegte
Abweichung ergibt `OBSERVED_MISMATCH`. Maskierte Positionen tragen niemals
zur Entscheidung bei.

Der erste Umfang uebernimmt keine L1-Schwelle und keine Float-Rundung. Seine
Erreichbarkeitsfixtures verwenden ausschliesslich rezeptorisch erzeugte
Werte, deren beobachtete Komponenten durch homogene Wiederholung oder exakt
darstellbare binaere Mittelwerte unveraendert bleiben. Fuer nicht exakt
gebundene PPB-Prototypwerte ist ohne prospektive 336-Werte-Herkunftsevidenz
kein regulaerer Match zulaessig; der Aufruf stoppt dann fail-closed. Die
fruehere 18-Werte-Aggregatbindung darf nicht als 336-Werte-Beleg
umetikettiert werden.

Diese enge Regel prueft Teilhinweisabruf, nicht Variationstoleranz. Die
bereits bestaetigte Memory-Aehnlichkeitsfunktion und ihre Schwellen bleiben
unveraendert.

## Bankbefunde ohne Rangfolge

Jede der drei internen Banken erzeugt genau einen der folgenden Befunde:

```text
BANK_ABSENT_VALID
BANK_NO_OBSERVED_MATCH
BANK_UNIQUE_OBSERVED_MATCH
BANK_MULTIPLE_OBSERVED_MATCHES
```

Die Bedeutung ist rein kardinal:

- `BANK_ABSENT_VALID`: kein zulaessiger belegter Slot;
- `BANK_NO_OBSERVED_MATCH`: zulaessige Slots vorhanden, aber null Treffer;
- `BANK_UNIQUE_OBSERVED_MATCH`: genau ein Treffer;
- `BANK_MULTIPLE_OBSERVED_MATCHES`: mindestens zwei Treffer.

Bei Mehrfachtreffern ist weder kleinste Distanz noch juengster Index noch
Support noch Slot-ID ein Tie-Breaker. Auch vollstaendig wertgleiche
Mehrfachslots bleiben mehrere Treffer und fuehren zur Enthaltung.

Jeder Scanbeleg bindet Bankrolle, gepruefte Slot-IDs und Slotdigests,
Trefferzahl, geordneten Treffersetdigest, Maskendigest, Probe- und
Zustandsdigest. Vollstaendige Kandidatenwerte werden nur fuer einen
eindeutigen Treffer in den nachfolgenden internen Bereichsbefund uebergeben.

## Interne Aufloesung von A_RECENT

B4 und Fast bleiben interne Rollen genau eines oeffentlichen Bereichs.

1. Hat B4 oder Fast `BANK_MULTIPLE_OBSERVED_MATCHES`, entsteht
   `A_RECENT_INTERNAL_AMBIGUITY`; es gibt keinen A-Kandidaten.
2. Besitzt genau eine interne Bank einen eindeutigen Treffer, entsteht ein
   `A_RECENT`-Kandidat mit genau diesem Herkunftsbeleg.
3. Besitzen beide einen eindeutigen Treffer und sind die vollstaendigen 288
   visuellen Werte samt Wertedigest gleich, entsteht ein A-Kandidat mit zwei
   Herkunftsbelegen.
4. Besitzen beide einen eindeutigen Treffer, ihre vollstaendigen visuellen
   Werte sind aber verschieden, entsteht `A_RECENT_INTERNAL_CONFLICT`; es
   gibt keinen A-Kandidaten.
5. Sind beide Banken leer, entsteht `A_RECENT_ABSENT_VALID`.
6. Gibt es keinen Treffer, aber mindestens einen zulaessigen internen Slot,
   entsteht `A_RECENT_NOT_APPLICABLE`.

Interne Mehrdeutigkeit und interner Konflikt sind gueltige fachliche
Enthaltungsgruende. Beschaedigte Evidenz ist dagegen kein regulaerer Status.

## Aufloesung von B_STABLE

Fuer die visuelle Slow-Bank gilt:

- kein stabiler Slot: `B_STABLE_ABSENT_VALID`;
- stabile Slots, aber kein Treffer: `B_STABLE_NOT_APPLICABLE`;
- genau ein Treffer: `B_STABLE_APPLICABLE` mit einem Kandidaten;
- mehrere Treffer: `B_STABLE_INTERNAL_AMBIGUITY` ohne Kandidaten.

Support darf nur Stabilitaet belegen. Er darf keine Rangfolge zwischen
mehreren passenden Prototypen erzeugen.

## Oeffentliche Zwei-Bereich-Entscheidung

Die oeffentliche Kardinalitaet wird erst nach den internen Scans gebildet.
Es existieren weiterhin hoechstens zwei Kandidatenbereiche:

```text
A_RECENT
B_STABLE
```

Harte interne Konflikte oder Mehrdeutigkeiten fuehren immer zur Enthaltung,
auch wenn der jeweils andere Bereich eindeutig waere:

```text
A_RECENT_INTERNAL_AMBIGUITY -> ABSTAIN_INTERNAL_AMBIGUITY
A_RECENT_INTERNAL_CONFLICT  -> ABSTAIN_INTERNAL_CONFLICT
B_STABLE_INTERNAL_AMBIGUITY -> ABSTAIN_INTERNAL_AMBIGUITY
```

Ohne harten internen Befund gilt:

| A-Kandidat | B-Kandidat | Bereichslage | Ergebnis |
| ---: | ---: | --- | --- |
| 0 | 0 | beide Bereiche leer | `ABSTAIN_NO_CONTEXT` |
| 0 | 0 | mindestens ein Bereich belegt, aber unpassend | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| 1 | 0 | eindeutig | `ADMIT_SINGLE_CONTEXT`, `A_RECENT` |
| 0 | 1 | eindeutig | `ADMIT_SINGLE_CONTEXT`, `B_STABLE` |
| 1 | 1 | zwei Bereiche anwendbar | `ABSTAIN_AMBIGUOUS_CONTEXT` |

Auch wertgleiche A- und B-Kandidaten bleiben zwei oeffentliche Kandidaten.
S2-KQ fuehrt keine Konsistenz-Sonderzulassung, Rangfolge oder automatische
Auswahl ein.

## Getrennte Hypothese

Nur `ADMIT_SINGLE_CONTEXT` darf genau eine unveraenderliche
`PartialCueContextHypothesis336V1` erzeugen. Sie bindet:

- ausschliesslich `A_RECENT` oder `B_STABLE` als Bereich;
- die 256 maskierten Positionen und die zugehoerigen Kandidatenwerte;
- Slot-, Bankscan-, Bereichs-, Probe-, Masken-, Zustands- und
  Hypothesendigest;
- bei A einen oder zwei interne Herkunftsbelege, ohne B4 oder Fast als
  oeffentlichen Bereich auszugeben.

Die Hypothese enthaelt keine beobachteten Werte, keine zusammengesetzte
Ersatzwahrnehmung, keine Feldkontakte und keine Behauptung, dass maskierte
Werte wahrgenommen wurden. S2-KQ ruft keinen Kontextverbraucher auf.

## Statische Erreichbarkeit

Alle folgenden Quellen sind echte `1920 x 1080 RGB8`-Bilder mit dem
unveraenderten `12 x 8 x 3`-Rezeptorraster sowie strikt fortgeschriebene
PCM-Fenster. Kandidatenwerte duerfen nie hinter dem Rezeptor eingesetzt
werden.

### Bestehende reale Basis

Die frisch rekonstruierbare S2-JX-Geschichte

```text
X X X X Y Y D1 D2 D3 D4 D5 D6 D7 D8 D9
```

materialisiert zwei Grundfaelle:

- maskiertes `D9`: unter den neun juengsten B4-Eintraegen und drei
  Fast-Slots passt jeweils nur D9; beide Werte sind gleich, X-Slow passt
  sichtbar nicht. Ergebnis `A_RECENT`;
- maskiertes `X`: kein D-Slot passt auf allen beobachteten Positionen,
  waehrend der bitidentisch gebildete stabile X-Prototyp eindeutig passt.
  Ergebnis `B_STABLE`.

Die zyklischen binaeren S2-JX-Muster besitzen auf `0..31` fuer verschiedene
Ordinalzahlen unterschiedliche Teilfolgen. Diese Eindeutigkeit folgt aus
der gebundenen Periode 11 und wird vor einer spaeteren Ausfuehrung fuer alle
tatsaechlich belegten Slots nochmals ohne Memoryaufruf materialisiert.

### Bereichsmehrdeutigkeit

Die S2-KP-Geschichte

```text
B0 B0 B0 B0 D1 D2 D3 D4 D5 D6 D7 D8 D9 A0
```

erzeugt eindeutig A0 in B4/Fast und B0 stabil in Slow. Beide sind auf
`0..31` gleich; ihre Abweichung auf Position 32 ist maskiert. Es entstehen
ein A- und ein B-Kandidat, daher `ABSTAIN_AMBIGUOUS_CONTEXT`.

### Mehrere interne B4-Treffer

Die frische Geschichte `C0 C1` wird gegen eine maskierte C1-Probe geprueft.
C0 und C1 unterscheiden sich nur auf der maskierten Position 32. Anders als
bei der frueheren Vollprobe passen deshalb beide B4-Slots. Der korrekte
S2-KQ-Befund ist `BANK_MULTIPLE_OBSERVED_MATCHES` und danach
`A_RECENT_INTERNAL_AMBIGUITY`; es darf kein rangierter C1-Treffer entstehen.

### Echter B4/Fast-Konflikt ohne B4-Mehrfachtreffer

Eine getrennte elfstufige Geschichte verwendet nur die Carrier 0
(`OBSERVED`) und 32 (`MASKED`); alle uebrigen visuellen Carrier bleiben 0.
Die notierten Werte sind Rezeptorwerte:

| Rolle | Carrier 0 | Carrier 32 |
| --- | ---: | ---: |
| `C0` | `3/4` | `0` |
| `C1` | `1/4` | `1` |
| `U` | `1` | `0` |
| `V` | `1/4` | `0` |
| `T` | `1/2` | `1` |

Die Geschichte lautet:

```text
C0 C1 U V U V U V U V T
```

Alle Werte sind durch ganzzahlige `uint8`-Blocksummen erzeugbar. Fuer
`1/2` enthaelt der betroffene 21.600-Byte-Kanalblock gleich viele Bytes 127
und 128; fuer `1/4` entsprechend ein Viertel Byte 63 und drei Viertel Byte
64; fuer `3/4` drei Viertel Byte 191 und ein Viertel Byte 192. Es wird kein
Memoryvektor handgeschrieben.

Mit dem unveraenderten Fast-Faktor `0.5` gilt auf Carrier 0:

```text
C0,C1 -> 1/2
1/2,U -> 3/4
3/4,V -> 1/2
```

Jedes weitere U/V-Paar kehrt exakt zu `1/2` zurueck. Nach vier Paaren und T
ist Fast auf der beobachteten Position exakt `1/2`, unterscheidet sich aber
auf Carrier 32 vom exakten B4-T-Wert. Wegen B4-Kapazitaet 9 sind C0 und C1
vor der Probe verdraengt; die acht U/V-Eintraege unterscheiden sich auf
Carrier 0 von T. B4 besitzt daher genau einen Teilhinweistreffer, Fast
ebenfalls genau einen, ihre Vollwerte sind verschieden. Ergebnis:
`A_RECENT_INTERNAL_CONFLICT` und Enthaltung.

Die auditive Quelle bleibt in dieser Geschichte bitidentisch im Inhalt,
aber besitzt je Formation ein neues strikt spaeteres PCM-Fenster und einen
neuen Quelldigest. Sie beeinflusst den visuellen Teilscan nicht.

### Mehrere stabile Slow-Treffer

Zwei reale Bilder `S0` und `S1` sind auf `0..31` identisch und unterscheiden
sich auf allen maskierten Positionen `32..287` um den vollen Bytebereich.
Die getrennte Bildung

```text
S0 S0 S0 S0 S1 S1 S1 S1 D1 D2 D3 D4 D5 D6 D7 D8 D9
```

erzeugt wegen visueller Volldistanz `256/288 > 0.01` zwei getrennte stabile
Slow-Prototypen mit Support 3. Die neun paarweise getrennten D-Zustaende
verdraengen S0 und S1 vollstaendig aus B4. Der S0-Fast-Slot laeuft vor
seinem Ablauf bereits bei D2 durch LRU-Ersetzung verloren; S1 wird bei D3
ersetzt. D1 bis D9 erzeugen wegen ihrer visuellen Abstaende oberhalb der
Fast-Schwelle keine Fast-Updates und damit keine neuen Slow-Prototypen.

Die maskierte S0-Probe findet folglich keinen A-Treffer, aber genau die zwei
stabilen Slow-Prototypen. B4-, Fast- und Slow-Scan werden vollstaendig
abgeschlossen. Erst danach entstehen `A_RECENT_NOT_APPLICABLE`,
`B_STABLE_INTERNAL_AMBIGUITY` und Enthaltung; Support darf keinen Gewinner
bestimmen. Der fallbezogene Bildungsumfang betraegt 17 statt 8 Formationen.
Die Scan- und Vergleichsbudgets bleiben unveraendert.

### Abwesenheit und sichtbare Unvereinbarkeit

- Ein frisch validierter Nullzustand ohne Formation ergibt
  `ABSTAIN_NO_CONTEXT`.
- Ein frisch rekonstruierter S2-JX-Endzustand wird mit einer spaeteren
  realen Probe geprueft, deren beobachteter Carrier 0 exakt `1/2` ist.
  Alle dort vorhandenen binaeren B4-, Fast- und stabilen X-Werte besitzen
  auf dieser Position 0 oder 1. Es gibt vorhandene, aber keine passenden
  Kandidaten; Ergebnis `ABSTAIN_NO_APPLICABLE_CONTEXT`.

Damit sind Single-A, Single-B, A/B-Mehrdeutigkeit, interne
B4-Mehrdeutigkeit, echter B4/Fast-Konflikt, Slow-Mehrdeutigkeit, gueltige
Abwesenheit und sichtbare Unvereinbarkeit statisch erreichbar. Keine dieser
Ableitungen verwendet Vollprobenergebnisse als Funktionseingang.

## Nichtzirkularitaet und Auswertung

Ein spaeterer Versuch bindet drei getrennte Wurzeln:

```text
FormationPlan -> MemoryState
PartialCuePlan -> MaskedMemoryCue336V1
EvaluationPlan -> Zielwerte und erwarteter Status
```

Formation und Teilhinweisprobe duerfen den Evaluationsplandigest nicht
enthalten. Erst ein versiegeltes read-only Funktionsergebnis darf mit dem
vorab versiegelten Evaluationsplan verbunden werden.

Der Auswerter prueft getrennt:

- korrekte Slotinventarisierung und Trefferkardinalitaet;
- korrekte A-interne Aufloesung;
- korrekte oeffentliche A/B-Zulassung oder Enthaltung;
- Trennung der Hypothese von aktueller Wahrnehmung und Feld;
- identische Vor-/Nachzustandsdigests;
- Uebereinstimmung mit der unabhaengigen Direktbaseline.

Fachlich falsche, aber vollstaendig belegte Ergebnisse falsifizieren die
jeweilige S2-KQ-Prognose. Quellen-, Masken-, Slot-, Digest-, Dimensions-,
Read-only- oder Aufzeichnungsbruch ergibt `NOT_EVALUABLE` und darf nicht als
regulaere Enthaltung erscheinen.

## Direkte Pflichtbaseline

Die unabhaengige generische Slotscan-/Maskenbaseline erhaelt denselben
validierten Zustand und dieselbe Teilhinweisprobe. Sie muss separat:

1. alle belegten B4-, Fast- und stabilen visuellen Slow-Slots iterieren;
2. ausschliesslich die beobachteten Positionen vergleichen;
3. pro Bank nur die Trefferzahl und Trefferdigests bilden;
4. B4/Fast nach derselben oeffentlichen A-Anatomie aufloesen;
5. erst danach die Kardinalitaet von A und B bestimmen;
6. hoechstens eine getrennte Hypothese bilden.

Die Baseline darf weder die spaetere S2-KQ-Funktion noch deren Scan-, A-
Projektions-, Entscheidungs- oder Hypothesenhelfer aufrufen. Sie besitzt
keinen Zugriff auf Zielwerte oder Sollstatus.

## Ressourcen- und Groessengrenzen

Pro Funktionsarm gelten folgende harte Maxima:

| Ressource | Maximum |
| --- | ---: |
| validierte Memoryzustaende | 1 |
| maskierte Proben / Maskenplaene | `1 / 1` |
| gescannte B4-/Fast-/visuelle Slow-Slots | `9 / 3 / 4` |
| gesamte gescannte Slots | 16 |
| beobachtete Vergleiche | `16 x 32 = 512` |
| zusaetzliche B4/Fast-Vollwertvergleiche | 288 |
| gesamte funktionale Wertvergleiche | 800 |
| oeffentliche Bereichskandidaten | hoechstens 2 |
| ausgegebene Hypothesenwerte | 256 oder 0 |
| logische Funktionsoperationen | hoechstens 12 |
| Memory-, Rezeptor-, Verbraucher- oder Feldaufrufe | 0 |
| kanonische Ausgabe | hoechstens 32.768 Byte |

Funktion und Direktbaseline erhalten identische Grenzen. Fuer beide Arme
zusammen gelten damit hoechstens 32 Slotpruefungen, 1.600 Wertvergleiche,
24 logische Operationen und 65.536 Byte kanonische Ergebnisdaten. Das
validierte Zustandsobjekt wird nicht dupliziert oder vollstaendig in das
Ergebnis serialisiert; Zustands-, Slot- und Wertedigests binden die
Herkunft.

Vor einer Implementierung muss die konkrete unveraenderliche Ausgabeform
gegen diese Bytegrenzen materialisiert werden. Eine Grenzueberschreitung
darf nicht durch Weglassen von Slotkardinalitaet oder Herkunftsbelegen
verdeckt werden.

## Falsifikations- und Stoppregeln

S2-KQ ist bei gueltiger Evidenz fachlich falsifiziert, wenn:

- eine vorherige Vollprobe oder deren ausgewaehlter Kandidat benoetigt wird;
- ein maskierter Wert die Kandidatensuche beeinflusst;
- ein passender Slot wegen Index, Support, Distanz oder Listenreihenfolge
  bevorzugt wird;
- mehrere passende Slots oder beide oeffentlichen Bereiche zu einer
  Zulassung fuehren;
- B4 oder Fast als dritter oeffentlicher Bereich erscheint;
- ein interner A-Konflikt durch B umgangen wird;
- eine Hypothese beobachtete Werte, Ersatzwahrnehmung oder Feldkontakte
  enthaelt;
- Funktion und unabhaengige Direktbaseline bei identischem Eingang
  abweichen;
- ein Probezugriff irgendeinen Memoryzustand veraendert.

Der Aufruf stoppt fail-closed und ohne Teilhypothese bei:

- ungueltiger State-, Slot-, Profil-, Quellen-, Zeit- oder Digestbindung;
- nicht unabhaengiger, unvollstaendiger oder ueberlappender Maske;
- Zielwerten oder Evaluationsrollen im Funktionsinput;
- nicht prospektiv belegbarer sichtbarer Gleichheit;
- mehr als `9/3/4` Slots oder irgendeiner Ressourcenueberschreitung.

## Aussagegrenze und naechster Schritt

S2-KQ bindet erstmals die direkte Suche in einem bestehenden
336-Werte-Memoryzustand aus einer unvollstaendigen aktuellen Wahrnehmung.
Es behauptet noch keinen realen Teilhinweisabruf, keine automatische
Maskenerkennung, keine Variationstoleranz, keine Semantik und keine
Feldwirkung.

Nach statischer Abnahme genuegen eine kleine private read-only
Slotscan-/A-Projektionsfunktion, eine unabhaengige Direktbaseline und
fokussierte neutrale Tests. Eine neue Lauf- oder Recorderarchitektur ist
nicht begruendet. Erst danach darf ein kleiner realer Funktionslauf mit
frisch gebildeten Zustaenden separat freigegeben werden.
