# Befund 002: Minimale lokale Trägerfunktion

## 1. Bezug

Ausgeführt wurde
[Methodik 002](../methodik/002_MINIMALE_LOKALE_TRAEGERFUNKTION.md).

Geprüft wurde, ob die bisher geforderte lokale Minimalfunktion bereits durch
bekannte unabhängige Filtermechanik getragen wird:

```text
lokaler Kontakt
-> lokale Aktivierung
-> begrenzter Nachhall
-> ungetriebene Relaxation
```

## 2. Implementierte Baselines

### B0: Zustandslos

```text
a_i(t) = u_i(t)
h_i(t) = 0
```

### B1: Unabhängiger Leaky-Nachhall

```text
a_i(t) = u_i(t)
d = exp(-dt / tau)
h_i(t + dt) = d * h_i(t) + (1 - d) * a_i(t)
```

Jeder Träger liest ausschließlich seinen eigenen Kontakt und seinen eigenen
vorherigen Nachhall. Es existiert keine Nachbarschaftswirkung.

B2 mit mehreren Zeitkonstanten und B3 mit lokaler Nachbarschaft wurden gemäß
Vorregistrierung nicht implementiert.

## 3. Ausführung

```text
python -m unittest -v tests.test_minimal_local_carrier
```

Ergebnis:

```text
14 Tests
14 bestanden
0 Fehler
0 Fehlschläge
```

Geprüfte Parameterfamilie:

```text
tau in {0.25, 1.0, 4.0}
dt  in {1.0, 0.5, 0.25}
```

Damit wurden neun Kombinationen der Zeitkonstante und technischen
Schrittweite geprüft. Die Werte sind Sonden, keine ausgewählten
Systemparameter.

## 4. Funktionsbefunde

### F1: Lokale Gegenwartsaufnahme getragen

Der aktuelle Kontakt erscheint unverändert als lokale Aktivierung. Kontakt an
einem Träger verändert keinen anderen unabhängigen Träger.

### F2: Begrenzter Nachhall getragen

B0 besitzt nach Kontaktende keine Spur. B1 erhält nach einem endlichen Kontakt
eine endliche lokale Spur.

Dieser Unterschied zeigt nur die mathematisch eingebaute Funktion des
Leaky-Zustands.

### F3: Ungetriebene Relaxation getragen

Ohne neuen Kontakt nimmt der Betrag des B1-Nachhalls in allen neun
Parameterkombinationen bei jedem Schritt monoton ab.

Die korrekte Bezeichnung ist **ungetriebene programmierte Relaxation**. Der
Versuch weist keine natürlich entstandene Relaxation nach.

### F4: Polarität getragen

Positive und negative Impulse behalten während der Relaxation ihr Vorzeichen.
Ein Gegenkontakt kann eine vorhandene Spur abschwächen oder umkehren.

### F5: Endliche Lage getragen

Bei Eingängen und Vorzuständen im normalisierten Bereich `[-1, 1]` bleibt B1
ohne Clipping in diesem Bereich. Ungültige Werte werden abgewiesen und nicht
stillschweigend begrenzt.

### F6: Atomare Lokalität getragen

Vektorberechnung und permutierte unabhängige Skalarberechnung ergeben nach
Rückordnung exakt dieselbe Lage. Es besteht keine serielle
Träger-zu-Träger-Wirkung.

### F7: Zeitskalenkonsistenz getragen

Ein konstanter Kontakt über dieselbe Gesamtdauer erzeugt bei `dt = 1.0`, `0.5`
und `0.25` bis auf reine Gleitkommatoleranz dieselbe Endspur.

### F8: Geschichtsgrenze sichtbar

B1 kann bei gleicher aktueller Aktivierung verschiedene unmittelbare
Vorgeschichten unterscheiden, solange ihre Nachhallwerte verschieden sind.

Es wurden aber auch zwei verschiedene Geschichten konstruiert, die exakt auf
denselben B1-Nachhall fallen:

```text
Geschichte A: [1, 0]
Geschichte B: [0, d]
d = exp(-dt / tau)
```

Beide erzeugen nach zwei Schritten denselben Zustand. Eine anschließende
identische Probe bleibt ebenfalls identisch. Die frühere Differenz ist
vollständig verloren.

## 5. Baselineentscheidung

B1 erfüllt F1 bis F7 vollständig. Damit genügt ein unabhängiger lokaler
Leaky-Zustand für die aktuell formulierte Minimalfunktion.

Die bindende Aussage lautet:

```text
Kontakt + Nachhall + Relaxation
rechtfertigen noch kein Neuron,
keine Nachbarschaft
und kein MCM-Feld.
```

B2 und B3 bleiben geschlossen. Eine komplexere Mechanik würde im aktuellen
Stand nur reichere Trajektorien erzeugen, ohne einen nachgewiesenen
Funktionsmangel zu beheben.

## 6. Kritische Einordnung

Der Befund ist zu einem wesentlichen Teil mathematisch notwendig. B1 wurde
genau so definiert, dass es einen exponentiell abklingenden Zustand trägt.

Der Forschungswert liegt deshalb nicht in der Entdeckung von Nachhall, sondern
in der Abgrenzung:

- Die bisherige Funktionsforderung ist nicht MCM-spezifisch.
- Ein unabhängiger Filter genügt.
- Ein einzelner Leaky-Zustand komprimiert Geschichte stark.
- Räumliche Feldwirkung wurde weder benötigt noch beobachtet.
- Neuronähnliche Träger wären derzeit unbegründete Zusatzmechanik.

## 7. Nicht gezeigt

Nicht gezeigt sind:

- sensorspezifische MCM-Feldbildung,
- lokale Überlagerung zwischen Trägern,
- Weiterleitung oder räumliche Ausbreitung,
- ein gemeinsames inneres Muster,
- Erfahrung über schnellen Nachhall hinaus,
- Organisationsgeschichte,
- Lernen oder Feldintelligenz.

## 8. Evidenz

**E1 für die Implementierung und Scheitergrenze der B0/B1-Baselines.**

Weiterhin **E0** für:

- MCM-Trägerdynamik,
- neuronähnliche Träger,
- lokale Nachbarschaftswirkung,
- sensorspezifisches MCM-Feld,
- gemeinsamen MCM-Strang,
- Feldintelligenz.

## 9. Architekturentscheidung

Ein MCM-Träger wird noch nicht als Neuron implementiert.

Der vorhandene B1-Code bleibt Forschungsbaseline und wird nicht zur
freigegebenen MCM-Runtime erklärt.

Vor weiterer Trägermechanik muss eine Funktion benannt werden, die:

- aus konkretem räumlich-zeitlichem Weltkontakt folgt,
- von unabhängigen B1-Trägern nicht getragen wird,
- nicht bereits durch mehrere feste Zeitkonstanten erklärt wird,
- keine gewünschte Feldform vorwegnimmt.

## 10. Bester nächster Schritt

Methodik 003 soll in einer kleinen kontrollierten Rezeptorfläche untersuchen,
welche beobachtbare Funktion überhaupt eine Wechselwirkung zwischen lokalen
Trägern erfordern würde.

Dabei dürfen räumliche Muster, Ausbreitung und Überlagerung nicht als Ziel
vorgegeben werden. Zuerst wird geprüft, welche Information unabhängige lokale
Träger bereits vollständig erhalten und welcher konkrete Weltkontakt dadurch
tatsächlich nicht verarbeitet werden kann.
