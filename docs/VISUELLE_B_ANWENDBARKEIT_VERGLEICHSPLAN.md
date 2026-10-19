# Prospektiver Vergleich visueller B-Anwendbarkeit

## Aufgabe und eingefrorener Bezug

Nur Planung. Keine neue Stabilisierungsgeschichte oder Memoryänderung.
Verwendet wird der tatsächlich gebildete Memoryzustand nach Formation 4 des
geschlossenen Laufs `structure-av-system-20260912-01`, vor seinem Hinweis.
Dieser Bestand ist bereits untersucht, kein unberührter Bestätigungskorpus.
Sein visueller Slot 000 ist stabil; Prototyp, Generation und sämtliche
A-Inhalte bleiben für alle Hinweise unverändert. Quellen-/Record-/Prüfdigests
sind vor späterer Verarbeitung aus der bestehenden Bindung zu übernehmen.

Ziel ist B-Anwendbarkeit, nicht erneuter Supportnachweis. Die öffentliche
Entscheidung bleibt eine zweite, getrennte Ebene. Keine Hypothesenanwendung.

## Genau zwei Regeln

Sicht I = Originalindizes 0..31 der unveränderten 288-dimensionalen visuellen
Repräsentation. Historische Regel: alle q[i] == p[i], numerische Gleichheit
wie in `_s2kq_private_partial_cue_retrieval_336.py::_slot_record`.

Einzige Alternative, nur für stabile visuelle B-Kandidaten:

`max(abs(q[i] - p[i]) for i in I) <= tau`

`tau` wird einmal als Binary64-Ergebnis von `1.0 / 255.0` gebunden.
Aufsteigende Originalindexfolge, keine Rundung der Terme, keine zusätzliche
Epsilonprüfung. Alle 32 numerischen Terme und ihre Indizes speichern.
Gleichstand an tau ist zulässig. Unabhängige Direktrechnung schreibt ihre
eigene Schleife und übernimmt weder Terme noch Entscheidung des Primärarms.

Begründung: Der vorhandene Rezeptor berechnet lokale RGB8-Kanalmittel und
dividiert durch 255 (`finite_video_path.py:195–204`). Eine vorab erlaubte
Änderung von höchstens einer RGB8-Stufe pro Pixel/Kanal begrenzt in exakter
Arithmetik die Änderung jedes Zellkanalmittels durch 1/255. Der Maximumabstand
verhindert Verdünnung einer einzelnen sichtbaren Abweichung durch Mittelung.

Dies ist ein ausdrücklich gewähltes enges diagnostisches Pegelbudget, keine
allgemeine semantische Toleranz und nicht die Auflösung des gemittelten
Rezeptorwerts. Es garantiert insbesondere keinen Abstand <= tau zu einem
bereits gemittelten Prototyp. Die tatsächliche Binary64-Kette kann Grenzfälle
anders behandeln; solche Fälle bleiben sichtbar. Die Vollvektorgrenze 0,01
liefert hier weder Herleitung noch Fallback. Keine Suche nach anderem tau.

## Sieben vorab bestimmte Hinweise

Grundrezepte und geometrische Koordinaten unverändert aus der bestehenden
Strukturquellenversiegelung. Jede Quelle wird vor Analyse separat gebunden.
Hinweise entstehen ausschließlich aus vor Analyse okkludierten RGB-Frames:
Zellkanäle für Komponenten 0..31 bleiben erhalten, alle übrigen werden null.
Verdeckte Originalwerte oder Generatorrollen gelangen nicht zum Scan.

| Nr. | Vollständiges Quellenrezept vor Okklusion | Getrennte Bewertungsrolle |
| --- | --- | --- |
| 1 | q04 unverändert | gelernter Eingang |
| 2 | q05 unverändert | gelernter Eingang |
| 3 | q06 unverändert | gelernter Eingang; Exaktkontrolle zur Quellenrolle |
| 4 | q06, sämtliche Kanalbytes plus 1 | neue positive Pegelvariante |
| 5 | q06, sämtliche Kanalbytes minus 1 | neue negative Pegelvariante |
| 6 | q01 unverändert | andere verdeckte Struktur bei gleicher sichtbarer Quelle |
| 7 | q06 plus Rechteck [0,0,160,135), RGB=(216,216,216) | zusätzliche sichtbare Struktur |

Bei 4/5 liegen die vorhandenen Ausgangspegel 24/216 nach Änderung weiterhin
im RGB8-Bereich; kein Clipping. Änderung erfolgt vor Okklusion. Bei 7 wird
die erste vollständige Rasterzelle überschrieben, ohne weitere Änderung.
Keine Materialisierung oder Analyse dieser neuen Hinweise jetzt.

Nr. 3 und 6 haben rezeptbedingt dieselben sichtbaren Inhalte, aber verschiedene
verdeckte Struktur. Ihre späteren getrennt analysierten Cuewerte sind trotzdem
zu prüfen, nicht allein aus dem Rezept als gemessen gleich zu deklarieren.
Wenn sie gleich sind, kann keine der beiden Regeln daraus unterschiedliche
B-Zuordnungen begründen. Das ist eine absichtliche Verlust-/Fehlzulassungskontrolle,
kein Anlass zur Erweiterung der Sicht. Generatorrollen sind Bewertungsannahmen,
keine erkannte Objektidentität. Wiederkehrende q04 zählt nicht als unabhängige
Replikation. Exakte Quelle ist nicht automatisch exakter Prototyp.

## A und öffentliche Entscheidung

A-Scans und `_resolve_a` unverändert. Pro Hinweis einmal produktiver A-Scan
und einmal vorhandene Direktbaseline; deren Ergebnisse dürfen für beide
B-Arme wiederverwendet werden, weil Zustand und Cue identisch sind.
Beide B-Arme scannen alle vier Plätze; stabile Belegung ist die bestehende
Voraussetzung. B-Auflösung nach Trefferzahl und öffentliche A/B-Auflösung
bleiben unverändert. Keine Bevorzugung von B und kein Zusammenführen mehrfacher
A-Treffer. Ausbleibende öffentliche Hypothese ist kein technischer Fehler.

## Bewertung ohne Verlustverrechnung

Für jeden Hinweis: B-Prüfbarkeit, vollständige Treffermenge, Zielgeneration,
historische/alternative Anwendbarkeit, A-Status und öffentliche Entscheidung.
Erwartete Zielbeziehung gilt für 1..5, nicht für 6/7. Das ist eine vorgebundene
Aufgabenbewertung, keine Aussage, dass eine Mischung niemals einen bekannten
Bestandteil enthält.

Getrennte Nenner und Tabellen für gelernte Eingänge (N=3), neue Varianten
(N=2), verdeckte Strukturkontrolle (N=1) und sichtbare Strukturkontrolle (N=1):
- erhaltene richtige B-Anwendbarkeit und Verluste gegenüber Exakt;
- neue richtige B-Anwendbarkeit, neue beziehungsweise verhinderte falsche;
- B-Mehrdeutigkeit;
- richtige öffentliche Hypothese, Fehlzulassung und Enthaltung separat.

Erhaltungsnenner D enthält nur richtige historische Treffer der jeweiligen
Ebene; D=0 bleibt Erhaltung nicht geprüft. A-Enthaltung füllt keinen
B-Erhaltungsnenner und verdeckt keine alternative Fehlanwendbarkeit.
Keine positive Gesamtsumme, die Strukturfehler mit Variantengewinnen verrechnet.

## Endlicher Umfang und notwendiger Anschluss

Höchstens sieben visuelle Analysen, keine Audio-/NJ-Analyse, Formation oder
Feld-/Runtimeausführung. Ein RGB-Frame gleichzeitig, 6.220.800 Byte; keine
verdeckte Vollsichtanalyse. Jeder Hinweis erhält eigene Quellenidentität
und einen nativen Zeitpunkt nach dem eingefrorenen Zustand: Fenster
[26+6j,27+6j) bei Zeitbasis 1/30, j=0..6; gemeinsame Zeit wie OB. Kein
Fortschreiben des eingefrorenen Zustands zwischen Abrufen.

B: 7 Hinweise × 4 Plätze × 4 Implementierungsarme = 112 Slotbelege.
Bei der belegten einen stabilen Generation höchstens 448 Abstandsterme
(Alternative plus Direktrechnung) und 448 Exaktvergleiche (Referenz plus
Direktrechnung). A: 7 × 2 × 12 Slotprüfungen = 168, höchstens 5.376
sichtbare Vergleiche sowie 4.032 interne Vollwertvergleiche. Offline-Prüfung
erhält separat dieselben Obergrenzen, ohne Rezeptor-/Memorywiederholung.
14 öffentliche Primärentscheidungen plus 14 Direktentscheidungen.

Kleinster Anschluss: eigener regelgebundener visueller B-Scan, Wiederverwendung
unveränderter Sicht-/Quellenvalidierung und A/B-Auflösung, unabhängige
Direktrechnung sowie nach Verifikation getrennte Bewertung. Historische
Funktionen nicht umwidmen. Vor Implementierung sind die vollständigen
Quellen-, Prüf- und Abschlussformate innerhalb vorhandener Einzelgrenzen
(Scanbeleg 32.767 Byte) und Gesamtgrenze 4.194.304 Byte zu bilanzieren;
Operationszahlen allein beweisen keine passende Artefakthülle.

Negative Ergebnisse sind regulär: keine neuen B-Treffer, zusätzliche falsche
Anwendbarkeit, fortbestehende A-Enthaltung oder unzureichende sichtbare Evidenz.
Auch ein Erfolg begründet nur diese eng gebundene B-Regelprüfung, keine
Defaultänderung. Gates False; keine automatische Folgeausführung.
