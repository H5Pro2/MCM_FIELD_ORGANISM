# Nullpfad-Korrekturvertrag fuer gekoppelte Substratphysik

## Status

```text
Vertragstyp:                       projektweite Methodenkorrektur im F3-Zweig
gewaehlte Korrektur:               K2 Parameterneutralitaet
aktiver M-Gleichzustand:           materiell neutral, nicht allgemein funktional neutral
exakter schneller Nullpfad:        Kopplungsparameter gleich null
Umschalten waehrend eines Laufs:   verboten
Pattern-Leser oder spaetere Gate:  weiterhin verboten
Gleichung, Runtime oder Versuch:   noch nicht zugelassen
```

## Vorrang und Geltungsbereich

Dieser Vertrag korrigiert fuer neue Arbeiten im F3-Zweig die bisherige
Forderung, ein gleichfoermiger langsamer Materialzustand muesse unter jeder
zulaessigen S-Lage exakt die heutige S-H-Runtime erzeugen.

Die Korrektur gilt ausschliesslich fuer eine unteilbare gekoppelte
Substratphysik, bei der derselbe weltbedingte Materialaustausch sofort auf S
zurueckwirkt. Historische Audits bleiben als Herleitung erhalten.

Unveraendert bleiben alle Verbote gegen:

- Labels, Reward, Ziele und Zieltopologien;
- Partner-, Episoden-, Objekt- und Clusteridentitaeten;
- getrennte Schreib-, Konsolidierungs-, Abruf- oder Loeschphasen;
- Pattern-Leser, adaptive Kanten und Observerrueckschreibung;
- Parameterwahl nach einem gewuenschten Ergebnis.

## 1. Grund der Korrektur

Der mathematische Minimalvertrag hat drei gleichzeitig unvereinbare
Bedingungen nachgewiesen:

```text
N1 gleichfoermiges M ist fuer jede S-Lage funktional neutral
N2 S kann M aus diesem Zustand weltbedingt umverteilen
N3 derselbe erste Austausch wirkt sofort auf S zurueck
```

N2 und N3 erzeugen beim ersten weltbedingten Austausch eine S-Wirkung. N1
verbietet genau diese Wirkung. Eine weitere Nichtlinearitaet loest diesen
Kausalwiderspruch nicht.

## 2. Entscheidung fuer K2

Der Nullpfad wird kuenftig durch einen expliziten, vor dem Lauf festen
Kopplungsparameter beschrieben:

```text
lambda_SM = 0:
keine S-zu-M-Kreuzwirkung
keine M-zu-S-Rueckwirkung
heutige S-H-Fortsetzung unveraendert

lambda_SM != 0:
aktive gekoppelte S-M-Naturphysik
weltbedingter M-Austausch darf ab dem ersten Kontakt auf S rueckwirken
```

`lambda_SM` ist hier nur eine Rollenbezeichnung, noch kein Feldname und kein
gewaehlter Zahlenwert.

### Warum K2 die kleinste Korrektur ist

K2 fuegt keinen neuen Zustand, Leser und keine Lebenszyklusphase hinzu. Sie
trennt lediglich zwei feste Forschungsarme:

- bestehende schnelle Nullruntime;
- aktive gekoppelte Materialhypothese.

Formation und Rueckwirkung bleiben im aktiven Arm dieselbe unteilbare
Naturwechselwirkung.

## 3. Materieller Referenzzustand

Die gleichfoermige endliche M-Verteilung bleibt der materielle
Referenzzustand:

```text
M_i = M_total / Anzahl_der_Orte
```

Sie bleibt:

- geometrisch translations- und spiegelungssymmetrisch;
- frei von gespeicherten Inhalten und bevorzugten Orten;
- bei gleichfoermigem S und ohne Weltkontakt stationaer;
- Ausgangspunkt jedes frischen aktiven Kandidatenlaufs.

Sie ist jedoch bei aktiver Kopplung **nicht** fuer beliebige
S-Inhomogenitaet funktional neutral. Eine reale S-Differenz darf M sofort
verschieben und die gebundene S-Rueckarbeit ausloesen.

Diese erste Wirkung ist keine Praegung und kein Memory. Sie ist die direkte
Antwort der aktiven gekoppelten Naturphysik.

## 4. Exakter Nullpfad

### Mathematische Gleichheit

Bei `lambda_SM = 0` muessen fuer identischen schnellen Startzustand,
identische Weltzufuhr und identische Organismusdauer gelten:

```text
S_candidate(t) = S_current(t)
H_candidate(t) = H_current(t)
```

fuer den gesamten Verlauf innerhalb der vorregistrierten numerischen
Praezisionsgrenze.

M darf in diesem Arm weder S beeinflussen noch durch S als behauptete
Organismusfunktion fortgeschrieben werden. Am saubersten bleibt M
gleichfoermig und kausal abgekoppelt.

### Snapshotgrenze

Ein spaeteres Kandidatenschema mit zusaetzlichem M kann keinen byteidentischen
vollstaendigen Snapshot-Digest der heutigen Schemafassung besitzen. Deshalb
werden getrennt geprueft:

- exakte S-H-Verhaltensprojektion;
- stabile neue S-H-M-Snapshotfortsetzung;
- explizite Schemaversion;
- keine Behauptung byteidentischer Gesamtsnapshots ueber verschiedene
  Schemata hinweg.

Die heutige Runtime bleibt als unveraenderter separater Baselinearm erhalten.

## 5. Parameter darf keine Organismusfunktion werden

`lambda_SM` wird vor einem Arm festgelegt und bleibt fuer dessen gesamten
Verlauf konstant.

Verboten sind insbesondere:

- Einschalten nach einer Bildungsphase;
- Ausschalten zum Vergessen;
- Umschalten bei Probe, Wiederholung oder Schwelle;
- Anpassung anhand von Observerwert, Erfolg oder Zielantwort;
- andere Werte fuer Bildung, Wirkung, Loesung und Wiederpraegung;
- lokale oder inhaltsabhaengige Lambda-Werte.

Der Nullparameter ist eine Forschungsablation, kein Schalter im Organismus.

## 6. Neue Bedeutung von Neutralisierung

Kuenftig werden drei Interventionen streng getrennt.

### A0: Kopplungsablation

`lambda_SM = 0` fuer einen frischen vollstaendigen Vergleichsarm. Dies ist der
exakte heutige schnelle Nullpfad.

### A1: M-Konfigurationsneutralisierung

Eine entstandene M-Verteilung wird mengenbilanziert auf die gleichfoermige
Referenzverteilung gebracht. Bei weiterhin aktiver Kopplung darf die naechste
S-Probe erneut M bewegen und sofort rueckwirken.

A1 prueft die kausale Rolle der entstandenen M-Konfiguration. A1 ist nicht der
heutige Runtime-Nullpfad.

### A2: Richtungsablation

Nur eine Kreuzrichtung wird in einem separaten Forschungsarm entfernt. Diese
Ablation prueft S-zu-M und M-zu-S kausal, ist aber keine zulaessige
Produktionsruntime.

## 7. Evidenzkorrektur

Eine aktive gekoppelte Grundantwort wird nicht als langsame Wirkung
interpretiert. Ein spaeterer Geschichtsbefund muss deshalb als Differenz
zwischen kontrollierten aktiven Armen isoliert werden:

```text
gleicher aktiver Kopplungsparameter
gleiche gegenwaertige S-H-Lage
gleiche byteidentische Probe
unterschiedliche reale Vorgeschichte und M-Konfiguration
-> unterschiedliche weitere S-Trajektorie
```

Notwendig bleiben:

- vollstaendiger M-Tausch;
- mengenbilanzierte M-Neutralisierung;
- geometrische Permutation;
- M-zu-S-Richtungsablation;
- aktive frische Gleichzustandsbaseline;
- Nullparameterbaseline der heutigen Runtime.

Nur der Unterschied oberhalb der aktiven frischen Grundantwort kann spaeter
als substratvermittelte Geschichtswirkung untersucht werden.

## 8. Pflichtbaselines nach der Korrektur

Mindestens erforderlich sind:

1. heutige S-H-Runtime ohne Kandidatenschema;
2. Kandidatenschema mit `lambda_SM = 0`;
3. aktive Kopplung aus frischem gleichfoermigem M;
4. aktive Kopplung mit passiver M-Diffusion ohne S-Rueckarbeit;
5. einseitige S-getriebene Drift ohne gebundene Rueckarbeit;
6. dieselbe Drift mit separatem Pattern-Leser;
7. konstante lineare Cross-Diffusion;
8. Richtungs-, Vorzeichen- und M-Konfigurationsablationen.

Ein Unterschied zwischen Arm 1 und aktiver Kopplung ist nur ein
Mechanikunterschied. Er ist kein Memorybefund.

## 9. Auswirkungen auf bestehende Vertrage

Fuer neue F3-Arbeiten gilt:

```text
alter Satz:
gleichfoermiges M reproduziert unter jeder S-Lage die heutige Runtime

ersetzt durch:
gleichfoermiges M ist materiell symmetrisch und ohne S-Kraft stationaer;
die heutige Runtime wird exakt durch lambda_SM = 0 reproduziert
```

Nicht geoeffnet werden:

- R1 und seine lokalen Schliessungsformen;
- nichtkonservativer L-Eigenfluss;
- F2 Drift plus separater Leser;
- adaptive Beziehungen oder Topologie;
- alte H2-Radial- und Phasenfeldkandidaten.

Geoeffnet wird nur die erneute mathematische Pruefung der bilinearen
konservativen F3-Form unter dem korrigierten Nullpfad.

## Forschungsentscheidung

```text
K1 Zustandsneutralitaet:           verworfen fuer unteilbare F3-Kopplung
K2 Parameterneutralitaet:          verbindlich gewaehlt
K3 getrennter Pattern-Leser:       weiterhin geschlossen
aktiver M-Gleichzustand:           materieller Referenzzustand
heutiger schneller Nullpfad:       exakte Parameterablation
Memory-, Organisations- oder KI-Claim: nein
```

## Bester naechster Schritt

Als naechstes wird der mathematische F3-Minimalvertrag unter K2 neu
formuliert. Er muss genau eine kleinste kontinuierliche Kantenform bestimmen
und statisch pruefen:

1. nichtnegative gerichtete M-Raten und exakte M-Erhaltung;
2. weltbedingten Fluss aus gleichfoermigem M;
3. gebundene S-Rueckarbeit desselben Flusses;
4. Invarianz des S-Bereichs ohne Clipping;
5. aktiven frischen Referenzarm und exakten Nullparameterarm;
6. Reduktion gegen einseitige Drift und konstante Cross-Diffusion.

Erst wenn diese Bedingungen gemeinsam erfuellbar sind, darf eine statische
Implementierungsspezifikation entstehen.

Der
[K2-mathematische F3-Minimalvertrag](K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md)
hat diese gemeinsame statische Existenz inzwischen fuer genau eine
kontinuierliche Kantenform nachgewiesen. Code und Versuch bleiben bis zu einer
Implementierungsspezifikation gesperrt.
