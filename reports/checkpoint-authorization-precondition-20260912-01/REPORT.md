# Workerautorisierung ergänzt; Metadaten-Vorbedingung verletzt

Auftrag: enge Ergänzung der Workerautorisierung und Herleitung der
Metadatenobergrenze. **PRECONDITION_STOP, null neue Testaufrufe.**
Der historische 24/24-Teilnachweis ist unverändert. Kein Hauptlauf.

## Implementierter, noch unqualifizierter Anschluss

`tools/_checkpoint_transfer_entry.py`, Version `checkpoint.transfer-entry.v2`:
Vor Gateöffnung und Sitzungserzeugung prüft `authorize_worker()` den festen
Autorisierungspfad, die exakte Autorisierungsform, Lauf-/Manifest-/Profil- und
Codebindung sowie den Hash der verbrauchten Hauptzulassung. Danach beansprucht
der Worker exklusiv seine eigene Rollenmarke mit Autorisierungsdigest und
Abschnitt. Referenz: 1–7; Save: 1–4; Restore: 5–7. Der Dispatch allein reicht
nicht mehr. Die Rollenmarke verhindert Wiederanlauf derselben Rolle.

Die bisherigen v1-Settings werden wegen der neuen Version nicht akzeptiert.
Es wurde keine neue Hauptzulassung erzeugt. Der Einstieg und seine Quellen
sind noch nicht durch den freigegebenen Ergänzungsaufruf qualifiziert.

## Konkrete Rechnung

`tools/_checkpoint_transfer_metadata.py` bildet serialisierte Record-,
Checkpoint-, Vergleichspunkt-, Konto- und Fehlerhüllen nach den vorhandenen
Feldern ab. Native Inhalte sind nur in dieser Formatberechnung durch
Platzhalter ersetzt und separat über ihre unveränderten Deckel erfasst;
keine Runtimezustände werden dadurch verändert. Dieselbe bestehende
Klassifikationsfunktion bestimmt die Metadatenanteile. Die 65.536 Byte
werden nicht mehr als angenommener Verbrauch eingesetzt.

Spitze der gerechneten Alternativen: **restore-failure-7**.

| Beitrag | Byte |
|---|---:|
| Bereits erforderliche administrative Bindungen und Nachweise | 36.670 |
| Vorherige Arm-/Checkpointmetadaten | 12.737 |
| Drei begrenzte Prozesslogs | 24.576 |
| Vollständige Fehlerpublikation einschließlich temporärem Namen | 27.410 |
| Rollenmarken | 768 |
| Summe | **102.161** |
| Unveränderte Grenze | **65.536** |
| Überschreitung der Schutzrechnung | **36.625** |

Alle Beiträge und Fortschrittsalternativen stehen in `precondition.json`.
Quellen-/Codestand und zwölf vorbereitete neue Prüffälle sind dort gebunden.
Keine der bisherigen 24 Prüfungen wird wiederholt.

Zusätzliche neue Qualifikation, Hauptautorisierung, gemeinsame Runtimebindung
und endgültiger Abschluss sind noch nicht auf diese Summe aufgeschlagen.
Diese fehlenden positiven Beiträge können die bereits bestehende Überschreitung
nicht beseitigen. Deshalb wurde vor der Qualifikation gestoppt, nicht eine
unvollständige Bilanz als passende Gesamtreserve ausgegeben.

## Aussagegrenze und Korrekturrichtung

Die Zahl ist **keine Messung des realen Laufs und keine bewiesene notwendige
Mindestgröße**. Sie widerlegt die Tragfähigkeit der derzeit hergeleiteten
Schutzhülle, nicht die prinzipielle Möglichkeit einer kleineren Darstellung.
Eine bloße Rückkehr zum eingesetzten Wert 65.536 wäre keine Korrektur.

Die größten Ansatzpunkte sind die mehrfach enthaltenen administrativen
Budget-/Herkunftsangaben und die vollständige Ledgerdiagnostik in der
zweifachen Fehlerpublikation. Eine weitere Korrektur müsste deren tatsächlich
erforderliche Inhalte gemeinsam, eindeutig auflösbar und ohne Informationsverlust
binden; nicht Wahrnehmungswerte, Zustände oder Logs kürzen. Alternativ müsste
eine engere Formatobergrenze sachlich bewiesen werden. Hier wurde weder eine
solche Änderung noch eine neue Verpackungsmechanik vorgenommen.

Es liegt noch **keine endgültige Einmalbindung** vor. Keine Quellenpayloads
gelesen, keine Analyse, kein Memory-/Feldaufruf, kein neuer Test und kein Gate
geöffnet. `memory-restart-transfer-20260912-01` bleibt unbenutzt.
