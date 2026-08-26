# S1-XU: Statischer Funktions- und Falsifikationsvertrag

## Gegenstand

S1-XU bindet ausschliesslich die technische Funktion **zeitliche
Aktualisierung unter begrenzter Kapazitaet**. Geprueft werden soll spaeter,
ob ein bestehender perzeptiver Zustand durch eine geordnete Folge teilweise
aehnlicher und teilweise widerspruechlicher Eingaben kontrolliert
fortgeschrieben werden kann.

Der Vertrag fuehrt keine Gleichung, Parameter, Implementierung, Tests oder
Ausfuehrung ein. Feldintegration, Feldrueckwirkung, Semantik und
Produktionspfade bleiben ausgeschlossen.

## Getrennte Systemrollen

### PPB-1

PPB-1 ist die zu pruefende private Engineeringkomponente. Sie darf in einem
spaeteren, gesondert freizugebenden Ablauf nur den begrenzten Bankzustand
verwenden, der aus der gebundenen Eingabegeschichte erreichbar ist.

### Statische Prototypbank

Die Gegenbaseline besitzt dieselbe Modalitaet, dieselbe Zahl von
Prototypslots, dieselben Eingaben in derselben Reihenfolge und dasselbe
Probebudget. Ihre nach der gemeinsamen Bildungsphase gebundenen Prototypen
bleiben unveraendert. Spaetere Expositionen werden ihr vollstaendig
uebergeben, duerfen aber ihre statischen Prototypen nicht aktualisieren.

Beide Systeme erhalten weder Rohhistorie beim Abruf noch zusaetzliche
Eingaben, Slots, Proben oder Wiederholungen. Ein Vorteil durch ungleiche
Budgets macht den gesamten Vergleich ungueltig.

## Gemeinsame Ablaufanatomie

Jede Geschichte besitzt dieselben getrennten Phasen:

1. **Frischstart:** unabhaengiger leerer Zustand mit identischer Kapazitaet.
2. **Bildung:** dieselbe geordnete Anfangsexposition fuer beide Systeme.
3. **Aktualisierung:** dieselbe geordnete spaetere Exposition; nur die
   jeweilige vorab definierte Systemregel darf den Zustand behandeln.
4. **Trennung:** keine Rohhistorie und kein nachtraeglicher Zustandsumbau.
5. **Read-only Probe:** identische spaetere Proben in identischer Reihenfolge.
6. **Receipt:** getrennte Zustands-, Abruf-, Verdraengungs- und
   Fehlverhaltensrollen.

Probe und Auswertung duerfen keinen Zustand veraendern. Geschichten duerfen
keinen Zustand untereinander tragen.

## Fuenf verpflichtende Geschichten

### H1: Wiederholte Bestaetigung

Ein bereits gebildeter Zustand erhaelt weitere ausreichend aehnliche
Expositionen. Die spaetere Probe enthaelt eine gebundene aehnliche Variante
und eine gebundene negative Kontrolle.

Die Funktion ist nur korrekt, wenn PPB-1 die positive Probe nicht schlechter
als vor der Bestaetigung behandelt, keine unbegruendete neue Identitaet
erzeugt und die negative Kontrolle nicht zusaetzlich akzeptiert. Mehr
Support, ein neuer Digest oder eine geaenderte Slotzahl reichen nicht als
Funktionsbefund.

### H2: Graduelle Veraenderung

Ausgehend von einem gebildeten Ausgangszustand folgt eine geordnete Kette
kleiner, jeweils benachbarter Veraenderungen bis zu einem vorab gebundenen
Endzustand. Die Probe prueft Ausgang, Zwischenlage, Endzustand und negative
Kontrolle getrennt.

Die dynamische Gegenprognose lautet: PPB-1 bildet die Richtung der
erreichbaren Aktualisierung im spaeteren Abruf ab. Gegenueber der statischen
Bank muss die Endzustandsprobe funktional besser behandelt werden, ohne dass
die negative Kontrolle schlechter wird. Ein allein verschobener Prototyp
ohne besseren Abruf ist kein Erfolg.

### H3: Widerspruechliche Wahrnehmung

Nach stabiler Bildung folgen Expositionen eines vorab als widerspruechlich
abgegrenzten Zustands. Die Kapazitaet erlaubt je nach spaeter gebundener
Fixture entweder eine getrennte Aufnahme oder zwingt zu einer kontrollierten
Entscheidung. Ausgangs- und Konfliktzustand werden anschliessend getrennt
read-only geprueft.

Zulaessig sind nur vorab registrierte Ergebnisse: klare Trennung,
kontrollierte Aktualisierung oder kontrollierte Verdraengung. Unkontrollierte
Mittelung, bei der beide Proben falsch zugeordnet werden, gilt als
Fehlverhalten. Der gewaehlte Sollfall muss vor jeder Implementierung
eindeutig gebunden werden.

### H4: Kapazitaetsdruck und Verdraengung

Die Bank wird bis zur identischen Kapazitaetsgrenze belegt. Danach trifft
genau ein neuer, vorab abgegrenzter Zustand ein. Vor der Ausfuehrung muss
feststehen, welcher vorhandene Zustand nach der technischen
Verdraengungsregel erhalten und welcher freigegeben werden soll.

Gemessen werden Kapazitaetseinhaltung, Opferidentitaet, erhaltene
Identitaeten, Aufnahme des neuen Zustands und spaetere Abrufqualitaet aller
betroffenen Proben. Ueberkapazitaet, Doppelbelegung, nichtdeterministischer
Gleichstand oder ein nicht registriertes Opfer machen den Fall ungueltig
beziehungsweise fehlerhaft.

### H5: Spaeterer Abruf nach Aktualisierung

Nach einer gueltigen Aktualisierung folgt eine gebundene Trennphase ohne
Rohdatenzugriff. Danach werden der aktualisierte Zustand, der fruehere
Zustand und eine negative Kontrolle read-only geprueft.

PPB-1 muss die vorab gebundene aktualisierte Zielprobe funktional besser
oder eindeutig anders gemaess Sollrolle behandeln als die statische Bank.
Der Abruf darf weder Bankzustand noch Identitaet, Ablaufrolle oder
Verdraengungsstand veraendern.

## Getrennte Messrollen

### Aktualisierung

- Distanz und Erkennungsentscheidung fuer alte, zwischenliegende und neue
  Probe vor und nach der Aktualisierungsphase;
- gerichtete Verbesserung zur vorab gebundenen Zielprobe;
- keine Ableitung allein aus Digest-, Slot- oder Zaehleraenderung.

### Zustandsidentitaet

- Fortsetzung einer vorhandenen Identitaet;
- Neuanlage einer getrennten Identitaet;
- explizite Freigabe oder Verdraengung;
- keine doppelte, verlorene oder nachtraeglich umgedeutete Identitaet.

Identitaet ist eine Audit- und Kausalrolle, kein eigener Funktionsgewinn.

### Abrufqualitaet

- read-only Distanz und Erkennungsentscheidung pro registrierter Probe;
- positive, aehnliche und negative Proben getrennt;
- direkter gepaarter Vergleich beider Systeme fuer dieselbe Probe.

### Verdraengung

- Kapazitaet vor und nach dem neuen Zustand;
- erwartete und tatsaechliche Opferrolle;
- Erhaltungsstatus aller nicht zu verdraengenden Zustaende;
- Abruf des neuen, erhaltenen und freigegebenen Zustands.

### Fehlverhalten

- falsche positive und falsche negative Zuordnung;
- Veraenderung waehrend read-only Probe;
- Zugriff auf Rohhistorie;
- Ueberkapazitaet, Doppelbelegung oder Teiltransition;
- Retry, Reihenfolgedrift oder ungebundene Gleichstandsentscheidung.

## Erfolgs-, Stopp- und Ungueltigkeitsregeln

Ein spaeterer Ablauf darf nur als funktional erfolgreich gelten, wenn:

1. alle Geschichten aus getrennten Frischzustaenden vollstaendig vorliegen;
2. PPB-1 und Baseline identische Eingabe-, Kapazitaets- und Probebudgets
   erhalten;
3. H1 keine Sicherheitsregression zeigt;
4. H2 und H5 eine vorab gebundene bessere oder funktional andersartige
   Abrufreaktion fuer den aktualisierten Zustand zeigen;
5. H3 die vorab registrierte Konfliktrolle ohne unkontrollierte
   Fehlzuordnung erfuellt;
6. H4 Kapazitaet und vorab registrierte Verdraengungsrolle einhaelt;
7. keine Entscheidung nur auf Zustandszahl, Zaehler oder Digest beruht;
8. alle read-only Proben Zustand und Identitaet unveraendert lassen.

PPB-1 wird fuer diese Entwicklungsrichtung gestoppt, wenn keine
verhaltensbezogene Gegenprognose gegen die statische Prototypbank verbleibt,
H2 oder H5 keinen gebundenen Abrufunterschied zeigt oder der Vorteil nur aus
einem groesseren Budget entsteht.

Der Vergleich ist methodisch ungueltig bei ungleichen Eingaben, Kapazitaeten,
Probeordnungen oder Wiederholungszahlen, bei Rohhistorienzugriff, Carry
zwischen Geschichten, Teilreceipts, Retry oder nachtraeglich geaenderten
Sollrollen.

## Claim- und Implementierungsgrenze

S1-XU bindet nur eine pruefbare technische Funktion. Es belegt weder eine
MCM-spezifische Memory-Mechanik noch Feldwirkung. Nicht freigegeben sind
Code, Tests, Parameter, Fixturematerialisierung, Ausfuehrung, API, Snapshot,
Feldintegration, Rueckwirkung und Semantik.

## Entscheidung

`PASS_PPB1_BOUNDED_TEMPORAL_UPDATE_FUNCTION_AND_FALSIFICATION_CONTRACT_BOUND`

Der kanonische Vertragsdigest lautet
`d487b930ba65733421788f3be86443386cfa7eda377ca54dfa9c367ba2d2a238`.

## Naechster Schritt

S1-XV darf ausschliesslich statisch die Vollstaendigkeit, Fairness,
Nichtzirkularitaet und eindeutige Materialisierbarkeit dieses Vertrags
pruefen. Keine Gleichung, Implementierung, Tests oder Ausfuehrung.
