# Unterschiedlich starke Rückmeldungen: erreichbare historische Auswahlwirkung

2026-10-04. Ausschließlich analytische Vorprüfung nach Projektleiterauftrag.
Keine Implementierung, keine Quellenmaterialisierung, keine Tests oder
Forschungsdurchläufe. Der große U/L-Vergleich auf LZ1 bleibt geschlossen.

## Ergebnis und genau ein Ansatz

Zwei regulär erhaltene Originalnachfolger A und B bleiben unverändert.
Eine zusätzliche Zielbeobachtung Z liegt zwischen A und Persistenz.
Zwei Vorgeschichten mit identischem letztem Feedback und aktuellem Hinweis
führen bei U zu verschiedenen Ausgaben, bei L zur gleichen Ausgabe.
Dies ist eine exakte historische Wirkung, kein Rundungseffekt und noch kein
Nutzenbeleg. Eine zusätzliche Kandidatenspur wird ausdrücklich mitgezählt.

Für j=0,...,47 sei V(x)[j]=x+j/4096. Definiere
H1=V(1/8), H2=P=V(1/2), A=V(1/4), B=V(3/4), Z=V(3/8).
Ein reguläres Vierframesegment T(Y) lautet [H1,H2,Y,H1].
Alle Profile, Eigentümer, Streamdaten und Zeitabstände sind innerhalb einer
Geschichte konstant; Ordinale streng fortlaufend, Segmentgrenzen alle vier
Frames. Keine Phasen-/Fortsetzungslabels gehen als Systemeingang ein.
Die Buchstaben sind ausschließlich analytische Bezeichnungen für Framewerte.

Beide analytischen Geschichten bestehen aus:

| Teil | Geschichte I | Geschichte II |
| --- | --- | --- |
| Reguläres Aufnahmepräfix, Frames 1–16 | T(A),T(A),T(B),T(B) | identisch |
| Ältere Rückmeldung, Frames 17–20 | T(A) | T(B) |
| Letzte Rückmeldung, Frames 21–24 | T(Z) | T(Z) |
| Aktueller Hinweis, Frames 25–26 | H1,H2 | H1,H2 |

Die interessierende, vor Zielkenntnis eingefrorene Prognose gilt Frame 27.
Die letzte Y-Rückmeldung an Frame 23 ist identisch. Auch die dazwischenliegende
reguläre Gerüstrückmeldung an Frame 25 ist in beiden Geschichten identisch
(H1); sie aktualisiert keine A/B-Y-Zelle. Der gesamte letzte abgeschlossene
Vierframeblock und der aktuelle Zweiframehinweis sind damit identisch.

## Lebenszyklus: keine frei gesetzten Zellen

Aus CandidateTwoArm.close_segment und PerceptionRecencyArm.close_segment:

1. T(A) wird an Frame 4 Kandidat, die zweite vollständige disjunkte Aufnahme
   bestätigt ihn an Frame 8 durch Promotion in den ersten Retained-Platz.
2. T(B) wird an Frame 12 Kandidat, die zweite Aufnahme promoviert ihn an
   Frame 16 in den zweiten Retained-Platz. Keine Verdrängung.
3. Die A-Y-Zelle erhält an 7,11,15 die Kontextfehler 0,1/2,1/2,
   jeweils mit Persistenzfehler 1/4. Daraus entsteht EC_A=3/8, EP_A=1/4.
   Die B-Y-Zelle erhält erstmals an 15 (0,1/4). Direkte Promotion übernimmt
   die vorhandene Bewertung unverändert; kein künstliches Initialisieren.
4. An Frame 19 erhalten beide erhaltenen Y-Hypothesen Feedback, auch die
   nicht gewählte. T(A) bzw. T(B) bestätigt an Frame 20 ausschließlich eine
   vorhandene Spur. Originalframes, Generationen und Fehlerzellidentitäten
   bleiben erhalten. Die Aktualitätsreihenfolge unterscheidet sich danach;
   sie ändert hier weder die strikte Auswahlregel noch verursacht sie eine
   Verdrängung. Die Mengen der Originalidentitäten sind in beiden Geschichten
   gleich, nicht sämtliche Metadaten.
5. Beim Hinweis an 21/22 existiert noch kein Z-Kandidat. Nur A und B sind
   für Ziel 23 eingefroren. Beide erhalten die tatsächliche Z-Rückmeldung,
   mit jeweils eigenem Kontextfehler und identischem Persistenzfehler.
6. Erst nach Aufnahme des vollständigen T(Z) entsteht an Frame 24 ein neuer
   Kandidat mit Originalframes 21–24. Er ist weder gleich A/B noch bereits
   bestätigt: keine Promotion, keine Verdrängung der beiden Retained-Spuren.
7. Beim Hinweis 25/26 werden A, B und der Z-Kandidat regulär gefunden.
   Der Z-Kandidat ist kalt: Er existierte beim Freeze für Ziel 23 noch nicht
   und erhält kein rückwirkendes Feedback. Er bleibt vollständig im Ticket,
   ist aber gemäß unveränderter Regel noch nicht auswählbar. Kein Treffer
   wird abgeschnitten. Es konkurrieren genau zwei warme Originalnachfolger.

Die Gerüsthinweise [Y,H1] entsprechen höchstens Offset 2 vorhandener Spuren
und haben keinen Nachfolger; sie erzeugen keine zusätzlichen Y-Updates.
Durch den identischen, nicht konstanten j/4096-Anteil passen die Skalierungen
1/2 und 2 nicht auf den aktuellen exakten Zweiframehinweis. A/B/Z treffen
an Offset 0 mit factors=[1.0], nicht an anderen fortsetzungsberechtigten Offsets.

Speicherumfang bleibt im vorhandenen Rahmen: acht Retained-Originalframes,
vier Kandidatenframes nach Frame 24 sowie die regulären aktuellen/formenden
Halter. Kein zusätzlicher History-Puffer; eine 416-Byte-Bank, gleiche maximal
sechs Zellen und dieselben 18-Originalframe-/2-Ausgabe-Grenzen. Dies ist eine
statische Einordnung, keine neue Heapmessung. Ein offenes Ticket hält weiterhin
seine Originale bis Feedback/Bereinigung. Es gibt keinen externen Schutz der
beiden Retained-Spuren und keine unterdrückte reguläre Aufnahme.

## Exakte Rechnung

mae48 ist hier jeweils der skalare Abstand; alle Komponentenabstände,
48-fachen Summen, Halbierungen und angegebenen Werte sind exakt binary64-
darstellbar. Die bestehende Operationsfolge .5*old + .5*error liefert daher
dieselben Brüche. Alpha, Auswahl, Abruf und Speicherlayout werden nicht verändert.

| Zustand/Feedback | EC_A | EC_B | gemeinsames EP |
| --- | ---: | ---: | ---: |
| Nach Präfix, beide Geschichten | 3/8 | 0 | 1/4 |
| I: nach A an Frame 19 | 3/16 | 1/4 | 1/4 |
| II: nach B an Frame 19 | 7/16 | 0 | 1/4 |
| Sofortfehler auf Z an Frame 23 | 1/8 | 3/8 | 1/8 |
| I: nach Z, vor Prognose 27 | 5/32 | 5/16 | 3/16 |
| II: nach Z, vor Prognose 27 | 9/32 | 3/16 | 3/16 |

U wählt ausschließlich das eindeutige negative Minimum von EC−EP:

| Geschichte | d_A | d_B | Z-Kandidat | U-Ausgabe |
| --- | ---: | ---: | --- | --- |
| I | −1/32 | 1/8 | kalt | A |
| II | 3/32 | 0 | kalt | P |

L speichert in beiden Geschichten nach dem identischen Z-Feedback die
Sofortfehler EC_A=1/8, EC_B=3/8, EP=1/8. Daher d_A=0 und d_B=1/4:
in beiden Fällen P. Die kalte Z-Konkurrenz bleibt auch bei L ausgeschlossen.
Der Unterschied U(I)=A gegenüber U(II)=P stammt aus dem älteren Feedback
an Frame 19; dieselbe letzte Rückmeldung und derselbe Hinweis reichen zur
Bestimmung von U nicht aus. Die Recency-Reihenfolge liefert keinen Tie-Break.

Der Mechanismus wird verständlich über die Fehlerdifferenzen: Beim Z-Feedback
ist A gegenüber P genau gleich gut (d=0). Dieses schwache Feedback löscht eine
ältere negative EMA-Differenz nicht, sondern halbiert sie. L vergisst sie.
Bei B ist das letzte Feedback ungünstig; in Geschichte II hebt es dessen
älteren Vorteil genau auf. Keine frei gewählte Fehlerzelle ist erforderlich.

## Möglicher Vorteil und möglicher Nachteil

Für dieselbe bereits eingefrorene Prognose in Geschichte I sind zwei nächste
reguläre Zielwerte möglich, die den Armen vorher nicht bekannt sind:

| Tatsächliches Ziel 27 | U(I)=A: MAE | L(I)=P: MAE | Wirkung der älteren Erfahrung |
| --- | ---: | ---: | --- |
| A | 0 | 1/4 | Vorteil 1/4 |
| B | 1/2 | 1/4 | Nachteil 1/4 |

Beide Fortsetzungen können anschließend mit H1 zum normalen Vierframeblock
abgeschlossen werden. A/B bestätigt eine erhaltene Spur und verdrängt keine.
Der Z-Kandidat erhält beim Feedback an 27 erstmals eine Bewertung; das ändert
die schon eingefrorene Vorhersage nicht. Bei längerem Weiterbetrieb würde er
allerdings als dritte warme Hypothese mitwirken. Bei Wiederholung von T(Z)
könnte er promovieren und eine erhaltene Spur verdrängen. Deshalb belegt dieses
Beispiel ausdrücklich nur den beschriebenen endlichen Entscheidungspunkt;
es ist kein Vertrag für einen unverändert zweihypothesigen Dauerbetrieb.

Es ist keine Häufigkeit für die beiden möglichen Ziele vorgegeben. Deshalb
folgt weder ein erwarteter Nettonutzen noch eine Anpassungsleistung aus dem
Beispiel. Die historische Wirkung kann helfen oder schaden.

## LZ1-Grenze und Anschluss

Der LZ1-Vorteil gegenüber Persistenz bleibt gültig. Auf der LZ1-Quelle belegt
er jedoch keine zusätzliche reguläre Auswahlwirkung länger zurückliegender
Erfahrung: U entscheidet dort wie das Wiederholen der zuletzt beobachteten
Fortsetzung, abgesehen von numerischen Grenzfällen. Die abgenommene U/L-
Vorprüfung und der geschlossene große Vergleich werden dadurch nicht revidiert.

Hier ist ein erreichbarer Unterschied mit schwächerer letzter Rückmeldung
analytisch nachgewiesen. Empfohlener nächster Schritt beim Projektleiter:
dieses eng begrenzte Beispiel fachlich abnehmen und gegebenenfalls ausschließlich
eine kleine neutrale Lebenszyklusprüfung beauftragen, die Z-Kaltstatus,
Originalidentitäten und die beiden Entscheidungen kontrolliert. Noch keine
Quellenserie oder Vergleichshülle; vor einem längeren Vergleich wäre der Einfluss
des anschließend warmen Z-Kandidaten gesondert konzeptionell zu schließen.

Gelesene Codegrundlagen:
[Aufnahme/Promotion](../tools/_s2uc_four_arm.py),
[Bestätigung/Aktualität](../tools/_s2uc_perception_recency.py),
[Abruf](../tools/_s2uc_factor_hint.py),
[Hinweis vor Aufnahme](../tools/_s2uc_pair_context_adapter.py),
[Fehlerfeedback und Auswahl](../tools/_s2uc_multi_error.py).
