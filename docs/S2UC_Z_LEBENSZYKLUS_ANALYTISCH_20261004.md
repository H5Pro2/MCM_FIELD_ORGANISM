# Warmer Z-Kandidat: analytische Übergänge 28–32

2026-10-04. Auftrag ausschließlich analytisch. Keine Adapterausführung, keine
Quellenmaterialisierung, keine Wiederholung der bestandenen Prüfung. Ausgang
sind die gespeicherten Zustände vor deren Abschlussbereinigung, nicht die bereits
geleerten Adapter. Fortsetzung ist hier eine Herleitung, kein Wiederanlauf.

## Ausgang und Auswahl für Ziel 31

Fallnamen bezeichnen ältere Rückmeldung und Abschlussziel 27. A=V(1/4),
B=V(3/4), Z=V(3/8), P=H2=V(1/2); T(Y)=[H1,H2,Y,H1].
Originale A:1–4, B:9–12, Z:21–24. Zellschlüssel (Rolle,Generation,Offset):
A=(retained,1,0), B=(retained,2,0), Z=(candidate,3,0).
Alle drei sind warm. EP_A=EP_B=7/32, aber EP_Z=1/4: Z hat eine kürzere
Bewertungshistorie. Die Persistenz-EMA darf deshalb nicht vereinheitlicht werden.

| Zustand nach 28 | EC_A | EC_B | EC_Z | d_A | d_B | d_Z | U für 31 | L für 31 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A-A | 5/64 | 13/32 | 1/8 | −9/64 | 12/64 | −8/64 | A | A |
| A-B | 21/64 | 5/32 | 3/8 | 7/64 | −4/64 | 8/64 | B | B |
| B-A | 9/64 | 11/32 | 1/8 | −5/64 | 8/64 | −8/64 | Z | A |
| B-B | 25/64 | 3/32 | 3/8 | 11/64 | −8/64 | 8/64 | B | B |

d_i=EC_i−EP_i; jeweils eindeutiges negatives Minimum. Die Auswahl hängt nicht
vom noch unbekannten Ziel 31 ab und gilt deshalb für alle drei Anschlüsse.
L verwendet die letzten tatsächlichen Rückmeldungen an 27: nach A die Paare
(0,1/4),(1/2,1/4),(1/8,1/4); nach B
(1/2,1/4),(0,1/4),(3/8,1/4), Reihenfolge A/B/Z.
Z ist uneingeschränkt wählbar und gewinnt bei U im Zustand B-A.

Frame 29 liefert zunächst die gemeinsame Gerüstrückmeldung H1 auf das noch
offene Ticket für 29. Dessen Treffer an Offset 2 waren nicht fortsetzungsberechtigt;
es gibt keine Fehlerzellupdates. Aufnahme 29/30 liefert dann den identischen
Hinweis H1,H2 und friert die drei Originalnachfolger für Ziel 31 ein.

## Zwölf Übergänge: Feedback 31 und Abschluss 32

Sofortfehler (ec_A,ec_B,ec_Z;ep) sind:

- Ziel A: (0,1/2,1/8;1/4).
- Ziel B: (1/2,0,3/8;1/4).
- Ziel Z: (1/8,3/8,0;1/8).

Alle drei lebenden eingefrorenen Hypothesen erhalten Feedback, unabhängig von
der Wahl. U aktualisiert jedes eigene Paar mit .5*alt+.5*neu; L ersetzt es
durch das jeweilige Sofortfehlerpaar. Sämtliche folgenden Werte sind exakt
dyadisch und in der vorhandenen binary64-Operationsfolge exakt darstellbar.

**Zahlen in der Spalte EC und EP sind Zähler zum gemeinsamen Nenner 128.**
Die Zellen dort gelten nach Feedback 31, vor einer eventuellen Löschung an 32.
EP nennt (EP_A=EP_B,EP_Z). Bestand ist in Aktualitätsreihenfolge alt→neu angegeben.

| Ausgang | Block | U/L für 31 | EC_A,EC_B,EC_Z /128 | EP_AB,EP_Z /128 | Aktion 32; Bestand danach |
| --- | --- | --- | --- | --- | --- |
| A-A | T(A) | A/A | 5,58,16 | 30,32 | A bestätigt; retained B,A; candidate Z |
| A-A | T(B) | A/A | 37,26,32 | 30,32 | B bestätigt; retained A,B; candidate Z |
| A-A | T(Z) | A/A | 13,50,8 | 22,24 | Z promoviert, B gelöscht; retained A,Z |
| A-B | T(A) | B/B | 21,42,32 | 30,32 | A bestätigt; retained B,A; candidate Z |
| A-B | T(B) | B/B | 53,10,48 | 30,32 | B bestätigt; retained A,B; candidate Z |
| A-B | T(Z) | B/B | 29,34,24 | 22,24 | Z promoviert, A gelöscht; retained B,Z |
| B-A | T(A) | Z/A | 9,54,16 | 30,32 | A bestätigt; retained B,A; candidate Z |
| B-A | T(B) | Z/A | 41,22,32 | 30,32 | B bestätigt; retained A,B; candidate Z |
| B-A | T(Z) | Z/A | 17,46,8 | 22,24 | Z promoviert, B gelöscht; retained A,Z |
| B-B | T(A) | B/B | 25,38,32 | 30,32 | A bestätigt; retained B,A; candidate Z |
| B-B | T(B) | B/B | 57,6,48 | 30,32 | B bestätigt; retained A,B; candidate Z |
| B-B | T(Z) | B/B | 33,30,24 | 22,24 | Z promoviert, A gelöscht; retained B,Z |

Bei T(A)/T(B) wird dieselbe erhaltene Originalspur vollständig bestätigt und
ans Ende der Aktualitätsreihenfolge verschoben. Keine Generation, Zelle oder
Originalspur wird ersetzt. Der Kandidat Z bleibt samt aktualisierter Bewertung.

Bei T(Z) bestätigt der vollständige disjunkte Block 29–32 den Kandidaten
21–24. Diese Originale bleiben erhalten; die Bestätigungsframes ersetzen sie
nicht. Z wechselt (candidate,3,0)→(retained,3,0); EC und EP werden bitgleich
mitgenommen, nicht erneut bewertet. Candidate wird leer. Verdrängt wird der
älteste Retained-Eintrag unmittelbar vor 32: nach Abschluss A an 28 ist das B,
nach Abschluss B ist das A. Die Auswahl für 31 ändert diese Reihenfolge nicht.
Die jeweilige Offset-0-Fehlerzelle wird gelöscht; allgemein löscht die bestehende
Regel sämtliche Zellen der verdrängten Retained-Generation. In diesen Zuständen
existieren keine weiteren Zellen dieser Generation. Insbesondere wird deren
eben an 31 verarbeitetes Feedback nicht übersprungen, sondern erst danach
zusammen mit der verlorenen Spur verworfen.

Für L gilt bei Z-Promotion dieselbe Identitätsmitnahme und dieselbe Löschung,
mit den gerade an 31 gespeicherten Paaren: A=(1/8,1/8), B=(3/8,1/8),
Z=(0,1/8), danach Entfernung von A oder B gemäß Tabelle.

An 32 entsteht vor Aufnahmeabschluss das Gerüstticket für 33 aus [Y,H1].
Nur Offset-2-Treffer ohne Nachfolger; es hält keine berechtigte Hypothese für
ein späteres Fehlerupdate. Die Z-Promotion an 32 kann daher kein zusätzliches
Feedback, keinen Kaltreset und keinen verlorenen Update-Schlüssel für 31 erzeugen:
das Ticket für 31 wurde bereits abgearbeitet. Ziel 33 wird hier nicht ausgeführt.

## Interpretierbarkeit und notwendige Beobachtungsgrößen

**Ja, ein längerer Vergleich ist als Vergleich der Fehlerbewertung unter einem
gemeinsamen regulären Speicherlebenszyklus interpretierbar.** Er ist kein
Vergleich mit dauerhaft genau drei identischen Hypothesen: Nach Z-Promotion
bleiben zunächst zwei erhaltene Spuren, später können neue Kandidaten entstehen.

Begründung durch gleiche Übergänge: Startbestand, Eingang und Zeitfolge sind
je U/L-Paar gleich. Aufnahme, exakte Bestätigung, Recency-Reihenfolge,
Promotion und Verdrängung lesen keine Fehlerwerte oder Auswahlentscheidungen.
Der Abruf hängt nur von Hinweis und Bestand ab. Feedback betrifft alle
berechtigten Hypothesen, nicht nur die ausgewählte. Daher bleiben innerhalb
jedes gepaarten Verlaufs Bestand, Berechtigung, Kalt/Warm-Status, Identitäten
und gültige Feedbackgelegenheiten induktiv gleich. Verschiedene Vorgeschichten
dürfen verschiedene Bestandsreihenfolgen haben; Gleichheit wird innerhalb des
U/L-Paars verlangt, nicht zwischen verschiedenen Quellenhistorien.

Der Unterschied B-A: U=Z, L=A ist zulässige Bewertungswirkung im gemeinsamen
Bestand. Unterschiedliche Zellenalter sind Teil der bestehenden U-Heuristik,
kein Ressourcenvorteil. Ein Befund wäre deshalb der Gesamtwirkung dieser
Fehlerbewertung samt regulärem Lebenszyklus zuzuschreiben, nicht isoliert einer
festen historischen Zeitspanne oder garantiert gleich zuverlässigen Schätzern.

Für einen späteren, separat festzulegenden Vergleich notwendig:

- Pro Entscheidung vollständiger geordneter Bestand, Originalordinalidentitäten,
  Rolle/Generation/Offset, Hinweise, sämtliche Treffer und Ausschlussgründe.
- Eigene EC/EP-Paare je Zelle, Warm/Kalt, gültige Feedbackzeitpunkte und
  Historienlänge; alle d-Werte, Gleichstände, Enthaltungen und eingefrorene Ausgabe.
- Feedback für alle eingefrorenen Hypothesen einschließlich nicht gewählter,
  Lebendigkeit und Update/Löschgrund; Promotion mit bitgleicher Mitnahme,
  Verdrängung samt gelöschten Zellen, keine Rückfüllung oder rückwirkende Updates.
- Ereignisweiser U/L-Abgleich des Bestands und der Feedbackgelegenheiten;
  jede Abweichung vor einem Bewertungsnutzenurteil als Integritätsproblem klären.
- Vollständige Fehler, Gewinne und Schäden auf vorab festgelegter Gesamtmenge;
  zusätzlich getrennte Abschnitte mit zwei/drei warmen Hypothesen, Kandidaten-
  Warmwerden und Promotion/Verdrängung, ohne nachträgliche Auswahl günstiger Ziele.
- Gleiche feste Speicherbudgets und tatsächliche Original-/Zellbelegung,
  transienter Speicher und Ausgaben; L darf insbesondere keine gelöschte
  Historie im Beobachter als kostenloses Gedächtnis weiterverwenden.

In B-A ergibt die analytische Ausgabe Z gegenüber A für Ziel A einen Nachteil
1/8, für Ziel B einen Vorteil 1/8 und für Ziel Z einen Vorteil 1/8. Dies sind
bedingte Einzelfehler, keine neuen Messungen und keine Verteilungsannahme.
Ein durchschnittlicher Nutzen bleibt offen.

## Anschlussentscheidung und Beleggrundlage

Lebenszyklusfrage für die zwölf angefragten Übergänge analytisch abgeschlossen.
Empfehlung an den Projektleiter: einen begrenzten Nutzenvergleich konzeptionell
vorregistrieren, einschließlich Quellenverteilung, vollständiger Zielmenge,
Unsicherheit und obiger Lebenszyklusbeobachtung. Keine weitere Regeländerung
erforderlich; noch keine Implementierung oder Ausführung daraus ableiten.

Gelesene Ausgangsdaten: events[index=28].before_cells, events[index=28].after
und letztes Forecast in den vier [belegten Fallketten](../reports/s2uc/strong-feedback-neutral-20261004-01/REPORT.md).
Bei Frame28 gibt es kein Fehlerfeedback; before_cells sind daher auch die
Zellwerte nach der dortigen reinen Retained-Bestätigung, vor Bereinigung.
Regeln: [CandidateTwoArm](../tools/_s2uc_four_arm.py),
[Recency-Bestätigung](../tools/_s2uc_perception_recency.py),
[Feedback/Promotion](../tools/_s2uc_multi_error.py).
Keine versiegelten Berichte, Messurteile oder Produktionsdateien verändert.
