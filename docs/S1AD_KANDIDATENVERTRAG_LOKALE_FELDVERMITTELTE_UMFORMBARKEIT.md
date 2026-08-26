# S1-AD: Kandidatenvertrag fuer lokal feldvermittelte Umformbarkeit

Stand: 2026-08-11

Status: `KANDIDAT_AUFGERISSEN_NATURURSACHE_NOCH_OFFEN`

## Zweck

Dieser Vertrag formuliert den ersten konkreten Substratkandidaten nach S1-AC.
Er ist eine statische Hypothese und keine Implementierungsfreigabe.

## Kandidatenrolle

Der Kandidat besitzt an jedem bestehenden Feldort eine begrenzte lokale
Disposition `C_i`. Normale Feldteilnahme soll nicht nur den aktuellen
S-Zustand veraendern, sondern die spaetere Umformbarkeit dieser Disposition:

```text
S/H-Feldteilnahme
-> lokale Disposition C_i veraendert sich
-> spaetere S/H-Feldteilnahme trifft auf veraenderte Disposition
```

`C_i` ist kein Episodenspeicher, kein Objektbezeichner, kein Label und kein
Embedding. Der Name bezeichnet nur die noch zu begruendende lokale Rolle.

## Erforderliche Naturursache

Der Kandidat ist nur zulaessig, wenn eine eigenstaendige inhaltsfreie
Naturannahme gefunden wird, die erklaert:

1. wodurch `C_i` durch normale Feldteilnahme veraendert wird;
2. welche endliche Groesse oder Bilanz die Disposition begrenzt;
3. warum dieselbe Wechselwirkung `C_i` spaeter auf S zurueckwirkt;
4. warum diese Wechselwirkung lokal und ortsgleich bleibt;
5. welche technische Entwicklung durch die Annahme ausgeschlossen wird.

Die Aussage "C_i soll Wiederholungen behalten" ist keine Naturursache.
Ebenso unzureichend sind "C_i soll vergessen", eine feste Schwelle, ein
Zaehler, ein Timer oder eine vorgegebene Phasenfolge.

## Lebenszyklus als Prueffunktion

Der Kandidat muesste prinzipiell dieselbe unveraenderte Wechselwirkung fuer
folgende technische Rollen tragen:

```text
Bildung       -> normale Feldteilnahme veraendert C_i
Erhaltung     -> C_i bleibt begrenzt unterscheidbar
Rueckwirkung   -> C_i veraendert spaetere Feldfortsetzung
Loesung       -> weitere Geschichte macht alte Wirkung irrelevant
Neubelegung   -> spaetere Geschichte kann dieselbe Kapazitaet anders nutzen
```

Diese Begriffe sind Anforderungen an spaetere Tests, keine fest
einprogrammierten Zustandsphasen.

## Pflichtabgrenzung

Vor einer Gleichung muss der Kandidat statisch gegen folgende Erklaerungen
abgegrenzt werden:

| Baseline | Ausschlussfrage |
| --- | --- |
| Nullpfad | Veraendert der Kandidat den schnellen Grundpfad? |
| leaky Spur | Ist `C_i` nur eine feste zeitliche Gewichtung alter S-Werte? |
| Integrator | Ist `C_i` nur ein aufsummierter Eingang? |
| Hysterese | Ist die spaetere Wirkung durch eine feste Kennlinie vorgegeben? |
| F3 | Ist `C_i` nur eine bekannte geschichtsabhaengige M-Verteilung? |
| konservierter Transport | Gibt es wirklich eine neue Naturrolle statt nur Umverteilung? |
| externe Episode | Wird irgendein Inhalt ausserhalb des Feldes gespeichert? |

## Gegenprognose

Ein zulaessiger Kandidat muss mindestens einen Verlauf erlauben, in dem trotz
Weltkontakt keine bleibende spaetere Wirkung entsteht. Ohne solche
Gegenprognose waere der Kandidat nur auf das gewuenschte Ergebnis zugeschnitten.

## Aktuelle Bewertung

Der Kandidat beschreibt die fehlende Zielrolle praezise, besitzt aber noch
keine unabhaengig hergeleitete Naturursache. Die bisher vorhandenen Befunde
bestimmen Feldkontakt, Nachhall und F3-Geschichtstraeger, aber keine neue
konstitutive Umformbarkeit von `C_i`.

```text
Zielrolle:                 plausibel formulierbar
lokale Ursache:            offen
endliche Bilanz:           offen
konjugierte Rueckwirkung:  offen
Baselineabgrenzung:        teilweise moeglich
Implementierung:           STOPP
```

## Entscheidung

`S1-AD` ist als Forschungsfrage zulaessig, aber als Mechanik noch nicht
zulassungsfaehig. Der Kandidat wird nicht implementiert und nicht als
MCM-Memory bezeichnet.

## Bester naechster Schritt

Eine einzige unabhaengige Naturannahme fuer die lokale Disposition `C_i`
bestimmen. Wenn keine solche Annahme aus dem bestehenden MCM-Feld folgt,
muss sie als externe, klar benannte digitale Materialhypothese eingebracht
und gegen die geschlossenen Baselines abgegrenzt werden.
