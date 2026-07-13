# Vertrag des gemeinsamen MCM-Strangs

## 1. Zweck

Der gemeinsame MCM-Strang ist die vorgesehene lokale Feldgrenze, an der bereits
gebildete visuelle, auditive und taktile MCM-Zustände gemeinsam gegenwärtig
werden können.

```text
visuelles MCM  --\
auditives MCM  ----> gemeinsamer MCM-Strang -> innere Gesamtlage
taktiles MCM   --/
```

Dieser Vertrag legt noch nicht fest, wie gemeinsame Feldwirkung entsteht.

## 2. Eingang und Ausgang

Der Strang erhält ausschließlich gültige Zustände gemäß dem
[sensorspezifischen MCM-Schnittstellenvertrag](001_SENSORSPEZIFISCHER_MCM_SCHNITTSTELLENVERTRAG.md).
Er erhält keine Rohsensorik und keine Observerdiagnose.

Sein Ausgang ist kein Patterncode. Die gegenwärtige räumlich-zeitliche
Zustandslage des Strangs selbst ist die multimodale innere Gesamtlage.

## 3. Erforderliche Eigenschaften

- Modalitäten und lokale Herkunft bleiben unterscheidbar.
- Gleichzeitigkeit und Zeitversatz bleiben kausal erhalten.
- Fehlende Modalitäten bleiben von Nullkontakt unterscheidbar.
- Jede mögliche Wechselwirkung ist lokal und offen dokumentiert.
- Alle Bereiche lesen denselben vorherigen Zustandsschnappschuss.
- Technische Iterationsreihenfolge bevorzugt keinen Sensorast.
- Lokale Aktivität und Nachhall sind endlich begrenzt.
- Ein einzelner Sensorast kann allein eine gültige Gesamtlage erzeugen.
- Neue Sensoräste sind ohne semantische Neudefinition bestehender Äste
  anschließbar.

## 4. Nicht festgelegt

Noch offen bleiben:

- Geometrie und Größe des Strangs
- Anzahl und Lage sensorischer Anschlüsse
- lokale Übertragungsform
- gerichtete oder ungerichtete Nachbarschaften
- Form und Zeitskala des Nachhalls
- lokale Ressourcenform
- mögliche Rückwirkung auf sensorische MCM-Felder
- jede langsamere Kopplungs- oder Organisationsvariable

Keine dieser Lücken darf durch eine willkürliche Konstante geschlossen werden,
bevor eine konkrete Funktion und Gegenprüfung benannt ist.

## 5. Verbotene Abkürzungen

Der Strang darf nicht als folgende Mechanik implementiert werden:

- einfache globale Summe als behauptete Feldwirkung
- bloße Datenverkettung als behauptete Integration
- globales Pooling oder Mittelwert
- feste multimodale Merkmalsformel
- Klassifikator, Clusterer oder Attention-Modul
- zentrale Gewinnerregel
- Pattern-, Episoden- oder Semantik-ID
- Reward-, Ziel- oder Wichtigkeitskanal
- externes Memory mit Rückschreiben

Summe, Verkettung und vollständig getrennte Felder sind zulässige Baselines,
nicht die Zielmechanik.

## 6. Erster Beobachtungsumfang

Ein erster passiver Versuch darf nur feststellen:

1. ob alle sensorischen Zustände verlustfrei und unterscheidbar ankommen,
2. ob gemeinsame Zeitlage korrekt dargestellt wird,
3. ob fehlende und inaktive Äste getrennt bleiben,
4. ob Reihenfolge und Observer das Ergebnis nicht verändern,
5. ob eine vorgeschlagene lokale Zusammenführung mehr leistet als die
   verpflichtenden Baselines.

Er darf keine Musterbildung, Syntax, Kontext, Semantik oder Feldintelligenz
behaupten.

## 7. Baselines

### B0: Vollständig getrennte Felder

Keine gemeinsame Wechselwirkung. Die drei MCM-Zustände werden nur parallel
beobachtet.

### B1: Verkettung

```text
G = [V, A, T]
```

Erhält Information, erzeugt aber keine gemeinsame Feldwirkung.

### B2: Summe

```text
G = V + A + T
```

Kann Konstellationen ununterscheidbar machen und dient als Verlustbaseline.

### B3: Festes nichtplastisches Reservoir

Prüft, ob beobachtete zeitliche Vielfalt bereits aus fester Rekurrenz folgt.

Eine spätere Strangmechanik ist nur interessant, wenn eine benannte Funktion
nicht vollständig durch B0 bis B3 erklärt wird.

## 8. Pflichtkontrollen

- jede Modalität einzeln
- jede Zweierkombination
- alle drei Modalitäten
- kein aktiver Sensorast
- fehlender Ast gegen aktiven Nullzustand
- gleiche Energie in verschiedener Modalitätsverteilung
- gleiche Zustände in anderer Ankunfts- und Berechnungsreihenfolge
- kontrollierter Zeitversatz
- Amplitudenskalierung
- verschiedene technische Geometrien
- Observer an und aus
- vollständiger Reset

## 9. Stoppregeln

Die Untersuchung stoppt vor weiterer Mechanik, wenn:

- die gewünschte Eigenschaft nur durch Labels oder globale Auswahl entsteht,
- technische Reihenfolge die Gesamtlage verändert,
- fehlender Kontakt und Nullzustand zusammenfallen,
- eine Modalität die anderen nur durch Skalierung dominiert,
- eine Summe, Verkettung oder ein festes Reservoir alles erklärt,
- für einen positiven Befund eine neue semantische Variable nötig wird.

## 10. Freigabegrenze

Der Strang ist derzeit E0. Freigegeben ist nur die passive Vorregistrierung
eines Schnittstellen- und Baselineversuchs. Nicht freigegeben sind konkrete
Fusionsmechanik, plastische Kopplung, langfristige Organisation, Effektoren,
Handlung oder Semantik.

## 11. Bester nächster Schritt

[Methodik 001](../methodik/001_PASSIVE_SENSORSCHNITTSTELLEN_PRUEFUNG.md)
schreibt die passive Schnittstellenprüfung vor. Als Nächstes folgt nur ihr
mechanikfreies Testobjekt. Eine konkrete Strangdynamik bleibt gesperrt, bis eine
Funktion benannt ist, die B0 und B1 nicht bereits erfüllen.
