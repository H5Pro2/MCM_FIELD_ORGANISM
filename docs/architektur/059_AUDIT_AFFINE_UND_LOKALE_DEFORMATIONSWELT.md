# Audit: affine und lokale Deformationswelt

## Status

Konzeptioneller Weltträgeraudit auf
`E1 / LOCAL_DEFORMATION_CANDIDATE_ADMITTED`.

```text
reine Verschiebung als Hauptwelt:       verworfen
affine Fortsetzung als Hauptwelt:       verworfen
affine Fortsetzung als Baseline:        beibehalten
freie Lookupwelt:                       verworfen
lokal stetige Deformationswelt:         bedingt zugelassen
konkrete Weltfamilie:                    vorregistriert in Architektur 060
Generator:                               passiv nach Architektur 060 offen
Memory-Rolle und Feldruntime:            gesperrt
```

Dieser Audit folgt aus der
[offenen Weltbeziehungsform-Grenze](058_OFFENE_WELTBEZIEHUNGSFORM_GRENZE.md).

Er prüft nur, welche Außenwelt die nächste Forschungsfrage fair tragen kann.
Er wählt keine innere MCM- oder Memory-Mechanik.

## 1. Auditfrage

Die nächste Welt soll gleichzeitig:

1. keine endliche Liste fester Beziehungen voraussetzen;
2. aus realen lokalen Kontakten identifizierbar sein;
3. neue konkrete Anfluglagen tragen;
4. eine frühere Beziehung funktional irrelevant werden lassen;
5. eine weitere neue Beziehung aufnehmen können;
6. keine globale Zielform in den Organismus schreiben;
7. starke feste Schätzer als Gegenmodelle zulassen.

Die Frage ist nicht, welche Welt mathematisch am kompliziertesten ist.

Gesucht ist die kleinste Welt, die den festen Zwei-Regime-Automaten verlässt,
ohne das Projekt auf einen programmierten Formelschätzer zu verschieben.

## 2. Reine Verschiebung

```text
T(x) = x + d
```

### Vorteil

- lokal und geometrisch anschaulich;
- neue Werte von `d` können außerhalb früherer Werte liegen;
- technisch leicht symmetrisch und leakfrei aufzubauen.

### Grenze

Ein einziger vollständiger Kontakt bestimmt:

```text
d = y - x
```

Der letzte beobachtete Verschiebungswert trägt danach jeden Holdout derselben
Beziehung.

### Entscheidung

Als Hauptwelt verworfen.

Sie wiederholt die B6-Grenze mit einem skalaren statt binären Regimewert.

## 3. Affine Fortsetzung

```text
T(x) = a * x + b
```

### Vorteil

- konkrete Werte von `a` und `b` können neu sein;
- mindestens zwei nicht entartete Kontakte sind erforderlich;
- neue Anfluglagen lassen sich klar als Holdouts trennen;
- Identifizierbarkeit ist exakt prüfbar.

### Kritische Grenze

Die Welt legt eine globale geschlossene Form fest.

Nach zwei nicht entarteten Kontakten gilt:

```text
a = (y2 - y1) / (x2 - x1)
b = y1 - a * x1
```

Ein exakter Zwei-Punkt-Schätzer löst damit die gesamte Beziehung.

Das Ergebnis würde vor allem prüfen:

```text
Kann das System zwei globale Parameter bewahren?
```

Diese Frage ist technisch legitim, verschiebt den Fokus aber von lokaler
Feldorganisation zu vorstrukturierter Parameterschätzung.

### Entscheidung

Als primäre Welt verworfen.

Die affine Fortsetzung bleibt:

- Identifizierbarkeitskontrolle;
- starke feste Baseline;
- bewusst einfacher Nullvergleich.

## 4. Freie Lookupwelt

```text
x_i -> y_i
ohne lokale Beziehung zwischen benachbarten x
```

### Vorteil

Sie besitzt keine globale Parameterform.

### Grenze

Für ein neues `x` existiert ohne zusätzliche Weltregularität keine begründete
Fortsetzung.

Ein positiver Holdout wäre entweder:

- Wiederholung;
- Archivsuche;
- oder nachträglich gewählte Ähnlichkeit.

### Entscheidung

Verworfen.

Eine nicht identifizierbare Welt kann keinen negativen Organismusbefund
tragen.

## 5. Lokal stetige Deformationswelt

Die bedingt zugelassene Welt besitzt eine lokale räumliche Fortsetzungsform:

```text
y = T(x)
```

Es wird keine globale geschlossene Formel für `T` vorausgesetzt.

Die einzige Weltregularität ist lokale Stetigkeit:

```text
nahe x-Lagen
-> begrenzt nahe y-Lagen
```

In Forschungsnotation kann dies später durch ein vorregistriertes lokales
Änderungsbudget begrenzt werden:

```text
|T(x_i) - T(x_j)|
<=
L * |x_i - x_j|
```

`L` ist eine Eigenschaft der äußeren Prüfwelt. Es ist kein Runtimewert.

## 6. Warum lokale Stetigkeit die kleinere faire Struktur ist

Ohne irgendeine Regularität ist Generalisierung unmöglich.

Die affine Welt gibt eine vollständige globale Form vor.

Lokale Stetigkeit gibt nur vor:

```text
benachbarte Weltursachen dürfen nicht beliebig auseinanderbrechen
```

Sie bestimmt nicht:

- die konkrete Deformationsform;
- einen globalen Parametervektor;
- die Anzahl möglicher Beziehungen;
- eine innere Darstellung;
- die spätere Feldwirkung.

Damit ist sie schwächer als eine affine Formel, aber stärker als eine
beliebige Lookupwelt.

## 7. Nichtaffinität als Pflichtkontrolle

Mindestens drei nicht entartete Kontaktpaare müssen zeigen, dass die konkrete
Weltform nicht vollständig affin ist.

Für drei geordnete Anfluglagen:

```text
x1 < x2 < x3
```

darf die mittlere Austrittslage nicht exakt auf der Geraden zwischen den
äußeren Paaren liegen:

```text
y2
!=
y1 + (x2 - x1) * (y3 - y1) / (x3 - x1)
```

Die Differenz muss oberhalb der vorregistrierten numerischen Toleranz liegen.

Damit wird verhindert, dass der affine Zwei-Punkt-Leser die Hauptwelt
vollständig trägt.

## 8. Lokaler statt globaler Holdout

Der primäre Holdout liegt innerhalb eines erfahrenen lokalen Bereichs:

```text
x_i < x_holdout < x_j
```

Die benachbarten Bildungskontakte begrenzen die mögliche Weltfortsetzung,
ohne sie als globale Formel festzulegen.

Extrapolation außerhalb jedes erfahrenen Bereichs wird zunächst nicht
gefordert. Sie würde eine deutlich stärkere Weltannahme benötigen.

## 9. Neue konkrete Deformationsform

Eine spätere Lebensphase verwendet eine andere lokal stetige Form:

```text
T_alt != T_neu
```

`T_neu` darf:

- keine Kopie einer früheren Form sein;
- nicht nur umbenannt werden;
- nicht durch ein Phasenlabel angekündigt werden;
- keine identischen lokalen Kontaktpaare wiederholen.

Sie muss dasselbe Rezeptor-, Dock-, Zeit-, Energie- und Präzisionsbudget
verwenden.

## 10. Identifizierbarkeitsstufen

Die spätere Weltfamilie muss mindestens enthalten:

```text
D0  keine neue Beziehungserfahrung
D1  ein einzelnes Kontaktpaar
D2  zwei nicht entartete Kontaktpaare
D3  drei nichtaffine lokale Kontaktpaare
D4  zusätzliche lokale Kontakte
D5  randgleiche Paarungspermutation
```

Erwartungsgrenzen:

- D0 erlaubt keine Anpassungsforderung.
- D1 trägt höchstens eine lokale Punktfortsetzung.
- D2 erlaubt eine affine, aber keine nachgewiesen nichtaffine Form.
- D3 ist die kleinste Stufe für lokale Nichtaffinität.
- D4 prüft Reichweite und Stabilität.
- D5 zerstört die lokale Beziehung bei gleichen Randgrößen.

Diese Stufen sind Beobachtungsgrenzen, keine programmierten Lernschwellen.

## 11. Lösung und erneute Bildung

Nach neuer lokaler Erfahrung wird geprüft:

```text
gleiche neue lokale Geschichte
+ unterschiedliche alte Deformationsgeschichte
-> gleiche neue Holdoutfortsetzung
```

Eine weitere neue Deformationsform muss nach eigener lokaler Erfahrung erneut
Holdoutrelevanz tragen können.

Ohne neue Erfahrung wird weder richtige Umschaltung noch Rückkehr gefordert.

## 12. Pflichtbaselines

Die konkrete Weltfamilie muss mindestens vergleichen:

```text
L0  heutige unveränderte Feldruntime
L1  letzter lokaler Verschiebungswert
L2  affine Zwei-Punkt-Fortsetzung
L3  feste lineare Nachbarschaftsinterpolation
L4  feste stückweise lineare Interpolation
L5  feste lokale Polynominterpolation
L6  feste rekursive lokale Ausgleichsrechnung
L7  nächstes bekanntes Deformationstemplate
L8  festes lokales Reservoir mit eingefrorenem Leser
L9  vollständiges Kontaktarchiv mit festem Interpolator
```

Ein endlicher Regimeautomat bleibt zusätzliche Pflichtkontrolle, ist aber
nicht mehr das stärkste Gegenmodell.

## 13. Neue Stopplinie

Eine lokal stetige Welt kann von einem festen Interpolator vollständig
getragen werden.

Falls L3, L4, L5, L6 oder L9 alle Holdouts erklärt, ist nur gezeigt:

```text
lokale Weltgeschichte
-> rekonstruierbare lokale Fortsetzungsform
```

Das ist noch keine organische Feldorganisation.

Die Welt ist dann weiterhin nützlich als Funktionsgrundlage, gibt aber keine
bestimmte innere Mechanik frei.

## 14. Warum diese Welt trotzdem näher am Projektziel liegt

Die Weltbeziehung ist:

- lokal statt global parametrisiert;
- räumlich verteilt statt ein einzelner Regimewert;
- durch mehrere Kontakte getragen;
- auf neue lokale Lagen übertragbar;
- lösbar und durch neue lokale Geschichte ersetzbar;
- ohne Objekt-, Klassen- oder Sprachlabel formulierbar.

Damit passt sie besser zu einem gemeinsamen MCM-Feld als eine globale affine
Parameteraufgabe.

Das ist eine methodische Passung, kein Nachweis organischer Entwicklung.

## 15. Unzulässige Vorwegnahmen

Der Organismus darf nicht erhalten:

- Stützstellen;
- Interpolationsgewichte;
- Nachbarschaftslisten nur für Memory;
- einen Deformationsvektor;
- eine Kurven-ID;
- `L`;
- eine Zielkurve;
- Fehler gegen den späteren Austritt;
- einen globalen Fitparameter;
- eine Auswahl zwischen Interpolatoren.

Diese Größen dürfen nur im äußeren Generator oder passiven Baselineobserver
existieren.

## 16. Scheitergrenzen

Die konkrete Prüfwelt scheitert, wenn:

- ihre Hauptformen doch affin sind;
- Holdouts außerhalb jeder erfahrenen lokalen Umgebung liegen;
- lokale Stetigkeit nur durch ein Runtimeflag bekannt wird;
- dieselben konkreten Paare wiederholt werden;
- neue Formen durch Zeit oder Ereigniszahl bezeichnet sind;
- D5 die Randverteilungen nicht erhält;
- ein Reset alte Wirkung entfernt;
- Generator oder Observer in das Feld zurückschreibt;
- starke feste Interpolatoren nicht verglichen werden;
- aus einem Baselinesieg direkt eine Memory-Mechanik abgeleitet wird.

## 17. Aussagegrenze

Der Audit trägt:

- die Ablehnung reiner Verschiebung als zu schwach;
- die Ablehnung affiner Fortsetzung als zu global vorstrukturiert;
- affine Fortsetzung als starke Baseline;
- die Ablehnung beliebiger Lookupwelten als nicht identifizierbar;
- die bedingte Zulassung einer lokal stetigen Deformationswelt;
- D0 bis D5 und L0 bis L9 als Mindestgrenzen.

Er trägt nicht aus sich allein:

- die inzwischen separat vorregistrierte konkrete Deformationswelt;
- ein numerisches Änderungsbudget `L`;
- eine Stützstellengeometrie;
- eine innere Feld- oder Memorydarstellung;
- eine Updategleichung;
- Feldintelligenz.

## Freigabegrenze

```text
Weltträgeraudit abgeschlossen:          ja
lokale Deformationswelt bedingt offen:  ja
konkrete Weltfamilie vorregistriert:    ja, in Architektur 060
Generator freigegeben:                  ja, nur passiv nach Architektur 060
Memory-Kandidat freigegeben:            nein
Runtime-Erweiterung freigegeben:        nein
```

## Nächster Schritt

Die
[minimale lokal stetige Deformationswelt](060_MINIMALE_LOKAL_STETIGE_DEFORMATIONSWELT.md)
ist inzwischen vorregistriert und umgesetzt. Der
[Baselinebefund](../forschung/008_LOKALE_DEFORMATIONSWELT_BASELINEBEFUND.md)
bestätigt die erwartete Grenze: L4 trägt alle fair identifizierbaren Holdouts.
Memory-Rolle und Feldruntime bleiben unverändert.
