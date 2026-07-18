# GF_001 Befund: minimale lokale Feldwirkung

## Kurzurteil

`GF_001` trägt E2 ausschließlich für die kausale Wirkung der beiden festen
lokalen Forschungsbaselines B2 und B3:

```text
lokale Aktivierungsprobe aus Feld(t)
-> fester symmetrischer Leser
-> veränderte lokale Aktivierung in Feld(t+1)
```

Die Wirkung tritt innerhalb derselben Dockreihe und zwischen auditiver und
visueller Dockreihe auf. Sie verschwindet bei Ablation aller lokalen Proben.

Der Lauf wählt keine MCM-Feldmechanik aus. Sämtliche beobachteten Antworten
werden vollständig durch die vorgegebenen Mittelungsformen erklärt.

## Laufgrenze

Der Lauf folgt der
[vorregistrierten Methodik](GF_001_METHODIK_MINIMALE_LOKALE_FELDWIRKUNG.md):

- gemeinsame synthetische 2×3-Geometrie,
- eine auditive und eine visuelle Dockreihe,
- vier symmetrische axiale lokale Offsets,
- genau ein kausaler Übergang vom abgeschlossenen Vortakt,
- unabhängiger Neuaufbau jedes Zweigs,
- kein Nachhallupdate und keine Eigenzustandsrückkopplung.

Geprüft wurden 4 Baselines in jeweils 14 Zweigen, insgesamt 56 unabhängige
Zweigläufe.

## Baselines

### B0: Rezeptorprojektion

Die Antwort entspricht exakt dem aktuellen Rezeptorkontakt. Lokale Ablation
verändert sie nicht.

### B1: Hold-State

Die Antwort entspricht exakt der vorherigen Eigenaktivierung. Lokale Ablation
verändert sie nicht. B1 bleibt eine technische Kontrollbaseline und ist für
`GF_001` kein zulässiger Feldwirkungskandidat.

### B2: lokaler Aktivierungsmittelwert

B2 liest ausschließlich vorhandene lokale Aktivierungsproben aus dem
abgeschlossenen Vortakt.

```text
maximale lokale Ablationsdifferenz: 0,55
```

Nach vollständiger Sample-Ablation ist die Antwort an allen sechs Positionen
exakt null.

### B3: gemeinsamer Kontakt- und Lokalmittelwert

B3 liest aktuellen Rezeptorkontakt und lokale Aktivierungsproben gemeinsam.

```text
maximale lokale Ablationsdifferenz: 0,40
```

Nach Sample-Ablation fällt B3 exakt auf die reine aktuelle
Rezeptorprojektion zurück.

## Lokale Reichweite

Für die isolierten Einheitsquellen entsteht am kontrollierten Ziel:

| Baseline | innerhalb derselben Dockreihe | zwischen Dockreihen |
|---|---:|---:|
| B2 | `1/3` | `1/3` |
| B3 | `1/4` | `1/4` |

Die Gleichheit ist kein entdecktes Feldgesetz. Sie folgt aus derselben lokalen
Anzahl vorhandener Proben und der modalitätsneutral verwendeten
Mittelungsform.

## Pflichtkontrollen

Alle vorregistrierten Kontrollen schließen:

- Sample-Iteration: Fehler null,
- Neuronen-Iteration: Fehler null,
- horizontale Spiegelung: äquivariant,
- vollständiger Dockreihentausch: äquivariant,
- vollständige Nullquelle: exakt ruhig,
- Observerentfernung: identische Antwort,
- unabhängiger Neuaufbau: identische Antwort,
- Nachhall: in allen 56 Zweigen exakt null.

Expliziter Nullkontakt und Rezeptorabwesenheit bleiben bei B3 unterscheidbar.
Der Unterschied entsteht durch die feste Leserform: Ein vorhandener Nullwert
nimmt am Mittelwert teil, ein fehlender Rezeptorwert nicht.

## Tatsächlich gezeigt

Der bestehende gemeinsame Feldträger besitzt die technische Kausalstruktur,
um lokale Aktivierungsproben aus dem abgeschlossenen Vortakt an jedem Neuron
atomar zu lesen.

Eine feste symmetrische Funktion kann damit:

- lokale Vorfeldinformation kausal wirksam machen,
- Wirkung innerhalb eines Docks weitergeben,
- Wirkung zwischen Docks weitergeben,
- räumliche Spiegelung und Docktausch ohne Vorzugsrichtung tragen.

## Nicht gezeigt

Nicht gezeigt sind:

- dass B2 oder B3 eine geeignete MCM-Mechanik ist,
- dass das Feld selbst eine Übergangsform entwickelt,
- dauerhafte Wirkung über den einen Vortakt hinaus,
- Beziehung, Ressourcenbindung oder Topologie,
- Stabilisierung, Abschwächung, Lösung oder Wiederbindung,
- organisches Memory,
- Semantik, Reflexion, Lernen oder Selbstregulation.

## Stärkste Alternativerklärung

> Ein gewöhnlicher synchroner Nachbarschaftsoperator liest den vorherigen
> Aktivierungsvektor und berechnet daraus einen neuen Vektor.

Diese Erklärung trägt den gesamten positiven Befund. Die Mittelwerte sind
fest vorgegeben, nicht aus Weltkontakt entstanden.

## Kritische Grenze

`GF_001` beantwortet die Architekturfrage:

```text
Kann der gemeinsame Feldträger lokale Vorfeldwirkung technisch tragen?
-> ja
```

Er beantwortet nicht die Entwicklungsfrage:

```text
Welche lokale Wirkung sollte sich aus Weltkontakt bilden?
-> offen
```

Ein unmittelbarer Einbau von B2 oder B3 würde die offene Forschungsfrage durch
eine harte Programmierung ersetzen.

## Evidenz

```text
Methodik und technische Invarianten: E1
kausale Wirkung von B2 und B3:       E2
MCM-spezifische Übergangsmechanik:   E0
organische Feldorganisation:         E0
organisches Memory:                  E0
```

Ergebnisdigest:

```text
c9355116d4fb9eb9695fc468c2a90cec3f9b2fb7f3d59070a5cb69a65183f496
```

## Runtimefreigabe

Keine.

B2 und B3 bleiben ausschließlich feste Forschungsbaselines im
`GF_001`-Versuchsharness.

## Nächster sinnvoller Schritt

Vor einem weiteren Wirkungsversuch muss eine nicht tautologische fehlende
Feldfunktion formuliert werden:

> Welche beobachtbare Leistung fehlt der reinen Rezeptorprojektion, die lokale
> Vorfeldwirkung erfordert, ohne bereits Mittelwert, Gewicht, Gewinner oder
> Zieltopologie vorzugeben?

Erst diese Funktionsgrenze kann entscheiden, welche lokalen Wirkungsfamilien
als Gegenmodelle geprüft werden dürfen. Weitere beliebige Leserformeln würden
nur den Suchraum fester Programmierungen vergrößern.
