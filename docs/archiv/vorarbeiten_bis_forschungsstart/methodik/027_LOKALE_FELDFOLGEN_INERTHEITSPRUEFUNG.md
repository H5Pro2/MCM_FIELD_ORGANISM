# Methodik 027: Lokale Feldfolgen-Inertheitsprüfung

## 1. Status

Vorregistrierte passive Nullprüfung. Es wird keine neue MCM-Übergangsfunktion
eingeführt.

## 2. Anlass

Befund 020 zeigt, dass zwei gespiegelte Kontaktfolgen am gemeinsamen Endpunkt
dieselbe aktuelle Aktivierung und denselben eigenen Nachhall besitzen, während
ihre linke und rechte Nachhallumgebung spiegelbildlich verschieden bleibt.

Die räumliche Orientierung ist damit lokal lesbar. Noch ungeprüft ist, ob sie
in der vorhandenen Neuronenruntime irgendeine spätere Wirkung besitzt.

## 3. Forschungsfrage

Bleiben zwei lokal lesbar verschiedene räumliche Feldlagen unter allen heute
vorhandenen MCM-Neuronenübergängen kausal identisch?

Die erwartete Nullvorhersage lautet:

```text
gleicher Eigenzustand
+ gleicher aktueller Rezeptorkontakt
+ spiegelbildlich verschiedene lokale Feldproben
+ vorhandener Hold- oder Rezeptorprojektionsübergang
→ gleiche nächste Aktivierung und gleicher nächster Nachhall
```

## 4. Kontrollierte Feldgeschichten

Die Prüfung übernimmt unverändert die fünf lokalen Träger aus Methodik 015:

```text
L: Position 0 → 1 → 2
R: Position 4 → 3 → 2
```

Position 2 ist das gemeinsame Zentrum. Beide Zweige besitzen dort:

- dieselbe aktuelle Aktivierung,
- denselben eigenen Nachhall,
- denselben aktuellen Rezeptorkontakt,
- dieselbe technische Neuronenidentität,
- denselben Quell- und Zielzeitpunkt.

Nur die getrennten lokalen Feldproben links und rechts unterscheiden sich.

## 5. Kausale Zeittrennung

```text
räumliche Nachhalllage in t
→ abgeschlossene lokale Feldproben aus t
→ MCMNeuronDrive für t+1
→ vorhandener Übergang
→ Neuronenzustand in t+1
```

Keine in `t+1` erzeugte Aktivität darf im selben Schritt erneut als Feldprobe
verwendet werden.

## 6. Vorhandene Übergänge

Es werden ausschließlich die bereits vorhandenen Nullbaselines geprüft:

### T0: Hold

```text
activation(t+1) = activation(t)
afterimage(t+1) = afterimage(t)
```

Der Übergang ignoriert Rezeptorkontakt und lokale Feldproben.

### T1: Rezeptorprojektion

```text
activation(t+1) = aktueller Rezeptorkontakt
afterimage(t+1) = 0
```

Der Übergang ignoriert Eigenzustand und lokale Feldproben.

Die Gleichungen beschreiben vorhandene technische Baselines. Sie sind keine
MCM-Feldmechanik.

## 7. Passive Gegenmessung

Vor jedem Übergang liest der bestehende lokale Observer getrennt:

- linken Aktivierungsunterschied,
- rechten Aktivierungsunterschied,
- linken Nachhallunterschied,
- rechten Nachhallunterschied,
- räumliches Orientierungsvorzeichen.

Die Gegenmessung muss bestätigen:

```text
Orientierung(L) = -Orientierung(R)
```

Damit ist ausgeschlossen, dass identische Übergangsausgaben nur aus
versehentlich identischen Feldproben entstehen.

## 8. Parameterfamilie

Die Prüfung übernimmt die bereits zulässigen Variationen aus Methodik 015:

- mehrere feste B1-Zeitkonstanten,
- mehrere Kontaktamplituden,
- null, kurze und längere kontaktlose Pause,
- exakter Reset.

Für jeden Parametersatz müssen beide Zweige dieselbe Trägergeometrie und
denselben aktuellen Zentrumskontakt besitzen.

## 9. Kontrollen

1. Exakte Spiegelung der vollständigen Feldlagen.
2. Identischer Zentrum-Eigenzustand vor dem Übergang.
3. Identischer aktueller Zentrum-Rezeptorkontakt.
4. Entgegengesetztes passiv gelesenes Orientierungsvorzeichen.
5. Vertauschte Zweig- und Probenauswertungsreihenfolge.
6. Observer an und aus.
7. Unveränderter vorheriger Neuronenzustand.
8. Atomarer Übergang von `t` nach `t+1`.
9. Exakter Reset entfernt die räumliche Differenz.
10. Keine Rohwelt-, Muster- oder Semantikdaten im Ergebnis.

## 10. Primärmessungen

Für T0 und T1 werden getrennt gemessen:

```text
delta_activation =
    activation_L(t+1) - activation_R(t+1)

delta_afterimage =
    afterimage_L(t+1) - afterimage_R(t+1)
```

Zusätzlich werden Digests von:

- vorherigem Zentrumzustand,
- vollständiger lokaler Wahrnehmung,
- Übergangsausgabe,
- nächstem Aktivierungs- und Nachhallzustand

gebildet.

Der vollständige Digest des nächsten `MCMNeuron` ist ausdrücklich kein
Gleichheitskriterium. Das Neuron bewahrt seine aktuelle `perception` als
technische Herkunft. Weil die lokalen Feldproben verschieden sind, müssen
deshalb auch die vollständigen Neuron-Digests verschieden bleiben.

Die entscheidende Trennung lautet:

```text
verschiedene Wahrnehmungsprovenienz bleibt erhalten
+ gleiche Übergangsausgabe
→ lokale Feldprobe ist angekommen, aber für Aktivierung und Nachhall inert
```

## 11. Entscheidung

### Erwarteter Nullbefund

Wenn der passive Observer die Feldorientierung unterscheidet, T0 und T1 aber
exakt gleiche nächste Aktivierungs- und Nachhallwerte erzeugen, trägt der
Versuch:

> Die vorhandene MCM-Neuronenruntime transportiert lokale Feldproben kausal bis
> an die Übergangsgrenze, aber keiner der vorhandenen Übergänge verwendet
> deren räumliche Asymmetrie.

Dies ist der konkrete Funktionsmangel:

```text
lokale Feldgeschichte ist lesbar
aber für den nächsten lokalen Zustand kausal inert
```

### Unerwarteter Unterschied

Ein Unterschied unter T0 oder T1 wäre zuerst als Implementierungsfehler zu
behandeln. Beide Baselines besitzen definitionsgemäß keinen Pfad von lokalen
Feldproben zur Ausgabe.

Ein Unterschied ausschließlich im vollständigen Neuron-Digest ist dagegen
erwartet und notwendig, solange er vollständig aus der unterschiedlichen
`perception` stammt.

## 12. Stärkstes Gegenargument

Der erwartete Befund folgt direkt aus den vorhandenen Übergangsfunktionen. Die
Prüfung entdeckt daher keine neue Dynamik.

Ihr Wert liegt in der exakten Trennung:

- Feldinformation erreicht das Neuron,
- Feldinformation ist passiv lesbar,
- Feldinformation wirkt noch nicht auf den Folgezustand.

## 13. Nicht freigegeben

- Anwendung des Orientierungsvorzeichens als Aktivierungsänderung,
- Fortsetzung einer Bewegungsrichtung,
- Diffusion oder Nachbarmittelung,
- feste Rekurrenz,
- Feldspannung oder Impulsvariable,
- adaptive Kopplung,
- Rezeptorrückschreibung,
- Handlung, Semantik oder Zielrichtung.

## 14. Evidenzgrenze

Maximal E1 für die kausale Inertheit räumlicher Feldproben unter den
vorhandenen Übergängen.

E0 bleiben:

- eigenständige lokale Feldfolge,
- MCM-spezifische Folgewirkung,
- organische Feldorganisation,
- sensorische Selbstregulation,
- Feldintelligenz.

## 15. Bester nächster Schritt

Nach dem Nullbefund darf noch keine Übergangsregel gebaut werden. Zuerst muss
eine konkrete Weltfunktion benannt werden, die eine lokale Feldfolge leisten
soll und die nicht bereits durch Projektion, unabhängigen Nachhall, festen
Puffer, Rekurrenz oder Diffusion erfüllt wird.
