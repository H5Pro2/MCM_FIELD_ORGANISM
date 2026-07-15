# Methodik 013: Live-Mikrofon-Pass/Mute/Pass-Gate

## 1. Korrektur des Versuchsaufbaus

Methodik 012 erzeugt eine vollständig synthetische Sound-Mute-Sound-Welt. Die
beabsichtigte reale Prüfung ist davon verschieden:

```text
20 Sekunden reales Mikrofon durchlassen
-> 20 Sekunden Mikrofonwirkung für die MCM exakt nullen
-> 20 Sekunden reales Mikrofon wieder durchlassen
```

Die reale Umgebung und die laufenden Ventilatoren bleiben unverändert. Eine
manuelle Umschaltung ist nicht erforderlich.

## 2. Lage des Gates

```text
Mikrofonstream
-> technisches Pass/Mute/Pass-Gate
-> auditive Rezeptoren
-> sparsamer Feldkandidat
```

Das Gate liegt vor den Rezeptoren und außerhalb der MCM. Es ist eine
kontrollierte technische Kontaktunterbrechung.

## 3. Verhalten während Mute

Der Hardwarestream wird während der Mute-Phase weiterhin in Echtzeit gelesen,
damit:

- das Audiogerät geöffnet bleibt,
- die Systemzeit fortläuft,
- Puffer nicht auflaufen,
- Phase 3 ohne erneuten Gerätestart folgt.

Jeder gelesene Mute-Chunk wird unmittelbar verworfen und durch einen exakten
Nullchunk gleicher Länge ersetzt. Es wird kein Mute-Audio gespeichert.

## 4. Wichtige Abgrenzung

Mute bedeutet nicht:

- dass die Ventilatoren oder die Außenwelt still sind,
- dass der Sensor technisch fehlt,
- dass das Mikrofon ausgeschaltet ist,
- dass Offline-Erholung vorliegt.

Mute bedeutet ausschließlich:

> Die aktuell laufende reale Mikrofonwirkung erreicht die auditive
> Rezeptorschicht für 20 Sekunden nicht.

## 5. Exakte Taktung

```text
Abtastrate:       48.000 Hz
Chunk:            480 Samples / 10 ms
Pass 1:           2.000 Chunks
Mute:             2.000 Chunks
Pass 2:           2.000 Chunks
Gesamt:           6.000 Chunks / 60 Sekunden
```

Phasenwechsel erfolgen ohne Wandzeitentscheidung auf Chunkgrenzen.

## 6. Pflichtprüfungen

1. Pass-Chunks werden bitgetreu weitergegeben.
2. Mute-Chunks sind nach dem Gate bitgenau null.
3. Die zugrunde liegende Quelle wird auch während Mute exakt einmal je Chunk
   gelesen.
4. Ungültige Hardwareframes werden durch Mute nicht verborgen.
5. Das Gate speichert keine Audioframes.
6. Nach 100 ms Mute ist die aktuelle Rezeptorlage exakt null.
7. Lokaler Nachhall relaxiert ausschließlich gemäß B1.
8. Phase 3 öffnet denselben laufenden Hardwarestream wieder.
9. Kein Nachhallkandidat beeinflusst das Gate.
10. Audioüberläufe bleiben technische Fehler oder Zähler.

### Verbindliche Berichtsform

Der Mute-Bericht muss vier Schichten getrennt ausweisen:

```text
1. Gate-Ausgabe nach Pass oder Mute
2. zeitlich begrenzter Rest des 100-ms-Rezeptorfensters
3. stabile aktuelle Rezeptorlage nach Fensterlösung
4. separat fortwirkender und relaxierender Feldnachhall
```

Ein gemeinsamer Mute-Mittelwert über Übergang und stabile Lage ist nicht mehr
zulässig.

## 7. Interpretation

Der Vergleich von Pass 1 und Pass 2 prüft, ob die reale Umgebungsanregung nach
einer kontrollierten sensorischen Unterbrechung wieder erscheint. Da die
Außenwelt nicht eingefroren ist, müssen beide Passphasen nicht numerisch
identisch sein.

Der Vergleich darf keine Geräuschklasse, Wiedererkennung oder Memoryleistung
behaupten.

## 8. Evidenzziel

Maximal **E2** für die kausale Wirkung der technischen Kontaktunterbrechung auf
Rezeptorlage und B1-Feldnachhall. Reflexion, Offline-Erholung, organische
Entwicklung und Feldintelligenz bleiben **E0**.
