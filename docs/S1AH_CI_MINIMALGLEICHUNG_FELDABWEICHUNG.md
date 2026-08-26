# S1-AH: Minimale Gleichungsform fuer `C_i` und lokale Feldabweichung

Stand: 2026-08-11

Status: `PRUEFMODELL_KEINE_IMPLEMENTIERUNGSFREIGABE`

## Zweck

S1-AH formuliert die kleinste mathematische Form der in S1-AG bestimmten
Materialhypothese. Die Form ist ein Reduktions- und Konsistenzmodell. Sie ist
kein Nachweis einer neuen MCM-Natur.

## Lokale Feldteilnahme

Zuerst wird eine inhaltsfreie lokale Feldteilnahme `E_i` aus der bestehenden
S/H-Lage und der festgelegten lokalen Geometrie abgeleitet:

```text
E_i = P_i(S, H, lokale Nachbarschaft)
```

`P_i` darf keine Quelle, kein Objekt, kein Label und keine Weltbedeutung
lesen. Die konkrete Projektion bleibt bis zur technischen Spezifikation
offen.

## Begrenzte Disposition

Die lokale Feldabweichung lautet:

```text
Delta_i = E_i - C_i
```

Als kleinste begrenzte Form wird vorlaeufig angenommen:

```text
dC_i/dt = alpha * (1 - C_i^2) * Delta_i
```

mit:

```text
C_i in [-1, 1]
alpha >= 0
```

Der Faktor `(1 - C_i^2)` haelt den kontinuierlichen Zustand innerhalb seines
begrenzten Bereichs, ohne Clipping oder Reset. `alpha` ist eine technische
Materialkonstante, kein Wiederholungszaehler.

## Rueckwirkung

Die Rueckwirkung darf nicht als getrenntes Speicherlesen eingefuehrt werden.
Die zulassige Rollenform ist deshalb nur:

```text
dS/dt = F_MCM(S, H, Weltkontakt) + R(Delta, C, lokale Geometrie)
```

`R` muss aus derselben lokalen Wechselwirkung wie `dC_i/dt` abgeleitet
werden. Ein unabhaengiger fester Leser `S += gain * C_i` ist als
Gain-Baseline zu klassifizieren und erfuellt den Kandidatenvertrag nicht.

## Formale Eigenschaften

Das Pruefmodell erfuellt auf Darstellungsebene:

- lokale Ursache durch `Delta_i`;
- endlichen Zustandsbereich durch die Begrenzungsfunktion;
- kontinuierliche Veraenderung ohne Schwelle;
- prinzipielle Umformbarkeit durch spaetere Feldgeschichte;
- keine Inhalts- oder Episodenkennung.

Es erfuellt noch nicht automatisch:

- eine fachlich begruendete Ressourcenbilanz;
- eine nichtreduzierbare Rueckwirkung;
- eine neue MCM-spezifische Naturrolle.

## Statische Reduktion gegen Baselines

Die Gleichungsform muss vor jeder Implementierung auf folgende Reduktionen
geprueft werden:

1. Bei festem `E_i` und ohne Rueckwirkung ist sie eine begrenzte leaky Spur.
2. Bei Rueckwirkung nur ueber `C_i` ist sie ein zustandsabhaengiger Gain.
3. Bei Wegfall der Begrenzungsfunktion ist sie ein lokaler Integrator.
4. Bei fester Umkehr- oder Speicherkennlinie ist sie Hysterese.
5. Bei ortsuebergreifender Bilanz kann sie auf konservierten F3-Transport
   reduzieren.

Wenn eine dieser Reduktionen die gesamte Wirkung erklaert, bleibt das Modell
eine transparente Engineering-Baseline und wird nicht als neue
Substratphysik bezeichnet.

## Gegenprognosen

Das Modell muss mindestens folgende technische Verlaeufe zulaassen:

- identische Eingabe und identischer Anfangszustand erzeugen identische
  Snapshots;
- Nullkopplung laesst die S/H-Grundbahn unveraendert;
- homogene Feldteilnahme bei passender Disposition erzeugt keine beliebige
  weitere Verdichtung;
- unterschiedliche Vorgeschichte kann nur ueber den Zustand `C_i` wirken,
  nicht ueber Metadaten oder gespeicherte Weltinhalte.

## Entscheidung

```text
minimale Form:              formuliert
Begrenzung:                 formal vorhanden
gemeinsame Rueckwirkung:    noch nicht hergeleitet
Baseline-Reduktion:         offen und zwingend
Implementierung:            gesperrt
Memory-Claim:               nein
```

## Bester naechster Schritt

Die konkrete gemeinsame Rueckwirkungsform `R` statisch herleiten und zeigen,
dass sie nicht nur ein fester Leser oder Gain ist. Erst danach darf dieses
Pruefmodell als private technische Baseline implementiert werden.
