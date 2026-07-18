# Technischer Übergabevertrag 009

## Status

Architekturentscheid und technische Voruntersuchung vor `GF_001`.

Dieser Schritt ergänzt keine Runtime-Mechanik. Er bestimmt, welche zeitliche
Aussage ein bereits vorhandenes `ReceptorCompletionEvent` tragen darf.

## Ausgangsproblem

Die Prüfungen 007 und 008 zeigen:

- Audio besitzt ein exaktes Quellfenster auf der Sample-Uhr, aber keine
  belastbare Abbildung dieses Fensters auf die Organismusuhr.
- Video besitzt eine Frameidentität, aber weder Aufnahmezeitpunkt noch
  Belichtungsdauer.
- Read-Dauer, nominelle Rate und Backend-Einstellwerte sind keine
  Weltstützen.

Eine Rekonstruktion der unbekannten Außenweltzeit wäre daher unbelegt.

## Kausale Grenze

Ein reduzierter Rezeptorzustand darf ab dem gemessenen Abschluss seiner
technischen Bildung an den Organismus übergeben werden:

```text
Quellkontakt
-> sensorspezifische Reduktion
-> abgeschlossener ReceptorContactFrame
-> gemessene Übergabegrenze auf der Organismusuhr
-> möglicher Eintritt in das gemeinsame MCM-Feld
```

Die Übergabegrenze sagt ausschließlich:

> Dieser abgeschlossene reduzierte Zustand steht dem Organismus ab jetzt
> kausal zur Verfügung.

Sie behauptet nicht:

- wann der äußere Weltkontakt exakt begann,
- wie lange er in der Außenwelt bestand,
- dass ein Audio- und ein Videozustand dieselbe äußere Gegenwart abbilden,
- dass der Zustand bis zum nächsten Rezeptorereignis gültig bleibt,
- dass mit jeder Übergabe ein vollständiger Feldschritt ausgeführt wird.

## Vorhandener technischer Träger

Der Vertrag benötigt keinen neuen Zustandstyp.

`OrganismTimedReceptorFrame` bewahrt:

- den vollständigen reduzierten `ReceptorContactFrame`,
- sein natives Quellfenster,
- das gemessene technische Bildungsintervall auf der Organismusuhr.

`ReceptorCompletionEvent` bewahrt:

- Modalitätsherkunft,
- Snapshotidentität,
- technischen Read-Beginn,
- gemessene Abschluss- und Übergabegrenze.

Die Übergabe verändert weder Kontaktwerte noch Quellfenster. Sie fügt keine
Gültigkeitsdauer hinzu.

## Tragfähigkeit

Der Vertrag ist für **kausale Verfügbarkeit** ausreichend:

1. Kein Feldzustand kann einen noch nicht abgeschlossenen Rezeptorzustand
   lesen.
2. Alle Übergaben lassen sich auf einer gemeinsamen Organismusuhr ordnen.
3. Gleiche Abschlusszeiten bleiben ungeordnet.
4. Unterschiedliche Modalitätsraten bleiben sichtbar.
5. Die unbekannte Außenweltstütze wird nicht durch Schätzung ersetzt.

Der Vertrag ist nicht ausreichend für:

- äußere Gleichzeitigkeit,
- Kontaktintegration über reale Dauer,
- Halten eines letzten Zustands,
- Ratengewichtung,
- Feldfortschritt,
- multimodale Beziehung oder Organisation.

## Abgleich mit den realen Audits

Die 326 Abschlussereignisse aus Audit 003 können als kausale Übergaben gelesen
werden. Ihre Verteilung bleibt unverändert:

| Rolle | Ergebnis |
|---|---:|
| auditive Übergaben | 310 |
| visuelle Übergaben | 16 |
| exakt gemeinsame Abschlussgruppen | 0 |

Der Befund aus Audit 003 bleibt bestehen: Ein vollständiger Feldschritt pro
Übergabe wäre durch die schnellere auditive Strecke dominiert. Der neue
Vertrag löst diese Ratenfrage ausdrücklich nicht.

## Befund

Das gemeinsame MCM-Feld benötigt für kausalen Eingang keine erfundene
Außenweltzeit. Es benötigt eine sichere Organismusgrenze, ab der ein
abgeschlossener Rezeptorzustand verfügbar ist.

```text
unbekannte Weltzeit
!= gemessene Übergabezeit
!= Feldwirkungsdauer
!= Feldschritt
```

Damit ist die Rezeptorübergabe zeitlich ausreichend definiert. Offen bleibt,
wie asynchrone Übergaben in einer rateninvarianten kontinuierlichen Feldzeit
wirken dürfen.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Die nächste technische Prüfung muss zwei streng getrennte Größen verwenden:

1. kontinuierlich verstrichene Organismuszeit,
2. punktuelle kausale Rezeptorübergaben.

Sie muss zeigen, ob ein passiver gemeinsamer Feldvorschlag bei gleicher
Weltgeschichte gegenüber verschieden dichter Übergabe derselben Kontakte
invariant bleibt. Dabei sind Halten, Interpolation, globale Ratenangleichung
und vorgegebene Modalitätsgewichte unzulässig.

Die nachfolgende
[Technische Übergabemodell-Falsifikation 010](TECHNISCHE_UEBERGABEMODELL_FALSIFIKATION_010.md)
zeigt, dass Punktübergabe und vollständige Quellfenster ratenabhängig sind,
Halten eine zusätzliche Annahme wäre und der rateninvariante
Quellfortschritt derzeit nur für Audio belegt ist.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
