# Minimaler Rezeptorprozessvertrag

## Zweck

Dieser Vertrag beschreibt nur die gemeinsame Grenze aller Sinnesrezeptoren.
Er legt keine gemeinsame Rezeptordynamik fest.

Der Ausgangspunkt ist der
[Rezeptorzustandsrollen-Abgleich 011](../gemeinsames_feld/TECHNISCHER_REZEPTORZUSTANDSROLLEN_ABGLEICH_011.md):
Audio besitzt bereits einen endlichen rollenden Quellenprozess, Video ist
derzeit eine zustandslose Einzelbildtransformation.

## Gemeinsame Grenze

Jeder Rezeptorpfad darf eine eigene lokale Prozessform besitzen:

```text
lokaler Quellkontakt
-> modalitätseigener Rezeptorprozess
-> abgeschlossener unveränderlicher Snapshot
-> kausale Übergabe
```

Zulässig sind:

- ein endlicher zustandstragender Quellenprozess,
- eine ausdrücklich zustandslose Transformation,
- andere später geprüfte lokale Prozessformen.

Nicht zulässig ist, aus der gemeinsamen Schnittstelle eine gemeinsame
Fenstergröße, Schrittweite, Zerfallsrate oder Halteregel abzuleiten.

## Zustandsbesitz

Wenn ein Rezeptor Zustand trägt, dann gilt:

1. Der Zustand gehört ausschließlich zum lokalen Rezeptorprozess.
2. Er verändert sich nur durch neuen lokalen Quellkontakt oder belegten
   Fortschritt seiner nativen Quellstütze.
3. Er ist endlich und muss seine frühere Wirkung vollständig verlieren
   können.
4. Seine Quelluhr und Herkunft bleiben erhalten.
5. Observer, Verteiler und gemeinsames Feld schreiben nicht in ihn zurück.

Ein zustandsloser Rezeptor muss bei identischer aktueller Probe unabhängig
von früheren Proben exakt dieselbe Ausgabe erzeugen.

## Snapshot und Abwesenheit

Jede Ausgabe ist ein abgeschlossener unveränderlicher Rezeptorsnapshot. Sie
trägt nur die bei ihrer Bildung belegte Quelllage.

```text
kein neuer Snapshot
!= fortbestehender Kontakt
!= Nullkontakt
!= gültiger letzter Wert
```

Fehlende Ausgabe erzeugt daher weder einen gehaltenen Kontakt noch einen
ersatzweisen Nullwert. Ob und wie ein lokaler Prozess zwischen Ausgaben
weiterläuft, muss aus seiner eigenen geprüften Quellmechanik folgen.

## Verbotene Vereinheitlichungen

- Sample-and-Hold oder `valid_until`,
- letzter gemeinsamer Kontaktpuffer,
- erfundene Kontaktdauer,
- gemeinsame Fenster- oder Hopgröße,
- gemeinsame Zerfallsrate,
- globale Ratennormalisierung,
- Modalitätsgewichte oder Gewinner,
- Feldrückwirkung in die Rezeptoren,
- Bedeutung, Objektklasse oder Muster-ID,
- Speicherung von Rohpayloads.

## Passung zum aktuellen Stand

### Audio

Der rollende `100-ms`-Prozess mit `10-ms`-Quellfortschritt erfüllt die
Zustandsbesitzgrenze als bereits vorhandene technische Rezeptormechanik. Das
ist keine Freigabe, diese Werte auf andere Sinne zu übertragen.

### Video

Die zustandslose Bildtransformation ist weiterhin zulässig. Der Vertrag
fordert nicht automatisch ein visuelles Zeitfenster. Er macht lediglich
sichtbar, dass Video derzeit keinen lokalen Prozess zwischen Frames trägt.

### Verteiler und gemeinsames Feld

Beide lesen nur abgeschlossene Snapshots. Der Verteiler bewahrt Dock-Anatomie,
aber keine Kontaktgeschichte. Das gemeinsame MCM-Feld besitzt seinen eigenen
Neuronen- und Nachhallzustand; dieser ist kein Rezeptorzustand.

## Freigabestatus

```text
Architekturvertrag: E0 / CONTRACT_ONLY
neue Rezeptordynamik: nicht freigegeben
Halten:              nicht freigegeben
Feldrückwirkung:     nicht freigegeben
```

Der Vertrag kann spätere Kandidaten abweisen. Er implementiert keinen neuen
Prozess und wählt keine zeitliche Eingangsform für das gemeinsame Feld.
