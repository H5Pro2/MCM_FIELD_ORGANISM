# Audit der Organismusgrenze

## Status

```text
vorhandene Runtime gelesen:                    ja
neue Zustandsgröße ergänzt:                    nein
Formel oder Updategleichung ergänzt:            nein
Memory-Kandidat freigegeben:                   nein
organismische Erhaltungsbedingung nachgewiesen: nein
```

Dieser Audit folgt aus dem
[konzeptionellen Substratrollenaudit](087_KONZEPTIONELLER_SUBSTRATROLLENAUDIT.md).
Er prüft ausschließlich die vorhandene Architektur aus Sicht des laufenden
Organismus:

```text
Was kann das heutige System verlieren?
Was muss es für weitere Weltteilnahme erhalten?
Was wird durch reale Feldteilnahme tatsächlich beansprucht?
Welche spätere Funktionsänderung folgt bereits ohne Memory-Ziel?
```

## Prüfkriterium

Eine organismische Erhaltungsgröße müsste alle folgenden Bedingungen erfüllen:

1. Sie gehört zum vollständigen kausalen Organismuszustand.
2. Sie besitzt bereits ohne Memory-Aufgabe eine notwendige Feldfunktion.
3. Reale Feldteilnahme verändert oder beansprucht sie.
4. Ihr Verlust beeinträchtigt die weitere Aufnahme oder Weitergabe von
   Feldwirkung.
5. Ihr Erhalt oder ihre Erneuerung geschieht innerhalb desselben Organismus.
6. Ihre Wirkung ist lokal, endlich und bilanziell nachvollziehbar.
7. Sie enthält keine Bedeutung, Beziehung oder gewünschte Erinnerung.
8. Sie ist nicht vollständig durch Nachhall, Leaky-Integration, Ermüdungsspur
   oder adaptive Gewichte erklärt.

Eine bloß technisch notwendige Konfiguration genügt nicht. Ebenso wenig genügt
ein Zustand, dessen Verlust nur die gegenwärtige Ausgabe verändert, ohne die
weitere Feldfähigkeit zu beeinträchtigen.

## Vorhandener kausaler Organismuszustand

Die heutige gemeinsame Feldruntime trägt:

- die lokale `activation`;
- den schnellen lokalen `afterimage`;
- die gegenwärtige abgeschlossene `perception`;
- die feste MCM-Neuronengeometrie;
- feste lokale Abtastnachbarschaften;
- feste Rezeptordocks;
- die gemeinsame technische Organismuszeit;
- die letzte abgeschlossene Rezeptorverteilung für eine kausale Fortsetzung.

Zusätzlich existieren Architekturverträge für Energie, Ressourcen,
Selbstregulation, Offline-Erholung und Memory. Diese Grenzen stehen auf
`E0`, `CONTRACT_ONLY` oder `RESEARCH_CLOSED`. Sie sind keine laufenden
Organismusgrößen und dürfen nicht als vorhandene Erhaltungsfunktion gelesen
werden.

## Was das System verlieren kann

### Aktivierung

`activation` kann sich durch Feldrelaxation verändern oder bei fehlendem
Kontakt abklingen. Damit verliert das Feld seine gegenwärtige räumliche Lage.

Ein neutralisierter Aktivierungszustand kann jedoch im nächsten zulässigen
Rezeptorfenster wieder vollständig neuen Weltkontakt aufnehmen. Die Fähigkeit
zur Aufnahme wurde nicht verbraucht.

```text
Verlust gegenwärtiger Feldlage:        ja
Verlust späterer Aufnahmefähigkeit:    nein
organismische Erhaltungsgröße:         nein
```

### Schneller Nachhall

`afterimage` trägt eine kurze geschichtsabhängige Gegenwart. Er relaxiert nach
einer festen Zeitkonstante und kann vollständig auf den neutralen Zustand
zurückgeführt werden.

Sein Verlust beseitigt die schnelle Spur, vermindert aber weder Rezeptordocks
noch Feldkopplung oder spätere Aufnahmefähigkeit.

```text
Verlust schneller Vorgeschichte:       ja
Verlust späterer Feldfähigkeit:        nein
eigenständige Erhaltungsfunktion:       nein
```

### Wahrnehmung

`perception` ist die abgeschlossene lokale Sicht eines Takts. Sie wird beim
nächsten atomaren Fortschritt neu aus Vorzustand, Feldproben und
Rezeptorkontakt gebildet.

Sie ist keine erneuerungsbedürftige Fähigkeit, sondern ein gegenwärtiges
kausales Übergabeobjekt.

### Technische Zeitkontinuität und Snapshot

Der Zeitvertrag verhindert Lücken, Überlappung und unzulässige Fortsetzungen.
Ein Snapshot kann den letzten bekannten Zustand technisch rekonstruieren.

Zeit und Persistenz werden aber nicht durch Feldteilnahme erhalten. Ihr Verlust
macht eine technische Fortsetzung ungültig, beschreibt jedoch keinen
innerorganismischen Verbrauch und keine Erneuerung.

```text
für korrekte Runtime notwendig:         ja
durch Feldteilnahme beansprucht:        nein
organismische Erhaltungsgröße:          nein
```

### Feste Anatomie und Feldparameter

Neuronengeometrie, Nachbarschaft, Rezeptordocks, Reaktionszeit und
Nachhallzeit sind für die heutige Feldfunktion technisch notwendig. Sie sind
jedoch unveränderliche Voraussetzungen der Runtime.

Die Feldteilnahme kann sie weder schwächen noch erhalten oder erneuern. Würden
sie entfernt, wäre der Programmvertrag beschädigt, nicht eine organismische
Ressource verbraucht.

## Audit der drei Suchbereiche

### 1. Lokale Betriebsfähigkeit

Das Feld besitzt eine technisch fest bereitgestellte Fähigkeit, Kontakt
aufzunehmen und über symmetrische Nachbarschaften weiterzugeben.

Es besitzt aber keinen lokalen Betriebsfähigkeitszustand:

- Aufnahme verbraucht keine Rezeptionsmöglichkeit;
- Weiterleitung verändert keine spätere Leitfähigkeit;
- ein neutraler Schnellzustand ist weiterhin vollständig aufnahmefähig;
- Begrenzung auf den normierten Wertebereich ist keine Ressourcenbilanz.

```text
Funktion vorhanden:                     ja
eigene veränderliche Betriebsfähigkeit: nein
```

### 2. Organismische Erhaltung

Im heutigen Feld existiert keine Größe, deren Verlust durch gewöhnliche
Feldteilnahme droht und deren Erhalt für weitere Teilnahme notwendig ist.

Die Architekturbezeichnung `field.energy_resource_boundary` ist nur ein
geschlossener Vertrag. Sie enthält keine Energie, Kapazität, Arbeit,
Regeneration oder Selbsterhaltung.

```text
technische Betriebsbedingungen:         vorhanden
innerorganismische Erhaltungsbedingung: nicht vorhanden
```

### 3. Beanspruchbare Kopplungsfähigkeit

Der momentane lokale Feldfluss beansprucht keine veränderliche Kopplung. Die
symmetrische Diffusionsanatomie und ihre Reaktionszeit bleiben vor und nach
jeder Feldlage identisch.

Kontakt kann Aktivierung erzeugen und Nachhall prägen. Er kann aber keine
vorhandene Leitfähigkeit verbrauchen, erhalten, lösen oder erneut
beanspruchen.

```text
momentane Feldwirkung:                   vorhanden
veränderliche Kopplungsfähigkeit:       nicht vorhanden
```

## Stärkste Gegenprüfung

Eine Zustandsgröße darf nicht allein deshalb als organismisch gelten, weil sie
im Snapshot liegt oder für eine Ausgabe kausal gelesen wird.

Für die heutige Runtime gilt:

```text
activation = 0
+ afterimage = 0
+ unveränderte technische Anatomie
+ neuer zulässiger Weltkontakt
-> vollständige erneute Feldaufnahme
```

Der Verlust aller schnellen Feldinhalte vermindert die technische
Feldfähigkeit nicht. Damit ist kein vorhandener schneller Zustand eine
organismische Erhaltungsressource.

## Ergebnis

```text
gemeinsames Wahrnehmungsfeld:                 vorhanden
fortsetzbarer schneller Organismuszustand:    vorhanden
eigene dynamische Betriebsfähigkeit:          nicht vorhanden
organismische Erhaltungsbedingung:             nicht vorhanden
beanspruchbare Kopplungsfähigkeit:             nicht vorhanden
physische Grundlage für organisches Memory:   nicht hergeleitet
```

Das ist ein belastbarer Architektur-Negativbefund:

> Das aktuelle System kann Feldinhalte verlieren, aber keine eigene
> Feldfähigkeit. Es nimmt Weltkontakt auf, ohne dabei eine für seine weitere
> Teilnahme notwendige organismische Größe zu beanspruchen oder zu erneuern.

Damit ist organisches Memory nicht widerlegt. Es fehlt jedoch eine
eigenständige organismische Erhaltungsbedingung, aus der ein späteres
Memory-Substrat physisch hervorgehen könnte.

## Freigabegrenze

Nicht freigegeben werden:

- eine Energie- oder Kapazitätsvariable;
- Ermüdung oder Regeneration;
- adaptive Rezeptor- oder Feldgewichte;
- veränderliche Kopplungen;
- Offline-Aufladung;
- Memory-, Reflexions- oder Selbstregulationsmechanik.

Keine dieser Mechaniken folgt automatisch aus dem festgestellten Mangel.

## Nächster sinnvoller Schritt

Vor jeder neuen Zustandsgröße wird ein darstellungsoffener
Erhaltungsfunktionsvertrag formuliert. Er muss zuerst ohne technische
Darstellung festlegen:

> Welche konkrete Feldfunktion muss bei Verlust einer organismischen Größe
> nachweisbar beeinträchtigt sein, und wodurch kann dieselbe Weltteilnahme
> diese Funktion erhalten oder erneuern?

Erst wenn diese Funktionsgrenze unabhängig von Memory, Lernen und Semantik
tragfähig ist, dürfen lokale Betriebsfähigkeit, organismische Erhaltung oder
beanspruchbare Kopplungsfähigkeit als technische Kandidaten verglichen werden.
