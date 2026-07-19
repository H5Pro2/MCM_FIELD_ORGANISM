# Reziproke Feld-Material-Kopplung und konstitutive Sättigung

## Status

Konzeptioneller Rückkopplungsaudit auf `E0 / NO_EQUATION_ADMITTED`.

```text
vorhandene schnelle Feldlage:                 x
hypothetische lokale Materialdisposition:     m
Abhängigkeiten konzeptionell geprüft:         ja
unabhängiges Materialgesetz vorhanden:        nein
zusätzliche Zustandsrolle zugelassen:          nein
Runtime-Erweiterung:                           gesperrt
```

Dieser Audit setzt die
[Grenze des homogen verteilten Skalarsubstrats](067_GRENZE_EINES_HOMOGEN_VERTEILTEN_SKALARSUBSTRATS.md)
fort und gleicht sie mit den früheren Familien K2, K6 und F8 ab.

## Fragestellung

Als kleinste verbleibende Rollenklasse wurde formuliert:

```text
vorhandene schnelle Feldlage x_i
<-> lokale homogene Materialdisposition m_i
```

Die Frage lautet nicht, ob sich zwei solche Rollen technisch koppeln lassen.
Das ist trivial möglich.

Geprüft wird:

> Erzwingt die Reziprozität selbst eine neue organische Memory-Funktion, oder
> bleibt sie ohne unabhängiges konstitutives Gesetz nur eine offene Stelle,
> in die jede gewünschte Wirkung programmiert werden kann?

## Reziprozität ist nur ein Abhängigkeitsgraph

Allgemein könnte eine gekoppelte Transition lauten:

```text
x(t+1) = P(x(t), u(t), Nachbarschaft(t), m(t))
m(t+1) = Q(m(t), x(t), u(t), Nachbarschaft(t))
```

`P` beschreibt die Feldfortsetzung, `Q` die hypothetische Materialfortsetzung.

Die beiden Abhängigkeiten zeigen nur:

- `m` darf eine spätere Feldtransition mitprägen;
- reale Feldwirkung darf `m` verändern;
- beide Rollen liegen in derselben lokalen Kausalfolge.

Sie bestimmen nicht:

- Richtung oder Stärke der Prägung;
- Stabilisierung oder Lösung;
- Begrenzung;
- Zeitskala;
- räumliche Mitwirkung;
- erneute Prägbarkeit;
- funktionale Wirkung unter einer späteren Probe.

Damit ist Reziprozität allein keine Mechanik und keine Naturbedingung.

## Fall A - Lineare reziproke Kopplung

Die kleinste lineare Form wäre sinngemäß:

```text
dx/dt = Lx + a*m + u
dm/dt = b*x - c*m
```

Bei festen Koeffizienten ist dies ein lineares System mit festen Eigenmodi und
festen Zeitkonstanten.

Es kann:

- mehrere zeitliche Reichweiten tragen;
- gedämpfte oder bei ungünstigen Koeffizienten instabile Modi bilden;
- gegenwärtige Feldtrajektorien verändern.

Es kann keine offene geschichtlich entwickelte Organisationsregel begründen.
Seine Wirkung fällt auf ein festes Mehrzeitskalenreservoir oder eine lineare
Rekurrenz zurück.

## Fall B - Fester Leser einer Materialspur

Wenn `Q` eine Spur bildet und `P` diese später additiv oder multiplikativ
liest, gilt:

```text
Feldgeschichte -> Materialspur -> feste Leserwirkung
```

Das ist die bereits verworfene Familie:

- K1 beziehungsweise F1 als lokale Spur;
- K2 beziehungsweise F3 als Empfänglichkeit;
- C1 als fester Leser.

Die Rückwirkung macht aus einer Spur kein organisches Memory, wenn Bildung und
Wirkung weiterhin unabhängig faktorisiert sind.

## Fall C - Veränderliche lokale Empfänglichkeit

`m` könnte bestimmen, wie stark ein Ort neuen Kontakt aufnimmt, Aktivierung
behält oder lokale Feldwirkung weitergibt.

Dann ist `m` funktional:

- Empfänglichkeit;
- Erregbarkeit;
- Reaktionszeit;
- lokale Verstärkung;
- lokale Dämpfung.

Bleibt jeder Ort unabhängig, ist dies K2: eine Metadisposition mit festem
Leser. Prägt sie die Zustandsänderung überlappender Bereiche, ist dies K6
beziehungsweise F8: lokale konstitutive Plastizität.

Die neue Bezeichnung `Materialdisposition` löst die alte Begründungslücke
nicht. Sie benennt weiterhin genau die gesuchte Wirkung.

## Fall D - Veränderliche lokale Leitfähigkeit

Wenn `m` den Nachbarfluss verändert, lautet die Wirkung sinngemäß:

```text
Fluss_ij = Leitfähigkeit(m_i, m_j) * (x_j - x_i)
```

Auch ohne gespeicherte Partner-ID wird damit die wirksame Kopplung
geschichtlich veränderlich.

Das kann räumliche Feldwege technisch bilden. Es legt aber bereits fest:

- dass Memory als Leitfähigkeit wirkt;
- wie zwei lokale Materialwerte eine Verbindung bestimmen;
- wann Feldfluss stärker oder schwächer wird;
- welche Kopplungsform als Topologie gelesen wird.

Die Kante wäre nicht als eigener Datensatz gespeichert, ihre Plastizität wäre
aber in der konstitutiven Leserform enthalten. Diese Lesart ist deshalb eine
implizite adaptive Kante und bleibt geschlossen.

## Fall E - Nichtlineare Attraktoren und Hysterese

Nichtlineare `P`- und `Q`-Regeln können:

- mehrere stabile Lagen;
- Hystereseschleifen;
- Fronten;
- Oszillation;
- metastabile räumliche Formen

erzeugen.

Ohne unabhängige physische Herleitung wären dabei jedoch bereits programmiert:

- Attraktorlagen;
- Umschaltgrenzen;
- Schleifenrichtung;
- Lösungsweg;
- Stabilitätsbereich.

Dies wiederholt den Attraktor- oder Hystereseautomaten aus den Audits 066 und
067.

## Fall F - Ressource, Erhaltung oder Energiebilanz

Eine begrenzte lokale oder globale Größe könnte Umbildung, Sättigung und
Freigabe physisch einschränken.

Wird sie nur eingeführt, damit das gewünschte Wiederbindungsverhalten
entsteht, ist sie die bereits verworfene Ressourcenfamilie K7 beziehungsweise
F5.

Eine Erhaltungs- oder Energiebilanz wäre nur dann eine neue Grundlage, wenn
sie unabhängig von der gewünschten Memory-Funktion als Materialprinzip
begründet wird und anschließend überprüfbare Einschränkungen erzeugt.

Diese unabhängige Begründung liegt noch nicht vor.

## Abgleich mit den früheren Familien

| neue Lesart | bereits geprüfte Familie | Ergebnis |
|---|---|---|
| `m` als zusätzliche Spur | K1 / F1 | feste Zeitspur |
| `m` als Empfänglichkeit | K2 / F3 | Spur plus Leser |
| `m` als gekoppelte Feldverformung | K6 / F8 | konstitutive Physik fehlt |
| `m` als Leitfähigkeit | K3 / F4 | implizite adaptive Kante |
| `m` als Ressource | K7 / F5 | Freigabe programmiert |
| `m` als Attraktorlage | F8 / Audit 066 | Zustandsautomat |

Damit entsteht durch den Begriff `Materialdisposition` keine zusätzliche
Kandidatenfamilie.

## Konstitutives Schließungsproblem

Die Architektur bestimmt inzwischen:

- wo eine spätere Rolle liegen müsste;
- welche lokalen Quellen sie lesen dürfte;
- wann sie frühestens zurückwirken dürfte;
- welche Baselines sie schlagen müsste;
- welche Funktionen Lösung und Wiederprägung bedeuten;
- welche Datenstrukturen unzulässig sind.

Sie bestimmt nicht die Materialgleichung.

Das ist kein fehlender weiterer Architekturblock. Es ist die eigentliche
offene physische Frage:

> Welche neutrale lokale Materialeigenschaft verändert sich unter realer
> Feldarbeit und verändert danach dieselbe Feldphysik, ohne dass gewünschte
> Erinnerung, Beziehung oder Lösung in ihre Gleichung geschrieben wird?

Solange diese Frage nicht unabhängig beantwortet ist, kann jede Gleichung so
gewählt werden, dass sie die vorab verlangten Tests besteht. Ein positiver
Befund wäre dann konstruiert.

## Sättigungsgrenze

Die abstrakte Kandidatensuche ist an dieser Stelle ausgeschöpft.

Weitere Varianten von:

- Disposition;
- Empfänglichkeit;
- Plastizität;
- Leitfähigkeit;
- Hysterese;
- Ressource;
- langsamer Spur

erzeugen ohne Materialprinzip keine neue Erkenntnis.

Hier muss die Forschung stoppen, bevor eine Prioritätsverschiebung oder
Mechaniküberladung entsteht.

## Was als unabhängiges Prinzip gelten könnte

Ein späteres Prinzip muss vor seiner Memory-Wirkung prüfbar sein. Es müsste:

1. aus vorhandener lokaler Feldwirkung ableitbar sein;
2. an jedem MCM-Ort identisch gelten;
3. eine begrenzte Zustandsentwicklung erzwingen;
4. Passivität oder eine explizite lokale Energiebilanz einhalten;
5. keine Bedeutung, Beziehung oder Zieltopologie kennen;
6. konkrete Verläufe ausschließen und nicht nur gewünschte Verläufe erlauben;
7. den heutigen Nullpfad exakt enthalten.

Die engste noch begründbare Richtung ist deshalb kein neuer Memory-Kandidat,
sondern ein Audit eines möglichen **lokalen Passivitäts- und
Feldarbeitsprinzips**.

Dabei darf nicht vorausgesetzt werden, dass Passivität bereits Memory,
Hysterese oder Lösung erzeugt.

## Freigabegrenze

```text
reziproke Rollenabhängigkeit geprüft:          ja
neue Familie gegenüber K2/K6/F8 gefunden:      nein
konstitutives Schließungsproblem bestimmt:     ja
abstrakte Kandidatensuche gesättigt:            ja
Materialdisposition ausgewählt:                nein
Passivitätsprinzip als Memory bestätigt:        nein
zusätzliche Zustandsrolle freigegeben:          nein
Gleichung oder Runtime freigegeben:             nein
```

## Nächster Schritt

Nicht weiter mit Gleichungsvarianten experimentieren.

Vor jeder Mechanik ist einmalig zu prüfen:

```text
vorhandene lokale Feldwirkung
+ lokales Passivitäts- und Feldarbeitsprinzip
-> erzwingt dies eine eigenständige Materialzustandsklasse?
```

Wenn daraus nur Dissipation, Leaky-Relaxation oder eine frei gewählte
Energielandschaft folgt, ist auch dieser Weg geschlossen. Dann muss die
Grundannahme eines digital simulierten organischen Memory-Substrats gemeinsam
neu bewertet werden.

Der anschließende
[Passivitäts- und Feldarbeitsaudit](069_PASSIVITAET_FELDARBEIT_UND_ENDE_DER_SUBSTRATHERLEITUNG.md)
zeigt inzwischen: Das vorhandene Feld erfüllt bereits ohne zusätzliche
Materialrolle eine exakte mathematische Passivitätsbilanz. Passivität schränkt
einen späteren Kandidaten ein, erzwingt ihn aber nicht. Die automatische
Substratherleitung endet hier.
