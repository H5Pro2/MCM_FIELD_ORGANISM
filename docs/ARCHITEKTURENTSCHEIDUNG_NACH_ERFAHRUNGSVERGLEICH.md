# Architekturentscheidung nach dem Erfahrungsvergleich

19.09.2026, ausschließlich statische Einordnung vorhandener Belege.
Bezug: `experience-comparison-real-20260919-01`, unverändert geschlossen:
**0 Gewinne, 0 Verluste, kein nachgewiesener Abrufvorteil**.
Repository-Bezug `537109994cf777f8d36cda617aafe12226806c25` und laufgebundenes
[Quelleninventar](../reports/experience-comparison-qualification-20260919-01/inventory.json).
Keine neue Implementierungs- oder Versuchsfreiheit.

## Welche Information ankommt

Audio liefert 48 logarithmisch verteilte spektrale Betragsmerkmale eines
100-ms-Fensters: Hann-Fenster, FFT-Beträge und gewichtete quadratische
Zusammenfassung je Band; anschließend feste NJ-Halbierung. Es sind keine
Quellen-, Objekt- oder Folgenkennungen. FFT-Phasen werden nicht ausgegeben
([Rezeptor, Zeile 128](../mcm_field_organism/log_spectral_receptor.py#L128)).
Der Abruf sieht nur die gebundenen 24 Bänder, nicht den vollständigen Verlauf.

Video liefert 288 normalisierte lokale RGB-Mittelwerte auf einem 12×8-Raster,
keine Objektkonturen, Bewegungszuordnung oder zeitliche Korrespondenz
([Rezeptor, Zeile 191](../mcm_field_organism/finite_video_path.py#L191)).
Der Hinweis verwendet die feste Teilansicht mit 32 beobachteten Komponenten.
Zwischen den ausgewählten Zeitstellen fehlt MCM Wahrnehmung; Decoderfortschritt
ist keine zusätzliche Memoryerfahrung. Diese konstruktiven Informationsgrenzen
sind belegt. Dass gerade sie die vier Fehlstellen verursachen oder zusätzliche
Merkmale sie beheben würden, ist dagegen nicht nachgewiesen.

## Was gespeichert bleibt

B4 hält begrenzt einzelne AV-Spuren, Fast gemeinsame AV-Prototypen, Slow
modalitätsgetrennte Prototypen. MATCHED schreibt Fast und PPB gewichtet fort;
Support sättigt, die Aktualisierung geht weiter
([Fast, Zeile 1635](../mcm_field_organism/_tspm1_private.py#L1635),
[PPB, Zeile 618](../mcm_field_organism/_ppb1_reference.py#L618)).
Ein Prototyp erhält nicht alle beitragenden Erfahrungen als getrennte abrufbare
Inhalte. Die ausführliche Herkunftskette im Beleg ist keine zusätzliche
operative Memory und darf nicht als verstecktes Zielwissen verwendet werden.

Im gespeicherten Vergleich sind die älteren B4-Zielspuren an den Kontrollstellen
nicht mehr als reine Zieltreffer verfügbar. Erfahren treffen jeweils neun andere
B4-Spuren sowie ein Fast- und ein auditiver Slow-Prototyp mit gemischter
Zielbeteiligung. Frisch treffen drei beziehungsweise zehn Kandidaten anderer
Fensterherkunft. Das belegt Verdrängung und Zusammenführung unter den bestehenden
Regeln, nicht die Speicherung oder Nichtexistenz eines semantischen Videoobjekts.
Vollständige Slot-/Updateketten stehen in der unveränderten
[Auswertung](../reports/experience-comparison-real-20260919-01/evaluation.json).

## Warum keine eindeutige Ausgabe entsteht

Mehrere Treffer innerhalb einer A-Bank begründen interne Mehrdeutigkeit;
die öffentliche Entscheidung enthält sich auch bei einem anwendbaren B-Slot
([A-Auflösung, Zeile 717](../tools/_s2kz_private_auditory_partial_cue_retrieval_336.py#L717),
[Entscheidung, Zeile 753](../tools/_s2kz_private_auditory_partial_cue_retrieval_336.py#L753)).
Das erklärt die beiden auditiven Enthaltungen konkret. Mehr Kandidaten im
erfahrenen Arm erzeugen keinen zusätzlichen öffentlichen Verlust, weil schon
der frische Arm mehrdeutig war. B-Vorrang wäre keine aus diesem Befund
begründete Korrektur: Zielbeteiligung des gemischten Prototyps genügt nicht.

Visuell findet keiner der Arme einen anwendbaren Kandidaten. Damit scheitert
bereits die Anwendbarkeit, nicht erst eine Rangwahl. Ob hauptsächlich
Prototypänderung, begrenzte Spurenerhaltung oder die feste Bildrepräsentation
maßgeblich ist, isoliert dieser Lauf nicht. Keine dieser Vermutungen wird
nachträglich zur diagnostizierten Hauptursache erklärt.

## Entscheidung

### Geschlossener S2-SFA-Methodenversuch

Der private Methodenversuch
[`s2sfa-visual-method-20260919-01`](../reports/s2sfa-method-real-20260919-01/REPORT.md)
vergleicht eine lineare SFA-Projektion mit der bestehenden Rohbaseline auf drei
positionsveränderten visuellen Farbmustern. Beide Arme ordnen `QA`, `QB` und
`QAB` korrekt zu. Es gibt weder zusätzliche korrekte Zuordnungen noch Verluste
oder Verwechslungen.

Die Rohbaseline erreicht damit auf diesem kleinen Bestand bereits die maximale
Trefferzahl; ein zusätzlicher SFA-Nutzen ist nicht nachgewiesen, eine
Unterlegenheit von SFA aber ebenso nicht. Die vorhandenen 288 lokalen
Rezeptorwerte reichen für diese konkrete Farbmusterzuordnung aus. Daraus folgt
weder eine Erklärung für frühere Video-Abrufgrenzen noch allgemeine
Formerkennung. Geringere zeitliche Veränderung allein ist kein Nutzenbeleg.

SFA wird nicht in Feld oder Memory integriert. Es werden weder schwierigere
Quellen nachgeschoben noch Parameter optimiert. Die Frage, wo bestehende
Speicherung oder Abrufregel nutzbare Information verliert, bleibt davon
getrennt und begründet keinen automatischen Folgeauftrag.

**Entwicklungspause für den Ausbau dieses Video-Abrufpfads empfohlen.**
Aus den Belegen lässt sich derzeit kein einzelner Änderungsansatz mit konkreter,
falsifizierbarer Aussicht auf besseren Zielabruf begründen. Daher kein neuer
Algorithmus, kein weiterer Parametersuchlauf und keine neue Vertragsserie.
Die technische Aufnahme, begrenzte Speicherung und korrekte Enthaltung bleiben
bestätigt; allgemeine Untauglichkeit jeder MCM-Architektur folgt daraus nicht.

Eine spätere Wiederaufnahme müsste zuerst eine beobachtbare Information benennen,
die richtige Zielbezüge von den belegten Konkurrenten unterscheidet, ohne
Auswertungsherkunft als operativen Eingang zu verwenden. Erst ein solcher
begründeter Ansatz wäre gegen den unveränderten heutigen Pfad als einfache
Baseline prüfbar. Kein zusätzlicher richtiger Zielabruf oder neue falsche
Zuordnungen wären Gegenbefunde, nicht Anlass zur nachträglichen Anpassung.
Das ist eine Entscheidungsvoraussetzung, kein neuer Prüfplan und keine Freigabe.

Historische Ergebnisse, Gates False, ME/MI-Sperre und ruhender Prognosezweig
bleiben unverändert. Keine Berechnung, Tests oder erneute Verifikation.

## Nachtrag: Erhaltung und Konsolidierung einer unterscheidbaren Erfahrung

Dieser Nachtrag ist eine statische Entscheidung anhand der gespeicherten
e03--e14-Übergänge des Erfahrungsvergleichs. Er autorisiert keine Änderung.

### Belegter Engpass

Die visuelle Zielspur entsteht bei e03 als B4-Generation in `b4.slot.002` und
als visuelle PPB-Generation an globalem Index 21. Bis e06 enthält diese
visuelle PPB-Komponente keinen `MATCHED`-Übergang. Bei e07 wird sie ersetzt;
die direkte B4-Generation wird später bei e12 in derselben Slot-ID ersetzt.
Der gespeicherte Transaktionsverlauf lautet für Index 21: e03 `CREATED`,
e04--e06 unverändert, e07 `REPLACED`. Die frühere Bezeichnung e06 als
Ersetzungsereignis ist damit berichtigt.
Vor dem visuellen Teilhinweis e14 ist somit keine direkte Zielgeneration mehr
aktuell. Die visuelle Slow-Bank hat keinen stabilen, scanberechtigten Slot;
`ABSENT_VALID` beweist dabei nicht, dass ihre physischen Slotcontainer frei
sind. Der zugehörige [Spurenbefund](../reports/experience-comparison-real-20260919-01/VISUAL_TRACE_E14.md)
hält diese Trennung fest.

Der beobachtete Engpass ist folglich nicht ein Abruf, der eine vollständig
erhaltene direkte Zielspur falsch auswählt. Die heutige Regel erhielt für diese
visuelle Generation vor ihrer Ersetzung **keinen `MATCHED`-Übergang unter der
gebundenen Regel**. Das ist kein Nachweis, dass die eingehenden Wahrnehmungen
keine relevante Ähnlichkeit oder Fortsetzung enthielten. Ob ein unterscheidbarer
Anteil der e03-Formation in einem aktuellen Fast-Prototyp verblieb, ist offen;
eine `MATCHED`-Herkunft wäre dafür allein kein Erhaltungsnachweis.

### Heutige Bestätigung

Die aktuelle Mechanik verarbeitet drei verschiedene Dinge nicht gleich:

- Ähnlichkeit eines einzelnen Zustands entscheidet, ob eine B4-, Fast- oder
  PPB-Operation den Kandidaten matcht, ersetzt oder neu belegt.
- Wiederholte Wahrnehmung erhöht bei einem bestehenden PPB-/Fast-Treffer den
  gesättigten Support und aktualisiert den Prototyp. Das ist eine
  zustandsbasierte Bestätigung, keine getrennte Erfahrungsspur.
- Einen zeitlichen Zusammenhang zwischen zwei Wahrnehmungen, etwa dass eine
  spätere Wahrnehmung dieselbe unterscheidbare AV-Erfahrung fortsetzt,
  verarbeitet der Memorykern nicht. Fast und PPB mitteln ihre passenden
  Zustände; sie bewahren keine abrufbare Folge einzelner Bestätigungen.

Der laufende Vergleich belegt nur die ersten beiden Formen. Insbesondere
liefert e03--e14 keine beobachtete Wiederholung der visuellen Zielgeneration,
die unter der gebundenen Regel zu `MATCHED` führt. Er beantwortet damit nicht,
ob die Wahrnehmungsfolge außerhalb dieser Regel eine relevante Fortsetzung
enthielt.

### Gegenüberstellung mit bestätigten Grundpfadbefunden

| Befund | Tatsächlich geprüft | Nicht geprüft |
| --- | --- | --- |
| S2-OB, begrenzter Aufrufereingang | Dasselbe vollständige, bytegebundene AV-Ereignis wurde viermal innerhalb einer fortgesetzten Sitzung gebildet. Fast wurde gematcht, beide PPB-Spuren erreichten Support 3; ein früher A-Abruf und spätere Stabilisierung sind getrennt bestätigt. | Varianten derselben Wahrnehmung, längere oder variable Abstände, konkurrierende Teilähnlichkeiten und ein eindeutiger B-Abruf nach A-Verdrängung. |
| S2-OA, fortgesetzter Gedächtniszyklus | Fünf vorgebundene, je viermal gleich gebildete visuelle Inhalte stabilisierten. Nach B4-Verdrängung blieb ein früher Inhalt bei q05 über seinen stabilen visuellen Slow-Slot abrufbar; später wurde seine Slow-Generation durch den fünften Inhalt ersetzt. | Wiederbegegnung einer veränderten Wahrnehmung, wechselnde oder widersprüchliche Konkurrenz während einer Wiederholung, zeitlich große Abstände und der Umgang mit Fast-Mischprototypen. |
| Erfahrungsvergleich e03--e14 | Eine einzelne visuelle Zielgeneration wurde erzeugt, dann unter der gebundenen Regel bis e07 nicht gematcht und ersetzt; e14 findet keinen anwendbaren aktuellen visuellen Kandidaten. | Ob e03 und spätere Medienwahrnehmungen außerhalb der heutigen Matchregel eine relevante Wiederholung, Variation oder Fortsetzung bilden. |

Damit ist die bestehende Fähigkeit präzise begrenzt: **Der Grundpfad kann
wiederholte, unter seinen gebundenen Regeln matchende vollständige Erfahrungen
stabilisieren und sie begrenzt gegen spätere B4-Verdrängung erhalten.** Offen
bleibt seine Eignung bei einer Veränderung oder Konkurrenz, die gerade keinen
solchen Match-Übergang erzeugt. Diese offene Differenz darf weder als fehlende
Wahrnehmungsähnlichkeit noch als bereits fehlende Speicherfähigkeit ausgegeben
werden.

### Entscheidung, Baseline und Verwerfungsbedingung

**Kein Zusatzanschluss wird vorgeschlagen oder implementiert.** Der zuvor
genannte generationgebundene Wiederbegegnungsanschluss wird zurückgestellt:
Sein zusätzlicher Nutzen gegenüber vorhandenen Generationen, gesättigtem Support
und Prototypupdates ist nicht belegt. Speichervergrößerung, Schwellenlockerung
oder Abrufänderung sind aus denselben Gründen nicht begründet.

Die faire Baseline bleibt der unveränderte Grundpfad. Erst eine spätere,
prospektiv gebundene Untersuchung müsste eine Wiederholung mit Variation und
eine konkurrierende oder widersprüchliche Wahrnehmung getrennt führen, ohne
operative Ziel- oder Quellenrollen. Sie müsste zeigen, dass eine zusätzliche
Bindung mehr erhält als die bestehenden Generationen, Support- und
Prototypupdates, ohne Konkurrenz fälschlich zu bestätigen. Bleibt dieser
Zusatznutzen aus, wäre der Anschluss verworfen. Ein read-only Abruf darf in
keinem Arm als neue Erfahrung zählen. Dies ist eine Aussagegrenze, keine neue
Versuchsfreigabe.
