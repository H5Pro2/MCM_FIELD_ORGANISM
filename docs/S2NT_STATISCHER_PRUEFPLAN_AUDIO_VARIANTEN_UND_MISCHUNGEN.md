# S2-NT: auditive Varianten und Mischungen diagnostisch unterscheiden

Stand 2026-09-08. Nur statischer Plan, keine Laufnummer oder
Ausfuehrungsfreigabe. S2-NS bleibt unveraendert geschlossen. Keine neue
Zulassungsregel, Maske, Quellenzerlegung, gelernte Repraesentation oder
Memory-/Feld-/Runtimeanbindung.

## Drei verschiedene Aufgaben

1. **Bestandteile wiedererkennen:** Eine Mischung kann reale Bestandteile
   einer Referenz enthalten. Die Generatorherkunft belegt deren kontrollierte
   Erzeugung, nicht ihre Erkennung durch das System. Dieser Vergleich besitzt
   keinen Komponentenextraktor und liefert keinen solchen Funktionsnachweis.
2. **Gesamte Wahrnehmung zuordnen:** Geprueft wird, ob die unveraenderten
   48 Halbprofilwerte unter einer festen direkten L1-Baseline die vorab
   zugelassenen Varianten von Additionen/Ersetzungen unterscheiden. Dies ist
   eine begrenzte technische Zuordnungsaufgabe, keine semantische Identitaet.
3. **Bei unzureichender Evidenz enthalten:** Fehlende Trennung wird als
   unzureichender Nachweis fuer diese Gesamtzuordnung berichtet. Es wird kein
   produktiver Enthaltungsmechanismus konstruiert. Ein naechster Abstand
   allein darf insbesondere Kontrollen nicht automatisch bekannt machen.

Erfolg bei einer Aufgabe ersetzt keinen Nachweis der anderen. Die folgenden
Bewertungszuordnungen sind kontrollierte Versuchsvorgaben, keine Behauptung,
dass jede Mischung grundsaetzlich eine andere Klangidentitaet besitzen muss.
Die bestehenden NS-Erwartungen werden weder ersetzt noch rueckwirkend geaendert.

## Neuer literaler Pruefbestand

14 getrennte PCM_F32LE-Quellen, je 4800 Samples bei 48000 Hz. Keine Videos.
Gruppen stehen in Tabellenreihenfolge; die drei Partialpositionen jeder
Gruppe bleiben einschliesslich Nullamplituden erhalten.

Feste Gruppenvorlagen (Frequenzen in mHz, keine spaetere Anpassung):

| Gruppenkuerzel | Frequenzen | Phasenseed |
| --- | --- | --- |
| f | (310000,1240000,5580000) | s2nt-pcm-001 |
| fshift | (319300,1277200,5747400) | s2nt-pcm-001 |
| g | (470000,1880000,8460000) | s2nt-pcm-002 |
| gshift | (484100,1936400,8713800) | s2nt-pcm-002 |
| u | (733000,2932000,11728000) | s2nt-pcm-003 |
| v | (887000,3548000,14192000) | s2nt-pcm-004 |

Jeder folgende Eintrag bindet Gruppe und exakte Amplitudenverhaeltnisse.
Zwei Eintraege bedeuten zwei Gruppen in der angegebenen Reihenfolge.

| Quellen-ID | Gruppen und Amplituden |
| --- | --- |
| nt-a01 | f:(4/20,2/20,1/20) |
| nt-a02 | g:(4/20,2/20,1/20) |
| nt-a03 | f:(4/20,2/20,1/20) |
| nt-a04 | f:(3/20,3/40,3/80) |
| nt-a05 | fshift:(4/20,2/20,1/20) |
| nt-a06 | f:(4/20,2/20,1/20); g:(0/1,0/1,1/20) |
| nt-a07 | f:(4/20,2/20,0/1); g:(0/1,0/1,1/20) |
| nt-a08 | g:(4/20,2/20,1/20) |
| nt-a09 | g:(3/20,3/40,3/80) |
| nt-a10 | gshift:(4/20,2/20,1/20) |
| nt-a11 | g:(4/20,2/20,1/20); f:(0/1,0/1,1/20) |
| nt-a12 | g:(4/20,2/20,0/1); f:(0/1,0/1,1/20) |
| nt-a13 | u:(4/20,2/20,1/20) |
| nt-a14 | v:(4/20,2/20,1/20) |

Rechenfolge wie die bestehende reine Funktion `pcm_bytes` in
`reports/s2nc/seal_inventory.py`, ohne ihren historischen Haupteinstieg:
`u = unsigned_LE(SHA256(seed + ':' + str(partial_index))[:4])`,
`phase = (float(u)/4294967296.0)*math.tau`.
Je Sample j: `t=float(j)/48000.0`, `f=float(millihz)/1000.0`,
`a=float(numerator)/float(denominator)`,
`angle=((math.tau*f)*t)+phase`. Akkumulation ab `0.0` in Gruppen-/Partialfolge,
abschliessend genau einmal `struct.pack_into('<f', ...)`. Kein Zwischen-Float32,
Clipping, Normalisieren oder Eingangs-Skalierungswechsel. Die maximal
vorgegebene Amplitudensumme ist 8/20; eine spaetere Domaenenverletzung fuehrt
trotzdem zum technischen Stopp, nicht zur Korrektur.

Die neutrale Verarbeitungsfolge ist literal
`nt-a01,nt-a02,nt-a03,nt-a04,nt-a05,nt-a06,nt-a07,nt-a08,nt-a09,nt-a10,nt-a11,nt-a12,nt-a13,nt-a14`.
Fuer Ordinal n=1..14: Uhr `audio.sample`, Fenster
`[(n-1)*4800,n*4800)`, nativer Snapshotindex `10*(n-1)` nach exakter
Teilbarkeitspruefung des Fensterstarts durch 480. Direkte Einzelanalyse,
keine rollende Pipeline. Oszillatorzeit j beginnt je Quelle bei null.

Vor jeder Rezeptoranalyse sind Dokument, alle Rezepte, Reihenfolge, Zeiten,
Payloadhashes, Python-/math-/Generatoridentitaet und Rezeptor-/NJ-Code und
Profile zu versiegeln. Built-in-math nur mit bestaetigter Herkunft, sonst
tatsaechliche Moduldateibindung. Getrennte Ausfuehrungs- und Evaluationswurzel.
`a01/a03` und `a02/a08` bleiben beabsichtigte Exaktkopien mit eigenen IDs und
Zeiten. Weitere Kollisionen dokumentieren, nicht deduplizieren oder ersetzen.

## Ausschliesslich nachgelagerte Bewertungszuordnung

Technischer Vergleicher: Referenzen `(nt-a01,nt-a02)`, Pruefquellen `a03..a14`;
alle Quellen gegen beide Referenzen pruefen, keine Auswahl anhand der Rollen.
Die Ausfuehrungswurzel bindet lediglich diese neutrale Vergleichsbelegung.
Nur die Evaluationswurzel enthaelt:

| Referenz | Exakt | Zulaessige Varianten | Addition | Ersetzung |
| --- | --- | --- | --- | --- |
| a01 | a03 | a04 Pegel, a05 Frequenz | a06 | a07 |
| a02 | a08 | a09 Pegel, a10 Frequenz | a11 | a12 |

`a13/a14` sind unabhaengige Kontrollrezepte ohne erlaubte Gesamtzuordnung.
Additionen erhalten alle drei Grundpartialkomponenten und ergaenzen eine;
Ersetzungen erhalten zwei und tauschen die dritte aus. Die fremde Komponente
besitzt die fest gebundene Phase der anderen Gruppe. Dieses Wissen bleibt
Generatorherkunft im Auswerter; es ist kein zusaetzlicher Rezeptoreingang.
Additionen und Ersetzungen sind Belastungskategorien, keine semantischen Labels.

## Repraesentation, Baseline und vorab fixes Trennkriterium

Unveraendertes `LogSpectralReceptor`-Profil: Hann, FFT, 48 logarithmische
Baender, 50..18000 Hz, Fenster 4800, Hop 480. Je Quelle ein direktes `analyze`,
danach einmal S2-NJ `s2nj.auditory.hann48.output-half.v1`. Rohwerte und
tatsaechlich gerundete Halbwerte mit Profil-, Quellen-, Zeit- und
Subnormal-/Unterlaufbindungen erhalten. Keine Kontaktbildung. Die vollstaendigen
48 Halbwerte sind ausschliesslich diagnostische Eingaben, keine neue Abrufsicht.

Einzige Distanzbaseline:

```text
terms(q,r) = tuple(abs(q[i] - r[i]) for i in 0..47 aufsteigend)
d(q,r) = sum(terms(q,r))/48
```

Historische Python-Binary64-Summationsfolge, nicht `statistics.mean`;
keine Gewichtung, Rundung oder Toleranz. Originalindizes und alle numerischen
Terme speichern. Eine unabhaengige direkte Nachrechnung verwendet dieselben
gebundenen Werte und Rechenfolge, aber keinen produktiven Distanzhelfer.
Keine Verwendung oder Aenderung der Memorygrenzen 0.1/0.01.

**Primaeres ordinales Kriterium je Referenz r:** Fuer BEIDE zulaessigen
Varianten v und BEIDE zugehoerigen Belastungen m (Addition/Ersetzung) muss
`d(v,r) < d(m,r)` gelten. Gleichstand zaehlt nicht als Trennung.
Aequivalent: `max(d(Varianten,r)) < min(d(Addition/Ersetzung,r))`.
Das sind vier vorab gebundene Ordnungspruefungen je Referenz, acht insgesamt.
Exaktkopien zaehlen nicht zu diesem Variantenkriterium. Addition und Ersetzung
getrennt ausweisen; ein Bestehen darf ein Scheitern der anderen nicht verdecken.

**Getrennte Kontrollen:** Jede Variante muss naeher an ihrer zugeordneten
als an der anderen Referenz liegen (vier Vergleiche, Tie = mehrdeutig).
Fuer jede Referenz muss jede ihrer zwei Varianten naeher liegen als a13,
a14 und die andere Referenz (zwoelf Vergleiche). Alle Teilkriterien einzeln
berichten; nur vollstaendiges Bestehen belegt die gebundene gemeinsame
L1-Ordnungsseparation. Exaktkontrollen separat, kein Ersatz fuer Varianten.

Es wird kein Zahlenwert als Annahmeschwelle aus den Messergebnissen gewaehlt,
auch kein Mittelpunkt eines beobachteten Abstandsintervalls. Eine positive
Ordnung ist ein endlicher deskriptiver Separationsbefund, keine kalibrierte
Zulassungsregel oder unabhaengige Generalisierungsqualifikation. Insbesondere
wird fuer Mischungen/Kontrollen kein geschlossener Nearest-Reference-Treffer
als richtige Zuordnung ausgegeben. Ohne weiteres freigegebenes Kriterium
bleibt ihre operative Zulassung beziehungsweise Enthaltung unbestimmt.

## Endliche Arbeit und moeglicher Gegenbefund

- 14 Quellen; spaeter genau 14 direkte Analysen und 14 NJ-Projektionen,
  672 gespeicherte Roh- und 672 Halbwerte. Hoechstens ein PCM-Fenster von
  19200 Byte gleichzeitig, keine Rohpayloadablage.
- 24 Quellen-/Referenzpaare plus genau ein Referenz-/Referenzpaar =
  25 Distanzzeilen je Implementierung, je 1200 Einzelbanddifferenzen;
  mit Direktnachrechnung hoechstens 2400. Keine weiteren Paarvergleiche.
- 24 vorab benannte Ordnungspruefungen ausschliesslich aus gespeicherten
  Distanzen: acht primaere, vier Referenzzuordnungen, zwoelf Kontrollen.
  Roh-/Halbvektorgleichheit auf denselben 25 Paaren: maximal 2400
  Komponentengleichheitspruefungen; darin die tatsaechliche Variation separat
  kennzeichnen, nicht als zusaetzlichen Distanzarm.
- Ein atomarer Gesamtbeleg maximal 2097152 Byte einschliesslich Quellen-,
  Profil-, Roh-/Halbwert-, Term- und Direktbelegen. Bestehende Belegwege
  wiederverwenden, keine Recorderplattform. Separate read-only Pruefung ohne
  Rezeptorwiederholung: bis 672 Halbierungspruefungen, 2400 gespeicherte
  Termbindungen/-pruefungen, 2400 Gleichheitspruefungen, 50 Summen und
  24 Ordnungspruefungen; keine
  zusaetzlichen Quellpaare. Verifikationsbeleg maximal 262144 Byte.

Nur tatsaechlich vom Referenzvektor abweichende Pegel-/Frequenzwerte zaehlen
als gepruefte Rezeptorvariation. Eine nominale Variante mit identischen
Werten bleibt sichtbar und liefert keinen positiven Variationsnachweis;
kein Ersatzfall. Nenner fuer Pegel, Frequenz, Addition, Ersetzung und
Kontrollen getrennt, alle geplanten Quellen bleiben im Bericht.

Ueberlappung, umgekehrte Distanzordnung, Gleichstand oder fehlende
Referenztrennung sind regulaere negative beziehungsweise gemischte Ergebnisse.
Eine Mischung naeher als eine erlaubte Variante widerlegt hier die erwartete
Trennung durch diese L1-Abstandsbewertung; numerische Verschiedenheit allein
rettet sie nicht. Das beweist NICHT, dass jede moegliche Auswertung der
48-dimensionalen Repraesentation scheitern muss. Bitgleiche Halbvektoren bei
unterschiedlichen vorgebundenen Gesamtzuordnungen belegen dagegen eine konkrete
Repraesentationskollision fuer dieses Profil. Roh-/Halbgleichheit getrennt
berichten, um NJ-Rundungsverlust nicht als Rezeptorverlust umzudeuten.

Technische Quellen-, Profil-, Zeit-, Normalform-, Digest- oder Ressourcenfehler
bleiben NOT_EVALUABLE, keine fachliche Ueberlappung. Kein Retry, Ersatzseed,
Quellenwechsel, zweite Suche oder nachgemessene Variationseinschraenkung.
Ein negativer Befund begruendet weder eine neue Memoryregel noch automatisch
eine groessere Repraesentation. Die naechste Entscheidung bleibt beim Analysten.

Jetzt ausschliesslich dieser Plan; Vorversiegelung, Implementierung,
Materialisierung und Vergleich sind nicht freigegeben. Keine Projektfunktionen
oder Tests ausgefuehrt. Historische Belege bleiben unveraendert, Gates `False`.
