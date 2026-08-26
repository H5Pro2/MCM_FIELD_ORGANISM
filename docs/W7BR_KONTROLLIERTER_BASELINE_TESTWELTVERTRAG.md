# W7-BR: Kontrollierter Baseline-Testweltvertrag

Stand: 2026-08-10

Status: `STATISCH_GEBUNDEN_KEIN_LAUF`

## Zweck

Dieser Vertrag definiert einen spaeteren technischen Vergleichslauf fuer die
F3-Referenz. Er bindet nur Eingabeordnung, Snapshots, Baselines und
Abbruchregeln. Es werden keine Medieninhalte interpretiert und keine
Bedeutungen vergeben.

## Testweltgrenze

Zulaessig sind ausschliesslich:

- kontrollierte audiovisuelle Dateien;
- reproduzierbare Video- oder Audiosignalfolgen;
- kontrollierte Browser-Testweltpayloads.

Nicht Teil dieses Vertrags sind Kamera, Live-Mikrofon, physische Sensorik,
direkte Bildschirmrueckkopplung oder reale Aufbaupruefungen.

## Vergleichsarme

Jeder spaetere Durchlauf bindet dieselbe Rezeptorfolge an diese Arme:

| Arm | Rolle |
| --- | --- |
| N0 | schneller Null- oder Grundpfad |
| L1 | unabhaengige leaky Referenzspur |
| F3 | transparente F3-Referenz |
| SR | Snapshot/Restore-Kontrolle |

Ein optionaler Kandidatenarm ist in diesem Vertrag nicht vorgesehen. Die
Substratlinie bleibt bis zu einem neuen statischen Zulassungsentscheid
geschlossen.

## Gebundene Testquelle

Als erste Testquelle ist die vorhandene synthetische Weltfamilie
`controlled_history_holdout_world_family()` gebunden. Sie liefert zwei
geometrisch gleich aufgebaute Welten:

```text
world.history.same
world.history.changed
```

Beide Welten verwenden dieselben vier Phasenpositionen:

```text
contact.0 -> gap.0 -> contact.1 -> probe.0
```

Die ersten drei Phasen bilden die kontrollierte Vorgeschichte. `probe.0`
ist die gemeinsame spaetere Probe. Die Weltfamilie wird als synthetische
Quelle aus `mcm_field_organism.controlled_audio_video_test_world` geoeffnet;
es werden keine externen Medien oder Live-Quellen verwendet.

Vor einer Ausfuehrung muessen die beiden Welt-Digests sowie die konkreten
Snapshot-Digests der vier Phasen unveraenderlich protokolliert werden. Dieses
Dokument bindet die Quelle, fuehrt diese Digestbildung aber noch nicht als
Forschungs- oder Vergleichslauf aus.

Die technische Quellenbindung lautet:

```text
world.history.same    = 3b410299a1f0e23a4bbb45578a538878a481ec31e5ae025f0b0311074a1c0b06
world.history.changed = a4009b3e1845b46169d07bd1bb1b088d3a5dbf48107776e290cd4543d1b85d3c

contact.0 = b36b4758cb57a2344e895b907810297d63e3925758d937c2dff1b8afa0e709be
gap.0     = 1a4c7ca5c3917ddb7ee5afc7442e6ed527cf61eb7d8d8ccec53f52a643276846
probe.0   = f2f2a5dfb388e496acc0d742997563f5df0fa4020a6e017fb2c346406f595d84

same.contact.1    = bbd1c72cfd0c69c83748bab2db39e51df69a4aaff58d3710edd4da3221bbceea
changed.contact.1 = 4f924c70c72d3ae1ba25b845e617c3cae7bd1e1793eb4bca1447d2c806243dea
```

Die identischen Phasendaten sind in beiden Welten digestgleich. Die
abweichende `contact.1`-Phase ist die einzige gebundene Vorgeschichts-
Intervention. Die Digests beschreiben technische Eingaben; sie tragen keine
semantische Bedeutung.

## Technische Snapshot-Bindung

Mit `NeutralLocalFieldSubstrateConfig(1.0)` und
`NeutralFastAfterimageConfig(0.5)` wurden die Snapshotpunkte technisch
aufgebaut und jeweils unmittelbar restauriert. Die restaurierten Digests
waren an allen Punkten identisch mit den Ausgangsdigests:

```text
world.history.same
contact.0 = 342deb16e777c4184d663c0a12d8be5a491988b83bfe516f5adc0fe71dd14960
gap.0     = f65e3830cf1a1f8e1ea69898687bd8cf3ad2b897c72c19af67d4a5b9d45a6f86
contact.1 = c0403739cf913312f2b5889b874fbff023859a6ee0e8283c07faac5eab72dc3f
probe.0   = 1c81971799fbeabfc731be22353c8a1037d046a7174d8b8dc6418d8b64fd6947

world.history.changed
contact.0 = 342deb16e777c4184d663c0a12d8be5a491988b83bfe516f5adc0fe71dd14960
gap.0     = f65e3830cf1a1f8e1ea69898687bd8cf3ad2b897c72c19af67d4a5b9d45a6f86
contact.1 = 2d31ba545d14ce759e8c94aa8b8bb0fbfb64c85c2bcc20d1e9dd504e6cd3d399
probe.0   = 8e4fcab5fac0246bb7157409944db6e08a8d022c132964c5dfd42528c13543e9
```

Der Befund ist auf technische Snapshot- und Restore-Gleichheit begrenzt.
Die spaetere Differenz der beiden Probe-Snapshots ist nur eine beobachtete
Zustandsdifferenz dieses technischen Pfades und kein Memory-Nachweis.

## Eingabeordnung

Vor dem Lauf muessen fuer jede Folge unveraenderlich gebunden sein:

1. Quellenkennung und Quelldigest;
2. Rezeptorpfad und Modalitaet;
3. Anzahl und Reihenfolge der Rezeptorframes;
4. Feldschrittzeiten und Snapshotpunkte;
5. Konfigurationsdigest jedes Vergleichsarms.

Die Folge darf waehrend des Laufs nicht umsortiert, gekuerzt oder durch eine
semantische Beschreibung ersetzt werden.

## Minimaler Ablauf

```text
gleiche Anfangsaufnahme
-> Folge A einmalig
-> Snapshot P1
-> gleiche Probe

gleiche Anfangsaufnahme
-> Folge A wiederholt
-> Snapshot P2
-> gleiche Probe

gleiche Anfangsaufnahme
-> Folge B mit gleicher Laenge und gleichem Budget
-> Snapshot P3
-> gleiche Probe
```

Die Folgen A und B duerfen keine menschlichen Labels oder Zielbedeutungen
tragen. Ihre technische Unterscheidung erfolgt ausschliesslich ueber
gebundene Rezeptorwerte, Reihenfolge und Digest.

## Technische Auswertung

Zulaessig sind nur:

- Snapshot-Digest und Restore-Gleichheit;
- Komponentenwerte und Feldtrajektorien;
- Distanz zwischen identischen Probeverlaeufen;
- Abweichung vom Nullpfad und von L1;
- Reproduzierbarkeit bei identischem Eingang.

Der passive API-Auswerter ist
`mcm_field_organism.current_api.compare_controlled_probe_baseline_set`.
Er nimmt bereits erzeugte Snapshots entgegen, veraendert keinen Zustand und
liefert nur numerische technische Distanzen.

Unzulaessig sind Aussagen ueber Erinnerung, Lernen, Bedeutung, innere
Wahrnehmung, Feldzeit, Organisation oder KI.

## Abbruchkriterien

Der Lauf wird technisch verworfen, wenn:

- ein Quelldigest fehlt oder sich aendert;
- ein Snapshot nicht exakt wiederherstellbar ist;
- Rezeptorframes fehlen oder doppelt eingehen;
- ein Vergleichsarm andere Parameter oder ein anderes Budget verwendet;
- die Auswertung eine nicht gebundene Interpretationsvariable einfuehrt;
- ein gesperrter Live- oder physischer Sensorpfad verwendet wird.

Ein verworfener Lauf erzeugt keinen Forschungsbefund und wird nicht durch
nachtraegliche Interpretation repariert.

## Aussagegrenze

Ein spaeterer positiver technischer Unterschied bedeutet zunaechst nur:

```text
geschichtsabhaengige technische Zustandsdifferenz
```

Er bedeutet nicht automatisch Praegung, Vergessen, Memory, Lernen oder
feldbasierte KI.

## Freigabestatus

```text
Testweltvertrag:       statisch gebunden
konkrete Medien:       noch nicht gebunden
Forschungsauftrag:     nein
Ausfuehrung:           nein
Memory-Claim:          nein
```

## Bester naechster Schritt

Als naechstes werden fuer genau einen technischen Durchlauf die konkreten
kontrollierten Eingabedateien oder synthetischen Rezeptorfolgen mit Digest,
Schrittfolge und Snapshotpunkten gebunden. Erst danach kann eine getrennte
Ausfuehrungsfreigabe geprueft werden.
