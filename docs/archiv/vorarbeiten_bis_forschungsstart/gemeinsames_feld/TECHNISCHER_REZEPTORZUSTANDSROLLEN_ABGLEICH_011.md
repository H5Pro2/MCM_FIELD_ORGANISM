# Technischer Rezeptorzustandsrollen-Abgleich 011

## Status

Passive Verhaltensprüfung vor `GF_001`.

Der Abgleich prüft, welcher Teil der vorhandenen Eingangsarchitektur heute
tatsächlich Zustand trägt. Es wird kein aktueller Rezeptorzustand, Halten,
Nachhall oder Feldfortschritt ergänzt.

## Gegenhistorien

### Audio

Zwei auditive Pfade erhalten dieselbe aktuelle Nullprobe:

- Pfad A besitzt zuvor ein vollständiges Sinusfenster,
- Pfad B besitzt ausschließlich Nullkontakt.

Nach einem neuen `10-ms`-Hop unterscheiden sich ihre Ausgaben maximal um
`0,4295238308`. Nach einem vollständigen `100-ms`-Nullfenster ist die frühere
Aktivität in Pfad A exakt verschwunden.

Damit ist der auditive Eingang ein endlicher rollender Quellenprozess:

```text
letzte 100 ms Samples
-> alle 10 ms ein unveränderlicher auditiver Snapshot
```

Der Prozess trägt Quellgeschichte. Der ausgegebene Snapshot selbst besitzt
keine Gültigkeitsdauer und wird nicht zwischen Ausgaben fortgeschrieben.

### Video

Ein visueller Rezeptor sieht zuerst einen starken lokalen Kontrast und danach
das Probe-Bild. Ein frischer Rezeptor sieht nur dasselbe Probe-Bild mit
derselben Frameidentität.

Ergebnis:

```text
maximale Wertdifferenz = 0
Snapshot-Digest gleich = ja
```

Der visuelle Rezeptor ist damit aktuell eine zustandslose
Einzelbildtransformation. Frühere Bilder wirken nicht in seine nächste
Ausgabe hinein.

### Rezeptorenverteiler

Ein Verteiler erhält vor der Probe einen kontrastierenden Kontakt. Ein zweiter
Verteiler erhält nur die identische Probe. Beide besitzen dieselbe feste
Dock-Anatomie.

Die Probe-Digests sind exakt gleich. Der Verteiler bewahrt seine Docks, aber
keine früheren Kontakte.

## Rollenabgleich

| Bereich | tatsächlich getragener Zustand | nicht getragen |
|---|---|---|
| auditiver Rezeptor | endliches rollendes Samplefenster | fortbestehende Ausgabe |
| visueller Rezeptor | Konfiguration | Bildgeschichte, fortbestehende Ausgabe |
| Rezeptorsnapshot | unveränderliche aktuelle Messform | Gültigkeitsdauer |
| Verteiler | stabile Dock-Anatomie | Kontaktgeschichte |
| gemeinsames MCM-Feld | eigener Neuronen- und Nachhallzustand | aktueller Rezeptorpuffer |

## Befund

Die drei in Audit 010 diskutierten Rollen sind nicht frei auswählbare Namen.
Die aktuelle Implementierung enthält bereits:

```text
Audio = eigener endlicher dynamischer Rezeptorprozess
Video = punktueller zustandsloser Rezeptorsnapshot
Verteiler = zustandslose Kontaktübergabe bei stabiler Anatomie
```

Es existiert an der gemeinsamen Dockgrenze kein modalitätsübergreifender
„gegenwärtiger Rezeptorzustand“, der zwischen Übergaben physisch fortbesteht.
Ein solcher Zustand kann deshalb nicht als bereits vorhandene Eigenschaft
gelesen werden.

Gleichzeitig wäre es falsch, Audio nur als unabhängige Punktfolge zu behandeln:
Seine aufeinanderfolgenden Snapshots überlappen kausal im rollenden
Quellenprozess.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Die nächste Entscheidung liegt jetzt vor dem gemeinsamen MCM-Feld: Entweder
bleiben Rezeptoren ausdrücklich modalitätseigene dynamische Prozesse, oder es
müsste ein begründeter gemeinsamer Vertrag für gegenwärtigen Rezeptorkontakt
entstehen. Eine solche Vereinheitlichung darf weder Videohalten verstecken
noch die bekannte auditive Fenstergeschichte löschen.

Vor neuem Runtime-Code ist daher ein minimaler Rezeptorprozessvertrag zu
formulieren, der nur Zustandsbesitz, Übergabe und Lösung beschreibt. Seine
konkrete Dynamik darf nicht für alle Sinnesarten hart gleichgesetzt werden.

Der nachfolgende
[Technische Rezeptorprozessvertrag 012](TECHNISCHER_REZEPTORPROZESSVERTRAG_012.md)
setzt genau diese Grenze als `CONTRACT_ONLY` um, ohne eine neue
Rezeptordynamik freizugeben.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
