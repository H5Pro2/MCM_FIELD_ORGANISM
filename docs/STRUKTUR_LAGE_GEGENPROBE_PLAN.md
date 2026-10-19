# Begrenzte Struktur-/Lage-Gegenprobe

Status: ausschließlich statisch geplant, keine Quellen erzeugt oder analysiert.
Der Detailvergleich bleibt geschlossen. Keine neue Laufnummer, kein Tracker,
keine Memory-/Feldintegration. Gates False; ME/MI gesperrt.

## Konkrete Lücke gegenüber LV/LX

LV untersuchte Anordnungen zweier Quadrate unter Lage-, Größen- und
Kontrastvariation; LX ergänzte maskenkonditionierte Projektion. Die bessere
Zentroidzuordnung beantwortet nicht, ob die vorhandene Ganzbildprojektion
eine verschobene Struktur von einer veränderten Struktur unterscheidet,
während ein anderer räumlicher Anteil im Bild unverändert stehen bleibt.

Genau diese fehlende Freistellung wird geprüft: gleiche neue Geometrien auf
gleichmäßigem Hintergrund als Anschlusskontrolle, daneben dieselben auf
einem feststehenden Muster. Keine Objektmaske, kein Ausschnitt, keine
Korrespondenz aus Generatorrollen. Das ist weiterhin ein synthetischer
Bildvergleich, kein Nachweis für das reale Video oder beliebige Hintergründe.

## Vorab festgelegte Quellen

14 getrennte RGB8-Quellen, jeweils 1920×1080, RGB-Kanalreihenfolge, keine
Kompression, Skalierung, Antialiasing, Zufallszahlen oder Rundungsoperationen
bei der Erzeugung. Koordinaten ganzzahlig; Rechtecke links/oben inklusive,
rechts/unten exklusiv. Ein Frame entsteht in genau dieser Reihenfolge:

1. Hintergrund H0: überall RGB (24,24,24).
2. Nur bei H1: darüber RGB (48,48,48) in Rechtecken
   [320,0,400,1080] und [0,270,1920,330]; Überlappung wird gleich überschrieben.
3. Vordergrund RGB (216,216,216), vereinigte Rechtecke ohne Addition:
   Form A: [0,0,480,90] und [195,90,285,360];
   Form B: [0,0,90,360] und [90,135,480,225].
   Alle Vordergrundkoordinaten werden um die nachstehende Position verschoben.

Positionen P0=(640,405), P1=(720,405), P2=(640,465). Kein Clipping.
Gleiche Vordergrundfarbe und Pixelanzahl beider Formen verhindern einen
Vergleich allein über den Gesamtpegel; die Anordnung ist unterschiedlich.
Die Projektion erhält weder diese Aussage noch Rechtecke oder Positionen.

Quellenreihenfolge q01…q12: H0 vor H1, darin A vor B, darin P0,P1,P2.
q13 ist eine getrennte Exaktkopie von q01; q14 von q07. Identitäten und
Zeitbindungen bleiben getrennt. Keine weiteren Quellen oder Ersatzfälle.
Bei einer späteren Bindung erhält qNN Frameindex NN−1 und rationalen
Zeitpunkt (NN−1)/30 Sekunden. Diese Reihenfolge ist nur administrativ,
kein beobachteter Bewegungsverlauf und kein funktionaler Projektionseingang.

Vor einer späteren Analyse sind sämtliche Rezepte, Reihenfolge, Bytehashes,
Profil-/Code-/Umgebungsbindungen zu versiegeln. Ausführungswurzel enthält
nur Quellen und technische Bindungen; Bewertungswurzel enthält nachstehende
Rollen, Paare und Kriterien. Keine Quellenwahl nach Messergebnissen.

## Unveränderte Ansichten und Paarliste

`LocalChannelGridReceptor` aus `mcm_field_organism/finite_video_path.py`:
12×8×3, 288 Werte. Genau einmal pro Quelle analysieren.
`project_pose_form` aus `tools/_s2lv_private_pose_form_projection.py`:
vorhandene POSE_V1 und FORM_DESCRIPTOR_12X12_V1 aus genau diesen Werten.
Keine neue Hintergrundbereinigung: die vorhandene Randmedian-/Aktivitäts-
rechnung bleibt einschließlich ihrer Grenzen unverändert. Keine Zielmaske.

Je Hintergrund und Referenz A/P0 beziehungsweise B/P0 werden genau fünf
gerichtete Paare gebunden: Referenz gegen dieselbe Form an P1 und P2 sowie
gegen die andere Form an P0,P1,P2. Zusammen 20 Paare. Dazu ausschließlich
q01→q13 und q07→q14: insgesamt 22. Keine volle Paarmatrix.

Je Paar getrennt:

- Rohsicht: `sum(abs(q[i]-r[i]) for i in range(288))/288`.
- Form: dieselbe aufsteigende Binary64-Reihenfolge über 144 Werte, geteilt
  durch 144. Kein Zusammenmischen beider Skalen, kein Abstand über Pose.
- Posewerte vollständig beschreibend speichern; keine Identitätsentscheidung
  aus Schwerpunkt oder Bounding Box.

Direktnachrechnung mit eigener Schleife, ohne produktiven Distanzhelfer.
Einzelterme und Wertebindungen erhalten. Bestehende interne Formvalidierung
bleibt bestehen; sie ist keine nachträgliche Vergleichstoleranz.

## Falsifizierbare Kriterien

Für jeden der vier Referenzfälle (H0/H1 × A/B) und jede Ansicht getrennt:
`max(Distanz zu gleicher Form an P1,P2) < min(Distanz zu anderer Form an P0,P1,P2)`.
Das bindet Beziehungserhaltung und Strukturunterscheidung gemeinsam. Ein
bloß unterschiedlicher Vektor besteht nicht. Gleichstand besteht nicht.
Vier Kriterien pro Ansicht, acht insgesamt, H0 und H1 getrennt berichten.

Zusätzlich je Referenz und verschobener Position P1/P2 die gepaarte Kontrolle:
Distanz zur gleichen verschobenen Form strikt kleiner als zur anderen Form
an genau dieser Position. Acht Kriterien pro Ansicht, 16 insgesamt. Diese
Einzelbefunde ersetzen kein nicht bestandenes Gesamtkriterium.

Zwei Exaktpaare müssen rohe und Formwerte bitgleich und beide Distanzen null
liefern. Posegleichheit separat bestätigen. Exaktkontrollen zählen nicht als
Variationsbeleg. Primär- und Direktwerte müssen bitgleich sein; Abweichung
ist ein technischer Fehler, kein fachliches negatives Ergebnis.

Für jedes Gesamtkriterium den vorzeichenbehafteten Trennrand
`min_andere - max_gleiche` berichten, ohne daraus eine Annahmeschwelle
abzuleiten. Formgewinne und Formverluste gegenüber Rohsicht einzeln ausweisen.
Keine Gesamtmittelung, die H1-Verluste mit H0-Erfolgen verdeckt.

Eine durch den bestehenden Projektor ausdrücklich abgewiesene fehlende
Formaktivität wird als fehlende Formevidenz mit festem Nenner erhalten,
nicht durch Ersatzwerte repariert. Andere technische Fehler bedeuten Stopp.

## Endliches Arbeitsbudget für eine spätere Freigabe

- 14 Frameerzeugungen und 14 Rezeptoraufrufe, 14 bestehende Formprojektionen.
- Höchstens ein vollständiger RGB-Frame im Arbeitsschritt; 6.220.800 Byte
  Rohinput pro Frame. Keine Rohbildliste im Arbeitsspeicher.
- 4.032 rohe und 2.016 Formwerte plus 14 native Posebelege.
- 22 Paare × (288+144) × zwei Rechnungen: maximal 19.008 Band-/Formdifferenzen.
- 24 Ordnungskriterien aus gespeicherten Distanzen, keine neue Paarrechnung.
- Exaktkontrollen: zwei Paare × 432 Wertgleichheiten, unabhängig nochmals
  864 Gleichheitsprüfungen: insgesamt höchstens 1.728; native Posepayloads
  separat vergleichen.
- Eine unabhängige Offline-Verifikation: höchstens 19.008 gespeicherte Terme
  prüfen, ohne erneute Differenz-, Rezeptor- oder Projektionsberechnung;
  höchstens 88 Summen und 24 Ordnungsergebnisse kontrollieren. Arbeit separat
  protokollieren, nicht dem primären Differenzbudget zuschlagen.
- Gesamtbeleg höchstens 1.048.576 Byte, Metadaten 65.536 Byte,
  Verifikation 262.144 Byte, aktive Gesamtbilanz 4.194.304 Byte.
  Vor Implementierung/Ausführung müssen transitive Quellen, Qualifikation,
  Abschluss und Fehleralternativen konkret gemeinsam hineinpassen. Diese
  Planobergrenzen sind keine bereits gemessene Hüllenbilanz und keine
  Freigabe, bestehende engere Klassenlimits zu erhöhen.

## Entscheidung nach einem späteren Befund

H0-Erfolg allein wiederholt die begrenzte Tragfähigkeit der Formnormalisierung.
H1-Erfolg würde diese nur auf den hier festgelegten Hintergrund erweitern.
H1-Verlust trotz H0-Erfolg wäre ein konkreter Hinweis auf fehlende räumliche
Trennung im Ganzbildansatz, noch keine Begründung eines bestimmten Segmentierers.
Scheitern beider Ansichten begründet keine Schwellen- oder Quellenanpassung.

Auch vollständiges Bestehen beweist weder Objektidentität noch zeitliche
Korrespondenz oder sichere Lernbindung. LV/LX/LY und MQ werden nicht erneut
ausgeführt. Kein neuer Tracker, keine neue Memoryebene, kein automatischer
Folgeversuch. Jetzt endet der Auftrag mit diesem Plan.
