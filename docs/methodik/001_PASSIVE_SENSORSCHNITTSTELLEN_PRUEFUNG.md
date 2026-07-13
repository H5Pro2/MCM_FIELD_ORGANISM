# Methodik 001: Passive Sensorschnittstellen-Prüfung

## 1. Status

Diese Methodik ist eine Vorregistrierung. Sie führt keine Runtime, keine
MCM-Gleichung, keine gemeinsame Feldkopplung und keine Lernmechanik ein.

Untersucht wird ausschließlich die technische Grenze zwischen drei bereits
gedachten sensorspezifischen MCM-Zuständen und einem später möglichen
gemeinsamen MCM-Strang.

```text
synthetischer visueller MCM-Zustand  --\
synthetischer auditiver MCM-Zustand  ----> passiver Schnittstellen-Prüfrahmen
synthetischer taktiler MCM-Zustand   --/
```

Der Prüfrahmen ist noch kein gemeinsamer MCM-Strang. Er darf Zustände nur
entgegennehmen, validieren, kanonisch darstellen und dem passiven Observer zur
Prüfung zugänglich machen.

## 2. Forschungsfrage

Kann die vereinbarte Schnittstelle gleichzeitig vorhandene, fehlende,
inaktive, verzögerte und nachhallende sensorspezifische MCM-Zustände vollständig
unterscheidbar und unabhängig von technischer Ausführungsreihenfolge tragen,
ohne Rohsensorik, Semantik oder versteckte Fusion einzuführen?

## 3. Hypothesen

### H1: Zustandsunterscheidung

Für jeden Sensorast bleiben mindestens folgende Zustände unterscheidbar:

```text
Kanal fehlt
!= Kanal technisch nicht verfügbar
!= gültiger Kanal ohne aktuellen Kontakt
!= gültiger aktiver Nullzustand
!= aktiver Feldzustand
```

### H2: Modalitätserhalt

Gleiche numerische Aktivierungs- und Nachhallwerte in verschiedenen
Modalitäten bleiben verschiedene technische Feldlagen.

### H3: Atomare Zeitlage

Aktivierung, Nachhall, Ressourcen und Präsenz eines Übergabezustands gehören
zum selben abgeschlossenen Schnappschuss. Gemischte Zeitschritte werden
abgewiesen.

### H4: Reihenfolgeneutralität

Bei identischem Eingangssatz ist die kanonische Gesamtdarstellung unabhängig
von Übergabe-, Validierungs- und Observer-Reihenfolge.

### H5: Observer-Neutralität

Mit und ohne Observer entstehen dieselben angenommenen und abgewiesenen
Zustände sowie derselbe kanonische Zustandsdigest.

### H6: Reset

Nach vollständigem Reset hängt der nächste Zustand nur von den anschließend
eingespeisten Schnittstellenzuständen ab. Vorherige Prüffälle hinterlassen
keine verdeckte Spur.

## 4. Nullhypothesen

- **N1:** Fehlender Kontakt und aktiver Nullzustand kollidieren.
- **N2:** Modalitätsherkunft geht bei gleichen Zahlenwerten verloren.
- **N3:** Veränderte Übergabereihenfolge verändert die Gesamtdarstellung.
- **N4:** Veraltete, doppelte oder zeitlich gemischte Zustände werden
  stillschweigend angenommen.
- **N5:** Observer-Aktivität verändert den geprüften Zustand.
- **N6:** Ein Reset lässt frühere Zustände fortwirken.

Jeder bestätigte Punkt N1 bis N6 stoppt die technische Umsetzung des
gemeinsamen MCM-Strangs.

## 5. Synthetischer Schnittstellenzustand

Die Prüfung verwendet keine Kamera-, Audio- oder Touchpaddaten. Jeder Zustand
enthält ausschließlich die im Schnittstellenvertrag festgelegten Rollen:

```text
modality_id
channel_id
snapshot_id
timestamp
geometry_id
carrier_ids
activation
afterimage
local_resources
presence
validity
```

Die Zahlenwerte sind Testreize und keine behauptete MCM-Physik. Sie werden so
gewählt, dass Gleichheit, Vorzeichen, Null, Grenzwert und kleine Differenz
separat vorkommen. Keine Zahlenkombination erhält eine Muster- oder
Bedeutungskennung.

## 6. Zustandsfamilien

Für jeden der drei Sensoräste werden dieselben technischen Familien erzeugt:

| Familie | Präsenz | Aktivierung | Nachhall | Zweck |
|---|---|---:|---:|---|
| P0 | Kanal fehlt | nicht vorhanden | nicht vorhanden | Abwesenheit |
| P1 | nicht verfügbar | nicht auswertbar | nicht auswertbar | technischer Ausfall |
| P2 | kein Kontakt | Null | möglich | Kontaktpause bei weiter bestehendem Feld |
| P3 | aktiver Nullzustand | Null | Null oder vorhanden | gültiger Kontakt ohne numerische Auslenkung |
| P4 | aktiver Feldzustand | von Null verschieden | beliebig gültig | gegenwärtige Feldlage |

`P2` und `P3` müssen auch bei identischen Zahlenwerten verschieden bleiben.
Ein Nachhall in `P2` ist zulässig, weil fehlender aktueller Kontakt nicht das
Fehlen unmittelbarer Feldgeschichte bedeutet.

## 7. Prüffälle

### 7.1 Einzelmodalität

Jeder Sensorast wird allein in P0 bis P4 geprüft. Die beiden anderen Äste sind
explizit P0 und werden nicht durch Nullvektoren ersetzt.

### 7.2 Zweierkombinationen

Geprüft werden:

```text
visuell + auditiv
visuell + taktil
auditiv + taktil
```

Für jedes Paar werden gleiche, entgegengesetzte und unterschiedlich starke
technische Zustände verwendet.

### 7.3 Dreierkombination

Alle drei Äste werden gleichzeitig in folgenden Lagen geprüft:

- gleiche Aktivierungswerte
- verschiedene Aktivierungswerte
- gleiche Gesamtamplitude bei verschiedener Modalitätsverteilung
- aktueller Kontakt in einem Ast und nur Nachhall in einem zweiten
- ein aktiver Ast, ein aktiver Nullzustand und ein fehlender Ast
- alle drei ohne aktuellen Kontakt, aber mit verschiedener Nachhalllage

### 7.4 Zeitfälle

- alle Zustände aus demselben Schnappschuss
- ein kontrolliert späterer Zustand
- ein veralteter Zustand
- ein doppelt übergebener `snapshot_id`
- gleiche Zeit mit widersprüchlichem Inhalt
- nicht monotone Zeitfolge
- Aktivierung und Nachhall aus verschiedenen Schnappschüssen

Nur offen definierte synchrone oder kontrolliert asynchrone Fälle dürfen
angenommen werden. Verdeckte Zeitmischung ist immer ein Fehler.

### 7.5 Reihenfolge

Für drei gleichzeitig vorliegende Äste werden alle sechs Übergabepermutationen
geprüft. Zusätzlich werden Validierungs- und Observer-Reihenfolge variiert.

Die kanonische Darstellung und ihr Digest müssen in allen zulässigen
Permutationen exakt gleich sein.

### 7.6 Reset und Wiederholung

Jeder Prüffall wird:

1. aus leerem Zustand ausgeführt,
2. unmittelbar identisch wiederholt,
3. nach einem konträren Vorlauf und vollständigem Reset wiederholt.

Alle drei Ergebnisse müssen exakt übereinstimmen.

## 8. Messgrößen

Gemessen werden ausschließlich technische Eigenschaften:

- Anzahl angenommener und abgewiesener Zustände
- Erhalt aller erlaubten Zustandsrollen
- Auftreten verbotener oder unbekannter Rollen
- eindeutige Trennung der Präsenzzustände
- Modalitäts- und Kanalidentität
- Schnappschuss- und Zeitkonsistenz
- kanonischer Zustandsdigest
- Permutationsdifferenz
- Observer-an/aus-Differenz
- Reset-Differenz
- Kollisionen zwischen absichtlich verschiedenen Eingängen

Es werden keine Muster, Bedeutungen, Rollen, Aufmerksamkeit oder Intelligenz
gemessen.

## 9. Kanonische Darstellung

Für die technische Vergleichbarkeit darf der Prüfrahmen eine kanonische
Darstellung erzeugen. Sie muss:

- nach technischer Modalitäts- und Kanalidentität geordnet sein,
- jede Modalität als getrennten Eintrag erhalten,
- Präsenz und Gültigkeit ausdrücklich tragen,
- Zahlenwerte unverändert übernehmen,
- keine Summe, Mittelung, Normierung oder Klassifikation durchführen,
- ausschließlich für Validierung und Digestbildung dienen.

Die kanonische Darstellung ist B1, also eine geordnete Verkettungsbaseline. Sie
ist keine gemeinsame Feldwirkung und kein inneres Musterobjekt.

## 10. Baselines

### B0: Vollständig getrennte Zustände

Die drei sensorischen MCM-Zustände bleiben separat. B0 ist die Referenz dafür,
welche Information an der Grenze vorhanden war.

### B1: Kanonische Verkettung

Alle Zustände werden geordnet und unverändert gemeinsam dargestellt. B1 prüft
Transport und Unterscheidbarkeit, aber keine Wechselwirkung.

### B2: Numerische Summe

Nur geometrisch kompatible Aktivierungsvektoren werden komponentenweise
summiert. Gezielt erzeugte Kollisionspaare müssen zeigen, welche
Modalitätsverteilungen B2 nicht unterscheiden kann.

B2 darf den Versuch nicht bestehen, wenn sie als vollständiger Ersatz für die
Schnittstelle gelesen wird. Ihr Zweck ist der Nachweis des erwarteten
Informationsverlusts.

### B3: Festes nichtplastisches Reservoir

B3 wird vorregistriert, aber in Versuch 001 noch nicht ausgeführt. Ohne
dynamischen Strangkandidaten gibt es keine zeitliche oder funktionale Leistung,
gegen die ein Reservoir sinnvoll verglichen werden könnte.

B3 wird verpflichtend aktiviert, sobald eine konkrete schnelle
Strangdynamik vorgeschlagen wird. Dann muss dieselbe Eingangsfolge, Geometrie,
Zeitbasis und Ausleseprüfung verwendet werden. B3 erhält weder Lernen noch
Reward.

## 11. Erwartung

Erwartet wird:

- B0 und B1 erhalten alle technischen Unterschiede.
- B2 erzeugt absichtlich konstruierte Kollisionen.
- P0 bis P4 bleiben trotz teilweise identischer Zahlenwerte unterscheidbar.
- alle sechs Übergabepermutationen ergeben denselben Digest.
- Observer an/aus und vollständiger Reset erzeugen Differenz null.
- ungültige Zeitmischungen werden deterministisch abgewiesen.

Diese Erwartung folgt aus dem Schnittstellenvertrag. Ihre Bestätigung wäre ein
Implementierungs- und Invariantenbefund, keine Emergenz.

## 12. Erfolgskriterien

Versuch 001 gilt nur dann als technisch bestanden, wenn:

1. alle erlaubten Zustandsrollen unverändert erhalten bleiben,
2. keine verbotene Rolle angenommen wird,
3. P0 bis P4 eindeutig unterscheidbar bleiben,
4. verschiedene Modalitäten bei gleichen Zahlen nicht kollidieren,
5. jede unzulässige Zeitmischung abgewiesen wird,
6. alle Übergabepermutationen exakt denselben Digest ergeben,
7. Observer-an/aus-Differenz exakt null ist,
8. Reset-Differenz exakt null ist,
9. B2-Kollisionen sichtbar und als Verlust markiert werden,
10. keine Aussage über gemeinsame Feldwirkung abgeleitet wird.

## 13. Scheiter- und Stoppkriterien

Der Versuch scheitert und die Schnittstelle wird überarbeitet, wenn:

- ein Nullvektor mehrere Präsenzzustände ununterscheidbar macht,
- Rohsensorik oder semantische Kennungen erforderlich werden,
- technische Reihenfolge den Zustand verändert,
- Zeitmischung stillschweigend toleriert wird,
- eine Modalität nur aufgrund ihrer Position bevorzugt wird,
- der Observer für ein korrektes Ergebnis erforderlich ist,
- frühere Prüffälle einen Reset überdauern,
- B1 bereits als gemeinsame Feldwirkung ausgegeben wird,
- ein positiver Befund zusätzliche Schwellwerte oder Zielmerkmale benötigt.

Bei einem Scheitern wird keine Feldmechanik ergänzt. Zuerst wird die
Zustandsgrenze korrigiert und Versuch 001 vollständig wiederholt.

## 14. Aussagegrenze und Evidenz

Ein dokumentierter positiver Lauf könnte **E1** tragen für:

- die Implementierung des Sensorschnittstellenvertrags,
- technische Zustandsunterscheidung,
- atomare Zeit- und Reihenfolgeneutralität,
- Observer- und Reset-Neutralität.

Er trägt keine Evidenz für:

- eine sensorspezifische MCM-Dynamik,
- gemeinsame multimodale Feldwirkung,
- Musterbildung,
- Organisationsgeschichte,
- Lernen, Kontext, Semantik oder Feldintelligenz.

Bis zur tatsächlichen Implementierung und erfolgreichen Wiederholung bleibt
der Status E0.

## 15. Freigabe nach positivem Lauf

Ein positiver Lauf gibt ausschließlich die technische Schnittstelle für
weitere passive Forschung frei. Er gibt noch keine gemeinsame
Strangdynamik frei.

Vor einer Strangmechanik muss zunächst eine konkrete Funktion benannt werden,
die B0 und B1 nicht erfüllen und deren Prüfung nicht bereits die gewünschte
Lösung vorgibt.

## 16. Bester nächster Schritt

Nach Annahme dieser Vorregistrierung wird ein minimales unveränderliches
Schnittstellen-Testobjekt mit automatisierten Invariantentests implementiert.
Es enthält nur Zustandsvalidierung, kanonische Darstellung und passive
Messung. Eine MCM- oder Stranggleichung bleibt weiterhin ausgeschlossen.
