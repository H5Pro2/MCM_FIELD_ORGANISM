# Kontinuierlicher Zwei-Beziehungs-Baselinebefund

## Status

Passiver Welt- und Baselinebefund auf `E2 / BASELINE_BOUNDARY`.

Die
[kontinuierliche Zwei-Beziehungs-Weltfamilie](../architektur/057_MINIMALE_KONTINUIERLICHE_ZWEI_BEZIEHUNGS_WELTFAMILIE.md)
wurde mit der unveränderten Feldruntime und den vorregistrierten Baselines
`B0` bis `B9` ausgewertet.

```text
Weltbeobachtungen: 768
Runtimeänderung:   nein
Memory-Rolle:      nein
Feldwriteback:     nein
```

## 1. Ergebnisdigest

```text
Welt:
77ad7eeefd173f3d51c679009ad598c9d03ff4f756cbf883943aaecbbce03945

Baselines:
d2039a9f515ad450e44b97493eb29b57c44d50ac10a2311b515ed9eabd154c37
```

## 2. Gesamtergebnis

| Baseline | Abdeckung | Treffer bei Antwort |
|---|---:|---:|
| B0 aktuelle Runtime | 0 / 768 | keine Antwort |
| B1 feste Leaky-Exit-Spuren | 768 / 768 | 384 / 768 |
| B2 Übergangszähler | 704 / 768 | 328 / 704 |
| B3 begrenzte Produktspur | 768 / 768 | 312 / 768 |
| B4 letzter Austritt | 768 / 768 | 384 / 768 |
| B5 Bewegungsautomat R0 | 768 / 768 | 360 / 768 |
| B6 Zwei-Regime-Automat | 768 / 768 | 504 / 768 |
| B7 Ereigniszahl | 768 / 768 | 552 / 768 |
| B8 exakte Templates | 240 / 768 | 96 / 240 |
| B9 permanente Doppelspur | 768 / 768 | 504 / 768 |

Die Gesamtquote allein entscheidet nicht. K2 und K6 enthalten absichtlich
noch keine neue Erfahrung und K4 besitzt absichtlich keine stabile lokale
Beziehung.

## 3. Heutige Runtime B0

Vor jedem unbezeichneten Holdout außerhalb der sichtbaren Cue-Kontrolle waren
`activation` und `afterimage` exakt null.

Die aktuelle Runtime besitzt dort keinen Ausgangsleser und keine
geschichtliche Unterscheidung. B0 enthält deshalb keine erfundene
Zufallsantwort:

```text
Abdeckung = 0
```

Das bestätigt die bekannte schnelle Feldgrenze. Es zeigt kein Versagen einer
bereits vorhandenen Memory-Funktion, weil keine solche Rolle existiert.

## 4. Stärkste einfache Erklärung

B6 liest nur die zuletzt real beobachtete Beziehung:

```text
r(n) = x(n) * y(n)

späterer Austritt = r(n) * neuer Anflug
```

Der feste Leser trägt:

```text
K0 dauerhaft R0:       48 / 48
K1 dauerhaft R1:       48 / 48
K2 Wechsel, k = 0:      0 / 48
K3 Wechsel, gesamt:   192 / 240
K6 Rückkehr, k = 0:     0 / 48
K7 Rückkehr, gesamt:  192 / 240
```

Die jeweils fehlenden `48` Fälle in K3 und K7 sind exakt die
`k = 0`-Lebensläufe. Sobald mindestens ein vollständiger Kontakt der neuen
Beziehung erlebt wurde, erklärt B6 alle späteren K3- und K7-Holdouts.

Das Scheitern in K2 und K6 ist korrekt: Ohne neue Außenwelterfahrung kann der
unbezeichnete Wechsel nicht erkannt werden.

## 5. B9 bringt keinen zusätzlichen Funktionsgewinn

B9 bewahrt beide Beziehungstabellen dauerhaft und verwendet dieselbe feste
Letztbeziehungsregel.

Seine Ergebnisse sind in jeder Kontrollgruppe exakt gleich zu B6.

Permanente Doppelspeicherung trägt in dieser Welt daher keine zusätzliche
beobachtbare Funktion.

## 6. Weitere Abgrenzungen

- B1 und B4 liegen insgesamt exakt bei `0,5`.
- B2 enthält Enthaltungen bei ausgeglichenen Zählern.
- B3 reagiert auf jüngere Produktgeschichte, bleibt aber schwächer als B6.
- B7 erreicht eine hohe Gesamtquote, scheitert jedoch an verschobenen
  Wechselstellen und trägt keine allgemeine Weltbeziehung.
- B8 deckt nur `240 / 768` Zweige und scheitert außerhalb exakter bekannter
  Präfixe.
- K4 bleibt für beziehungslesende Baselines randgleich unentscheidbar.

## 7. Tatsächlich gezeigt

Der Lauf zeigt:

- der kontinuierliche Weltgenerator trägt K0 bis K7 reproduzierbar;
- der Weltwechsel gelangt nicht als Runtimeinformation in das Feld;
- die heutige schnelle Feldruntime ist vor den Holdouts exakt angeglichen;
- Ereigniszahl und exakte Templates tragen die Weltfamilie nicht allgemein;
- ein fester Zwei-Regime-Leser genügt nach einer neuen Erfahrung;
- B6 und B9 sind funktional gleich;
- Observer und Baselines schreiben nicht in die Runtime zurück.

## 8. Nicht gezeigt

Der Lauf zeigt nicht:

- organisches Memory;
- eine notwendige neue Zustandsrolle;
- natürliche Feldorganisation;
- Lösung oder Wiederbindung eines inneren Trägers;
- semantische Resonanz;
- Reflexion, Sprache oder Handlung;
- Feldintelligenz.

## 9. Stopplinie

```text
Zwei feste Weltbeziehungen
+ ein zuletzt beobachteter Beziehungswert
-> vollständige Holdoutfunktion nach einer neuen Erfahrung
```

Deshalb wird aus diesem Befund kein Memory-Kandidat abgeleitet.

Eine neue Mechanik wäre nur dann begründbar, wenn vorab eine beobachtbare
Funktion formuliert wird, die B6 nicht bereits durch einen festen
Regimezustand erfüllt.

## 10. Stärkstes Gegenargument

Die Weltfamilie ist selbst auf zwei bekannte Beziehungsformen begrenzt. Ein
Zwei-Regime-Automat ist daher kein zufälliges schwaches Gegenmodell, sondern
eine strukturell passende vollständige Erklärung.

Mehr Kontakte oder längere Laufzeiten würden diese Grenze nicht lösen.

## Nächster Schritt

Vor einer weiteren Welt- oder Runtimeerweiterung muss konzeptionell geklärt
werden:

> Welche kleinste reale Weltfunktion verlangt eine neu erfahrbare
> Beziehungsform, ohne dass deren mögliche Formen bereits als feste
> Regimezustände vorgegeben werden?

Bis diese Frage nicht-tautologisch beantwortet ist, bleiben Memory-Rolle,
Updategleichung und Feldruntime geschlossen.
