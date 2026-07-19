# Zulassungsvertrag für einen feldinternen Freiheitsgrad

## Status

```text
Vertragsstufe:          E0 / CONTRACT_ONLY
zusätzliche Feldfunktion: funktional abgegrenzt
Variable:               nicht festgelegt
Gleichung:              nicht festgelegt
Datenstruktur:          nicht festgelegt
Runtime-Änderung:       gesperrt
passiver Kandidat:      nicht freigegeben
```

Dieser Vertrag folgt aus dem
[Audit der MCM-Feldtopologie-Nutzbarkeit](098_AUDIT_MCM_FELDTOPOLOGIE_NUTZBARKEIT.md).

Er sucht keinen Speicherplatz. Er beschreibt ausschließlich, welche
zusätzliche Feldfunktion grundsätzlich begründet sein müsste, bevor eine
digitale Darstellung untersucht werden darf.

## Ausgangsgrenze

Die vorhandene Runtime besitzt:

```text
aktuelle Feldform
+ feste lokale Nachbarschaft
+ feste symmetrische Diffusion
+ optionalen schnellen Nachhall
-> nächste Feldform
```

Diese laufende Feldwirkung ist kausal real. Ihre funktionale Weiterleitung
verändert sich jedoch nicht durch Feldgeschichte.

## Gesuchte Funktion

Gesucht wird:

> Ein fehlender feldinterner Freiheitsgrad, durch den das gemeinsame MCM-Feld
> seine spätere lokale Wirksamkeit aus eigener Welt- und Feldgeschichte
> verändern könnte.

Diese Formulierung bezeichnet keine Variable und keinen Zustandstyp.

Sie legt insbesondere nicht fest, ob eine spätere digitale Darstellung:

- an einem Feldträger liegt;
- räumlich verteilt ist;
- als Mediumeigenschaft beschrieben wird;
- mehrere schnelle Feldrollen gemeinsam betrifft;
- überhaupt als zusätzliche gespeicherte Größe erforderlich ist.

## Funktionaler Minimalunterschied

Ein zulässiger Freiheitsgrad müsste grundsätzlich ermöglichen:

```text
Weltgeschichte A ─┐
                  ├-> bekannte schnelle Feldlage angeglichen
Weltgeschichte B ─┘
                     + identischer späterer Weltkontakt
                     -> unterschiedliche lokale Feldweiterleitung
```

Der Unterschied muss bereits während der Feldbildung auftreten. Ein
nachgeschalteter Observerwert oder eine spätere Datenbankabfrage genügt nicht.

## Verbindliche Anforderungen

### 1. Reale lokale Entstehungsursache

Eine Veränderung darf nur aus tatsächlich abgeschlossener lokaler Welt- und
Feldwirkung entstehen.

Nicht ausreichend sind:

- verstrichene Zeit allein;
- Aufrufzahl;
- Wiederholungszähler;
- Phasen- oder Ereigniskennung;
- Observerauswertung;
- importierte Geschichte;
- zufällige interne Anregung.

### 2. Zugehörigkeit zum gemeinsamen MCM-Feld

Die mögliche Wirkung muss innerhalb derselben Feldkausalität liegen, die
Rezeptorkontakt, lokale Feldwahrnehmung und nächste Feldbildung verbindet.

Ein separates Memory-Modul, eine Relationstabelle oder ein nachgeschalteter
semantischer Leser erfüllt diese Bedingung nicht.

### 3. Kausale Änderung späterer Feldweiterleitung

Die frühere Feldteilnahme muss die spätere Aufnahme, räumliche Weitergabe oder
lokale Feldbildung tatsächlich verändern.

Nur ein anderer gespeicherter Wert ohne andere Feldwirkung genügt nicht.

### 4. Nichtredundanz

Die Wirkung darf nicht vollständig erklärt werden durch:

- aktuellen Rezeptorkontakt;
- aktuelle Aktivierung;
- schnellen Nachhall;
- mehrere feste Zeitskalen;
- feste Diffusion;
- statische Rekurrenz;
- unabhängigen Integrator;
- feste Sättigung;
- festen Attraktor;
- globale oder lokale Normalisierung;
- künstliches Rauschen.

### 5. Räumliche Begrenzung

Entstehung und Wirkung müssen an einen endlichen lokalen Feldweg gebunden
bleiben.

Eine sofortige globale Änderung, globale Rangliste oder globale
Kapazitätsverteilung ist unzulässig.

### 6. Zeitliche Begrenzung

Keine entstandene Wirkung darf allein wegen ihrer Entstehung unbegrenzt
fortbestehen.

Gleichzeitig darf eine feste Ablaufzeit nicht bestimmen, wann die Wirkung
endet. Die tatsächliche weitere Feldgeschichte muss kausal relevant bleiben.

### 7. Abschwächung und vollständige Funktionslosigkeit

Andere reale lokale Feldgeschichte muss eine frühere Wirkung abschwächen und
vollständig funktionslos werden lassen können.

Unzulässig sind:

- Löschbefehl;
- Reset als Organismusfunktion;
- besondere Lösungsphase;
- fest programmierte Löschschwelle;
- passive Rückkehr, die nur einen alten Sollzustand rekonstruiert.

### 8. Weltbezogene Neubildung

Nach vollständiger Funktionslosigkeit muss neue lokale Weltgeschichte wieder
eine Wirkung hervorbringen können.

Welche Feldbereiche beteiligt sind und welche Form entsteht, darf nicht
vorgegeben werden.

### 9. Gleiche Naturbedingung

An technisch gleichartigen Feldorten muss dieselbe lokale Naturbedingung
gelten.

Unzulässig sind:

- spezielle Lernneuronen;
- feste Rollen für Quelle oder Ziel;
- feste Neuronenindizes;
- Partner- oder Kantenlisten;
- modalitätsspezifische Lernregeln;
- semantisch ausgezeichnete Feldorte.

### 10. Zeit- und Ausführungsneutralität

Eine spätere Mechanik müsste:

- von realer Organismusdauer statt Aufrufzahl abhängen;
- bei gröberer und feinerer technischer Zeitteilung denselben kausalen Verlauf
  tragen;
- unabhängig von Neuronen- und Sampleiteration sein;
- Snapshotunterbrechung exakt überstehen;
- durch einen passiven Observer unverändert bleiben.

## Drei notwendige Beobachtungsebenen

Jeder spätere Kandidat muss getrennt ausweisen:

```text
aktuelle Feldform
laufende lokale Feldwirkung
mögliche entwickelte Feldorganisation
```

Eine komplexe oder wiederkehrende Feldform ist noch keine entwickelte
Organisation. Eine entwickelte Organisation ist erst dann Kandidat, wenn sie
eine spätere Feldfunktion kausal verändert.

## Verbotene Vorfestlegungen

Der Vertrag führt nicht ein:

- Gewicht;
- Kante;
- Partner;
- Beziehung;
- Memory-Slot;
- Kapazitätswert;
- Lernrate;
- Schwelle;
- Verstärkungsregel;
- Zielmuster;
- Objekt- oder Wortklasse;
- Reward;
- Bedeutung;
- gewünschte Topologie.

Auch die Begriffe Abschwächung, Lösung und Neubildung bezeichnen nur
beobachtbare Funktionen. Sie sind keine erlaubten Befehle oder Updatephasen.

## Verhältnis zu früheren Verträgen

Der
[darstellungsoffene lokale Organisationsvertrag](039_DARSTELLUNGSOFFENER_LOKALER_ORGANISATIONSZUSTAND.md)
und die
[funktionale Grenze verteilter Organisation](041_FUNKTIONALE_GRENZE_VERTEILTER_LOKALER_ORGANISATION.md)
bleiben als Baseline- und Kausalitätsgrenzen gültig.

Der neue Vertrag korrigiert nur die Forschungsreihenfolge:

```text
früher:
fehlenden Memory-Zustand annehmen
-> Darstellung suchen

jetzt:
fehlende Feldfunktion begründen
-> prüfen, ob ein zusätzlicher Freiheitsgrad notwendig ist
-> Darstellung weiterhin offenlassen
```

Der
[Memory-Substratvertrag](048_DARSTELLUNGSOFFENER_MEMORY_SUBSTRATVERTRAG.md)
bleibt historische Forschungsgrenze. Er gibt keine aktuelle Priorität zur
Suche nach einem separaten Substrat.

## Zulässige spätere Interventionen

Erst nachdem ein konkreter Kandidat unabhängig begründet wurde, müsste seine
kausale Rolle mindestens durch folgende Gegenfakten geprüft werden:

1. gleiche Weltgeschichte ohne mögliche Organisationsbildung;
2. gleiche spätere Probe bei verschiedener Vorgeschichte;
3. Angleichung aller bekannten schnellen Feldrollen;
4. Neutralisierung der Kandidatenwirkung;
5. Tausch der Kandidatenwirkung zwischen kontrollierten Zweigen;
6. Blockade des realen lokalen Feldwegs;
7. vollständige funktionale Lösung;
8. neue Weltgeschichte nach dieser Lösung.

Diese Interventionen sind Prüfanforderungen. Sie definieren keine
Kandidatenmechanik.

## Scheiterfälle

Ein möglicher Kandidat wird gestoppt, wenn:

- seine Wirkung nur aus der gewählten Formel folgt;
- eine einfachere Baseline dieselbe Funktion trägt;
- er nur mehr oder länger speichert;
- er feste Attraktoren oder Zielzustände einführt;
- er ohne Weltkontakt entsteht;
- er nicht vollständig funktionslos werden kann;
- er für Neubildung einen Reset oder freien Slot benötigt;
- eine Ereignis-, Partner- oder Bedeutungskennung erforderlich ist;
- technische Schrittweite oder Iterationsreihenfolge das Ergebnis bestimmt.

## Offener Nullausgang

Der Vertrag lässt ausdrücklich zu:

> In der gegenwärtigen Architektur kann kein unabhängig begründeter
> feldinterner Freiheitsgrad gefunden werden.

In diesem Fall wird keine Variable erfunden. Stattdessen muss konzeptionell
neu bewertet werden:

- ob die aktuelle MCM-Zustandsgrenze zu eng ist;
- ob reale Weltteilnahme eine noch fehlende funktionale Randbedingung besitzt;
- ob das Ziel mit der gewählten digitalen Feldklasse grundsätzlich nicht
  erreichbar ist.

## Freigabegrenze

```text
zusätzliche Feldfunktion beschrieben: ja
unabhängige physische Ursache gefunden: nein
digitale Darstellung gewählt:         nein
Updategleichung gewählt:               nein
passiver Kandidat freigegeben:         nein
Runtime-Erweiterung freigegeben:       nein
Feldtopologie-Evidenz:                 E0
```

## Richtungsentscheidung

Der nächste Schritt darf keinen Mechanismus implementieren.

Zuerst muss geprüft werden, ob in der vorhandenen Welt-, Rezeptor- und
Feldkausalität eine **unabhängig notwendige Feldfunktion** fehlt, die auch ohne
das gewünschte Memory- oder Topologieergebnis sinnvoll wäre.

Ohne diese Begründung bleibt der Freiheitsgrad rein funktional beschrieben
und die Runtime geschlossen.

## Wie es am besten weitergeht

Als nächster Schritt ist ausschließlich ein konzeptioneller
**Ursachenaudit der feldinternen Organisationsfunktion** zulässig.

Er prüft:

```text
Welche reale lokale Feldteilnahme könnte eine veränderte spätere
Feldwirksamkeit notwendig machen, auch wenn daraus niemals Memory,
Semantik oder Feldtopologie entsteht?
```

Kann diese Frage nicht unabhängig beantwortet werden, wird kein Kandidat
freigegeben.

## Umsetzungsstatus

Der
[Ursachenaudit der feldinternen Organisationsfunktion](100_URSACHENAUDIT_FELDINTERNE_ORGANISATIONSFUNKTION.md)
hat alle zugelassenen vorhandenen Quellen geprüft.

Keine Quelle trägt ohne neue Mechanik eine eigenständige spätere Feldfunktion
über Aktivierung, Nachhall und feste Diffusion hinaus. Der offene Nullausgang
dieses Vertrags ist damit eingetreten. Runtime und Kandidatenfreigabe bleiben
geschlossen.
