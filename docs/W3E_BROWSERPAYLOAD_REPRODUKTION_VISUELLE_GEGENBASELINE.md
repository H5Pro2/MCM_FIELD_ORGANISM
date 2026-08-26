# W3-E: Browserpayload-Reproduktion und visuelle Gegenbaseline

Stand: 2026-08-09

Entscheidung: `BROWSER_PAYLOAD_REPEAT_EXACT_VISUAL_CHANGE_PROPAGATES`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-E prueft am Fassade-only Browserpayloadpfad zwei technische Bedingungen:

1. Exakt derselbe kontrollierte Payloadverlauf ist wiederholbar.
2. Eine einzige kontrollierte visuelle Payloadaenderung bleibt im reduzierten
   Verlauf und im resultierenden Feld unterscheidbar.

## Kontrollpaar

```text
Kontrolle:  PNG-Grauwerte (48, 128, 208) + identische PCM-Hops
Wiederholung: PNG-Grauwerte (48, 128, 208) + identische PCM-Hops
Gegenbaseline: PNG-Grauwerte (48, 129, 208) + identische PCM-Hops
```

Jeder Arm verwendet eine frische Browserbruecke, frische Rezeptoren und ein
frisches neutrales Feld. Nur der mittlere visuelle Frame der Gegenbaseline
unterscheidet sich um einen Grauwert.

## Ergebnis

Kontrolle und Wiederholung besitzen exakt gleiche:

- reduzierte Sequenzen;
- Browserbatch-Digests;
- Endfeld-Snapshot-Digests.

Die Gegenbaseline behaelt die auditive Sequenz exakt bei. Gleichzeitig
unterscheiden sich:

- visuelle reduzierte Sequenz;
- Browserbatch-Digest;
- Endfeld-Snapshot-Digest.

Damit sind Wiederholbarkeit und die technische Weitergabe einer isolierten
visuellen Eingangsaenderung fuer diesen Aufbau gemeinsam kontrolliert.

## Verifikation

```text
122 passed
350 subtests passed
Python-Kompilierung erfolgreich
Kontrolle == Wiederholung
auditive Kontrolle == auditive Gegenbaseline
visuelle Kontrolle != visuelle Gegenbaseline
Felddigest Kontrolle != Felddigest Gegenbaseline
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-D-Browserpayload-Consumertest;
- `current_api` als einziger Projektimport;
- kontrollierte synthetische PNG- und PCM-Payloads;
- Browserbatch- und Feldsnapshot-Digests als technische Identitaetsmasse.

## Aussagegrenze

W3-E belegt technische Reproduzierbarkeit und Eingangsunterscheidbarkeit im
konkreten kontrollierten Aufbau. Er belegt keine semantische Unterscheidung,
kein Memory, Lernen, Feldzeit, Organisation, Selbstregulation oder KI. Es
wurde kein Browser oder Playwright gestartet und keine Kamera, kein
Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W3-F bildet die modalitaetsgespiegelte Audio-Gegenbaseline:

1. Die drei visuellen PNG-Frames bleiben exakt gleich.
2. Genau ein kontrollierter PCM-Hop wird in seiner Amplitude veraendert.
3. Die visuelle reduzierte Sequenz muss identisch bleiben.
4. Auditive Sequenz, Batchdigest und Endfelddigest muessen sich von der
   Kontrolle unterscheiden.
5. Der Aufbau bleibt Fassade-only, kamerafrei, ohne Browserstart und ohne
   Forschungsclaim.

## Spaeterer Umsetzungsstand W3-F

W3-F ist am 2026-08-09 umgesetzt worden. Eine einzelne
PCM-Amplitudenaenderung laesst die visuelle reduzierte Sequenz identisch und
veraendert auditive Sequenz, Batchdigest und Felddigest. Der aktuelle Verbund
besteht mit `123 passed` und 350 Subtests.
