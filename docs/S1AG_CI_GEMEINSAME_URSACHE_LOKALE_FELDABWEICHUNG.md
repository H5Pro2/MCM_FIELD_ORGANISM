# S1-AG: Gemeinsame Ursache fuer `C_i` - lokale Feldabweichung

Stand: 2026-08-11

Status: `DIGITALE_MATERIALANNAHME_STATISCH_ZU_PRUEFEN`

## Ursache

Als gemeinsame Ursache fuer Bildung und Rueckwirkung von `C_i` wird die
**lokale Feldabweichung** bestimmt:

```text
lokale aktuelle Feldteilnahme E_i
gegenueber
lokaler Substratdisposition C_i
```

Die Differenz ist keine Bedeutung und kein gespeicherter Inhalt. Sie ist eine
rein technische Materialgroesse: Wie stark weicht die aktuelle lokale
Feldteilnahme von der momentan ausgebildeten Disposition ab?

## Gemeinsame Wechselwirkung

Die Materialhypothese lautet:

```text
E_i - C_i
-> veraendert C_i
-> veraendert ueber dieselbe lokale Kopplung die spaetere S-Fortsetzung
```

Damit werden Bildung und Rueckwirkung nicht durch zwei unabhaengige
Kommandos beschrieben. Beide sollen aus derselben lokalen Feldabweichung
folgen.

## Fachliche Begrenzung

Die Feldabweichung allein ist noch keine ausreichende Materialtheorie. Vor
einer Gleichung muessen folgende Punkte gebunden werden:

1. Welche lokale Feldgroesse bildet `E_i` ohne semantische Interpretation?
2. Welche endliche Bilanz begrenzt `C_i`?
3. Wie bleibt die Rueckwirkung lokal und konjugiert zur Bildung?
4. Welche Dissipation oder Umformbarkeit folgt aus der Materialannahme?
5. Wie wird verhindert, dass `C_i` nur ein leaky Integrator oder ein Gain
   wird?

## Gegenprognosen

Die Materialannahme erlaubt folgende technische Gegenprognosen:

- Bei homogener Feldteilnahme und passender lokaler Disposition veraendert
  sich `C_i` nicht beliebig weiter.
- Bei abgeschaltetem Rueckwirkungspfad darf `C_i` keine spaetere S-Wirkung
  erzeugen.
- Bei identischer Feldfolge und identischer Startdisposition muessen die
  spaeteren Snapshots digestgleich sein.
- Bei vertauschter Vorgeschichte darf ein Unterschied nur auftreten, wenn
  die lokale Feldabweichung unterschiedliche Substratzustaende erzeugt.

## Baseline-Abgrenzung

Die Annahme ist noch nicht als neue MCM-Natur bestaetigt. Sie kann auf
bekannte Mechaniken reduzieren:

| Moegliche Reduktion | Konsequenz |
| --- | --- |
| feste zeitliche Gewichtung | leaky Spur, kein neuer Kandidat |
| aufsummierte Feldabweichung | Integrator, kein neuer Kandidat |
| feste Begrenzungskennlinie | Hysterese oder Saettigung, kein neuer Kandidat |
| reine M-Verteilung | F3 oder konservierter Transport, kein neuer Kandidat |
| reine Kopplungsverstaerkung | Gain-Baseline, kein neuer Kandidat |

Der erste `C_i`-Prototyp waere deshalb eine offen deklarierte digitale
Materialbaseline. Erst eine nichtreduzierbare gemeinsame Feld-/Substratwirkung
koennte ihn zu einem eigenstaendigen Kandidaten machen.

## Entscheidung

```text
gemeinsame Ursache:       lokale Feldabweichung E_i - C_i
Materialstatus:           digitale Hypothese
MCM-Naturstatus:          nicht bewiesen
Baseline-Risiko:          hoch und explizit zu pruefen
Gleichung:                noch nicht freigegeben
Implementierung:          noch nicht freigegeben
Memory-Claim:             nein
```

## Bester naechster Schritt

Die kleinste formale Materialgleichung fuer `E_i`, `C_i` und die gemeinsame
Rueckwirkung statisch formulieren und vor jeder Implementierung gegen leaky
Spur, Integrator, Gain, Hysterese und F3 reduzieren.
