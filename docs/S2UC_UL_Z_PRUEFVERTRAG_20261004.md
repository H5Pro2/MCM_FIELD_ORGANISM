# ULZ1: zeitliche Fehlerglättung unter gemeinsamem Speicherlebenszyklus

2026-10-04. Ein einzelner Prüfvertrag, ausschließlich konzeptionell.
Keine Implementierung, Materialisierung, Qualifikation oder Forschungsausführung
durch dieses Dokument autorisiert. Keine Fortsetzung verbrauchter LZ1-Freigaben.

## Gegenstand, Arme und überprüfbare Erwartung

U: vorhandene multi_error_exact_v1-Bewertung, erstes gültiges Feedback direkt,
danach EC=.5*EC+.5*ec und EP=.5*EP+.5*ep in bestehender binary64-Reihenfolge.
L: erstes und jedes weitere gültige Feedback EC=ec, EP=ep. Genau zwei Arme.
Beide wählen das eindeutige negative Minimum ihres eigenen EC−EP unter warmen
berechtigten Hypothesen, sonst Persistenz. Kalt, Gleichstand, Fehlerbehandlung,
Originalaufnahme, Abruf, Feedback, Promotion und Verdrängung bleiben unverändert.
A1/K1 aus. Keine Parameter-, Varianten- oder Seed-Suche, kein weiterer Arm.

Hypothese: U glättet zufällige Abweichungen und erzielt im stabilen Abschnitt
geringeren mittleren Fehler; L reagiert nach dem Verteilungswechsel schneller
und erzielt im frühen Wechselabschnitt geringeren Fehler. Die Konkurrenz des
warmen Z und reguläre Zellverluste können diese Erwartung widerlegen.
Untersucht wird diese Bewertungsstrategie mit ihrem tatsächlichen Lebenszyklus,
nicht ein allgemeiner MCM-Mehrwert oder eine isolierte feste Gedächtnisdauer.

## Feste Quellenfamilie ohne Ergebnisanpassung

V(x)[j]=x+j/4096 für j=0..47; H1=V(1/8), H2=V(1/2),
A=V(1/4), B=V(3/4), Z=V(3/8). Jeder Block T(Y)=[H1,H2,Y,H1].
Reguläre Aufnahme aller Frames, keine Bestandsinjektion oder Schutzregel.
Je Geschichte vier Präfixblöcke und 256 stochastische Blöcke = 1.040 Frames.
Präfix A,A,B,B bei Bit1(r−1)=0, sonst B,B,A,A. Es wird nichts vorgewärmt,
aus dem Beobachter zurückgefüllt oder beim Wechsel zurückgesetzt.

32 Wiederholungen r=1..32, jeweils zwei Bedingungen S und W und je U/L:
64 Geschichten, 128 Arme. Bit0(r−1) bestimmt den bevorzugten Endpunkt E:
0→A, 1→B; O ist der andere Endpunkt. Jede Kombination von Präfixrichtung und
E tritt achtmal auf. Z bleibt geometrisch unverändert; keine Spiegelung oder
Umdefinition nach Befund. Die asymmetrische Lage von Z wird ausdrücklich nicht
als räumlich symmetrischer Versuchsaufbau bezeichnet.

| Bedingung | Blöcke b=1..128 nach Präfix | b=129..256 |
| --- | --- | --- |
| S | Pr(E)=3/5, Pr(O)=1/5, Pr(Z)=1/5 | unverändert |
| W | Pr(E)=3/5, Pr(O)=1/5, Pr(Z)=1/5 | Pr(E)=1/5, Pr(O)=3/5, Pr(Z)=1/5 |

Begründung: Ein Endpunkt hat eine klare, aber nicht deterministische Mehrheit;
die zwei übrigen Alternativen haben gleiches positives Gewicht. Beim Wechsel
werden nur die Endpunktgewichte vertauscht. Die Zwischenwertgelegenheit bleibt
konstant, damit ein Wechsel nicht zugleich Z ein-/ausschaltet. Diese einfachen
rationalen Gewichte wurden nicht auf U-Ausgaben geprüft oder optimiert.
Die ausgewogene Endpunktorientierung begrenzt eine einseitige geometrische
Begünstigung; Ergebnisse je Orientierung bleiben sekundär sichtbar.

Deterministische, jetzt festgelegte Ziehung ohne Probelauf:
u = erste acht Bytes von SHA256 der UTF-8-Zeichenfolge
`MCM-ULZ1/source/v1/r={r}/b={b}`, unsigned big-endian; keine führenden Nullen.
Setze M=2^64. Vor dem Wechsel und in S: E falls 5u<3M,
sonst O falls 5u<4M, sonst Z. In W nach 128: E falls 5u<M,
sonst O falls 5u<4M, sonst Z. Keine Float-Schwellen. S/W verwenden dieselben
u derselben Wiederholung; U/L erhalten dieselben Werte derselben Geschichte.
Diese endliche Integerabbildung approximiert die rationalen Gewichte bis zur
Diskretisierung des 64-Bit-Gitters, sie behauptet keine exakte reelle Ziehung.
Keine Zukunft, Bedingung, Wahrscheinlichkeit oder Phasengrenze als Armeingang.
Profile dienen nur der Bindungsidentität, nicht als Policy-Feature.

Vor Materialisierung sind Rezept, Quellcode, Runtime, Masken, Grenzen und
Auswertungsverfahren per SHA256 zu binden. Alle 64 Quellen werden vollständig
vor dem ersten Policy-Aufruf materialisiert und mit Einzelhashes versiegelt.
Es gibt keine Auswahl nach sichtbaren Quellstatistiken, keine Ersetzung einer
ungünstigen Quelle und keinen Zugriff des Arms auf das Gesamtmanifest.

## Zielmengen, zwei primäre Fragen und Unsicherheit

Globale Ordinale beginnen bei 1. Prognosen an allen ungeraden Zielen
G={3,5,...,1039}, 519 je Geschichte/Arm. Ziel1041 zensiert.
G_init={3,5,...,15}; G_post={17,19,...,1039};
G_Y={4b+15: b=1..256}; G_skeleton=G_post ohne G_Y.
Keine Beschränkung auf warme, gewählte oder erhalten gebliebene Hypothesen.

Primär genau zwei gepaarte Kontraste D=MAE(U)−MAE(L):

1. Stabile Genauigkeit: S, Y-Blöcke33..128 (96 Ziele je Wiederholung).
   Erwartet D<0. Die erste feste Eingewöhnungsphase bleibt sekundär enthalten.
2. Früher Wechsel: W, Y-Blöcke129..160 (32 Ziele je Wiederholung).
   Erwartet D>0. Dies ist Fensterfehler, keine individuelle Anpassungslatenz.

Fenster sind aus den bisherigen Konzepten unverändert übernommen, nicht nach
ULZ1-Ergebnissen gewählt. Endpunktorientierungen werden primär gleich gewichtet.
Zuerst arithmetischer Mittelwert der Ziel-MAE innerhalb jeder Wiederholung,
dann ungewichteter Mittelwert der 32 gepaarten Wiederholungsdifferenzen.

Gepaarter Clusterbootstrap: 10.000 Ziehungen, jeweils 32 Wiederholungsindizes
mit Zurücklegen. Für z=0..9999, k=0..31: erste acht Bytes SHA256 UTF-8
`MCM-ULZ1/bootstrap/v1/z={z}/k={k}`, unsigned big-endian modulo32, plus1.
Dieselbe Indexmatrix für beide Bedingungen, alle Arme und Masken; niemals
Einzelziele unabhängig resamplen. Nominale zweiseitige 97,5%-Intervalle für
beide Primärkontraste (Bonferroni für zwei Fragen), Quantile .0125/.9875.
Sortieren, lineare Interpolation bei Position (n−1)q. Zusätzlich beide
Primärpunktwerte, alle 32 Differenzen und vollständige Zielzahlen ausgeben.

Stabilitätsvorteil belegt nur bei oberer Intervallgrenze<0; früher L-Vorteil
belegt nur bei unterer Grenze>0. Die erwartete Abwägung ist nur belegt, wenn
beide Kriterien erfüllt sind. Enthält ein Intervall0: betreffende Aussage
nicht nachgewiesen, keine Gleichwertigkeit. Ein Intervall vollständig auf der
Gegenseite widerlegt die jeweilige gerichtete Erwartung. Insbesondere U in
beiden Fenstern nachweislich besser widerlegt den erwarteten frühen L-Vorteil.
Kein positives Gesamturteil aus einer einzelnen gelungenen Teilfrage.

Sekundär vollständig: G, G_init, G_post, G_Y, G_skeleton, Y1..32,
Y33..128, Y129..160, Y161..256 jeweils S/W, samt Orientierungsaufteilung.
95%-Intervalle mit derselben Ziehungsmatrix, ausdrücklich explorativ ohne
zusätzliche konfirmatorische Erfolgsregeln. Vollständige kumulative Fehlerkurven,
Gewinn-/Schadensanzahl, -summe, maximaler Einzelschaden und schlechteste
Wiederholung; keine angenommene Schadensfreiheit. Persistenzfehler darf als
Beobachterdiagnostik erscheinen, ist kein weiterer primärer Arm/Kontrast.

## Gemeinsamer Lebenszyklus und vollständiger Beobachter

Z ist reguläre dritte Fortsetzung: Kandidatenbildung, Warmwerden, Konkurrenz,
Promotion und Verdrängung werden nie verhindert. Die Anzahl lebender Hypothesen
kann wechseln. Unterschiedliche Zellalter sind zulässig; jedes EC wird nur
gegen sein eigenes EP verglichen. Keine gemeinsame Ersatz-Persistenz-EMA.

Für jedes Ereignis U/L-Gleichheit verlangen: geordnete Retained-Originale,
Kandidat, forming/Hinweisbestand, Rollen/Generationen/Offsets, Originalidentitäten,
Abrufberechtigung, Kalt/Warm-Belegung, gültige Feedbackgelegenheiten und
Promotion-/Verlustereignisse. Abweichung → technisch NICHT_AUSWERTBAR,
keine nachträgliche Auswahl vermeintlich unverfälschter Fälle.

Pro Freeze sämtliche Treffer/Ausschlüsse, Zellenpaare, Differenzen, Wahlgrund,
Ausgabeoriginal/P und Ticketidentitäten festhalten. Pro Feedback sämtliche
Sofortfehler und Updates auch für nicht gewählte Hypothesen, Verlustgründe und
Zellwerte davor/danach; pro Promotion bitgleiche Mitnahme und gelöschte Zellen.
Eigene Feedbackzeitpunkte/Alter darf nur der externe Beobachter protokollieren.
L besitzt ausschließlich seine aktuelle Bank: beim Verlust löschen, bei neuer
Identität kalt beginnen, bei direkter Promotion mitnehmen. Keine Beobachter-
historie als L-Speicher, keine nachträgliche Neubewertung früherer Ziele.
Referenzen werden unabhängig von Produktionsbank und Produktionsauswahl
fortgeschrieben; Zugriff vom Arm auf Referenz/Archiv ist ausgeschlossen.

## Ressourcen und Export

Je Arm unveränderte Grenzen: 18 Originalframes, zwei Ausgabevektorslots,
20 kombiniert; Originalaliase physisch einmal zählen. 48 Float64 je Frame
(384 Nutzdatenbytes), gleiche Basisspeicherzählung, Eingangsframe separat.
Genau eine 416-Byte-Bank: 192 Zellenbytes (6×32), 16 Zielheader,
96 Ticketeinträge, 96 temporäre Updatepaare, 16 Steuerung. Kein zusätzlicher
Verlauf oder Zähler im Produktionsarm. Zusatz-Python-Heap höchstens16.384Byte,
Receipt höchstens16.384Byte, transientes UTF-8 höchstens32.768Byte.
Originalunion, gültige Zellen, temporärer Peak, Receipts und Ausgaben tatsächlich
je Arm berichten; gleiche Limits sind kein Nachweis gleicher tatsächlicher
Gesamtnutzung. Gemeinsame Basisobjekte/Framepayload und Beobachterkosten separat
ausweisen, keine verdeckte Entlastung durch Beobachterhalter.

64×1.040=66.560 Quellenframes, 133.120 Produktionsarm-Aufnahmen;
zusätzlich 133.120 unabhängige Referenzfortschreibungen separat bilanzieren.
33.216 bewertete G-Ziele je Arm insgesamt, davon16.384 Y-Ziele je Arm.
Je Primärkontrast:3.072 stabile bzw.1.024 frühe Wechselziele je Arm.

Bestehende Gesamtgrenzen:3.600s, Worker3.540s, Abschlussreserve60s;
Export64MiB einschließlich bis8MiB Vorbereitung und1MiB Abschlussreserve.
Exklusive Zielordner; kein Überschreiben, Wiederaufnehmen oder automatischer
Neustart. Quellen je≤32KiB (64=2MiB); komprimierter Paarexport je≤512KiB
(64=32MiB), expandiert je≤4MiB; Verwaltung/Auswertung≤1MiB. Maximal44MiB
einschließlich Vorbereitung/Abschluss, innerhalb64MiB. Vollständige Reihen
und Lebenszyklusbelege dürfen kompakt referenziert, aber nicht weggelassen
werden. Kein Abschneiden von Fällen, Zielen oder Hypothesen bei Überlauf.
Bei Grenzverletzung terminaler Fehlerabschluss mit vorhandenen Belegen,
keine Nutzenbewertung. Export und Referenzspeicher sind externe Kosten,
keine heimliche zusätzliche Produktionsmemory.

## Neutrale Qualifikation und spätere Startbedingungen

Nur nach gesondertem Entwicklerauftrag, vor realer Materialisierung:

- Q1: getrennte unabhängige Referenzen für U/L; L nur letzte gültige Paare,
  U unveränderte alpha-Reihenfolge, exakte Auswahl einschließlich Gleichständen.
- Q2: reguläre Kandidatenkonkurrenz, Warmwerden, Bestätigung, Promotion,
  Zellmitnahme und Verdrängung; alle maximal sechs berechtigten Zellen,
  verlorene Generationen, kalte Konkurrenz, atomare Updates/Bereinigung.
- Q3: Ereignisgleichheit und Kausalität, Ausgabe vor Ziel, alle ungewählten
  Hypothesen bewertet, keine Rückfüllung und kein Beobachterzugriff.
- Q4: Masken/Primärzahlen, gepaarte Cluster, Quantilgrenzen, gerichtete Urteile
  gegen unabhängig vorgegebene kleine Handtabellen; fehlende Ziele/Cluster
  und nur sekundärer Gewinn dürfen keinen Primärerfolg erzeugen.
- Q5: Startbindung, Quellenzugangssperre, exklusive Exporte, Crash/Abbruch,
  Zeit-/Speicher-/Dateigrenzen und neutraler vollständiger Größenablauf.

Für den Größenablauf ausschließlich ein technisches periodisches Muster
(A,A,B,Z,B,B,A,Z), modulo8 über b und r versetzt; keine Hash-Forschungsziehung,
keine S/W-Nutzeninterpretation. Ein Paket umfasst die begrenzten Q1–Q5 und
höchstens einen vollständigen neutralen Größenablauf; dessen Artefakte samt
Code/Bindung müssen in8MiB Vorbereitung passen. Zusätzliche breite Wiederholung
wird nicht durch diesen Vertrag autorisiert. Kleine Fehlerkorrekturen gehören
zum später konkret beauftragten Entwicklungspaket und sind offenzulegen.
Die bereits bestandenen Vierfälle bleiben historische Belege; sie werden
nicht als neue Forschungsserie oder zusätzliche Nutzenstichprobe wiederholt.

Nach technischer Abnahme: genaue Code-/Runtime-/Rezept-/Auswertungsbindung,
neutrale Ressourcenbelege und exakte Aufruf-/Exportbindung vorlegen. Erst eine
separate ausdrückliche Einmallauffreigabe erlaubt die64 Forschungsquellen und
128 Arme. Vorbereitung und Ausführung dürfen keine Vertragsparameter ändern.

## Anschlussentscheidung

Der Vertrag ist konzeptionell vollständig spezifiziert. Empfehlung: Projektleiter
prüft diese eine Vorregistrierung und beauftragt gegebenenfalls Implementierung
und neutrale Qualifikation. Eine reale Nutzenprüfung bleibt separat geschlossen.
Keine Aussage, dass U gewinnen wird; mittlerer Nutzen ist offen.
