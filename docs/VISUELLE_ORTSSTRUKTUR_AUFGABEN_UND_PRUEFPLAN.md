# Erhaltung visueller Ortsstruktur: begrenzter Aufgaben- und Pruefplan

Stand: 28.08.2026. **Nur dokumentierte Planung; keine Implementierung oder
Ausfuehrung.** Quellstand: Commit `3b05de3`. Der akzeptierte
[Funktionsbefund](../reports/tspm1_functional/functional-20260828-01/BEFUND.md)
macht B4 zur bevorzugten Arbeitsreferenz fuer die dort gepruefte Aufgabe.
TSPM-1 und PPB-1 bleiben Referenzen, ohne automatische Ersetzung oder Integration.

## 1. Frage und vorhandener Datenweg

Kann B4 die **Anordnung derselben lokalen visuellen Werte** erhalten und beim
spaeteren Abruf unterscheiden, wenn deren globale Verteilung gleich bleibt?
Untersucht werden feste Bildzellen, nicht Objekte oder Ansichtsunabhaengigkeit.

| Vorhandene Stelle | Tatsaechliche Verarbeitung und Grenze |
|---|---|
| `finite_video_path.py`, `LocalChannelGridReceptor.analyze` | Mittelt jeden der drei Kanaele innerhalb jeder Rasterzelle, normiert durch 255 und flacht in der Reihenfolge Zeile, Spalte, Kanal ab. Unterschiede innerhalb einer Zelle gehen verloren; Unterschiede zwischen Zellmittelwerten bleiben darstellbar. |
| `_ppb1_receptor_profiles.py`, `_source_configs("browser")` | Bestehendes Profil: 120 x 80 Pixel, 3 Spalten x 2 Zeilen, 30 Frames/s. Sechs Zellen mit je drei Kanaelen ergeben 18 Werte; jede Zelle ist 40 x 40 Pixel gross. |
| `receptor_contract.py`, `from_visual_receptor_state` | Uebernimmt Geometrie, geordnete `carrier_ids` und alle `channel_values` unveraendert in `ReceptorContactFrame.values`. |
| `_ppb1_active_receptor_batch_binding.py`, `_build_stream` | Prueft die genaue Geometrie und Traegerreihenfolge gegen das Profil; die Huelle behaelt die Originalframes. Keine globale Mittelung. |
| `_ppb1_reference.py` / `_tspm1_private.py` | PPB-1 speichert bzw. aktualisiert positionsweise Prototypwerte; TSPM-1 besitzt getrennte auditive/visuelle Wertetupel. Eine automatische oeffentliche Verbindung zum Feld besteht dadurch nicht. |
| `_tspm1_s2dr_private_comparison.py` | `_joint_values` und `_sequence` erzeugten bisher aus zwei Skalaren acht auditive und 18 gleiche visuelle Werte. B4 erhielt diese synthetischen Tupel direkt, nicht aus analysierten Bildern. `_advance_b4` bewahrt das Tupel; `_probe_joint_slots` vergleicht dessen Positionen. |

**Konkrete Luecke:** Nicht neue Merkmale, sondern eine private, gepruefte
Uebergabe der bereits vorhandenen ortsgebundenen Rezeptorwerte an B4.
Der kuenftige Versuch verwendet echte `analyze`-Ergebnisse kontrollierter
RGB-Arrays und `from_visual_receptor_state`, keinen direkten Ersatz durch
Sollvektoren. Keine Browser-, Kamera-, PNG-Decoder- oder Feldintegration ist
dafuer erforderlich. Die bestehende Batchbindung ist eine Quellenreferenz,
nicht ein zusaetzlich auszufuehrender Produktionsweg.

## 2. Konkrete Eingaben

Alle Bilder: `uint8`, Form `(80,120,3)`, jeder Zellblock konstant, alle drei
Kanaele gleich. Die folgenden Matrizen geben die sechs Zellintensitaeten an:

| Bild | Obere Zeile | Untere Zeile | Rolle |
|---|---|---|---|
| A | 64, 64, 64 | 192, 192, 192 | Ausgangsanordnung |
| B | 192, 192, 192 | 64, 64, 64 | Grosser Tausch: alle sechs Zellen verschieden |
| C | 192, 64, 64 | 64, 192, 192 | Kleiner Tausch: nur linke obere/untere Zelle vertauscht |

Bildpaare: **A/B und A/C**, jeweils in beiden Speicherrichtungen.
Jedes Grundbild hat pro Kanal 4800 Pixel mit Wert 64 und 4800 mit Wert 192,
also denselben Histogramm- und Mittelwert 128. Farbe und globale Helligkeit
koennen die Anordnung nicht verraten.

Toleranzvarianten: fuer jedes Bild einheitlich `delta = -8, 0, +8` auf alle
Pixelkanaele; kein Clipping. Es entstehen genau neun verschiedene Bildrezepte.
Bei gleichem Delta bleiben Verteilung und globale Helligkeit zwischen den
Anordnungen identisch. Sowohl passende als auch abweichende Anordnungen
erhalten dieselben Deltas; die Intensitaetsaenderung ist kein Antwortsignal.

Auditiver Eingang: immer acht Werte `0.0`, in der unveraenderten auditiven
Traegerreihenfolge des Browserprofils. Dies ist eine konstante synthetische
Kontrollmodalitaet, kein neuer Test des Audio-Rezeptors. Keine Lautstaerke-,
Zeit-, Bildnamen- oder Herkunfts-ID darf als Abrufmerkmal verwendet werden.

## 3. Ablauf und diagnostische Kontrolle

Vier unabhaengige Episoden: `(speichern A, abweichend B)`, `(B,A)`, `(A,C)`,
`(C,A)`. Je Episode wird aus frischem Zustand **ein** Originalbild mit Delta 0
gespeichert. Danach sechs read-only Proben in fester Reihenfolge:
Original 0, abweichend 0, Original -8, abweichend -8, Original +8, abweichend +8.
Proben duerfen weder gespeichert noch als neue Bildungsangebote verwendet werden.

Zwei Bedingungen erhalten dieselben Bilder, auditiven Werte und Budgets:

- **B4-Ort:** alle 18 Rezeptorwerte in ihrer geprueften Traegerreihenfolge.
- **B4-ohne-Ort:** je Kanal Mittelwert ueber die sechs Rezeptorzellen,
  danach an allen sechs Positionen wiederholt. Diese alleinige, deklarierte
  Ortsablation wird auf Bildungs- und Probeinput gleich angewandt. Ihr Wert
  wird gegen `global_channel_mean_baseline` des zugehoerigen Bildes geprueft.
  Es bleiben 18 visuelle Werte und dieselbe B4-Kapazitaet; kein neuer Speicher.

Die Kontrolle ist absichtlich ortsblind. Ihre Unfaehigkeit, A/B/C bei gleichem
Delta auseinanderzuhalten, ist ein diagnostischer Sollbefund, kein unfairer
Siegervergleich. Sie darf weder Bild-ID noch Originalvektor nebenher nutzen.

Fuer beide Bedingungen bleiben neun FIFO-Plaetze, Schreibregel, normalisierte
L1-Distanz, Schwelle `0.2` je Modalitaet und Tie-Regeln unveraendert.
Mit einem belegten Platz entsteht kein Tie. Slotwahl und Rueckgabe folgen
dem vorhandenen `_probe_joint_slots`; keine zusaetzliche Erkennungsregel.

## 4. Drei getrennte Pruefstellen

**Rezeptor und Uebergabe:** Der analytische Sollwert jeder Zelle/Kanalposition
ist ihre Pixelintensitaet geteilt durch 255. Maximaler positionsweiser Fehler
bis `1e-12` ist Rundungstoleranz, keine Matchschwelle. Traegerreihenfolge und
Geometrie muessen exakt dem vorhandenen Profil entsprechen. Das aus dem
Originalframe uebernommene Tupel muss exakt erhalten bleiben. Kein Sortieren,
Pooling oder Vertauschen im Ortsarm; die Kontrolltransformation bleibt separat.

**Speicherung:** Der belegte B4-Slot muss exakt dem tatsaechlich angebotenen
26-Werte-Tupel entsprechen, einschliesslich aller visuellen Positionen.
Vorher-/Nachher-Zustand, Belegungszahl, Slot und Werte werden aufgezeichnet.
Speicheridentitaet allein ist kein Erfolgsbeleg; die Werte muessen stimmen.
Bei jeder Probe bleiben Bankwerte, Belegung und Zustandsdigest unveraendert.

**Abruf:** Die drei Originalproben sollen erkannt werden und genau den
gespeicherten Originalvektor zurueckgeben, nicht den veraenderten Probevektor.
Die drei anders angeordneten Proben sollen als anderes Muster abgewiesen werden.
Gezahlt werden getrennt korrekte Wiedererkennung, Toleranztreffer,
falsche Ablehnung, falsche Gleichsetzung und falsche Rueckgabewerte.
Der externe Sollvergleich nutzt die bekannte Anordnung, nicht dieselbe
`0.2`-Schwelle, deren Eignung gerade geprueft wird.

**Wichtige statische Gegenprognose, noch kein Laufbefund:**

- Original +/-8: visuelle Distanz `8/255`, etwa `0.03137`.
- A/B: `128/255`, etwa `0.50196`, auch bei den symmetrischen +/-8-Proben.
- A/C: `256/1530`, etwa `0.16732`; mit +/-8 etwa `0.18824`.

Der vorhandene Abruf sollte daher den grossen Tausch ablehnen, den kleinen
aber trotz verschiedener gespeicherter Ortswerte noch als aehnlich annehmen.
Diese schwierigen Faelle bleiben im Plan. Ein solches Resultat waere eine
**Grenze der Abrufbewertung**, nicht automatisch ein Verlust im Rezeptor oder
Speicher. Es wird weder durch nachtraegliches Senken der Schwelle noch durch
Weglassen von C repariert. Die bestehende Darstellung kann ausreichend sein,
obwohl ihre bisherige globale Distanzschwelle die neue Aufgabe nicht erfuellt.

## 5. Endlicher Umfang und Ressourcen

Geplanter Hauptversuch: **28 Bildanalysen, acht frische B4-Zustaende, acht
Bildungsangebote, 48 read-only Proben**. Die 28 Rezeptorausgaben entstehen je
Episode aus sieben Bildern und werden unveraendert beiden Bedingungen
angeboten. Keine H1-H7-Zelle, kein TSPM-1-/PPB-1-Zustandsaufruf.

- Pro Bedingung vier Bildungen und 24 Proben; ein belegter Slot je Episode.
- Je Bank unveraendert maximal 255 logische Woerter, innerhalb der bisherigen
  Grenze 269; keine erhoehte Kapazitaet und kein Kapazitaetsdruck in dieser Aufgabe.
- Funktionale Schreibbilanz: 29 Woerter je Bildung, null je Probe;
  zusammen 232 Woerter. Initialisierung und Recorderarbeit separat erfassen.
- Eine Probe vergleicht einen 26-Werte-Eintrag: 26 funktionale L1-Terme,
  zusammen 1248. Keine Distanzberechnung zur Bildung im FIFO-Kern.
- Bestehende Obergrenzen 293 Schreibwoerter und 234 Distanzterme je Operation
  nicht erweitern. Zusaetzliche Distanz-Validierungsarbeit mitzählen;
  Rezeptorreduktion, Wertepruefung, globale Kontrollmittelung und Aufzeichnung
  separat ausweisen, nicht als kostenfrei behandeln.
- Ein Bild enthaelt 28800 Nutzbytes; es darf nur ausserhalb der Bank fuer
  Reduktion und Kontrolle gehalten werden. Bildrezepte und Eingabedigest
  genuegen als reproduzierbare Quellenbelege; kein Rohbildarchiv in B4.
  Python-RAM und reale Laufzeit sind Beobachtungswerte, keine logischen Woerter.

## 6. Wiederverwendung und kleinste spaetere Anpassung

Bestehende Rezeptorpruefungen werden nicht neu erfunden. Fuer eine spaeter
ausdruecklich freigegebene fokussierte Regression sind genau diese fuenf
unveraenderten Methoden vorgesehen (hier nur gelesen):

- `tests/test_finite_video_path.py`: `test_local_channel_contact_stays_in_its_cell_and_channel`
- gleiche Datei: `test_equal_global_means_at_different_places_remain_distinct`
- gleiche Datei: `test_state_is_immutable_and_has_no_raw_or_semantic_roles`
- gleiche Datei: `test_invalid_frame_and_geometry_domains_are_rejected`
- `tests/test_ppb1_receptor_profiles.py`: `test_all_four_profiles_bind_exact_existing_geometry`

Die alte Rezeptor-Ortspruefung benutzt ein anderes Raster; sie sichert das
Verfahren, ersetzt aber nicht die neue 3x2-Ende-zu-Ende-Pruefung. Die
Browser-/Feld-Handoff-Tests und historische Matrixlaeufe werden nicht mitgezogen.

Kleinste spaetere Implementierung: ein privater Bild-/Frame-zu-B4-Testadapter
und eine zugehoerige fokussierte Testdatei. Wiederverwendet werden
`VisualGridConfig`, `LocalChannelGridReceptor`, `from_visual_receptor_state`,
`global_channel_mean_baseline`, die vorhandenen `_B4State`-/`_FIFOEntry`-Formen,
`_advance_b4` und `_probe_joint_slots`. Der Adapter prueft Typ, Wertebereich,
Geometrie und exakte Traegerreihenfolge vor der Verkettung von acht auditiven
und 18 visuellen Werten. Quellen- und Probe-IDs bleiben nur im Protokoll.

Die bisherigen H1-H7-Wrapper und deren skalarer Erfolgsvergleich sind dafuer
nicht wiederverwendbar und werden nicht umgeschrieben oder freigeschaltet.
Der spaetere kleine Ergebnispruefer muss stattdessen die hier gebundenen
positionsweisen Sollwerte pruefen. Vorhandene lokale Dateiaufzeichnung kann
als Muster dienen; die geschlossene Plattforminfrastruktur bleibt unbenutzt.

## 7. Befund, Stopp und naechste Entscheidung

Aufzeichnen: Quellen/Konfiguration, Eingaberezepte, Laufzuordnung, jede
Rezeptorausgabe, tatsaechlicher Speicherinput, Slotwerte vor/nach Bildung,
Probeinput, Distanzen, ausgewaehlte Werte, unveraenderter Probe-Nachzustand,
Kosten und Fehler. Nach Abschluss nur Ergebnisdateien pruefen, nicht erneut
Modelle aufrufen. Vollstaendige lokale Aufzeichnung wie im akzeptierten
verhaeltnismaessigen Pruefplan; keine neue Plattformgarantie als Eingangstor.

Fachliche Verwechslungen bleiben auswertbare Ergebnisse. Technische
Herkunfts-/Reihenfolgefehler, unerlaubte Zustandsaenderung, Budgetverletzung
oder fehlende Belege stoppen; der Gesamtversuch ist dann nicht auswertbar.
Keine automatische Wiederholung, Teilfortsetzung oder nachtraegliche Anpassung.

Getrennt berichten: (1) Ortswerte im Rezeptor erhalten/verloren,
(2) korrekt an B4 uebergeben und gespeichert/veraendert,
(3) Anordnung beim Abruf korrekt unterschieden/falsch gleichgesetzt.
Die Ortsablation muss bei gleich verteilten Bildern ununterscheidbar bleiben;
ein scheinbarer Ortsvorteil dort macht den Vergleich methodisch ungueltig.

Dieser Auftrag endet beim Plan. Als naechste konkrete Freigabe ist die
begrenzte private Umsetzung samt fokussierter Pruefung dieses Umfangs zu
entscheiden, nicht eine weitere allgemeine Auditkaskade. Eine notwendige
Aenderung der Abrufregel waere erst nach getrenntem Befund zu entscheiden.
Der alte Einstieg, S2-FC, die verbrauchte 56-Zellen-Freigabe und der geschlossene
Plattformpfad bleiben gesperrt. Langzeitverdichtung, Gewohnheitsbildung,
Zeitfolgen, Semantik, Ansichtsunabhaengigkeit und Feldrueckwirkung sind nicht
Gegenstand dieser Aufgabe.
