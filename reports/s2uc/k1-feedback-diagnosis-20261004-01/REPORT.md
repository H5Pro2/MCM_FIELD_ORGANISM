# K1: Diagnose der Feedback- und Wiederkehrkette

Die31 zusätzlichen T1-Vorkommen scheitern an zwei aufeinanderfolgenden
Voraussetzungen: Alle31 sind der erste berechtigte Abruf ihres jeweiligen
Originalspur-Offsets und deshalb zunächst kalt. Bei27 wird die Originalspur
noch vor der zugehörigen Rückmeldung ersetzt. Bei vier wird die Rückmeldung
korrekt übernommen, aber der gleiche Originalspur-Offset danach nicht mehr
berechtigt abgerufen. Es gibt keinen belegten zusätzlichen warmen Wiederabruf.

Dies ist eine reine Auswertung gespeicherter Belege. Keine Quellen erzeugt,
keine Policy aufgerufen, keine Regel oder Frist geändert. Sämtliche Dateien
des Laufarchivs wurden vor und nach der Diagnose gehasht und blieben unverändert.

## Vollständigkeit und Identität

Die31 hinzugewonnenen Ziel-Hypothesen-Vorkommen gehören zu30 eindeutigen
Originalspuren und31 eindeutigen Originalspur-Offset-Linien. Am jeweiligen
Abruf sind31 unterschiedliche Fehlerschlüssel beobachtet worden, jeweils
einschließlich Fallidentität. Das sind keine31 unabhängig dauerhaft gespeicherten
Erfahrungen. In T1-3-2 wird dieselbe Originalspur53–56 an Ziel63 mit Offset0
und an Ziel75 mit Offset1 abgefragt. Die Rückmeldung für Offset0 macht Offset1
nicht warm; dies ist kein Promotionsverlust.

Die vollständige36-zeilige Zuordnung steht in `mapping.csv`:31 gewonnene und
fünf verlorene Vorkommen. `occurrences.json` ergänzt pro Zeile sämtliche
Bestandswechsel, beobachteten Abrufe, Feedbackbelege, Originalordinalen,
Gegenarm und spätere wertgleiche Hinweise. Die Belegstellen verwenden
Dateiname und JSON-Pointer im unveränderten Laufarchiv
`../k1-comparison-20261004-01/`. `contrasts.json` enthält F1 und F2.

Originalspuren werden anhand ihrer vier Originalordinalen verfolgt, Fehlerlinien
zusätzlich anhand des Offsets. Ein Wechsel von Kandidaten- zu Retained-Generation
bleibt dieselbe Originalspur. Wertegleiche spätere Hinweise ohne diese lebende
Originalspur sind ausschließlich historische Diagnose, keine berechtigten Abrufe.
Auch die letzte zensierte Prognose wurde auf weitere Hinweise geprüft.

## Ursachen mit getrennten Bezugszeitpunkten

| Stufe | Befund | Vorkommen |
| --- | --- | --- |
| Vor dem betrachteten Abruf | Kein früherer berechtigter Abruf und daher keine vorherige Feedbackgelegenheit für diese Originalspur-Offset-Linie | 31/31 |
| Verarbeitung der aktuellen Rückmeldung | Eingefrorener Schlüssel inzwischen tot; Update korrekt abgelehnt | 27/31 |
| Verarbeitung der aktuellen Rückmeldung | Update korrekt übernommen | 4/31 |
| Nach dem betrachteten Abruf | Keine weitere tatsächlich berechtigte Abrufgelegenheit derselben Originalspur-Offset-Linie | 31/31 |

Diese Zeilen sind Stufen derselben Kette, keine addierbaren disjunkten Ursachen.
Als primärer nachgelagerter Engpass werden27 Vorkommen dem toten Schlüssel und
vier der fehlenden weiteren Abrufgelegenheit zugeordnet. Kein Vorkommen bleibt
unzugeordnet; eine allgemeine Aussage über alle früheren wertgleichen Muster
wird daraus nicht abgeleitet.

### Die27 verworfenen Rückmeldungen

Alle27 folgen genau derselben zeitlichen Konstellation. Der Kandidat entsteht
am vollständigen Abschluss c. Sein erster berechtigter Hinweis endet bei c+8;
die Prognose für c+9 wird vor Aufnahme dieser Hinweisframes eingefroren.
Anschließend schließt der neue Viererblock bei c+8 und ersetzt den Kandidaten.
Wenn das Ziel c+9 eintrifft, ist dessen alter Fehlerschlüssel bereits tot.
Die Prognose selbst wird weiterhin korrekt ausgewertet, aber ihre Rückmeldung
darf keine Zelle für eine nicht mehr lebende Originalspur aktualisieren.

Es handelt sich bei diesen27 Fällen jeweils um echte Kandidatenersetzung,
nicht um eine bloße Umbenennung durch Promotion. Die eingefrorenen Referenzen
erlauben die abgeschlossene Prognose, schaffen aber keinen weiter abrufbaren
Kandidaten und keine Erlaubnis zur Wiederbelebung.

Beispiel T1-0-3: Originale25–28 werden bei28 Kandidat. Der erste berechtigte
Hinweis35–36 friert eine Prognose für37 ein. Ersetzung bei36; Feedback bei37
mit live=false. Wertgleiche Hinweise existieren später für47,55 und65, aber
die Originalspur25–28 ist dann kein lebender Bestand mehr.

Bei zehn der27 Fälle gibt es nach dem verlorenen Feedback noch wertgleiche
Hinweise im gespeicherten Eingang; bei17 nicht. Keiner dieser späteren Hinweise
ist ein tatsächlich berechtigter Abruf der verlorenen Originalspur. Diese zehn
Fälle belegen mögliche Wiederkehr der Werte, nicht den Nutzen einer ungetesteten
anderen Speicherregel.

### Die vier korrekt übernommenen Rückmeldungen

| Fall/Ziel | Originale/Offset | Rückmeldung | Anschließender Bestand | Erneuter gleicher Hinweis |
| --- | --- | --- | --- | --- |
| T1-2-4 /35 | 25–28 /0 | Bei35 übernommen | Promotion bei36, Originale bis Storyende erhalten | Keiner |
| T1-3-1 /71 | 61–64 /0 | Bei71 übernommen | Kandidat bei72 ersetzt | Keiner |
| T1-3-2 /63 | 53–56 /0 | Bei63 übernommen | Promotion bei64, Originale bis Storyende erhalten | Keiner |
| T1-3-2 /75 | 53–56 /1 | Bei75 übernommen | Dieselbe bestätigte Spur bis Storyende erhalten | Keiner |

Eine korrekt verarbeitete Rückmeldung wird erst bei einem späteren berechtigten
Abruf derselben Fehlerlinie nutzbar. Dieser zweite Schritt fehlt in allen vier
Fällen. Bei T1-3-1 wird zusätzlich die bereits bewertete Spur bei72 entfernt;
dies ist ein belegter Erfahrungsverlust, aber kein belegter verpasster späterer
Abruf: Bis zum Ende kommt der betreffende Hinweis nicht mehr vor.

Die zwei echten Promotionen erhalten die Originalspuren. Die Übernahme der
Fehlerzellen ist durch die gespeicherte erfolgreiche unabhängige Referenzprüfung
des gebundenen Laufcodes abgesichert. Im Archiv gibt es jedoch kein separates
vollständiges Zellabbild unmittelbar nach jeder Promotion. Direkte Belege sind
die übernommenen Updates und die erhaltenen Originale; daraus wird kein
nicht aufgezeichneter späterer Zellabruf erfunden. Der kalte Offset1 bei75 ist
ein anderer Fehlerschlüssel als der bei63 bewertete Offset0.

## Die fünf verlorenen T1-Nachfolger

| Fall | Ziel | Originale/Offset in U | Aufnahme | Feedback in U | Verlust in U |
| --- | --- | --- | --- | --- | --- |
| T1-1-1 | 51 | 45–48 /1 | 48 | 51 übernommen | 52 ersetzt |
| T1-1-2 | 51 | 45–48 /1 | 48 | 51 übernommen | 52 ersetzt |
| T1-1-3 | 51 | 45–48 /1 | 48 | 51 übernommen | 52 ersetzt |
| T1-1-4 | 51 | 45–48 /1 | 48 | 51 übernommen | 52 ersetzt |
| T1-2-3 | 27 | 21–24 /1 | 24 | 27 übernommen | 28 ersetzt |

K1 hat keine dieser fünf Originalspuren als Kandidaten aufgenommen: Die
entsprechenden neuen Zwischenblöcke wurden zugunsten des älteren Kandidaten
verworfen. U besitzt sie bei ihrem ersten kalten Abruf und übernimmt jeweils
das Feedback. U ersetzt sie aber am nächsten Abschluss vor einer erneuten
berechtigten Nutzung. In T1-1-1 und T1-1-4 kommen die Werte später erneut als
Hinweis vor, für Ziel69 beziehungsweise73; die ursprünglichen Spuren fehlen
auch bei U dann bereits. Drei verlorene Nachfolger passen zum tatsächlichen
Ziel, keiner zum T1-Modalwert. Keine der fünf Ketten erzeugt einen späteren
warmen Originalabruf. Das erklärt ihre fehlende Vorhersagewirkung in diesem Lauf.

## Warum F1 und F2 anders enden

**F1-Gewinn:** K1 bildet Originalspur1–4 bei4, erhält bei11 das erste Feedback
für Offset0 noch unter einem lebenden Kandidatenschlüssel und promoviert dieselben
Originale bei12. Bei19 erfolgt ein zweiter berechtigter Abruf desselben Offsets
mit prior_feedback=[11]. Der Fehler ist0 statt0,0078125 bei U. Aufnahme,
Rückmeldung, Erhaltung über Promotion und erneute Nutzung sind alle belegt.

**F2-Verlust:** U nimmt die neue Originalspur5–8 bei8 auf, übernimmt ihr Feedback
bei11, promoviert bei12 und verwendet den warmen Offset0 bei23 erneut. K1 hatte
den Zwischenblock5–8 verworfen. U erzielt Fehler0, K10,0078125. Auch hier ist
die entscheidende zweite Nutzung nach übernommener Rückmeldung tatsächlich da.

T1 hat für die31 zusätzlichen Linien keinen solchen vollständigen Zyklus.
Längere Abrufverfügbarkeit allein ist deshalb nicht gleichbedeutend mit zusätzlicher
später nutzbarer Fehlererfahrung. Promotion ist in den Gegenbeispielen Teil der
erfolgreichen Erhaltung, nicht die Verlustursache.

## Anschlussentscheidung

Aus diesen Belegen wird kein weiterer konkreter Speicherregelversuch empfohlen.
Aufzugeben ist die Annahme, eine pauschale Verlängerung um einen Viererblock
reiche aus, um kalte Abrufe in später nutzbare Fehlererfahrung umzuwandeln.
Ebenso wäre ein bloßes Nachtragen von Feedback zu bereits gelöschten Schlüsseln
bei unverändertem abrufbarem Bestand keine Lösung: Keine der31 Originallinien
wird anschließend tatsächlich erneut berechtigt abgerufen. Tote Fehlerzellen
wären noch keine nutzbare Erfahrung.

Die zehn späteren wertgleichen Hinweise reichen nicht aus, um eine neue
Erhaltungsregel festzulegen: Welche Originalspur sie budgetneutral verdrängen
würde und welche neue Erfahrung dadurch verloren ginge, ist nicht untersucht.
F2 belegt bereits, dass dieser Preis real ist. Eine alternative Frist oder
Umgehung der Lebendigkeitsprüfung wäre deshalb hier unbegründete Optimierung.

Der sinnvolle Abschluss dieses Teilzweigs ist: K1 deaktiviert lassen und den
negativen Primärbefund samt vollständiger Ursachenzuordnung übernehmen. Für
einen künftigen Entwurf muss der gesamte Zyklus Aufnahme → lebendiges Feedback
→ Erhaltung → erneuter berechtigter Abruf die prüfbare Anforderung sein.
Diese Diagnose startet keinen neuen Entwurf oder Versuch und beendet nicht
das Gesamtprojekt. Die nächste fachliche Entscheidung liegt beim Projektleiter;
eine weitere Bestätigungs- oder Replayrunde ist nicht erforderlich.
