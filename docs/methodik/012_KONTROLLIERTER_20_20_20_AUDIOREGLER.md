# Methodik 012: Kontrollierter 20/20/20-Audioregler

## 1. Zweck

Der reale Pilot 014 traf die vorgesehene mittlere Ruhephase messtechnisch
nicht. Deshalb wird eine vollständig kontrollierte äußere Testwelt gebaut:

```text
20 Sekunden Signal
-> 20 Sekunden exakte numerische Stille
-> 20 Sekunden dasselbe Signal
```

Der Regler gehört nicht zur MCM. Er ist ausschließlich eine deterministische
Quelle vor dem Audiorezeptor.

## 2. Signal

Die beiden Kontaktphasen verwenden dieselbe lokale Mehrtonlage:

```text
250 Hz + 1.000 Hz + 4.000 Hz
```

Jeder Anteil besitzt dieselbe feste technische Testamplitude. Die Summe bleibt
im normalisierten Audiodomainbereich. Am Beginn der dritten Phase startet
dieselbe Signalfolge erneut an derselben lokalen Phase.

Das Signal besitzt keine Bedeutung, Klasse oder Zielrolle.

## 3. Exakte Taktung

```text
Abtastrate:       48.000 Hz
Chunk:            480 Samples = 10 ms
Chunks je Phase:  2.000
Chunks gesamt:    6.000
```

Phasenwechsel liegen ausschließlich auf Chunkgrenzen. Betriebssystemzeit und
manuelle Reaktion werden nicht verwendet.

## 4. Stillevertrag

In Phase 2 liefert jeder Chunk ausschließlich exakte Nullen. Es gibt:

- kein Mikrofonrauschen,
- keine Restwellenform,
- keinen Fade,
- keinen Dither,
- keine automatische Pegelanpassung.

Das 100-ms-Rezeptorfenster darf zu Beginn der Stillephase noch Signalanteile
der vorherigen Weltphase enthalten. Nach zehn vollständigen Null-Chunks muss
die aktuelle Rezeptorlage exakt null sein.

## 5. Wiederkehrvertrag

Phase 3 verwendet dieselben Signalchunks wie Phase 1. Unterschiede der
Feldlage dürfen deshalb nur aus dem vorherigen Feldzustand stammen, nicht aus
einem anderen äußeren Signal.

Der Regler selbst besitzt nach Reset keine fortwirkende Geschichte.

## 6. Pflichtprüfungen

1. Exakt 2.000 Chunks pro Phase und 6.000 Chunks gesamt.
2. Phase 2 besteht bitgenau aus Nullwerten.
3. Entsprechende Chunks aus Phase 1 und 3 sind exakt gleich.
4. Ein weiterer Leseversuch nach Phase 3 wird abgelehnt.
5. Reset reproduziert dieselbe Chunkfolge und denselben Digest.
6. Der Regler speichert keine erzeugte Audiofolge.
7. Die Rezeptorlage wird nach einem vollständigen Nullfenster exakt null.
8. Feldnachhall relaxiert während der Stille gemäß seiner jeweiligen B1-Zeit.
9. Keine Nachhallvariante beeinflusst die Quelle.
10. Phase 3 erreicht unter identischer Weltwirkung wieder dieselbe
    Rezeptorlandschaft wie Phase 1.

### Verbindliche Berichtsform

Mute wird niemals als ein gemeinsamer Aktivitätsmittelwert ausgegeben. Jeder
Bericht trennt:

```text
exakte Gate-Ausgabe
-> Übergangslagen des Rezeptorfensters
-> stabile aktuelle Rezeptorlage
-> davon unabhängiger Feldnachhall
```

Ein Übergangsrest darf nicht als fortlaufende aktuelle Weltwirkung bezeichnet
werden.

## 7. Nachhallkandidaten

Parallel beobachtet werden weiterhin:

```text
tau = 0,05 s
tau = 0,20 s
tau = 1,00 s
```

Diese Werte sind Vergleichssonden. Keine Variante wird ausgewählt, verstärkt
oder in eine Runtime übernommen.

## 8. Entscheidungsgrenze

Ein positiver Lauf kann zeigen:

- die vollständige auditive Kette folgt kontrollierten Weltphasen,
- lokale Nachhallreichweite bleibt B1-erklärbar,
- Wiederkehr desselben Weltkontakts wird technisch reproduzierbar getragen.

Er zeigt keine natürliche Auswahl, Beziehungsgeschichte, Reflexion,
Offline-Erholung oder Feldintelligenz.

## 9. Evidenzziel

Maximal **E2** für die kausale technische Phasenantwort der vorhandenen
endlichen Kette. Zusätzliche MCM-Mechanik bleibt **E0**.
