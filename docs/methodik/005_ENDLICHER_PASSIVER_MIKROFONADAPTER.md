# Methodik 005: Endlicher passiver Mikrofonadapter

## 1. Status und aktueller Hardwarebefund

Methodik 005 definiert die Sicherheits- und Zustandsgrenze für den ersten
passiven Mikrofonzugriff.

Die erste Windows-Prüfung vor der Implementierung zeigte:

```text
vorhandener Audioausgang:  Lautsprecher (Realtek(R) Audio)
vorhandener Audioeingang:  keiner als AudioEndpoint registriert
Audiodienste:              aktiv
Python-Liveabhängigkeit:   sounddevice nicht installiert
```

Deshalb wurde zunächst nur der vollständig simulierbare Adapterzweig
implementiert. Nach dieser Vorregistrierung wurde ein USB-Mikrofon
angeschlossen. Windows meldete anschließend einen gültigen Eingabe-Endpunkt;
damit durfte der ausdrücklich begrenzte Livezweig geprüft werden.

## 2. Forschungsfrage

Kann ein endlicher Audioeingang dieselbe kontrollierte auditive Rezeptorkette
aus Methodik 004 kausal bedienen, ohne Rohsamples zu speichern, im Hintergrund
weiterzulaufen oder den Feldzustand durch Observeraktivität zu verändern?

## 3. Datenfluss

```text
endliche Mono-Framequelle
-> R0-Frequenzprojektion
-> kontinuierliche Frequenzlage
-> B2-Ereignisse und B3-Spikes nur parallel
-> unveränderliche passive Beobachtung
-> aggregierte technische Zusammenfassung
```

Rohsamples verlassen den jeweiligen Verarbeitungsschritt nicht.

## 4. Datenschutz- und Laufzeitvertrag

- Kein automatischer Start beim Programm- oder Systemstart.
- Kein Hintergrundprozess.
- Jeder Lauf besitzt eine vorab festgelegte Dauer.
- Die technische Obergrenze beträgt zunächst zehn Sekunden.
- Kein Rohsample wird in Dateien, Logs, Debugdaten oder Reports geschrieben.
- Keine Audiodatei wird erzeugt.
- Keine Netzwerkübertragung.
- Keine Sprache-zu-Text- oder Sprecheranalyse.
- Der Livezweig benötigt eine explizite technische Gerätekennung.
- Nach Ende oder Fehler wird der Stream geschlossen.

Die Obergrenze ist eine Sicherheitsgrenze, keine Eigenschaft des MCM-Feldes.

## 5. Quellenvertrag

Eine Framequelle liefert genau:

```text
frame_size Mono-Samples
im Bereich [-1, 1]
bei der vereinbarten sample_rate
```

Zwei Quellen müssen austauschbar sein:

- **S0:** deterministische simulierte Framequelle für Tests,
- **S1:** endlicher realer Mikrofonstream über eine optionale Audioabhängigkeit.

Die Verarbeitung hinter der Quellengrenze ist identisch.

## 6. Beobachtungszustand

Der passive Observer darf pro Fenster ausschließlich erhalten:

- fortlaufenden technischen Frameindex,
- relative technische Zeit,
- kontinuierliche Frequenzenergien,
- B2-Ereignisse,
- B3-Spikeanzahlen,
- B3-Membranreste.

Nicht enthalten sein dürfen:

- Rohsamples,
- rekonstruierte Audioframes,
- Wörter oder Transkripte,
- Gerätegeheimnisse,
- Dateipfade,
- semantische Ereignisnamen.

## 7. Zusammenfassung

Nach einem endlichen Lauf dürfen ausschließlich technische Aggregate
zurückgegeben werden:

- verarbeitete Fenster und Gesamtdauer,
- Minimum, Maximum und Mittel je Frequenzkanal,
- positive und negative B2-Ereigniszahlen,
- B3-Spikeanzahlen,
- Digest der technischen Beobachtungsfolge,
- technische Fehler- und Überlaufzahl.

Der Digest beweist Wiederholung technischer Zustände; er ist keine innere
Erinnerung.

## 8. Pflichtprüfungen des simulierten Zweigs

- exakte Fensterzahl aus endlicher Dauer,
- Stille,
- kontrollierter Tonbeginn und Tonende,
- Mehrklang,
- identische Wiederholung nach Reset,
- Observer an und aus,
- zu kurze Quelle,
- ungültige Samplezahl,
- ungültige Samplewerte,
- Überschreitung der Laufzeitgrenze,
- vollständiges Fehlen von Rohsamples in Beobachtung und Zusammenfassung,
- B2/B3 verändern die kontinuierliche Frequenzlage nicht.

## 9. Zusätzliche Pflichtprüfungen vor einem Live-Lauf

- Windows meldet mindestens einen Eingabe-Endpunkt.
- Die gewählte Gerätekennung besitzt Eingangskanäle.
- Unterstützte Abtastrate und Fenstergröße sind bekannt.
- Die optionale Audioabhängigkeit ist explizit installiert.
- Ein Testlauf öffnet und schließt den Stream ohne Hintergrundrest.
- Überlauf und Geräteverlust werden als technischer Fehler gemeldet.
- Der Nutzer weiß unmittelbar vor dem Lauf, dass aufgenommen wird.

## 10. Erfolgskriterien

Der simulierte Adapterzweig trägt nur dann E1, wenn:

1. die Framezahl exakt begrenzt ist,
2. Rohsamples nirgends im Ergebnis erscheinen,
3. Observer an und aus dieselbe Zusammenfassung erzeugen,
4. identische Quellen exakt denselben Digest erzeugen,
5. Fehler keinen gültigen Teilbefund ausgeben,
6. kontinuierliche Energie von B2/B3 unverändert bleibt,
7. nach Laufende keine Quelle weiter gelesen wird.

Der Livezweig kann nur bei tatsächlich vorhandenem Gerät bewertet werden.

## 11. Stoppregeln

Kein Livezugriff erfolgt, wenn:

- kein Eingabegerät vorhanden ist,
- die Gerätewahl nur geraten werden kann,
- Rohdatenhaltung nicht ausgeschlossen ist,
- die Laufzeit nicht hart begrenzt ist,
- eine Abhängigkeit stillschweigend installiert werden müsste,
- ein Stream nach dem Lauf weiter aktiv wäre,
- semantische Audioanalyse für den Versuch erforderlich würde.

## 12. Evidenzgrenze

Ein positiver simulierter Lauf kann E1 für den endlichen passiven Adaptervertrag
tragen. Er zeigt keine reale Weltteilnahme.

Ein späterer positiver Hardwarelauf könnte E1 für reale auditive Aufnahme
tragen. Er zeigt weiterhin kein Hören im semantischen Sinn, kein MCM-Neuron und
kein spikendes MCM-Feld.

## 13. Ausführungsnachtrag

S0 wurde vollständig implementiert und geprüft. Danach wurde folgendes Gerät
angeschlossen und explizit ausgewählt:

```text
Mikrofon (USB PnP Device(Echo-058))
Host-API:              Windows WASAPI
Eingangskanäle:        1
native Abtastrate:     48000 Hz
```

Der erste S1-Öffnungsversuch mit den synthetischen `8000 Hz` wurde vor dem
Streamstart wegen nicht unterstützter Abtastrate korrekt blockiert. Danach
wurde ausschließlich die technische Abtastrate auf `48000 Hz` und die
Fenstergröße auf `480` Samples angepasst. Die Fensterdauer blieb damit bei
`10 ms`; Frequenzsonden und B2/B3-Mechanik blieben unverändert.

Der freigegebene Lauf war auf zwei Sekunden begrenzt. Sein Ergebnis steht in
[Befund 005](../befunde/005_ENDLICHER_PASSIVER_MIKROFONADAPTER_BEFUND.md).
