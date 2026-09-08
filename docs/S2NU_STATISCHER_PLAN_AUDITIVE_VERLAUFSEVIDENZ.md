# S2-NU: statischer Plan fuer auditive Verlaufsevidenz

Nur Plan, keine Ausfuehrung oder Laufnummer. Ausgangspunkt ist der
[NT-Abschluss](S2NT_ABSCHLUSS_UND_STATISCHER_ANSATZVERGLEICH.md).
NT und MQ werden nicht wiederholt oder zur Anpassung benutzt. ME/MI bleiben
gesperrt. Ziel sind beobachtete Bandstrukturveraenderungen ueber die Zeit,
nicht zulaessige Variation, Komponentenzerlegung oder Objektidentitaet.

## Eine Messung und eine konkrete Gegenprognose

**Messverfahren: vorzeichenbehaftete zeitliche Banddifferenzen mit totaler
Variation.** Fuer fuenf geordnete Halbprofilvektoren z[0]..z[4], jeweils 48
Werte in unveraenderter Carrierreihenfolge:

```text
delta[k,i] = z[k+1,i] - z[k,i]                   k=0..3, i=0..47
step[k] = sum(abs(delta[k,i]) for i=0..47)/48
T = sum(step[k] for k=0..3)
```

Binary64, aufsteigende Indizes, Python-Builtin `sum`, keine Toleranz,
Gewichtung, Glaettung, Peakdetektion, Normalisierung oder Matchschwelle.
Alle 192 vorzeichenbehafteten Einzelterme je Verlauf, vier step-Werte und
T bleiben erhalten. Eine unabhaengige Direktnachrechnung benutzt keinen
produktiven Differenzhelfer. Dies sind Auswertungen vorhandener Rezeptorwerte,
keine neuen Rezeptormerkmale oder zusaetzlichen Eingangssignale.

Positives delta bezeichnet Zunahme, negatives Abnahme in derselben Bandposition;
null bedeutet keine numerisch beobachtete Aenderung. Eine stabile Bandposition
ist keine nachgewiesene fortgesetzte Klangkomponente. Auch Verlagerungen zwischen
Baendern werden nicht zu einer behaupteten Frequenzspur zusammengefasst.

**Primaere Hypothese:** `T(s02) < T(s03)`. s03 enthaelt genau dieselben fuenf
PCM-Fenster wie s02, aber die Reihenfolge `(0,3,1,2,4)` statt `(0,1,2,3,4)`.
Die ersten und letzten Fenster sind identisch. Eine stetige Pegelentwicklung
wird damit einer fest gebundenen Entwicklung mit zwischenzeitlicher Umkehr
gegenuebergestellt. Die Hypothese ist vor Rezeptoranalyse gebunden; kein
nachtraeglich gewaehlt hoher Unterschied und kein Mindestabstand.

## Zwei Kontrollen, keine weiteren Messalgorithmen

Alle Arme verwenden dieselben einmal gemessenen Fenster:

| Arm | Funktional verfuegbare Eingabe | Ausgabe |
| --- | --- | --- |
| Geordnet | fuenf Vektoren mit nativer Reihenfolge | delta, step, T |
| Anfang/Ende | ausschliesslich z[0], z[4] | beide Vektoren und `E=sum(abs(z[4,i]-z[0,i]))/48` |
| Ungeordnet | exakt dieselben fuenf Vektoren ohne Zeit-/Ordinalinformation | vollstaendiges Multiset mit Multiplizitaet, keine erfundene Reihenfolge |

Die ungeordnete Ansicht wird durch lexikographisches Sortieren der jeweils
384 kanonischen `<48d`-Bytes dargestellt, nicht nach Zeit oder Quell-ID. Keine
Abstaende zwischen Multisetmitgliedern und kein nachtraeglicher Sortierpfad.
Quellen- und Zeitbelege bleiben zur Integritaetspruefung getrennt erhalten,
sind aber keine funktionalen Eingaben dieser Kontrolle. Zustandshashes mit
Zeitanteilen oder Herkunftskennungen duerfen die Reihenfolge nicht verraten.

**Zusatznutzen liegt nur vor**, wenn auf den real erzeugten Werten die
Anfang-/Endvektoren und die vollstaendigen ungeordneten Multisets von s02/s03
jeweils bitgleich sind und die primaere strikte Ordnung besteht. Dann kann
keine Funktion ausschliesslich dieser identischen Kontrolleingaenge das
Gegenpaar unterscheiden. Der Zusatznutzen stammt nicht aus mehr Messwerten.
T-Gleichstand oder inverse Ordnung bedeutet primaeres Nichtbestehen.
Fehlende numerische Kontrollgleichheit bedeutet keinen isolierten Nachweis
des Reihenfolgenutzens; sie wird nicht durch Umordnung nach Messung repariert.

Dies ist eine kontrolliert konstruierte Reihenfolgegegenprobe, kein Nachweis
natuerlicher Quellenkorrespondenz. Insbesondere wird nicht verlangt, dass
sich beliebige verschiedene Verlaeufe in T unterscheiden.

## Neue, vorversiegelbare Quellen

Sechs PCM_F32LE-Stroeme, je fuenf unmittelbar aneinander anschliessende
Fenster a 4.800 Samples bei 48.000 Hz, insgesamt 30 Fenster. Kein Video.
Die folgenden Formeln sind die komplette Quellenfestlegung, keine Suche.

Neutrale Oszillatorgruppen, feste Partialfolge:

| Gruppe | Frequenzen in Hz | Amplituden | Phasenseed |
| --- | --- | --- | --- |
| g0 | 430, 1290, 3870 | 4/20, 2/20, 1/20 | s2nu-pcm-001 |
| g1 | 710, 2130, 6390 | 4/20, 2/20, 1/20 | s2nu-pcm-002 |
| g2 | 5870 | 1/20 | s2nu-pcm-003 |

Phase pro Gruppe und Partialposition p ab null:
`u=unsigned_LE(SHA256(seed+':'+str(p))[:4])`,
`phase=(float(u)/4294967296.0)*math.tau`.
Frequenzen und Amplituden werden durch Floatdivision ihrer ganzzahligen
Zaehler/Nenner gebildet. Kein Zufall ausser diesen festen Hashphasen.

Fuer lokalen Sampleindex j=0..4799 sei `t=float(j)/48000.0`.
`g(t)` entsteht durch Akkumulation ab `0.0` in Partialfolge von
`a*math.sin(((math.tau*f)*t)+phase)`.
Fuer Fensterposition k=0..4 ist `n=4800*k+j` und
`G(k,j)=0.5+(0.5*(float(n)/24000.0))`.

| Strom | Literale Synthese pro Fenster k und Sample j |
| --- | --- |
| s01 | `g0(t)` fuer k=(0,1,2,3,4) |
| s02 | `G(k,j)*g0(t)` fuer k=(0,1,2,3,4) |
| s03 | `G(pi[k],j)*g0(t)` mit pi=(0,3,1,2,4) |
| s04 | g0-Partialsumme mit `t'=float(4800*k+j)/48000.0`, `v=t'+((4.0/100.0)*(t'*t'))`, Winkel `((math.tau*f)*v)+phase` |
| s05 | `g0(t)+(h(k,j)*g2(t))`; h fuer k=0..4: `0.0, float(j)/4800.0, 1.0, 1.0-(float(j)/4800.0), 0.0` |
| s06 | `((1.0-w(k,j))*g0(t))+(w(k,j)*g1(t))`; w: `0.0, 0.0, float(j)/4800.0, 1.0, 1.0` |

Gruppen vollstaendig berechnen, auch bei Nullmultiplikatoren. Erst nach dem
jeweiligen Sampleausdruck einmal nach `<f` runden; keine Zwischen-Float32-
Rundung, kein Clipping oder Skalenwechsel. g0/g1/g2 haben ganze Periodenzahlen
je 100 ms; ihre lokale Oszillatorzeit ist bewusst periodisch wiederholt.
s04 verwendet dagegen die integrierte Phase eines kontinuierlichen
Frequenzanstiegs, keinen fensterweisen Frequenzsprung. Die Quellenamplituden
sind durch die festen Summen begrenzt; reale PCM-/Rezeptordomaenen bleiben
trotzdem technisch zu pruefen, niemals nachtraeglich zu korrigieren.

Nur die getrennte Evaluationswurzel nennt Kategorien: s01 unveraenderte
Fortsetzung; s02 kontinuierliche Pegelaenderung; s03 Reihenfolgekontrolle;
s04 kontinuierliche Frequenzaenderung; s05 hinzukommende und wieder
verschwindende Komponente; s06 Quellenwechsel mit einem Uebergangsfenster.
Die Messung erhaelt keine dieser Kategorien, Gruppenrollen oder Syntheseseeds.
Sie darf insbesondere s05 nicht allein aus dem Rezept als erkannt ausgeben.

## Rezeptor-, Zeit- und Versiegelungsbindung

Unveraenderter [LogSpectralReceptor](../mcm_field_organism/log_spectral_receptor.py):
Hann, FFT, 48 Baender, 50..18.000 Hz,
window_size=4800, hop_size=480. Genau ein direkter `analyze` je Fenster und
eine bestehende NJ-Halbprojektion, keine rollende Pipeline. Die Messkadenz ist
explizit 100 ms: direkt aneinander anschliessende, nicht ueberlappende Fenster;
der historische hop-Parameter wird nicht veraendert oder als neue Kadenz
ausgegeben. Zwischen zwei Stroemen wird kein delta berechnet.

Fuer Stromordinal s=1..6 und k=0..4: Uhr `audio.sample`,
`start=(s-1)*24000+k*4800`, `end=start+4800`, nativer
`snapshot_index=start//480` nach exakter Ganzzahligkeits-/Teilbarkeitspruefung.
Die Synthesezeit und pi in s03 verschieben diese nativen Fenster nicht.
Ausfuehrungsfolge: s01 bis s06, innerhalb jedes Stroms k=0 bis 4.
Quellen-ID `nu-sSS-wKK` bindet jedes Fenster getrennt, auch bei Bytegleichheit.

Vor jeder Analyse: Dokument, 30 Rezepte/Fenster, Payloadhashes, Zeiten,
Interpreter-/math-/Generatoridentitaet, Rezeptor-/NJ-Profile und Code,
Messformeln, Kontrollarme und Bewertungswurzel versiegeln. Die s02/s03-
Payloadpaare sind vorab festgelegt; weitere Kollisionen dokumentieren, nicht
beseitigen. Keine NT-/MQ-Quellen. Hoechstens ein PCM-Fenster gleichzeitig;
keine Rohpayloadablage. Roh-/Halbwerte mit Byte-/Hex- und Herkunftsbindungen
erhalten; Halbierungsrundung nicht als neue Wahrnehmungsinformation ausgeben.

## Auswertung, Unsicherheit und endliche Grenzen

Genau fuenf vorab gebundene ordinale Befunde aus gespeicherten T-Werten:
primaer `T(s02)<T(s03)`; getrennte deskriptive Kontrollen
`T(s01)<T(s02)`, `T(s01)<T(s04)`, `T(s01)<T(s05)`, `T(s01)<T(s06)`.
Die vier Kontrollen ersetzen kein primaeres Bestehen: Anfang/Ende oder der
ungeordnete Bestand koennen diese Unterschiede ebenfalls tragen. Es gibt
keine gewuenschte Rangfolge zwischen Pegel-, Frequenz-, Zusatz- und Wechselstrom.
Vorzeichen und Zeitpunkt aller Bandveraenderungen berichten, aber keine
Bandzunahme mit erkannter Partialaddition oder Abnahme mit Quellenverlust
gleichsetzen. Kein neuer Annahme- oder Enthaltungsalgorithmus.

Fehlende/ungueltige Fenster, Uhr-, Quellen-, Profil-, Werte- oder Digestfehler
sind technische Fehler. Kleine Unterschiede, Nullvariation, gleiche T-Werte,
strukturarme Ausgabe oder fehlende Gegenprognosentrennung bleiben regulare
negative/unsichere Ergebnisse. Kein epsilon zum Unterdruecken numerischer
Reste. Eine Abnahme und Zunahme in benachbarten Baendern kann viele Ursachen
haben; 100-ms-Mittelung, Filterbankueberlappung und fehlende Phase begrenzen
die Interpretation. T kann verschiedene Ordnungen zusammenfallen lassen.

- Spaeter 30 PCM-Fenster, 30 Analysen, 30 NJ-Projektionen; je 1.440 Roh-/Halbwerte.
- Pro Implementierung 24 zeitliche Uebergaenge x 48 = 1.152 Differenzen,
  plus sechs Anfang-/Endvergleiche x 48 = 288; mit Direktnachrechnung 2.880.
- Keine weiteren Quellpaare. Primaer und direkt je sechs T-, 24 step- und
  sechs E-Summen; ungeordneter Arm nur Bytekanonisierung/Sortierung.
- Kontrollgleichheit s02/s03: je Implementierung 96 Rand- und 240 sortierte
  Multisetkomponenten, zusammen maximal 672 Bitgleichheitspruefungen.
- Spaetere unabhaengige read-only Verifikation separat: maximal 1.440
  Vorwaertshalbierungen, 2.880 Termpruefungen, 72 Summen, 672
  Kontrollgleichheitspruefungen. Danach fuenf einmalige Ordnungskriterien.
- Metadaten maximal 65.536 Byte, atomarer Gesamtbeleg 2.097.152 Byte,
  Verifikationsbeleg 262.144 Byte; ein lebendes PCM-Fenster 19.200 Byte.
  Bestehende Belegwege, keine neue Recorderplattform.

Ein positives Primaerergebnis waere nur ein begrenzter Nachweis nutzbarer
Reihenfolgeinformation. Es lernt keine Zusammengehoerigkeit und erkennt
weder Bestandteile noch dieselbe Quelle sicher. Ein negatives Ergebnis
schliesst diese Messhypothese auf den festgelegten Verlaeufen; keine neue
Maske, Ersatzquelle oder nachgemessene Mechanik zur Rettung. Auch bei Erfolg
bleiben ME/MI gesperrt. Quellenproduktion, Implementierung, Qualifikation,
Berechnung und Ausfuehrung sind mit diesem Plan nicht freigegeben.
Keine Memory-, Feld- oder Runtimeaenderung; alle Gates bleiben `False`.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser begrenzten
Reihenfolgegegenprognose und ihrer getrennten Aussagegrenzen weiter.
