# Methodik 028: Weltfunktion geschichtsabhängige Wiederaufnahme

## 1. Status

Vorregistrierte Weltfunktionsdefinition. Es wird noch keine neue
MCM-Übergangsfunktion, kein Decoder und keine Rückkopplung eingeführt.

## 2. Anlass

Befund 031 zeigt:

```text
lokale Feldgeschichte erreicht das MCM-Neuron
+ räumliche Asymmetrie bleibt passiv lesbar
+ vorhandene Übergänge erzeugen gleiche Aktivierung und gleichen Nachhall
```

Damit ist die Kausalgrenze bekannt. Noch fehlt eine beobachtbare Weltleistung,
für die eine lokale Feldfolge überhaupt benötigt werden könnte.

## 3. Weltfunktion

Die kleinste untersuchte Funktion ist die geschichtsabhängige Wiederaufnahme
eines lokalen Kontakts nach einer kurzen Unterbrechung:

> Derselbe aktuelle lokale Weltkontakt darf abhängig von der zuvor tatsächlich
> erlebten Feldgeschichte verschieden in die nächste Feldlage eingehen, wenn
> der aktuelle Kontakt einmal eine Fortsetzung und einmal eine Rückkehr bildet.

`Fortsetzung` und `Rückkehr` sind ausschließlich nachträgliche
Versuchsbeschreibungen der Welttrajektorie. Sie werden nicht als Klasse,
Zielwert, Belohnung oder Eingabe an das Feld übergeben.

## 4. Minimale Welt

Die Welt besitzt fünf feste benachbarte Positionen:

```text
0 -- 1 -- 2 -- 3 -- 4
```

Ein einzelner Kontakt durchläuft drei sichtbare Schritte, einen kontaktlosen
Schritt und eine sichtbare Wiederaufnahme:

```text
A: 0 -> 1 -> 2 -> - -> 3
B: 4 -> 3 -> 2 -> - -> 1
C: 0 -> 1 -> 2 -> - -> 1
D: 4 -> 3 -> 2 -> - -> 3
```

Dabei sind:

- A und B räumlich gespiegelte Fortsetzungen,
- C und D räumlich gespiegelte Rückkehrverläufe,
- A und D bei der Wiederaufnahme aktuell identisch,
- B und C bei der Wiederaufnahme aktuell identisch.

Das Zeichen `-` bezeichnet genau einen Schritt ohne Kontakt. Es bezeichnet
keinen Reset.

## 5. Entscheidende Paarbildung

Die nichttriviale Kontrolle vergleicht:

```text
A gegen D:
gleicher aktueller Kontakt an Position 3
+ verschiedene vorherige Feldgeschichte
+ Fortsetzung gegen Rückkehr

B gegen C:
gleicher aktueller Kontakt an Position 1
+ verschiedene vorherige Feldgeschichte
+ Fortsetzung gegen Rückkehr
```

Damit kann der aktuelle Rezeptorrahmen allein die Beziehung nicht
unterscheiden.

## 6. Beobachtungsgrenze

Eine spätere passive Prüfung darf getrennt beobachten:

- den vollständigen Zustand vor der Unterbrechung,
- die lokale Feldlage während der Unterbrechung,
- den identischen aktuellen Rezeptorrahmen bei der Wiederaufnahme,
- den nächsten lokalen Aktivierungs- und Nachhallzustand,
- die vollständige Wahrnehmungsprovenienz.

Sie darf nicht:

- eine Sollrichtung einsetzen,
- Fortsetzung oder Rückkehr als Eingabe verwenden,
- einen Gewinner auswählen,
- ein Vorzeichen als Aktivierungsbefehl anwenden,
- die Welttrajektorie speichern oder wiedergeben,
- einen trainierten Klassifikator verwenden.

## 7. Funktionskriterium

Die Weltfunktion ist nur dann als fehlende Feldfunktion operationalisiert,
wenn alle folgenden Bedingungen gemeinsam erfüllt sind:

### W1: Aktuelle Gleichheit

Die verglichenen Zweige besitzen bei der Wiederaufnahme exakt denselben
aktuellen Rezeptorrahmen.

### W2: Kausal entstandene Geschichte

Die verschiedenen lokalen Feldlagen entstehen ausschließlich aus den zuvor
durchlaufenen Weltkontakten und der unveränderten Zeitfolge.

### W3: Spätere Feldfolge

Die Geschichte verändert erst nach der Wiederaufnahme einen klar benannten
lokalen Folgezustand. Passive Lesbarkeit der alten Feldlage genügt nicht.

### W4: Ablation

Exakter Reset oder Austausch der relevanten Feldgeschichte entfernt
beziehungsweise vertauscht den Unterschied.

### W5: Weltbezug

Die Auswertung ordnet den Unterschied erst nachträglich der realen
Fortsetzungs- oder Rückkehrbeziehung zu. Diese Beziehung darf nicht in die
Mechanik gelangen.

### W6: Baselinegrenze

Der Effekt muss gegen einfachere feste Erklärungen ausgewiesen werden. Er muss
nicht zwingend alle Baselines übertreffen; wenn eine Baseline genügt, begrenzt
das die Interpretation.

## 8. Verbindliche Baselines

```text
B0: aktuelle Rezeptorprojektion
B1: unabhängiger lokaler Nachhall
B2: fester Ein-Schritt-Puffer
B3: feste Rekurrenz
B4: Diffusion oder Nachbarmittelung
B5: direkte feste Abbildung der räumlichen Asymmetrie
```

Erklärt B0 den Unterschied, war die aktuelle Gleichheit fehlerhaft.

Erklären B1 bis B5 den vollständigen Effekt, ist eine
Geschichtsverarbeitung gezeigt, aber noch keine MCM-spezifische oder
organische Feldorganisation.

## 9. Falsifikationsbedingungen

Die Weltfunktionshypothese scheitert für diese minimale Welt, wenn:

- aktuell identische Paare nicht exakt hergestellt werden können,
- der Unterschied ohne vorherige Geschichte bestehen bleibt,
- ein Reset den Unterschied nicht entfernt,
- technische Iterationsreihenfolge das Ergebnis bestimmt,
- nur der vollständige Provenienz-Digest verschieden ist,
- die Auswertung ein gewünschtes Vorzeichen voraussetzt,
- eine Baseline denselben Befund vollständig trägt.

Ein Scheitern bedeutet nicht, dass Feldentwicklung unmöglich ist. Es bedeutet
nur, dass diese Weltleistung keine zusätzliche Mechanik begründet.

## 10. Nicht freigegeben

- neue Neuronenzustände,
- Orientierung als Übergangsregel,
- Bewegungsfortsetzung,
- feste oder adaptive Kopplung,
- Rezeptorrückschreibung,
- Ressourcenmechanik,
- semantische Bezeichnung,
- Handlung, Reward oder Zieltopologie.

## 11. Evidenzgrenze

Diese Methodik kann zunächst höchstens tragen:

```text
nichttautologische Weltfunktionsdefinition: E1
passive Geschichtsunterscheidung:           E0
kausale lokale Feldfolge:                   E0
organische Feldorganisation:                E0
Feldintelligenz:                            E0
```

## 12. Bester nächster Schritt

Als Nächstes wird ausschließlich geprüft, ob die vier Weltverläufe die
geforderten aktuell identischen Paare erzeugen und welche der vorhandenen
Zustände oder festen Baselines ihre Geschichte bereits vollständig lesbar
machen.

Erst nach diesem passiven Baseline-Lauf darf entschieden werden, ob überhaupt
ein unerklärter Funktionsrest für eine lokale Feldfolge übrig bleibt.
