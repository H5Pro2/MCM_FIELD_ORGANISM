# S1-AF: Materialeigenschaft von `C_i` - lokale feldvermittelte Akkommodation

Stand: 2026-08-11

Status: `DIGITALE_MATERIALHYPOTHESE_FUER_KANDIDATENPRUEFUNG`

## Entscheidung

Die erste konkrete Materialeigenschaft von `C_i` wird als **lokale
feldvermittelte reversible Akkommodation** bestimmt.

Damit ist gemeint:

```text
lokale Feldteilnahme
-> kontinuierliche Veraenderung von C_i
-> veraenderte lokale Kopplungsbereitschaft
-> spaetere veraenderte Feldwirkung
```

`C_i` wird dadurch nicht zu einem Datenspeicher. Es ist eine begrenzte lokale
Disposition des digitalen Substrats.

## Eigenschaften

Die Akkommodation besitzt fuer den ersten Entwurf folgende Eigenschaften:

1. **Lokal:** Nur die lokale Feldteilnahme und die gebundene lokale
   Nachbarschaft wirken direkt auf `C_i`.
2. **Kontinuierlich:** Veraenderung erfolgt ohne Speicherbefehl,
   Schwellenwert oder Phasenautomat.
3. **Begrenzt:** `C_i` bleibt in einem endlichen Zustandsraum.
4. **Reversibel:** Weitere Feldgeschichte kann die Disposition umformen oder
   abschwaechen.
5. **Konjugiert:** Die veraenderte Disposition wirkt ueber dieselbe lokale
   Kopplungsfamilie auf spaetere Feldschritte zurueck.
6. **Inhaltsfrei:** Kein Objekt, keine Quelle, keine Episode und kein Label
   wird gespeichert.
7. **Verteilt:** Mehrere lokale Dispositionen koennen gemeinsam auf das Feld
   wirken, ohne Zieltopologie oder Partnerbeziehungen vorzugeben.

## Rollenstruktur

Die Materialhypothese wird vor einer Gleichung nur durch folgende Rollen
beschrieben:

```text
C_i(t)       lokale begrenzte Disposition
E_i(t)       lokale Feldteilnahme aus S/H und Nachbarschaft
G(E_i, C_i)  Akkommodationswirkung
R(C_i, S_i)  Rueckwirkung auf spaetere Feldkopplung
```

`G` und `R` sind noch keine festgelegten Gleichungen. Sie muessen aus einer
gemeinsamen Materialannahme abgeleitet werden. Eine getrennte Schreibregel
fuer `C_i` und ein fester Leser fuer S waeren unzulaessig.

## Warum diese Eigenschaft gewaehlt wird

Sie bildet den kleinsten technischen Brueckenschritt zwischen dem
hypothetischen MCM-Wirkprinzip und einem entwickelbaren digitalen Substrat:

- sie benoetigt keine menschlichen Begriffe;
- sie setzt keine Episoden oder Bedeutungen voraus;
- sie erlaubt Veraenderung durch Weltkontakt;
- sie erlaubt spaetere Rueckwirkung;
- sie laesst Abschwaechung und Umformung offen;
- sie kann gegen bekannte leaky-, Integrator-, Hysterese- und F3-Baselines
  geprueft werden.

## Strenge Einschraenkung

Die Eigenschaft ist noch keine neue MCM-Natur. In einer konkreten Gleichung
koennte sie auf eine bekannte leaky Spur, einen Integrator oder eine
Hystereseform zurueckfallen. Dann waere sie eine technische Baseline und
keine neue Substratphysik.

Die Bezeichnung "Akkommodation" darf daher nicht als Nachweis von Praegung,
Memory, Lernen oder Organismusfunktion verwendet werden.

## Zulassungsfragen vor Implementierung

Vor einer Runtime-Erweiterung muessen beantwortet werden:

1. Welche lokale Feldgroesse ist die Ursache fuer `G`?
2. Welche Bilanz begrenzt `C_i` fachlich und nicht nur numerisch?
3. Wie wird `R` aus derselben Wechselwirkung hergeleitet?
4. Welche Gegenprognose unterscheidet Akkommodation von einer leaky Spur?
5. Wie kann konkurrierende Geschichte alte Wirkung umformen, ohne Reset?
6. Wie wird Snapshot, Restore und Nullpfad exakt erhalten?

## Entscheidung

```text
Materialeigenschaft:       lokale feldvermittelte reversible Akkommodation
Status:                    digitale Hypothese
Konkrete Gleichung:        noch nicht zugelassen
Runtimeimplementierung:    noch gesperrt
Memory-Claim:              nein
```

## Bester naechster Schritt

Die gemeinsame Ursache fuer Akkommodationsbildung und Rueckwirkung statisch
bestimmen. Erst wenn diese Ursache eine eigene Bilanz und eine nichttriviale
Gegenprognose besitzt, darf eine minimale Gleichung formuliert werden.
