# Passiver radialer Flussvertrag

## Status

Technischer Zulassungsvertrag auf Evidenzstufe E1. Keine
Geschwindigkeitsregel und keine Runtime-Freigabe.

## Zweck

Die radiale Kontaktmorphologie besitzt endliche Materialzellen, aber bisher
keine Form, einen möglichen Transport vollständig und prüfbar zu beschreiben.

Der passive Flussvertrag führt dafür Grenzflüsse ein:

```text
F(0), F(1), ..., F(n)
```

Positive Flüsse zeigen in Richtung wachsender radialer Koordinate, also nach
außen. Der Vertrag erhält einen vollständigen fremden Vorschlag. Er erzeugt
selbst keinen Fluss.

## Endliche Volumenbilanz

Für eine radiale Zelle `k` gilt:

```text
m_k(t + dt)
=
m_k(t) + dt * (F_k - F_(k+1))
```

Die inneren Flüsse erscheinen bei zwei Nachbarzellen mit entgegengesetztem
Vorzeichen und heben sich in der Gesamtbilanz auf.

Die Grenzfläche `q = 0` tauscht Material mit dem gemeinsamen ungebundenen
Anteil des jeweiligen Neurons:

```text
ungebunden(t + dt)
=
ungebunden(t) - dt * Summe aller F_richtung(0)
```

Alle Richtungsprofile eines Neurons beanspruchen damit dieselbe begrenzte
Eigentümerressource. Sie besitzen keine getrennten Materialreserven.

## Geschlossene äußere Grenze

An `q = 1` muss gelten:

```text
F(1) = 0
```

Material darf die geometrische Grenzfläche erreichen, aber das Neuron nicht
verlassen. Eine spätere Berührung zweier Neuronen bedeutet deshalb nicht,
dass Material zwischen Eigentümern übertragen wird.

## Geprüfte Bedingungen

`audit_radial_transport_proposal` prüft:

- exakten Bezug auf den abgeschlossenen Morphologiestand;
- vollständige Eigentümermenge;
- vollständige Richtungsprofile;
- exakt übereinstimmende radiale Grenzflächen;
- positive reale Dauer;
- geschlossene äußere Grenzen;
- Nichtnegativität jeder Zelle und des ungebundenen Anteils;
- Erhaltung der Gesamtmenge jedes einzelnen Neurons;
- Nullfluss-Invarianz;
- Unabhängigkeit von Eigentümer- und Profiliterationsreihenfolge;
- Unverändertheit des Quellzustands.

Nur wenn alle Bedingungen erfüllt sind, wird ein unveränderlicher möglicher
Folgezustand rekonstruiert. Dieser Zustand ist ein passives Prüfergebnis und
kein angewendeter Organismuszustand.

## Was Annahme bedeutet

Ein angenommener Vorschlag ist ausschließlich **kinematisch zulässig**:

```text
Diese Flüsse könnten Material bilanzerhaltend verschieben.
```

Die Annahme bedeutet nicht:

```text
Diese Flüsse besitzen eine natürliche Ursache.
Diese Bewegung soll stattfinden.
Diese Bewegung erzeugt Memory.
```

Der Audit setzt deshalb ausdrücklich:

```text
causal_source_verified = false
runtime_release_granted = false
```

## Kontrollen

Die Implementierung bestätigt:

- Nullfluss erhält die neutrale Morphologie;
- Fluss bei `q = 0` kann ungebundenes Material in die erste Zelle verschieben;
- innerer Fluss kann vorhandenes Material zwischen Nachbarzellen verschieben;
- mehrere Profile können den gemeinsamen ungebundenen Anteil nicht
  überziehen;
- eine leere Zelle kann kein Material abgeben;
- Material kann die äußere Eigentümergrenze nicht verlassen;
- eine andere radiale Auflösung wird nicht stillschweigend umgerechnet;
- umgekehrte Iterationsreihenfolge erzeugt denselben Vorschlag und Zustand.

## Nicht enthalten

Nicht implementiert sind:

- Geschwindigkeit;
- Wahl des Flussvorzeichens;
- Umrechnung von Rezeptorkontakt in Bewegung;
- Umrechnung von äußerer oder endogener Feldwirkung in Bewegung;
- Wachstum oder Zerfall;
- Attraktion oder Rückstellkraft;
- Kontaktwirkung;
- Feldrückwirkung;
- Runtime-Fortschreibung.

## Nächster Schritt

Als Nächstes wird keine beliebige Geschwindigkeitsformel gebaut. Zuerst werden
die bereits vorhandenen möglichen Ursachen einzeln gegen den Flussvertrag
abgegrenzt:

1. momentaner lokaler Feldfluss;
2. lokale Aktivierungsdifferenz;
3. äußerer Rezeptorkontakt;
4. endogener Rezeptorkontakt;
5. schneller Nachhall.

Gesucht wird zunächst, welche dieser Ursachen nur einen räumlich verteilten
Integrator oder eine fest vorgegebene Außen-/Innenbewegung erzeugen würde.
