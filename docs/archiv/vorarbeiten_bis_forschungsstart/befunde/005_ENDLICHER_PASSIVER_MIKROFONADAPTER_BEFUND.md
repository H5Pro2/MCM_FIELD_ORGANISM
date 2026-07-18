# Befund 005: Endlicher passiver Mikrofonadapter

## 1. Bezug

Ausgeführt wurden der simulierte Zweig S0 und anschließend ein einzelner,
ausdrücklich freigegebener Hardwarelauf S1 aus
[Methodik 005](../methodik/005_ENDLICHER_PASSIVER_MIKROFONADAPTER.md).

Vor der Implementierung war kein Mikrofon angeschlossen. Danach wurde ein
`USB PnP Device(Echo-058)` eingesteckt und von Windows als aktiver
Mono-Eingang erkannt.

## 2. Implementierte Grenze

Der Adapter verarbeitet eine vorab begrenzte Anzahl gleich großer Mono-Frames:

```text
endliche Framequelle
-> kontrollierte Frequenzprojektion
-> kontinuierliche Frequenzlage
-> parallele B2-Ereignisse und B3-Spikeanzahlen
-> unveränderliche technische Beobachtung
-> aggregierte Zusammenfassung
```

Rohsamples werden nur dem jeweiligen Rezeptorschritt übergeben. Sie erscheinen
weder in der Beobachtung noch in der Zusammenfassung oder im Digest.

## 3. Ausführung

```text
python -m unittest -v tests.test_finite_audio_adapter
```

Ergebnis:

```text
17 Tests
17 bestanden
0 Fehler
0 Fehlschläge
```

## 4. Getragene technische Befunde

- Die Laufdauer wird vor dem ersten Lesen validiert.
- Es wird exakt die angeforderte Framezahl gelesen und kein zusätzlicher Frame.
- Eine zu kurze oder ungültige Quelle bricht am betroffenen Frame ab und gibt
  keine gültige Teilzusammenfassung zurück.
- Stille, Tonbeginn und Tonende werden reproduzierbar aggregiert.
- Identische zurückgesetzte Quellen erzeugen denselben Beobachtungsdigest.
- Ein ein- oder ausgeschalteter Observer verändert die Zusammenfassung nicht.
- Beobachtungen sind unveränderlich und enthalten keine Rohsamples.
- Geänderte B2/B3-Parameter verändern die kontinuierliche Energiereferenz nicht.
- Die Energieaggregate entsprechen der direkten Rezeptorausgabe.
- Überläufe bleiben ein rein technischer Zähler.
- Der optionale Hardwareadapter verlangt eine explizite Gerätekennung und
  blockiert verständlich, wenn die optionale Abhängigkeit fehlt.
- Ein normal beendeter oder beim Start gescheiterter Stream wird geschlossen.

## 5. Hardwarelauf S1

Der erste Öffnungsversuch mit `8000 Hz` wurde von der Geräteprüfung vor dem
Streamstart korrekt abgewiesen. Das USB-Gerät meldete `48000 Hz` als native
Abtastrate. Für dieselbe Fensterdauer wurden deshalb verwendet:

```text
Gerät:          Mikrofon (USB PnP Device(Echo-058))
Host-API:       Windows WASAPI
Abtastrate:     48000 Samples pro Sekunde
Fenster:        480 Samples / 0.01 Sekunden
Dauer:          2.0 Sekunden
Fensterzahl:    200
Überläufe:      0
```

Die Frequenzsonden blieben unverändert bei `200`, `400` und `800 Hz`.

Technische Aggregate:

```text
Energie Minimum:  0.0001228782 / 0.0000572826 / 0.0000347809
Energie Maximum:  0.0087070344 / 0.0032042039 / 0.0018822030
Energie Mittel:   0.0026250244 / 0.0013021872 / 0.0006103709
B2 Beginn/Ende:   0 / 0 in allen drei Kanälen
B3 Spikeanzahl:   0 in allen drei Kanälen
```

Der Stream wurde nach exakt 200 Frames geschlossen. Es wurden keine
Rohsamples, Audiodateien oder Transkripte gespeichert.

## 6. Interpretation des Livebefunds

Die kontinuierliche Rezeptorlage R0 reagierte in allen drei Frequenzsonden auf
den realen Eingang. Die mit synthetischen Signalen geprüfte Standardschwelle
von `0.5` lag jedoch weit über den beobachteten realen Energien. Deshalb
erzeugten weder B2 noch B3 ein Ereignis.

Diese Nullausgabe darf nicht als fehlender Weltkontakt gelesen werden. Sie
zeigt vielmehr:

```text
reale kontinuierliche Mikrofonaktivität vorhanden
!= bestehende synthetische Schwelle für reale Pegel geeignet
```

Die Schwellen werden nach diesem Lauf nicht nachträglich angepasst. Dafür wäre
eine eigene, vorregistrierte Pegel- und Invarianzprüfung nötig.

## 7. Nicht geprüft

Nicht geprüft wurden:

- unterschiedliche reale Geräuschklassen oder Raumlagen,
- Gerätetrennung während eines laufenden Streams,
- Verhalten bei weiteren Treiber- und Hardwarefehlern,
- dauerhafte auditive Weltteilnahme.

## 8. Nicht gezeigt

Der Versuch zeigt nicht:

- Hören im semantischen oder erlebenden Sinn,
- ein auditives MCM-Feld,
- ein MCM-Neuron,
- spikende Feldkopplung,
- Lernen, innere Bezeichnung oder Feldintelligenz.

B2 und B3 bleiben passive Vergleichsrechnungen. Sie wirken nicht auf die
kontinuierliche Rezeptorlage zurück und werden nicht zu Neuronen erklärt.

## 9. Evidenz

**E1 für den endlichen passiven S0-Adaptervertrag.**

**E1 für einen einzelnen endlichen S1-Mikrofonkontakt.**

Weiterhin **E0** für:

- auditive MCM-Feldbildung,
- MCM-Neuronen und Feldkopplung,
- organische Entwicklung,
- Feldintelligenz.

## 10. Architekturentscheidung

Der Adapter darf als kontrollierte technische Eingangsgrenze bestehen bleiben.
Er führt keine neue Feldmechanik ein. Weitere reale Läufe bleiben jeweils
endlich und müssen ausdrücklich gestartet werden.

## 11. Bester nächster Schritt

Für die gewählte Reihenfolge **Hören vor Sehen** ist der nächste sinnvolle
Schritt eine vorregistrierte passive Pegelkarte realer auditiver Kontakte. Sie
muss zuerst R0 unter Stille, Stimme und kontrolliertem Ton vergleichen und
prüfen, ob feste absolute Schwellen überhaupt über Abstand und Eingangspegel
tragen.

Erst danach lässt sich begründet entscheiden, ob Spikeereignisse eine robuste
lokale Zeitinformation liefern oder nur willkürlich an einen Gerätepegel
angepasst würden. Eine Feldkopplung wird dadurch noch nicht freigegeben.
