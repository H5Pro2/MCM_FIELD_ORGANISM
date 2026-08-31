# S2-HM: Statischer Zwei-Bereich-Kontextkonfliktvertrag

Status: `STATIC_CONTRACT_BOUND_IMPLEMENTATION_LOCKED`

## Ausgangspunkt

S2-HL hat die read-only Nutzung eines ausdruecklich bereitgestellten
`B_STABLE`-Kontextes bestaetigt. Die konkrete Maskenfuellung ist vollstaendig
durch eine direkte, transparente Engineeringbaseline erklaert.

S2-HM prueft deshalb nicht erneut, ob neun maskierte Werte kopiert werden
koennen. Geprueft werden soll spaeter ausschliesslich, ob zwei gleichzeitig
verfuegbare Memory-Bereiche streng rollenadressiert verwendet werden koennen.

Noch nicht freigegeben sind Implementierung, Tests, Zustandsfunktionen,
Rezeptorausfuehrung, Runner, Ergebnisablage oder Feldintegration.

## Funktionsprognose vor jeder Umsetzung

Ein spaeterer privater Verbraucher erhaelt genau eine explizite Rollenbindung:

```text
requested_area = A_RECENT
```

oder

```text
requested_area = B_STABLE
```

Die Ausgabe darf ausschliesslich die visuelle Kandidatenkomponente der
angeforderten Rolle verwenden. Der gleichzeitig vorhandene Kandidat der
anderen Rolle darf weder Werte, Status noch Ressourcenentscheidung
beeinflussen.

- Bei `A_RECENT` ist `recent_content` aus B4 die einzige oeffentliche
  Wertquelle. Die interne Fast-Spur bleibt separat gebundene Evidenz und ist
  weder Ersatzquelle noch dritte Auswahlmoeglichkeit.
- Bei `B_STABLE` bleibt der stabile visuelle Slow-Kandidat die einzige
  Wertquelle.
- Es gibt keine Rangfolge, Verschmelzung, Naeheentscheidung oder automatische
  Kontextwahl.
- Sichtbare Probeanteile bleiben unveraendert. Nur die neun kanonisch
  maskierten Positionen duerfen gefuellt werden.
- Alle Speicher-, Bundle- und Projektionszustaende bleiben read-only.

Die staerkste Gegenbaseline ist eine unabhaengige direkte rollenadressierte
Maskenfuellung. Funktionale Gleichheit ist der erwartete Engineeringbefund.

## Erreichbare gleichzeitige A/B-Belegung

Eine blosse nachtraegliche Konstruktion zweier Kandidaten ist unzulaessig.
Beide Rollen muessen aus einer echten, fortgesetzten Speicherhistorie und
einer gemeinsamen Vollprobe entstehen.

### Kandidatenwerte

Der korrekte visuelle Kandidat `C` verwendet die bereits bekannte
18-Werte-Anordnung:

```text
C = (1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0)
```

Der abweichende Kandidat `F` behaelt alle sichtbaren geraden Positionen bei.
Nur die neun spaeter maskierten ungeraden Positionen werden um `154/255`
verschoben:

```text
F = (1,154/255,0,101/255,1,154/255,0,101/255,
     1,154/255,0,101/255,1,154/255,0,101/255,
     1,154/255)
```

Beide Vektoren sind durch `uint8`-Blockbilder erzeugbar. Ihr normalisierter
visueller L1-Abstand betraegt `77/255` und liegt damit oberhalb der nativen
Schwelle `0,2`. Eine spaetere Exposition mit dem jeweils anderen Kandidaten
darf den bestehenden Fast- oder Slow-Zustand daher nicht als dieselbe
visuelle Spur aktualisieren.

Die auditiven Bildungswerte verwenden zwei verschiedene 4-von-8-Masken mit
normalisiertem Abstand `0,25`. Damit sind auch die auditiven Spuren getrennt.
Die gemeinsame Abrufprobe verwendet an den beiden abweichenden Stellen den
Wert `0,5` und liegt zu beiden auditiven Kandidaten im Abstand `0,125`.

### Neutrale Vollproben

Fuer die Richtung `A=C, B=F` liegt die visuelle Vollprobe auf den neun
abweichenden Positionen bei `72/255` beziehungsweise `183/255`:

- Abstand zu A: `36/255`;
- Abstand zu B: `41/255`.

Fuer die Richtung `A=F, B=C` liegt sie dort bei `82/255` beziehungsweise
`173/255`:

- Abstand zu A: `36/255`;
- Abstand zu B: `41/255`.

Damit passen in beiden Richtungen A und B zur gemeinsamen Vollprobe, A bleibt
aber der eindeutig naehere B4-/Fast-Kandidat. Die Vollprobe dient nur der
read-only Kontextbereitstellung und gelangt nicht als Maskenwertquelle zum
Verbraucher.

## Zwei Bildungsgeschichten

Jede Geschichte beginnt mit frischen B4-, TSPM- und Composite-Zustaenden.

### Geschichte H1: A korrekt, B fremd

1. `F` wird viermal mit seiner auditiven Bildungsmaske exponiert.
2. Dadurch erreicht `F` Slow-Support `3` in `B_STABLE`.
3. `C` wird einmal mit der getrennten auditiven Maske exponiert.
4. `C` liegt danach als juengster B4-Inhalt und als getrennte Fast-Spur in
   `A_RECENT`; `F` bleibt stabil in B.
5. Die gebundene neutrale Vollprobe stellt beide Rollen gleichzeitig bereit.

### Geschichte H2: A fremd, B korrekt

1. `C` wird viermal mit seiner auditiven Bildungsmaske exponiert.
2. Dadurch erreicht `C` Slow-Support `3` in `B_STABLE`.
3. `F` wird einmal mit der getrennten auditiven Maske exponiert.
4. `F` liegt danach als juengster B4-Inhalt und als getrennte Fast-Spur in
   `A_RECENT`; `C` bleibt stabil in B.
5. Die zweite neutrale Vollprobe stellt beide Rollen gleichzeitig bereit.

Die Kandidaten- und Rollenidentitaeten muessen aus den validierten Speicher-,
S2-GC- und S2-GI-Belegen stammen. Geschichtenamen und Sollrollen bleiben reine
Auswertungsmetadaten.

## Gebundene Funktionszellen

Alle vier Primaerzellen erhalten dieselbe maskierte C-Probe. Die vollstaendige
Zielwahrnehmung ist nur dem nachgelagerten reinen Auswerter bekannt.

| Zelle | Geschichte | angeforderte Rolle | gerichtete Prognose |
|---|---|---|---|
| HM-01 | H1 | `A_RECENT` | korrekte C-Ergaenzung |
| HM-02 | H1 | `B_STABLE` | abweichende F-Ergaenzung |
| HM-03 | H2 | `A_RECENT` | abweichende F-Ergaenzung |
| HM-04 | H2 | `B_STABLE` | korrekte C-Ergaenzung |

Jede Zelle wird gegen eine unabhaengige direkte Maskenfuellung mit derselben
Rollenbindung, demselben Kandidaten und demselben funktionalen Budget
verglichen. `CURRENT_PERCEPTION_ONLY` bleibt eine gemeinsame Nullkontrolle und
darf keine maskierte Position ergaenzen.

## Auswertungsmetriken

Getrennt zu erfassen sind:

- Anzahl der genau neun ergaenzten Maskenpositionen;
- Erhaltung aller neun sichtbaren Werte;
- Maskenfehler und Gesamtfehler gegen die getrennte Zielfixture;
- Ergebnisgleichheit mit der direkten rollenadressierten Baseline;
- verwendete Rollen-, Kandidaten-, Komponenten- und Quelldigests;
- Unveraendertheit aller Vor-/Nachzustandsdigests;
- funktionale und native Ressourcen beider Arme.

Die Rolle gilt nur dann als isoliert verwendet, wenn zwei Ausfuehrungen mit
demselben A/B-Bundle und unterschiedlicher expliziter Rollenbindung jeweils
genau den gebundenen Kandidaten liefern.

## Fail-Closed- und Falsifikationsregeln

Vor jeder Ausgabe wird vollstaendig abgewiesen bei:

- fehlender oder unbekannter `requested_area`;
- fehlendem angeforderten Kandidaten;
- Rollen-, Bundle-, Probe-, Zustands- oder Quelldigestabweichung;
- mehrdeutiger oder doppelter Kandidatenquelle;
- A-Anforderung mit fehlendem B4-`recent_content`;
- Versuch, die interne Fast-Spur als A-Ersatzquelle zu verwenden;
- sichtbarem Konflikt zwischen Probe und angefordertem Kandidaten;
- Dimensions-, Masken- oder Ressourcenabweichung;
- veraendertem Speicher-, Bundle- oder Projektionszustand;
- Teilfuellung nach einem Validierungsfehler.

Die Funktionsprognose ist falsifiziert, wenn:

1. der nicht angeforderte Bereich einen Ausgabewert beeinflusst;
2. HM-01 bis HM-04 nicht der expliziten Rollenbindung folgen;
3. Verbraucher und direkte Baseline bei identischen Eingaben abweichen;
4. sichtbare Werte oder ein Quellzustand veraendert werden;
5. die gleichzeitige A/B-Belegung nicht aus den gebundenen Geschichten
   erreichbar ist.

Ein technisch korrekter und baselinegleicher Befund lautet spaeter hoechstens:

```text
ROLE_ADDRESSED_TWO_AREA_CONTEXT_VALID_DIRECT_FILL_EXPLAINS
```

Er ist kein Nachweis einer automatischen Kontextwahl oder eines
MCM-spezifischen Mechanismus.

## Stoppbedingungen

Der Implementierungspfad wird vor Code gestoppt, falls ein Materialisierungs-
audit zeigt, dass:

- A und B nur durch nachtraegliches Einsetzen von Kandidaten gleichzeitig
  erzeugt werden koennen;
- die zweite Exposition den stabilen B-Kandidaten trotz gebundener Abstaende
  aktualisiert oder ersetzt;
- eine gemeinsame Vollprobe nicht beide Rollen gueltig bereitstellen kann;
- die A-Quelle ohne automatische Auswahl nicht eindeutig festgelegt werden
  kann;
- eine faire unabhaengige Rollenbaseline nicht mit gleichem Budget moeglich
  ist.

## Abgrenzung und naechster Schritt

S2-HM fuehrt keine automatische Auswahl ein. Es veraendert weder B4, TSPM-1,
PPB-1, S2-GC, S2-GI noch den Feldpfad. Es bindet ausschliesslich die spaetere
Pruefung expliziter Rollenadressierung.

Der naechste zulassbare Schritt ist ein rein statischer Materialisierungs-,
Schwellen-, Quellen- und Nichtzirkularitaetsaudit der beiden Geschichten und
vier Primaerzellen. Erst ein bestandener Audit darf eine private Erweiterung
des Verbrauchers und der direkten Baseline vorbereiten.
