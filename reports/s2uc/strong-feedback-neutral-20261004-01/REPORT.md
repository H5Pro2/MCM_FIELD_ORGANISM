# Neutrale Lebenszyklusprüfung unterschiedlich starker Rückmeldungen

2026-10-04. **PASS: vier festgelegte Fälle mit jeweils 28 Frames**, einmal
ausgeführt, 112 U-Aufnahmen und 112 unabhängige Referenzfortschreibungen.
Unveränderter U-Adapter, A1/K1 deaktiviert. Kein Produktionsarm L und keine
längere Quellenserie. [Prüfskript](check.py), [Prüfbilanz](verification.json).

## Vier Fallketten und eingefrorene Entscheidung

T(Y)=[H1,H2,Y,H1], V(x)[j]=x+j/4096 für j=0..47; H1=V(1/8),
H2=P=V(1/2), A=V(1/4), B=V(3/4), Z=V(3/8). Gemeinsames Präfix:
T(A),T(A),T(B),T(B). Danach die drei in der Tabelle genannten Blöcke.
Die Fehler beziehen sich ausschließlich auf die vorab benannte Prognose 27.

| Fallkette nach Präfix | U für 27 | L für 27 | U-MAE | L-MAE | U−L |
| --- | --- | --- | ---: | ---: | ---: |
| [T(A),T(Z),T(A)](A-A.json) | A | P | 0 | 1/4 | −1/4 |
| [T(A),T(Z),T(B)](A-B.json) | A | P | 1/2 | 1/4 | +1/4 |
| [T(B),T(Z),T(A)](B-A.json) | P | P | 1/4 | 1/4 | 0 |
| [T(B),T(Z),T(B)](B-B.json) | P | P | 1/4 | 1/4 | 0 |

Die Prognose wurde beim Hinweis 25/26 eingefroren. Der bestehende Observer
prüft vor dem Feedback, dass selected_values exakt der zuvor bestimmten
Originalfortsetzung beziehungsweise Persistenz entspricht. Die abschließenden
A-/B-Werte ändern weder die vorherige Auswahl noch deren eingefrorene Herkunft.
Nach dem Feedback wird das Ticket regulär freigegeben, nicht weiterverwendet.

## Originale, Bestätigung und Fehlerwerte

In allen Fällen bleiben A-Originale [1,2,3,4] und B-Originale [9,10,11,12]
erhalten. Vollständige Kandidatenbestätigungen an 8 und 16 promovieren diese
Originale; reguläre Bestätigungen an 20 und 28 verwenden sie weiterhin.
Der unabhängige Bestandsabgleich erfolgt bei jedem Frame, einschließlich
Reihenfolge, Generationen und Originalordinalen. Keine Verdrängung von A/B.
Der bestehende Observer prüft zusätzlich eingefrorene Originalwerte und
Ticketschlüssel gegen den Bestand und die Referenz.

Vor Ziel 27 sind die tatsächlichen U-Werte exakt:

| Vorgeschichte | EC_A | EP_A | EC_B | EP_B | Entscheidung |
| --- | ---: | ---: | ---: | ---: | --- |
| I: ältere Rückmeldung A | 5/32 | 3/16 | 5/16 | 3/16 | A |
| II: ältere Rückmeldung B | 9/32 | 3/16 | 3/16 | 3/16 | P |

Die Werte stimmen mit der analytischen Herleitung und der unabhängig
fortgeschriebenen Feedbackreferenz überein. Alle nicht gewählten berechtigten
Hypothesen erhalten ebenfalls Feedback. Keine Zelle wurde injiziert.

Z ist an 24 regulär als Kandidat mit Originalen [21,22,23,24] entstanden.
Für Prognose 27 enthält das Ticket drei berechtigte Hypothesen. Z hat
evaluation=COLD, before=null und eine leere Feedbackhistorie. Somit ist Z
vollständig berücksichtigt und ausschließlich wegen fehlender Bewertung nicht
wählbar. Beim tatsächlichen Ziel 27 sind alle drei Schlüssel lebend; Z erhält
erstmals (EC,EP)=(1/8,1/4) bei A beziehungsweise (3/8,1/4) bei B.
Seine Feedbackhistorie ist danach genau [27]. Kein rückwirkendes Update.

L wird ausschließlich im Beobachter aus den tatsächlich protokollierten
gültigen Rückmeldungen berechnet, zugeordnet über unveränderte Originallinien
über die Promotion hinweg. Die letzten Werte vor 27 stammen bei A/B beide
von Ziel 23: (1/8,1/8) bzw. (3/8,1/8); Z hat keine Bewertung.
Kein negatives Minimum, deshalb in allen vier Fällen P. L erhält weder
Zukunftsinformation noch einen Produktionsspeicher oder zusätzliche Aufnahme.

An 28 bestätigt der letzte Block eine vorhandene A-/B-Spur. Ziel 29 bleibt
zensiert. In allen vier Fällen ist die abschließende Bereinigung bestanden:
Adapter geschlossen, Bank null, eingefrorene Halter frei, Kandidat,
Retained-Bestand und forming-Bestand leer.

## Ressourcen und Grenzen der Messung

| Fall | zusätzlicher Python-Peak | Receipt-Peak | UTF-8-Obergrenze |
| --- | ---: | ---: | ---: |
| A-A | 5.852 Byte | 896 Byte | 1.792 Byte |
| A-B | 5.844 Byte | 896 Byte | 1.792 Byte |
| B-A | 5.784 Byte | 892 Byte | 1.784 Byte |
| B-B | 5.776 Byte | 892 Byte | 1.784 Byte |

Je Fall: Bank 416 Byte, höchstens zwei Ausgabeslots, konservative Originalframe-
Obergrenze 16 und kombinierte Obergrenze 18. Alle bestehenden Grenzen
(16.384 Byte Zusatzheap, 18 Originalframes, 20 kombiniert) eingehalten.
Die Nullwerte der nicht eingeschalteten Frame-Tracing-Zähler sind keine
gemessene Nullbelegung. Der bestehende Meter erfasst Zusatzobjekte und
Operationstransienten; dies ist keine Gesamtmessung von Prozess, Referenz,
Eingangsquellen oder zugrunde liegendem Frame-/Basisspeicher. Referenz und
vollständige Belegketten sind externe Beobachterdaten, keine Policy-Eingaben.
Kein Ressourcenvergleich zweier Produktionsarme wird behauptet.

## Aussage und nächster Schritt

Historische Auswahlwirkung ist in diesem neutralen Beispiel technisch bestätigt:
identischer letzter Z-Block und identischer aktueller Hinweis, aber U entscheidet
aufgrund älterer Rückmeldung unterschiedlich. Die vier gezielt ausgewählten
Abschlüsse zeigen Gewinn und Schaden; ihre ausgeglichene Summe ist kein
geschätzter Erwartungsnutzen einer Quellenverteilung.

Empfehlung an den Projektleiter: den begrenzten Mechanismusbefund abnehmen.
Vor einem längeren Nutzenvergleich zuerst konzeptionell den weiteren Lebenszyklus
des nun warmen Z-Kandidaten klären: weitere Auswahlkonkurrenz und mögliche
Promotion/Verdrängung dürfen nicht als reine Zweihypothesenwirkung behandelt
werden. Diese Prüfung startet weder einen Folgeversuch noch eine Quellenserie.
LZ1-Abnahme, deren historische Wirkungsgrenze und der geschlossene große
U/L-Vergleich auf LZ1 bleiben unverändert.
