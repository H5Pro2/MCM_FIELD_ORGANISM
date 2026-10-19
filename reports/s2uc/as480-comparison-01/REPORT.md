# AS480 – Ergebnis des einmaligen Forschungslaufs

Auftrag: 6fecf399-7d55-455f-8f2a-0b576e5f61df. Datum: 2026-10-19.

**Gesamturteil: NO_ADDITIONAL_BENEFIT.** Technisch vollständig; keine identischen A/B-Hinweiskollisionen.

- S1 falsch: A480 wird weder von E noch von N korrekt zugeordnet.
- S2 wahr: keine zusätzliche falsche A-Zuordnung in B0/B480; beide Policies enthalten sich.
- S3 wahr: der korrekte A0-Exaktabruf bleibt erhalten; kein verlorener korrekter A-Abruf.
- S4 falsch: N und E haben identische Hauptzielfehler. Beide liegen unter P, aber N ist nicht strikt besser als E.

Hauptzielmittel: {"E": 0.0023202510123532727, "N": 0.0023202510123532727, "P": 0.00302567864944738}.
Beide Schadenflags sind falsch. Gleichstand ist kein Gleichwertigkeitsnachweis.

## Vier Hauptziele

| Fall | E-MAE | N-MAE | P-MAE | N−E | N−P |
|---|---:|---:|---:|---:|---:|
| A0 | 0 | 0 | 0.0028217105483764287 | 0 | -0.0028217105483764287 |
| A480 | 0.002827261547473519 | 0.002827261547473519 | 0.002827261547473519 | 0 | 0 |
| B0 | 0.0032263047829872368 | 0.0032263047829872368 | 0.0032263047829872368 | 0 | 0 |
| B480 | 0.0032274377189523353 | 0.0032274377189523353 | 0.0032274377189523353 | 0 | 0 |

A0: Quelle A, Ziel [9600,14400); E und N rufen retained1, Originale1–4, Offset0, Faktor1 exakt ab. Nachfolger ist Original3; Kontext-MAE0.
A480: Quelle A, Ziel [10080,14880); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.
B0: Quelle B, Ziel [9600,14400); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.
B480: Quelle B, Ziel [10080,14880); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.
Bei diesen Enthaltungen lautet die Fortsetzungsentscheidung ABSTAIN_NO_CONTEXT; Kontextvektor und Kontext-MAE fehlen, Schema-MAE verwendet P.
Vollständige E/N/P-Ausgabevektoren, tatsächliche Zielvektoren, Herkunft und Receipts: main-target-details.json; Rohzustände und Hinweise: A0-E.json bis B480-N.json.

## Lernfehler (Ziele3/5/7) getrennt

| Fall | Ziel | E-MAE | N-MAE | P-MAE | N−E | N−P |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 3 | 0.0028217105483764287 | 0.0028217105483764287 | 0.0028217105483764287 | 0 | 0 |
| A0 | 5 | 0.003237460407874307 | 0.003237460407874307 | 0.003237460407874307 | 0 | 0 |
| A0 | 7 | 0 | 0 | 0.0028217105483764287 | 0 | -0.0028217105483764287 |
| A480 | 3 | 0.0028217105483764287 | 0.0028217105483764287 | 0.0028217105483764287 | 0 | 0 |
| A480 | 5 | 0.003237460407874307 | 0.003237460407874307 | 0.003237460407874307 | 0 | 0 |
| A480 | 7 | 0 | 0 | 0.0028217105483764287 | 0 | -0.0028217105483764287 |
| B0 | 3 | 0.0028217105483764287 | 0.0028217105483764287 | 0.0028217105483764287 | 0 | 0 |
| B0 | 5 | 0.003237460407874307 | 0.003237460407874307 | 0.003237460407874307 | 0 | 0 |
| B0 | 7 | 0 | 0 | 0.0028217105483764287 | 0 | -0.0028217105483764287 |
| B480 | 3 | 0.0028217105483764287 | 0.0028217105483764287 | 0.0028217105483764287 | 0 | 0 |
| B480 | 5 | 0.003237460407874307 | 0.003237460407874307 | 0.003237460407874307 | 0 | 0 |
| B480 | 7 | 0 | 0 | 0.0028217105483764287 | 0 | -0.0028217105483764287 |

## Übergangsfehler (Ziel9) getrennt

| Fall | Ziel | E-MAE | N-MAE | P-MAE | N−E | N−P |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 9 | 0.003237460407874307 | 0.003237460407874307 | 0.003237460407874307 | 0 | 0 |
| A480 | 9 | 0.0032990167033034872 | 0.0032990167033034872 | 0.0032990167033034872 | 0 | 0 |
| B0 | 9 | 0.003232877573135427 | 0.003232877573135427 | 0.003232877573135427 | 0 | 0 |
| B480 | 9 | 0.0032982692856899768 | 0.0032982692856899768 | 0.0032982692856899768 | 0 | 0 |

Ziele3/5: kein Kontext, P. Ziel7: exakter Kandidat1-Abruf, Originale1–4, Offset0, Faktor1, Fehler0. Ziel9: exakter Kandidat1-Match mit Offset2; ABSTAIN_NO_SUCCESSOR, deshalb P. Die spätere Promotion beim Abschluss8 ändert diese zuvor eingefrorene Entscheidung nicht.

## Einzelschäden und Grenzen

Über alle20 Zielpaare: 0 Fälle mit N−E>0 oder N−P>0; 0 durch Signalgate verlorene eindeutige Exaktmatches. Alle Deltas stehen oben und in all-errors.json.
Keine gemeinsame oder zusätzliche falsche A-Zuordnung an den beiden B-Hauptzielen. Keine zusätzlichen Lern-/Übergangsfälle als unabhängige Hauptprüffälle gezählt.
Die feste Näherungsregel liefert hier keinen zusätzlichen Abruf. Das belegt weder allgemeine Nutzlosigkeit noch natürliche Robustheit, allgemeine Lernfähigkeit oder feldinterne Memory. Keine Parametersuche, kein Bootstrap, keine Ersatzquelle.

## Ausführung und Ressourcen

Genau ein Forschungsstart, zwei Quellen,44 Rezeptor-/44 NJ-Aufrufe, acht Arme und acht Bestandsreferenzen mit je88 Aufnahmen sowie40 bereits im Worker bestandene unabhängige skalare Prüfungen. Kein Replay beim Abschluss.
Alle acht Arme/Referenzen geschlossen, Worker beendet; Material nach Vergleich unverändert. terminal.json, worker-result.json und execution.jsonl enthalten die Nachweise.
Laufzeit 34.861384600s; Jobpeak 300109824 Bytes; Prozesspeak 230600704 Bytes. Harte Jobgrenze536870912 Bytes, maximal2 Prozesse, Worker240s/Gesamt300s; Bibliotheksthreads1.
Abschluss ist eine separate Archiv-/Dokumentationsphase ohne Material-/Policyaufrufe; deren Job-/Zeit-/Dateibilanz wird separat in delivery-resources.json ausgewiesen. Keine Behauptung, die interaktive Berichtsphase liege innerhalb der Supervisor-Wanduhr.
Einmalberechtigung und Verbrauchsmarker verbleiben unter as480-neutral-qualification-20261019-01. Kein Retry erlaubt. START.txt wurde unverändert verwendet; dessen generisches reason-Feld nennt noch qualification, maßgeblich sind mode=research, Berechtigung und dieser Auftragsbezug.
Der frühere OpenBLAS-Abbruch bleibt in der neutralen Bilanz dokumentiert. Die spätere Runtimebindungserweiterung bleibt eine Lieferbindung und wird nicht rückwirkend als Neutral-Vorstartnachweis ausgegeben.

## Anschlussvorschlag

Diese feste AS480-Gegenprobe abschließen. Als nächsten begrenzten Schritt eine rein lesende Ursachenanalyse der archivierten A480-Hinweise gegen die gespeicherte A-Spur fachlich entscheiden: prüfen, ob Fensterinhalt und Rezeptorprojektion den fehlenden Näherungsabruf erklären. Keine neue Quelle, keine neue Policy und keine Schwellenanpassung daraus automatisch freigeben.
Die unveränderten Regeln und das vorliegende negative Resultat bleiben Referenz. U und der abgeschlossene Fehlerbewertungszweig bleiben unverändert.
