# U/K1-Einmallauf: vollständig gültiger, fachlich begrenzter Gegenbefund

Der freigegebene Vergleich wurde genau einmal ausgeführt und mit COMPLETE
abgeschlossen. Alle24 Fälle,48 Arme und872 Ziele je Variante sind ausgewertet.
Der vertragliche Mechanismusgewinn und Gesamtnutzen sind NICHT_NACHGEWIESEN.
In T1 steigt die Anzahl lebender modaler Nachfolger mit vorherigem Feedback
nicht; sämtliche T1-Prognosefehler bleiben gleich. F1–F8 verbessern sich im
Mittel, enthalten aber Verluste und konkrete Schäden. Die Schadensgrenze ist
eingehalten. Das bessere Gesamtmittel allein erfüllt den vorab festgelegten
Nutzenvertrag nicht.

## Vier Vertragsurteile

| Urteil | Ergebnis | Entscheidender Befund |
| --- | --- | --- |
| Technik | AUSWERTBAR | Vollständiger Lauf, eigene Referenzen beider Varianten, keine Ressourcenverletzung |
| Mechanismus | NICHT_NACHGEWIESEN | U80/624, K180/624 modale Nachfolger mit vorherigem Feedback; kein strikter Zuwachs |
| Gesamtnutzen | NICHT_NACHGEWIESEN | T1-Fallmittel identisch; verlangte strikte T1-Verbesserung fehlt |
| Schaden | GRENZE_EINGEHALTEN | Schlechtester Fallmittelabstand0,001512096774 <1/32; G_w unverändert |

Die primäre Erwartung eines strikten Mechanismuszuwachses ist damit in diesem
Entwicklungsvergleich widerlegt. Die Aussage gilt für den festen Vergleich,
nicht für beliebige künftige Daten oder allgemeine Lernfähigkeit.

## Durchführung und Bindung

Vor Start wurde die vorgegebene Vorstartbindung exakt geprüft:
`c35c1146ebb6c6884d761a52fb50aa15df39f9d39f821e6b329103a76446f9b9`.
Der Zielordner war nicht vorhanden. Die operative Autorisierung wurde exklusiv
aus der Vorlage erzeugt, ausschließlich mit Statuswechsel zu AUTHORIZED_ONCE.
Anschließend erfolgte genau ein Aufruf des dokumentierten Run-Befehls.

Laufarchiv: `../k1-comparison-20261004-01/`.
Abschluss-SHA256:
`3eb073806e2f568b1528232dcbf6a4bebe838aaae7333a45f9c7bfaf6dea263c`.
Alle versiegelten Dateien wurden nach Abschluss anhand ihrer Hashes geprüft.
Das Archiv bleibt unverändert. Die Einmalautorisierung ist verbraucht; ihre
historische Datei bleibt unverändert, und der reservierte Ausgabeordner
verhindert eine Wiederholung. Kein Abbruch, keine Fallkürzung, kein Nachoptimieren.

16 gespeicherte T1-Fälle und8 feste F-Fälle:1.792 Quellpositionen,3.584
Armaufnahmen und3.584 eigene Referenzfortschreibungen. Alle24 Quellen wurden
vor dem ersten Policyaufruf materialisiert und im Manifest versiegelt.
624 T1-Ziele und248 F-Ziele ergeben872 je Variante, also1.744 Armprognosen.
Die letzte Prognose jedes Arms blieb zensiert. Keine Aussage auf einer
nachträglich ausgewählten Teilmenge.

## Vorhersagenutzen über vollständige Fallmengen

Die Werte sind gleich gewichtete Fallmittel; kleinere MAE ist besser.
Die Vertragsentscheidung verwendet die gespeicherten exakten Brüche.

| Fallmenge | U | K1 | K1−U |
| --- | --- | --- | --- |
| Alle16 T1-Fälle | 0,05347585104979002 | 0,05347585104979002 | 0 |
| Alle8 F-Fälle | 0,026776713709677418 | 0,02649319556451613 | −0,000283518145161288 |
| Alle24 Fälle | 0,04457613860308582 | 0,04448163255469872 | −0,00009450604838710 |

Alle16 einzelnen T1-Fallabstände sind0. Die vollständigen F-Fallabstände:

| Fall | K1−U als exakter Bruch | Dezimal |
| --- | --- | --- |
| F1 | −3/1984 | −0,0015120967741935483 |
| F2 | 3/1984 | 0,0015120967741935483 |
| F3 | 3/3968 | 0,0007560483870967742 |
| F4 | 0 | 0 |
| F5 | 0 | 0 |
| F6 | −11/3968 | −0,002772177419354839 |
| F7 | −1/3968 | −0,00025201612903225806 |
| F8 | 0 | 0 |

Über alle872 Zielpaare:20 Verbesserungen,11 Verschlechterungen und841
Gleichstände. Sämtliche Unterschiede liegen in F. Summierter Zielgewinn
5/32=0,15625; summierter Zielschaden11/128=0,0859375. Diese Ziel-Summen
ersetzen nicht die vertraglichen Fallmittel und die getrennte T1-Bedingung.
Größter einzelner Schaden1/128=0,0078125; schlechtester Fall F2.

G_w der vier S0-Fälle bleibt bei beiden Varianten0,03089406092961629.
Anpassung bleibt bei beiden0/52, in jeder Gruppe0/13. Alle20 negativen
Kontrollen bleiben im Nenner. Die324 Diagnoseziele haben bei beiden0 Ziele
mit lebendem modalem Nachfolger und vorherigem Feedback.

## Gewonnene und verlorene Erfahrung

Gezählt werden Ziel-Hypothesen-Vorkommen anhand ursprünglicher Ordinale und
Offset, keine einzigartigen lebenslang gespeicherten Episoden. In diesem Lauf
entspricht jede Mengenänderung einer Hypothese je betroffenem Ziel. Eine
zusätzliche kalte Hypothese ist noch keine nutzbare Fehlererfahrung.

| Menge | T1 | F | Gesamt |
| --- | --- | --- | --- |
| Zusätzliche berechtigte Nachfolger K1 gegenüber U | 31 | 32 | 63 |
| Verlorene berechtigte Nachfolger | 5 | 23 | 28 |
| Zusätzliche Nachfolger mit vorherigem Feedback | 0 | 29 | 29 |
| Verlorene Nachfolger mit vorherigem Feedback | 0 | 8 | 8 |

Von den31 zusätzlichen T1-Nachfolgern entsprechen26 dem Modalwert und22 dem
tatsächlichen Ziel. Alle sind bei ihrem Abruf kalt. Die fünf verlorenen
T1-Nachfolger enthalten keinen modalen, aber drei tatsächlich passenden
Nachfolger. Deshalb führt mehr Abrufverfügbarkeit hier weder zu mehr vorheriger
Feedbackerfahrung noch zu anderen Vorhersagen.

Unter den zusätzlichen F-Nachfolgern passen23 zum deterministischen Ziel,
unter den verlorenen14. Von29 zusätzlichen warmen Möglichkeiten passen20,
von8 verlorenen warmen Möglichkeiten passen6. Modale Ziele mit vorherigem
Feedback steigen in F von19 auf33; dieser Nebenbefund ersetzt nicht die
primäre T1-Prüfung80 gegen80.

## Konkrete Gewinne, Verluste und Schäden

- **Gewinn F1, Ziel19:** K1 hält die Originalspur1–4 über den Zwischenblock,
  erhält Feedback bei11 und promoviert die ursprüngliche Spur bei12. Bei19
  wird ihr Nachfolger aus Originalposition3 gewählt. K1-MAE0 statt
  U-MAE0,0078125. Die zusätzlichen Fehlerwerte entstehen aus echter früherer
  Rückmeldung, nicht aus einer nachträglichen Beobachterzuweisung.
- **Verlorene neue Erfahrung F2, Ziel23:** U besitzt die bei5–8 eingetroffene
  Spur, Feedback bei11 und Promotion bei12. K1 hat den Zwischenblock verworfen.
  U wählt bei23 den richtigen Nachfolger aus Originalposition7: MAE0.
  K1 hat diese Möglichkeit nicht und erzielt MAE0,0078125.
- **Irreführende alte Erfahrung F3, Ziel11:** K1 hält Originalspur1–4 mit
  günstigem Feedback bei7. Der frühere Fehler0 gegenüber Persistenz0,0078125
  führt zur Kontextwahl; diesmal ist der alte Nachfolger falsch. K1-MAE0,015625
  gegenüber U-MAE0,0078125. Der vorab erwartete Gegenfall ist eingetreten.
- **Fristverlust F5, Abschluss20:** U hält den Kandidaten aus9–12 während
  erneuter Bestätigung der anderen Spur weiter. K1 gibt ihn wegen der festen
  Frist frei. Der Bestandsverlust bleibt dokumentiert, auch wenn F5 insgesamt
  keinen MAE-Unterschied zeigt.

Die vollständigen Zielbelege einschließlich beider Hypothesenmengen und
Feedbackherkunft stehen in den24 `*-assessment.json`-Dateien des Laufarchivs.
`targets.csv` und `case-metrics.csv` in diesem Abschlussordner machen sämtliche
872 Ziele und24 Fälle zusätzlich direkt vergleichbar.

## Ressourcen und Abschluss

| Ressource | Befund | Grenze |
| --- | --- | --- |
| Zusatzheap im gebundenen Policy-Messumfang | 6.084 Byte | 16.384 Byte |
| Konservative Originalframe-Obergrenze | 16 | 18 |
| Ausgabeslots | 2 | 2 |
| Konservative kombinierte Obergrenze | 18 | 20 |
| Gepackte Bank | 416 Byte | 416 Byte |
| Receipt | 829 Byte | 16.384 Byte |
| UTF8-Obergrenze | 1.658 Byte | 32.768 Byte |
| Worker | 4,1661113s | 3.540s |
| Supervisor bis vor terminalem Schreiben | 5,9461979s | 3.600s |
| Gebundene Vorbereitung einschließlich operativer Autorisierung | 2.340.509 Byte | 8.388.608 Byte |
| Laufarchiv einschließlich Abschluss | 5.610.932 Byte | Teil der Gesamtbilanz |
| Vorbereitung plus Laufarchiv | 7.951.441 Byte | 67.108.864 Byte |

Der externe Abschlussbericht wird zusätzlich in der beigefügten Abschlussbilanz
gezählt und liegt ebenfalls innerhalb der64MiB. Der Worker ist beendet, Exitcode0;
der Laufabschluss meldet die eingehaltene Gesamtfrist. Der gespeicherte
Zeitwert schließt seine eigene Schreibdauer nicht ein. Framewerte sind die
gebundene konservative Bilanz, keine neu erhobene Trace-Messung. Zusatzheap
ist kein Gesamtprozess-RAM. Alle48 Arme melden Referenzgleichheit und Bereinigung.

## Entscheidung und nächster sinnvoller Schritt

K1 bleibt deaktiviert. Die feste Erhaltungsregel zeigt auf den F-Fällen
erwartete Gewinne und Nachteile, löst aber die primäre T1-Lücke nicht.
Keine Architekturübernahme oder positive allgemeine Lernbehauptung daraus
ableiten. Der Lauf ist ein Entwicklungsvergleich auf bekannten beziehungsweise
vorab festgelegten synthetischen Fällen, kein unabhängiger Transfernachweis.

Empfehlung: Den K1-Einmallauf als gültigen negativen Primärbefund abschließen.
Als nächsten begrenzten Auftrag die gespeicherten31 zusätzlichen T1-Nachfolger
auf ihre Feedback- und Wiederkehrzeitpunkte untersuchen: Fehlt eine zweite
Nutzungsgelegenheit, oder geht der Schlüssel vor ihr verloren? Erst diese
Diagnose sollte begründen, ob überhaupt eine weitere Speicherregel sinnvoll
ist. Kein automatischer Replay, kein Variieren der Erhaltungsdauer und keine
nachträgliche Absenkung der Kriterien.
