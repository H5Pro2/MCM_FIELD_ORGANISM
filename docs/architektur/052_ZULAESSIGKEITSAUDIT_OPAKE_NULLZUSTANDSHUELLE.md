# Zulässigkeitsaudit einer opaken Nullzustandshülle

## Status

Architekturentscheidung auf `E1 / ADMISSIBILITY_AUDIT`.

```text
opake Nullzustandshülle geprüft: ja
wissenschaftlicher Zusatznutzen: nein
darstellungsneutrale Umsetzung:  nein
technische Hülle freigegeben:    nein
Runtime bleibt unverändert:      ja
```

Dieser Audit folgt aus dem
[atomaren Zustandsrollen-Erweiterungsvertrag](051_ATOMARER_ZUSTANDSROLLEN_ERWEITERUNGSVERTRAG.md).
Er prüft, ob eine leere technische Memory-Hülle bereits vor Auswahl einer
Darstellung sinnvoll implementiert werden kann.

## Prüffrage

> Kann eine opake Nullzustandshülle die spätere Memory-Forschung technisch
> vorbereiten, ohne bereits eine Darstellungsfamilie, Zustandsdimension oder
> Kopplungsform zu bevorzugen?

Das Ergebnis lautet: **nein**.

## 1. Digitaler Zustand ist nie vollständig opak

Eine Runtime kann keinen völlig darstellungslosen Zustand enthalten. Auch
scheinbar neutrale Platzhalter treffen bereits Architekturentscheidungen.

### `None`

Ein Feld wie `memory_state: None` würde festlegen:

- jedes Neuron besitzt genau einen Memory-Slot;
- Nichtvorhandensein und Nullzustand sind identisch;
- die Rolle ist lokal am einzelnen Neuron adressiert;
- Snapshot und Output führen denselben Slot dauerhaft mit.

### Leere Bytes oder leeres Tupel

`b""` oder `()` würden zusätzlich festlegen:

- die Rolle besitzt eine lineare serialisierbare Nutzlast;
- Gleichheit wird über Byte- oder Elementgleichheit bestimmt;
- spätere Zustände müssen in diese Hülle migrieren;
- ein leerer Container bedeutet kausale Null.

### Abstraktes Objekt oder Protokoll

Auch ein abstraktes Objekt benötigt:

- einen konkreten Runtime-Typ;
- Identität oder Wertgleichheit;
- Serialisierung;
- Validierung;
- Kopier- und Lebenszyklusregeln.

Damit wäre die Hülle nicht darstellungsoffen. Sie würde die spätere Forschung
an eine vorzeitig gewählte Zustandsanatomie binden.

## 2. Kein zusätzlicher Kausalnachweis

Eine Nullhülle ohne Bildungs- und Wirkregel könnte ausschließlich zeigen:

```text
ein unbenutzter Platzhalter verändert die Runtime nicht
```

Das ist tautologisch. Sie könnte nicht prüfen:

- Entstehung aus Weltgeschichte;
- spätere kausale Mitprägung;
- Wirkung über `activation` und `afterimage` hinaus;
- natürliche Abschwächung;
- vollständige funktionale Wirkungslosigkeit;
- erneute Prägbarkeit;
- Freiheit von festen Baselines.

Die zentralen Anforderungen des Memory-Substratvertrags blieben deshalb
vollständig offen.

## 3. Die Nullkontrollen sind bereits getragen

Die heutige Runtime sichert bereits:

- unveränderliche abgeschlossene Neuronenzustände;
- atomare Veröffentlichung der nächsten Schicht;
- vollständiges Verwerfen fehlgeschlagener Vorschläge;
- neutrale Observer;
- deterministischen Snapshot-Rundlauf;
- nicht persistierte transiente Rezeptorverläufe;
- lokale Feldproben nur aus `activation` und `afterimage`;
- keine versteckte Memory-Rolle.

Eine leere Hülle würde diese Grenzen nur unter einem neuen Feldnamen erneut
testen. Sie würde keine neue technische Voraussetzung schaffen.

## 4. Unverhältnismäßiger technischer Eingriff

Die aktuelle Zustandsrolle ist breit und absichtlich strikt eingebunden:

```text
MCMNeuron-Konstruktion:       16 Code- und Testmodule
MCMNeuronOutput-Konstruktion: 15 Code- und Testmodule
Snapshot-Schema:              exakt Version 1
öffentliche Rollen:           explizit geprüft
```

Eine Nullhülle würde mindestens verändern:

- `MCMNeuron`;
- `MCMNeuronOutput`;
- `advance_mcm_neuron`;
- sämtliche Baseline-Transitions;
- Snapshot-Schema und Parser;
- Wiederherstellung und Digests;
- öffentliche Rollenverträge;
- zahlreiche Fixtures und Nulltests.

Dieser Eingriff wäre nur gerechtfertigt, wenn eine funktional begründete
Darstellung tatsächlich eingebunden werden soll. Für einen unbenutzten
Platzhalter ist der Umbau methodisch und technisch nicht vertretbar.

## 5. Gefahr einer statischen Sackgasse

Eine vorzeitig implementierte Hülle erzeugt Anschlussdruck:

```text
Slot ist vorhanden
-> irgendein Wert soll hineingeschrieben werden
-> irgendein Leser soll den Wert verwenden
-> Platzhalter wird nachträglich zur Mechanik erklärt
```

Dadurch würden genau die bereits geschlossenen Familien begünstigt:

- unabhängiger lokaler Skalar;
- Leaky-Memory;
- Übergangszähler;
- fester Vektor;
- serialisierte Ereignisliste;
- direkter Memory-Leser.

Der leere Slot wäre damit nicht neutral, sondern ein technischer Vorläufer
einer statischen Speicherarchitektur.

## 6. Keine versteckte Erweiterung über `Any`

Ein untypisiertes Feld wie `object` oder `Any` ist ebenfalls unzulässig.

Es würde:

- Endlichkeit und Wertebereich unprüfbar machen;
- kanonische Serialisierung verhindern;
- versteckte mutable Zustände ermöglichen;
- wissenschaftliche Interventionen undefiniert lassen;
- unterschiedliche Kandidaten unter inkompatiblen Regeln vermischen.

Darstellungsoffenheit bedeutet nicht Typ- oder Vertragslosigkeit.

## 7. Getragene Architekturentscheidung

Die Runtime bleibt unverändert, bis eine kleinste Darstellung durch eine
konkrete funktionale Unterscheidung begründet ist.

Verbindlich gilt:

```text
kein Platzhalter vor Funktionsbegründung
keine Schemamigration ohne kausalen Kandidaten
kein Memory-Feld ohne definierte Null- und Interventionssemantik
kein technischer Slot als Forschungsfortschritt
```

Der atomare Erweiterungsvertrag bleibt gültig. Er beschreibt die spätere
Einbindungsgrenze, nicht die Aufforderung, diese Grenze sofort im Code zu
materialisieren.

## 8. Was stattdessen vor einer Darstellung fehlt

Eine digitale Darstellung kann erst bewertet werden, wenn klar ist, welche
Weltgeschichten sie funktional unterscheiden muss.

Nicht Rohgeschichte, Mustername oder Beobachtersymbol soll gespeichert
werden. Maßgeblich ist eine spätere kausale Unterscheidung:

```text
verschiedene frühere lokale Weltgeschichte
+ angeglichene schnelle Zustände
+ identische spätere lokale Weltfolge
-> unterschiedliche spätere Feldbildung
```

Ohne eine solche Unterscheidung gibt es keinen Informationsgrund für einen
zusätzlichen Zustand.

## Freigabegrenze

```text
Nullhülle methodisch geprüft:           ja
Nullhülle wissenschaftlich notwendig:   nein
Nullhülle darstellungsneutral:           nein
bestehende Atomarität ausreichend:       ja
bestehende Snapshotgrenze ausreichend:   ja
neue Runtime-Rolle freigegeben:          nein
```

## Nächster Schritt

Der Vertrag der
[kausalen Zustandsäquivalenz](053_KAUSALE_ZUSTANDSAEQUIVALENZ.md)
ist inzwischen formuliert. Er bestimmt den notwendigen Informationsgehalt
nicht durch Rohdatenmenge, sondern durch unterschiedliche spätere
Feldtrajektorien unter identischen zulässigen Zukünften.

Als Nächstes wird die weltbegründete Relevanzgrenze bestimmt. Sie muss
verhindern, dass ein willkürlich gespeichertes Geschichtsbit mit festem Leser
bereits als Memory-Erfolg gilt. Bis dahin bleibt die Runtime unverändert.
