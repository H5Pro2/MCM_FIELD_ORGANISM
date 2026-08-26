# S1-D: Audit einer feldspannungsabhaengigen reziproken Mobilitaet

Stand: 2026-08-07

Status: `S1D_STATE_DEPENDENT_MOBILITY_BASELINE_COLLISION`

Implementierung: nicht zugelassen

Forschungslauf: nein

## Forschungsfrage

Kann genau eine MCM-spezifische Naturannahme die lineare B2-Referenz zu einem
minimalen nichtlinearen lokalen Substratkandidaten erweitern, ohne
Praegungsform, Attraktor, Schwelle oder Loeschregel vorzugeben?

Geprueft wird ausschliesslich:

> Die Geschwindigkeit des lokalen reziproken Austauschs zwischen schneller
> Feldlage S und langsamer Disposition L haengt vom Betrag ihrer gegenwaertigen
> lokalen Feldspannung ab.

`Feldspannung` bezeichnet hier nur die dimensionslose lokale Differenz
`q_i = S_i - L_i`. Sie ist keine physikalisch gemessene Spannung und keine
neue Zustandsrolle.

## Warum genau diese Annahme

Sie ist die engste nichtlineare Fortsetzung der vorhandenen MCM-Mechanik:

- sie verwendet nur den abgeschlossenen lokalen Vorzustand;
- sie erhaelt die ko-lokalisierte S-L-Kopplung;
- sie benoetigt keine Welt-, Objekt-, Episoden- oder Wiederholungskennung;
- sie kann ohne Schwelle und ohne feste Attraktorlandschaft formuliert werden;
- S-nach-L und L-nach-S bleiben Teile desselben Austauschs;
- der B2-Pfad entsteht als konstanter Spezialfall.

Es wird keine zweite Hypothese untersucht.

## Allgemeine statische Form

Fuer den internen Austausch am Feldort `i` wird nur die Klassenform betrachtet:

```text
q_i        = S_i - L_i
m_i        = m(abs(q_i))
dS_i/dt    = F0_i(S, Weltkontakt) - g * m_i * q_i
dL_i/dt    =                         (g/rho) * m_i * q_i
```

mit:

```text
rho > 1
g >= 0
m(r) endlich, stetig und strikt positiv
m(0) = 1
```

Eine konkrete Funktion `m` wird nicht gewaehlt. Eine solche Wahl wuerde vor
der Klassenentscheidung nur eine beliebige Relaxationskurve festlegen.

Bei `m(r)=1` entsteht exakt die lokale B2-Austauschform.

## Bilanz

Ohne den vorhandenen schnellen Anteil `F0` bleibt die gewichtete lokale
Summe erhalten:

```text
C_i = S_i + rho * L_i
dC_i/dt = 0
```

Fuer die quadratische Speicherfunktion

```text
E_i = 1/2 * (S_i^2 + rho * L_i^2)
```

gilt:

```text
dE_i/dt = -g * m(abs(q_i)) * q_i^2 <= 0
```

Die Annahme ist damit lokal passiv, besitzt den B2-Nullpfad und erzeugt ohne
Weltwirkung keine Eigenanregung. Diese Eigenschaften sind technische
Schutzbedingungen, kein Entwicklungsbefund.

## Reduktion der Austauschbahn

Solange `m` strikt positiv bleibt, besitzt der interne Austausch dieselbe:

- Erhaltungslinie `C_i`;
- einzige Gleichgewichtslage `S_i = L_i`;
- Bewegungsrichtung zum lokalen Ausgleich;
- Zustandsdimension;
- Kopplungsrichtung wie B2.

Mit der internen Parametrisierung

```text
d tau_i / dt = m(abs(q_i))
```

wird der kontaktfreie Austausch zur linearen B2-Ausgleichsgleichung in
veraenderter Laufgeschwindigkeit. Die geometrische Zustandsbahn bleibt
gleich; nur ihre Weltzeitparametrisierung aendert sich.

Unter fortlaufendem Weltkontakt kann die variable Mobilitaet andere
Zeitgewichtungen und dadurch andere Zahlenwerte erzeugen. Diese Wirkung ist
aber vollstaendig durch die fest programmierte Funktion `m` bestimmt. Sie
fuehrt keine veraenderliche Kopplungsform und keinen weiteren lokalen
Freiheitsgrad ein.

## Abgleich mit den Pflichtbaselines

| Baseline | Ergebnis |
| --- | --- |
| B0 | bei `g=0` exakt enthalten |
| B1 | nicht einseitig, aber weiterhin genau ein Relaxationsmodus |
| B2 | konstanter Spezialfall `m=1` |
| B3 | keine reine Ausgangssaettigung, jedoch feste nichtlineare Zeitgewichtung |
| B4 | gleiche Oberklasse einer fest zustandsabhaengigen Antwortmobilitaet |
| B5 | Entfernung von L-nach-S beseitigt die reziproke Feldwirkung |
| V | nichtlineare Einmodus-Relaxation statt neuer Materialorganisation |
| M | keine Hystereseschleife, aber auch keine umbildbare Kennlinie |
| F3 | keine neue umverteilbare Ressource |
| Q | keine unabhaengige Deformations- oder Materialkoordinate |

Die engste Kollision liegt bei der in S1-C bereits ausgeschlossenen
zustandsabhaengigen Mobilitaetsklasse. Gegenueber B2 wird die Geschwindigkeit,
nicht die Organisationsform erweitert.

## Lebenszyklusgrenze

Die Annahme liefert aus sich heraus keine:

- lokale Umbildung der Kopplungsform;
- metastabile, durch Weltgeschichte entstandene Organisationslage;
- funktionale Loesung durch konkurrierende neue Feldgeschichte;
- erneute Praegung derselben lokalen Faehigkeit mit anderer Wirkungsform.

Kontaktfreier Wirkungsverlust bleibt eine durch `m`, `g` und `rho` fest
bestimmte Relaxation. Eine Nullstelle oder ein Vorzeichenwechsel von `m`
wuerde dagegen feste Sperrlagen, Schwellen oder Instabilitaet programmieren
und verletzt den S1-C-Vertrag.

## Gegenprognose

Zwei lokale Zustaende mit gleichem `C_i` und gleichem Vorzeichen von `q_i`
muessen kontaktfrei auf derselben eindimensionalen Bahn in Richtung
`q_i=0` laufen. Beobachtete Umlagerung auf eine andere Bahn, dauerhafte
konkurrierende Lage oder richtungsabhaengige Wiederbindung kann diese
Hypothese nicht erklaeren.

Diese Gegenprognose ist unabhaengig von einem gewuenschten Memory-Ergebnis.

## S1-D-Entscheidung

```text
MCM-spezifische lokale Motivation:      ja
gemeinsame S-L-Nichtlinearitaet:        ja
Passivitaet und Nullpfad:               statisch ableitbar
neuer lokaler Freiheitsgrad:            nein
neue Organisationsbahn:                nein
Reduktion auf Pflichtbaseline:          zustandsabhaengige Mobilitaet
konkrete Gleichung zugelassen:          nein
Implementierung:                        STOPP
Forschungslauf:                         nein
```

Die gepruefte Annahme ist eine saubere technische nichtlineare Referenzidee,
aber kein eigenstaendiger Substratkandidat. Sie wird nicht implementiert.

## Aussagegrenze

Der Audit ist ein statisches Negativergebnis. Er belegt weder Unmoeglichkeit
eines MCM-Substrats noch Praegung, Feldzeitverdichtung, Memory, inneren
Kontext, Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Keine weitere Mobilitaets- oder Relaxationsfunktion variieren. Der
[S1-E-Dimensionsaudit](S1E_AUDIT_LOKALE_SKALARDIMENSION_UND_VERTEILTE_NICHTSEPARIERBARKEIT.md)
zeigt, dass keine zweite lokale Variable begruendet ist. Als naechstes soll
S1-F einen statischen Zulassungsvertrag fuer verteilte kausale
Nichtseparierbarkeit binden, ohne Beziehung, Topologie, Hysterese oder
Zielorganisation zu programmieren.
