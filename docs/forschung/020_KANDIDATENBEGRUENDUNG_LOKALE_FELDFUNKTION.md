# Kandidatenbegruendung einer lokalen Feldfunktion

## Status und Umfang

```text
separater Forschungslauf nach 019:       abgeschlossen
konkrete Kandidatenfamilien geprueft:    ja
unabhaengig begruendeter Kandidat:       nein
Memory-Mechanik behauptet:               nein
60-Sekunden-Lauf freigegeben:            nein
Runtime- oder Produktcode geaendert:     nein
```

Dieser Lauf prueft ausschliesslich, ob ein lokaler Funktions- und
Zustandskandidat bereits ohne Memory-Ziel begruendbar ist. Forschung 019
bleibt unveraendert abgeschlossen. Es werden keine Gleichung, Variable,
Parameter, Medienvoraussetzung oder technische Umsetzung eingefuehrt.

## Bindender Zulassungstest

Ein Vorschlag ist nur dann ein zulaessiger Kandidat, wenn alle folgenden
Fragen unabhaengig vom gewuenschten Memory-Ergebnis beantwortet werden:

1. Welche gegenwaertig notwendige lokale Feldfunktion erfuellt er?
2. Welcher observerunabhaengige Funktionsverlust tritt ohne diese Rolle ein?
3. Warum muss gerade Welt- und Feldteilnahme die Rolle veraendern?
4. Welche Zustandsrolle traegt die Funktion, ohne nur Geschichte zu
   akkumulieren?
5. Wie folgt ihre Rueckwirkung aus der Funktion statt aus einem festen Leser?
6. Wie werden Richtung, Skala, Begrenzung und Wirkungslosigkeit begruendet,
   ohne das gewuenschte Ergebnis einzubauen?
7. Wie kann die Rolle unabhaengig vertauscht, gleichgesetzt, neutralisiert und
   vom Wirkpfad getrennt werden?
8. Welche Vorhersage bleibt jenseits von Leaky-Spur, Integrator, fester
   Rekurrenz, adaptivem Gewicht und technischem Nebenzustand?

Ein Kandidat darf nicht allein dadurch begruendet werden, dass die aktuelle
Runtime nach dem Nullbefund eine geschichtliche Rolle nicht besitzt.

## Vorschlag A: lokale endliche Feldaufnahmekapazitaet

### Gedachte Funktion

Eine lokale Kapazitaet koennte bestimmen, in welchem Umfang ein Feldort
weitere Welt- und Feldwirkung aufnehmen kann. Beanspruchung koennte diese
Moeglichkeit veraendern, andere Weltgeschichte koennte sie wieder freigeben.

### Pruefung ohne Memory-Ziel

Im bestehenden MCM-Feld gibt es keinen Verlust, wenn ein Feldort beliebig
oft angeregt wird. Nach Abklingen von `activation` und `afterimage` besitzt er
dieselbe technische Aufnahmefaehigkeit wie zuvor. Eine zusaetzliche
Kapazitaetsgrenze wuerde daher nicht eine vorhandene Feldfunktion abbilden,
sondern erstmals festlegen, dass Aufnahme verbraucht oder begrenzt sein soll.

Fuer eine technische Fortschreibung waeren mindestens Verbrauchsrichtung,
Kapazitaetsmaximum, Beanspruchungsskala, Erholung und Rueckwirkung zu waehlen.
Damit entstehen genau die ausgeschlossenen Klassen:

```text
Kontakt akkumuliert Beanspruchung   -> Integrator
Beanspruchung klingt mit Zeit ab    -> Leaky-Spur
Kapazitaet begrenzt Feldaufnahme    -> fester adaptiver Leser
Kapazitaet kehrt zu einem Wert zurueck -> programmierter Sollzustand
```

### Urteil

```text
unabhaengige notwendige Funktion: nein
unabhaengige Zustandsrolle:       nein
Baselineabgrenzung:               nicht moeglich
Status:                           verworfen
```

## Vorschlag B: lokale rezeptorische oder innere Empfindlichkeit

### Gedachte Funktion

Eine Empfindlichkeitsrolle koennte spaetere gleiche Anregung lokal anders
aufnehmen. Dies entspricht oberflaechlich der in Forschung 018 gesuchten
veraenderten Feldempfaenglichkeit.

### Pruefung ohne Memory-Ziel

Eine Empfindlichkeit ist jedoch bereits die gesuchte Wirkung und noch keine
unabhaengige Funktion. Ohne eigene physische Rolle muss ein Entwickler
festlegen, welche Geschichte die Empfindlichkeit erhoeht oder senkt und wie
sie die naechste Aufnahme skaliert.

Auf Rezeptorebene waere dies ein Eingangsfilter vor der gesuchten inneren
MCM-Funktion. Auf Feldebene waere es ein adaptiver Gain oder ein
geschichtsabhaengiger Leser. Belastung und Erholung wuerden erneut ueber
Integrator, mehrere Leaky-Zeitskalen oder einen Sollbereich programmiert.

### Urteil

```text
Funktionsbezeichnung vorhanden:   ja
unabhaengige Begruendung:          nein
kausal eigene Zustandsrolle:       nein
Abgrenzung zu Gain/Leaky-Leser:    nein
Status:                            verworfen
```

## Vorschlag C: deformierbare lokale Kopplungsmoeglichkeit

### Gedachte Funktion

Eine endliche, raeumlich verformbare Kontaktflaeche koennte unabhaengig von
Memory beschreiben, wo ein Feldort lokale Kopplung physisch tragen kann. Die
bereits dokumentierte radiale Kontaktmorphologie stellt hierfuer eine passive
Anatomie bereit.

### Pruefung ohne Memory-Ziel

Dieser Vorschlag besitzt als einziger eine unterscheidbare anatomische Rolle.
Er besitzt aber weiterhin keine begruendete Materialphysik. Im vorhandenen
System fehlen:

- eine mechanische Beanspruchung mit Einheit und Bilanz;
- eine zur Verformung konjugierte Feldarbeit;
- Steifigkeit, Mobilitaet oder Fliesseigenschaft;
- eine begruendete Bewegungsrichtung und Zeitskala;
- eine aus Beruehrung folgende Feldrueckwirkung.

Der instantane lokale Feldfluss ist eine redundante Darstellung des schnellen
Feldzustands. Seine zeitliche Akkumulation waere ein Integrator. Eine
festgelegte Bewegung des Kontaktmaterials nach diesem Fluss wuerde Polung,
Skala und Kopplungsziel programmieren. Ein Rueckstellgesetz waere eine
Leaky- oder Attraktordynamik.

### Urteil

```text
unabhaengige anatomische Rolle:    bedingt plausibel
unabhaengige dynamische Funktion:  nicht begruendet
interventionsfaehige Zustandsrolle: als Anatomie denkbar, als Kandidat nein
Baselineabgrenzung:                nicht moeglich
Status:                            suspendiert, nicht zugelassen
```

Die Suspendierung aus dem konzeptionellen Substratrollenaudit wird nicht
aufgehoben.

## Vorschlag D: lokale Refraktaer- oder Erschoepfungsrolle

### Gedachte Funktion

Ein Feldort koennte durch wiederholte Anregung voruebergehend weniger
ansprechbar und nach Entlastung wieder ansprechbar werden.

### Pruefung ohne Memory-Ziel

Das heutige digitale Feld besitzt keine Schaedigungs-, Stoff-, Temperatur-
oder Energiebedingung, aus der Refraktaritaet notwendig folgt. Die Rolle
wuerde aus biologischer Analogie uebernommen. Ihre technische Minimalform ist
ein Belastungsintegrator mit Zerfall und ein fester Leser der verbleibenden
Empfindlichkeit. Ein Sollbereich oder Schutzwert waere ein programmiertes
Erhaltungsziel.

### Urteil

```text
im MCM intrinsisch notwendig: nein
biologische Analogie noetig:  ja
Baselineklasse:               Integrator + Leaky-Spur + fester Leser
Status:                       verworfen
```

## Abgleich der unabhaengigen Zustandsrolle

Keiner der geprueften Vorschlaege liefert derzeit eine Zustandsrolle, die
gleichzeitig:

- eine ohne Memory sinnvolle und im heutigen MCM notwendige Funktion traegt;
- durch lokale Welt- und Feldteilnahme aus eigener Kausalitaet veraendert
  wird;
- nach Angleichung der schnellen Rollen eigenstaendig fortbestehen kann;
- eine Rueckwirkung besitzt, die nicht als fester Leser programmiert wird;
- vollstaendige Wirkungslosigkeit und erneute Praegbarkeit ohne
  Loeschbefehl, Sollwert oder Leaky-Rueckkehr erlaubt;
- gegen die Pflichtbaselines aus Forschung 019 unterscheidbar ist.

Eine bloss opake Variable waere zwar technisch vertauschbar und
neutralisierbar. Diese Interventionsfaehigkeit begruendet aber weder ihren
Inhalt noch ihre Fortschreibung oder Rueckwirkung. Sie waere ein technischer
Speicherslot und damit kein zulaessiger Kandidat.

## Pflichtinterventionen und aktuelle Undurchfuehrbarkeit

Forschung 019 verlangt Vertauschen, Gleichsetzen, Neutralisieren sowie
getrennte Entstehungs- und Wirkpfadinterventionen. Fuer keinen Vorschlag kann
dies derzeit operationalisiert werden, ohne zuvor genau die fehlende
Mechanik zu waehlen:

| Intervention | Aktuelle Grenze |
|---|---|
| Kandidatenrolle vertauschen | Keine zugelassene eigenstaendige Rolle vorhanden. |
| Kandidatenrolle gleichsetzen | Keine funktionsbegruendete Zustandsdarstellung vorhanden. |
| Neutralzustand setzen | Ein Nullwert waere ohne Material- oder Funktionsmodell willkuerlich. |
| Entstehungsursache entfernen | Schreibursache ist fuer keinen Kandidaten unabhaengig bestimmt. |
| Wirkpfad trennen | Rueckwirkung waere fuer alle Vorschlaege erst zu programmieren. |
| Loesung und Wiederpraegung | Jede bisher formulierbare Form faellt auf Leaky, Integrator, Schwelle oder festen Leser zurueck. |

Deshalb waere ein Lauf nicht nur ergebnisoffen, sondern kausal undefiniert.

## Ausschlusskontrolle

Es wurden keine Labels, Bedeutungen, Rewards, Sollwerte, Gewinnerregeln,
Zielantworten oder Zieltopologien als Kandidatenursache verwendet. Datenbank-,
Rohdaten-, Embedding- und Observerzustand wurden nicht als MCM-Zustandsrolle
zugelassen. Kein Vorschlag erhaelt eine Ausnahme von den Leaky-, Integrator-,
Festleser-, Rekurrenz- oder technischen Baselines.

## Ergebnis

Der Forschungslauf findet **keinen derzeit begruendbaren konkreten
Kandidatenvorschlag**.

Das ist kein Beweis, dass eine weltgebildete reversible Feldempfaenglichkeit
unmoeglich ist. Es ist der engere Befund, dass die geprueften naheliegenden
Zustandsrollen ihre notwendige Funktion, Dynamik oder Rueckwirkung erst aus
dem gewuenschten Memory-Lebenszyklus beziehen wuerden.

Damit bleiben:

```text
Forschung 019:                     unveraendert abgeschlossen
60-Sekunden-Lauf:                  gesperrt
ausfuehrbare Vorregistrierung:     gesperrt
Runtime- und Produktentwicklung:   gesperrt
Kontaktmorphologie:                passive Anatomie, suspendiert
weltbezogene Speicherhypothese:    offen, aber ohne Kandidat
```

## Naechster fachlicher Schritt

Der naechste Schritt kann nicht die Implementierung eines der vier
Vorschlaege sein. Er benoetigt eine Entscheidung des Forschungsleiters
zwischen:

1. strenger Evidenzlinie: unveraenderte Feldruntime weiter nur hinsichtlich
   ihrer gegenwaertigen realen Feldreaktionen untersuchen, ohne Memory- oder
   Kandidatenanspruch;
2. expliziter Materialhypothese: genau ein konkretes Materialmodell als von
   aussen gesetzte Forschungsannahme deklarieren und seine programmierte
   Physik offen gegen alle Baselines pruefen.

Der zweite Weg waere keine aus dem bestehenden MCM abgeleitete notwendige
Mechanik und benoetigt deshalb eine ausdrueckliche neue Freigabe.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/019_VORREGISTRIERUNGSSKIZZE_WELTKONTAKT_BIS_60_SEKUNDEN.md`;
- `docs/architektur/017_SENSORISCHE_SELBSTREGULATION_GRENZVERTRAG.md`;
- `docs/architektur/027_DOPPELTE_SELBSTREGULATION_GRENZE.md`;
- `docs/architektur/041_FUNKTIONALE_GRENZE_VERTEILTER_LOKALER_ORGANISATION.md`;
- `docs/architektur/063_AUDIT_INTRINSISCHE_LOKALE_FELDBEANSPRUCHUNGSQUELLE.md`;
- `docs/architektur/064_GRENZE_DER_FESTEN_DIFFUSIONSANATOMIE.md`;
- `docs/architektur/065_PHYSISCHE_MINDESTANFORDERUNG_ORGANISCHES_MEMORY_SUBSTRAT.md`;
- `docs/architektur/066_GRENZE_EINES_ISOLIERTEN_LOKALEN_SUBSTRATZUSTANDS.md`;
- `docs/architektur/087_KONZEPTIONELLER_SUBSTRATROLLENAUDIT.md`;
- `docs/architektur/090_VERGLEICH_NOTWENDIGER_ORGANISMUSFUNKTIONEN.md`.

MINI_DIO- und externe MCM-Altquellen wurden nicht verwendet. Es wurde keine
Mechanik aus anderen Projekten uebernommen.
