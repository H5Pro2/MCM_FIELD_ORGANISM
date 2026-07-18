# Darstellungsoffener Memory-Substratvertrag

## Status

Verbindlicher Funktions- und Zustandsrollenvertrag auf
`E0 / CONTRACT_ONLY`.

```text
fehlende Zustandsrolle: funktional begründet
digitale Darstellung:   offen
Updategleichung:         offen
Runtime-Erweiterung:     gesperrt
```

Dieser Vertrag folgt aus dem
[Rollenabgleich des vorhandenen Feldes](047_ROLLENABGLEICH_MEMORY_SUBSTRAT.md).
Er ergänzt keine Variable, Kante, Lernrate, Schwelle, Kapazität oder
Zielorganisation.

## Architekturrolle

Die Grundrollen des Projekts lauten:

```text
MCM
= Möglichkeit der gemeinsamen Feldwahrnehmung

Memory-Substrat
= Möglichkeit, eigene Weltgeschichte kausal weiterwirken,
  funktionslos werden und erneut prägen zu lassen

mögliche Entwicklung
= nicht vorgegebener Ausgang des Zusammenspiels
  von Feldwahrnehmung, Memory und fortlaufender Weltteilnahme
```

Das Memory-Substrat ist weder eine nachgeschaltete Datenbank noch ein zweites
Gehirn. Es muss zum selben laufenden Organismusfeld gehören.

## Warum eine eigene kausale Rolle fehlt

Die aktuelle Runtime besitzt:

- `activation` als schnelle gegenwärtige Feldlage;
- `afterimage` als feste schnelle Zeitspur;
- `perception` als aktuelle lokale Wahrnehmungsgrundlage;
- lokale Feldproben als abgeleitete Vorfeldsicht;
- Snapshot-Persistenz als technische Zustandserhaltung.

Nach Angleichung der kausal gelesenen schnellen Rollen kann die aktuelle
Runtime unter derselben späteren Weltgeschichte keinen erworbenen
Funktionsunterschied erzeugen.

Eine zusätzliche kausal gelesene Zustandsrolle ist daher funktional
notwendig. Ihre digitale Form bleibt vollständig offen.

## Was fest programmiert sein darf

Fest vorgegeben werden dürfen ausschließlich digitale Naturbedingungen:

1. **Kausalität**
   Nur abgeschlossene Vorzustände und gegenwärtig verfügbare lokale
   Feldwirkung dürfen den nächsten Zustand beeinflussen.

2. **Atomare Zeit**
   Alle lokalen Vorschläge eines Feldfortschritts entstehen aus demselben
   abgeschlossenen Organismuszustand.

3. **Lokalität**
   Bildung und Wirkung bleiben an einen endlichen offengelegten Feldradius
   gebunden.

4. **Gleichheit der Naturbedingung**
   An technisch gleichartigen Feldorten gilt dieselbe unveränderte Regel.

5. **Endlichkeit**
   Zustandsumfang, Wertebereich, Präzision und Rechenaufwand bleiben begrenzt.

6. **Kontinuierliche Organismuszeit**
   Zustandsänderung hängt von real verstrichener Organismuszeit und nicht von
   bloßer Aufrufzahl ab.

7. **Technische Fortsetzbarkeit**
   Der vollständige kausale Zustand ist snapshotfähig. Serialisierung erzeugt
   keine eigene Wirkung.

8. **Passiver Observer**
   Beobachtung, Diagnose und Archivierung dürfen den Feldzustand nicht
   verändern.

Diese Bedingungen dürfen die Möglichkeit von Entwicklung bereitstellen. Sie
dürfen nicht bestimmen, welche konkrete Erfahrung oder Ordnung entsteht.

## Was ausschließlich aus Weltgeschichte entstehen muss

Nicht vorgegeben werden dürfen:

- welche Feldbereiche gemeinsam wirksam werden;
- welche frühere Erfahrung später trägt;
- Stärke, Dauer oder Richtung einer Prägung;
- Zeitpunkt oder Form einer Stabilisierung;
- welche weitere Weltgeschichte eine Wirkung abschwächt;
- wann vollständige Funktionslosigkeit erreicht wird;
- welche neue Prägung danach entsteht;
- semantische Rolle, Bezeichnung oder Bedeutung;
- gewünschte Topologie, Gewinner oder Zielstruktur.

Wiederholung darf Wirkung ermöglichen, ist aber keine programmierte
Verstärkungspflicht. Gleiche Wiederholungszahl muss bei anderer Feldlage nicht
zum gleichen Ergebnis führen.

## Kausaler Minimalzyklus

Eine spätere Substratmechanik muss mindestens folgenden offenen Lebenszyklus
tragen können:

```text
fortlaufende lokale Weltteilnahme
-> geschichtsabhängige Substratprägung
-> veränderte spätere lokale Feldbildung
-> weitere Weltgeschichte
-> Abschwächung
-> vollständige funktionale Wirkungslosigkeit
-> erneute Prägbarkeit
```

Der Zyklus bezeichnet beobachtbare Funktionen. Er legt weder Beziehung,
Ressource noch Topologie als Datenstruktur fest.

## 1. Weltgetriebene Entstehung

Eine Substratprägung darf nur entstehen, wenn reale lokale Feldwirkung
kausal vorlag.

Nicht ausreichend sind:

- verstrichene Zeit ohne Feldwirkung;
- technische Sensorabschlüsse ohne neue Quellenstütze;
- Observerauswertung;
- Snapshotladen;
- Phasenname oder Versuchsschritt;
- Wiederholungszähler ohne Feldursache.

Innere Feldwirkung darf später dieselbe lokale Naturbedingung anregen.
Reflexion ist jedoch noch nicht freigegeben und darf in einem ersten
Kandidaten keine Ersatzquelle für fehlenden Weltkontakt sein.

## 2. Wirkung während späterer Feldbildung

Memory darf nicht nur in einem nachgeschalteten Leser sichtbar werden.

Erforderlich ist:

```text
gleiche schnelle Ausgangslage
+ gleiche neue lokale Weltevidenz
+ unterschiedliche eigene Weltgeschichte
-> unterschiedliche lokale Zustandsbildung bereits vor der Probe
```

Die Substratrolle muss die spätere Feldbildung kausal mitprägen. Eine
Diagnose, die lediglich einen gespeicherten Wert mit der Probe multipliziert,
genügt nicht.

## 3. Zeitliche Eigenständigkeit

Die Wirkung muss über `activation` und den festen schnellen `afterimage`
hinausreichen, ohne ein Historienarchiv zu bilden.

Sie darf nicht vollständig erklärt werden durch:

- einen oder mehrere feste Leaky-Zustände;
- lokale Produktintegratoren;
- Sättigung;
- festen Leser;
- feste lokale Rekurrenz;
- feste Normalisierung.

Die Vergleichsgrenzen stehen im
[operationalen C2-Baselinevertrag](045_OPERATIONALE_C2_BASELINEKLASSEN.md).

## 4. Abschwächung

Dieselbe unveränderte Naturbedingung, die Prägung zulässt, muss unter anderer
realer Feldgeschichte auch Wirkung verlieren können.

Unzulässig sind:

- Löschbefehl;
- Reset;
- Phasenkennung;
- besondere Abschwächungsregel;
- globale Speicherverwaltung;
- nachträglich gewählte Gegenevidenz.

Bloße feste Relaxation ist eine Baseline und noch kein eigenständiger
Memory-Befund.

## 5. Vollständige funktionale Wirkungslosigkeit

Lösung bedeutet nicht zwingend, dass jeder digitale Zahlenwert exakt null
wird.

Verbindlich ist:

```text
alte Prägung
-> unter ihrer vollständigen kausalen Probe keine nachweisbare Wirkung
-> keine zulässige Zustandsintervention legt verborgene alte Wirkung frei
```

Eine technische Auswertungstoleranz darf nur Messfehler begrenzen. Sie darf
nicht als Schwelle in die Mechanik eingehen.

Eine frühere Feldform darf später erneut ähnlich entstehen. Entscheidend ist,
dass sie zuvor kausal wirkungslos war und nicht allein durch passive Rückkehr
rekonstruiert wurde.

## 6. Erneute Prägbarkeit

Nach vollständiger Wirkungslosigkeit muss neue lokale Weltgeschichte wieder
eine spätere Feldfunktion prägen können.

Dabei gilt:

- die alte Geschichte bevorzugt die neue Prägung nicht verborgen;
- ohne neue Weltgeschichte entsteht keine neue Wirkung;
- die neue Wirkung wandert bei Zustandsintervention kausal mit;
- ein No-New-World-Zweig bleibt neutral;
- kein freier Speicherplatz, Token oder Ressourcenwert wird vorausgesetzt.

Erneute Prägbarkeit ist eine Funktion des Substrats, keine programmierte
Wiederbindungsoperation.

## 7. Fortlaufender Weltkontakt

Das Substrat entwickelt sich im laufenden Feld:

```text
Wachzustand
= Weltkontakt ist primäre Feldursache

reduzierter Weltkontakt
= Feldruntime läuft weiter, äußere Anregung ist geringer

Ausschalten
= kontinuierliche Feldkausalität endet
```

Offline-Erholung ist später ein möglicher Betriebsmodus desselben laufenden
Feldes. Sie ist kein Training, Replay oder Speicherimport.

Ein Snapshot kann den letzten bekannten Zustand technisch rekonstruieren. Er
beweist keine ununterbrochene Fortsetzung desselben Lebensprozesses.

## 8. Zugehörigkeit zum Organismuszustand

Eine spätere Substratrolle muss:

- vollständig innerhalb des gemeinsamen MCM-Feldzustands liegen;
- bei jedem kausal relevanten Feldfortschritt verfügbar sein;
- im Snapshot vollständig enthalten sein;
- ohne Prozesscache, Closure oder externe Datenbank auskommen;
- vom passiven Observer unabhängig bleiben;
- keine Rohbilder, Audiosegmente, Objekte, Wörter oder Episoden speichern.

Die Runtime darf keine externe Suche durchführen, um eine innere Wirkung zu
erzeugen.

## Nullzustand

Der nachgewiesene Nullzustand einer späteren Substratrolle muss exakt die
heutige neutrale Runtime ergeben:

```text
Memory-Substrat im Nullzustand
-> keine zusätzliche Feldwirkung
-> activation unverändert nach heutiger Gleichung
-> afterimage unverändert nach heutiger Gleichung
-> heutige Wahrnehmungs- und Snapshotgrenzen unverändert
```

Der Nullzustand ist keine gelöschte Welt und kein gemessener Nullkontakt.

## Verbindliche Kausalinterventionen

Eine spätere Darstellung muss mindestens ermöglichen:

1. Substratlage zwischen kontrollierten Zweigen tauschen;
2. Substratlage exakt gleichsetzen;
3. Substratlage auf ihren nachgewiesenen Nullzustand setzen;
4. Entstehungsursache entfernen und spätere Probe erhalten;
5. Wirkpfad unterbrechen und Entstehung erhalten;
6. schnelle Zustände unabhängig angleichen;
7. vollständige funktionale Lösung ohne Reset prüfen;
8. neue Weltgeschichte nach Lösung kausal abtragen.

Diese Eingriffe dienen ausschließlich der Forschung. Sie sind keine
Runtime-Fähigkeiten des Organismus.

## Abgrenzung zu späteren Fähigkeiten

Der Memory-Substratvertrag beweist und programmiert nicht:

- semantische Resonanz;
- Syntaxbildung;
- Reflexionsrückwirkung;
- Eingangs- oder Feldselbstregulation;
- Resonanz zur Sprache;
- Handlung;
- Bewusstsein;
- Feldintelligenz.

Diese Fähigkeiten dürfen erst nach einer getragenen Kernmechanik als eigene
Funktionsfragen untersucht werden. Feldintelligenz bleibt eine mögliche
Fernhypothese, kein Entwicklungsziel.

## Verhältnis zum Vertrag 039

Der
[darstellungsoffene lokale Organisationszustand](039_DARSTELLUNGSOFFENER_LOKALER_ORGANISATIONSZUSTAND.md)
bleibt als engerer historischer Vorvertrag gültig. Er konzentriert sich auf
lokale Organisation, funktionale Ressourcenfreigabe und Wiederbindung.

Der aktuelle Vertrag liegt eine Ebene darunter:

```text
048: Welche Memory-Substratrolle fehlt grundsätzlich?
039: Welche Organisationsfunktion müsste ein späterer Kandidat tragen?
```

Ein Memory-Substrat muss nicht vorab als Beziehung oder Topologie beschrieben
werden. Erst beobachtete Entwicklung darf zeigen, ob solche Beschreibungen
überhaupt tragen.

## Freigabegrenze

```text
Memory-Funktion abgegrenzt:              ja
feste Naturbedingungen abgegrenzt:       ja
weltgeschichtlich offene Anteile benannt: ja
Lösung und erneute Prägbarkeit gefordert: ja
digitale Darstellung ausgewählt:         nein
Updategleichung ausgewählt:               nein
passiver Kandidat freigegeben:            nein
Runtime erweitert:                        nein
```

## Nächster Schritt

Der
[MINI_DIO-Abgleich zum Memory-Substrat](049_MINI_DIO_MEMORY_SUBSTRAT_ABGLEICH.md)
ist abgeschlossen. MINI_DIO trug ein kontinuierliches Feld mit kurzer
Vorzustandsspur, eine intrinsisch beobachtbare Eigenform und eine passive
bewegliche Beziehungsgeschichte. Es trug keine gemeinsame feldlokale
Memory-Substratfunktion.

Die feste indexgerichtete Neuronenkette und die erst bei Weltfinalisierung
gebildeten Observerbeziehungen werden nicht übernommen.

Die
[lokale Ereignisquellgrenze](050_LOKALE_EREIGNISQUELLGRENZE.md)
ist inzwischen bestimmt. Weltkontakt, lokales Vorfeld, Eigenzustand und
Organismuszeit liegen bereits kausal sauber im atomaren Feldfortschritt vor.
Eine geschichtlich fortwirkende Ereignisprägung existiert nicht.

Der
[atomare Zustandsrollen-Erweiterungsvertrag](051_ATOMARER_ZUSTANDSROLLEN_ERWEITERUNGSVERTRAG.md)
ist inzwischen formuliert. Der anschließende
[Zulässigkeitsaudit](052_ZULAESSIGKEITSAUDIT_OPAKE_NULLZUSTANDSHUELLE.md)
hat diese Hülle inzwischen geschlossen. Sie würde bereits einen lokalen Slot,
eine Serialisierungsform und einen Migrationspfad vorgeben, ohne eine
Memory-Funktion prüfen zu können.

Der Vertrag der
[kausalen Zustandsäquivalenz](053_KAUSALE_ZUSTANDSAEQUIVALENZ.md)
ist inzwischen formuliert. Erst ein Unterschied zukünftiger Feldwirkung kann
zusätzlichen Informationsgehalt begründen.

Die anschließende
[weltbegründete Relevanzgrenze](054_WELTBEGRUENDETE_RELEVANZGRENZE.md)
ist inzwischen formuliert. Sie trennt willkürlich gespeicherte Geschichtsbits
von vergangenen Unterscheidungen, die Information über eine noch unbekannte
spätere Rezeptorfortsetzung tragen.

Als Nächstes wird eine minimale passive Weltfamilie vorregistriert. Gleichung,
Memory-Kandidat und Runtime bleiben geschlossen.
