# DATEIBETRIEB-CHECKPOINT-BEDIENUNG: neutral qualifiziert

`media-restart-qualification-20260913-05`: **8/8, QUALIFIED**, genau ein
Testaufruf, 188,731 s. [Ergebnis](result.json), [vollständiges Log](stderr.log).
Quellen vor/nach dem Aufruf unverändert; Bezugscommit
`537109994cf777f8d36cda617aafe12226806c25`, uncommittierter Arbeitsstand.
[Code-, Profil- und Prüfbindung](preregistration.json), SHA-256:
`ad00488bc1b0a903e85a5e843f47416515429f71795573aadb06bd3f607c13e2`.

## Erreicht

- Gemeinsame Reservebasis an allen 21 synthetischen Fortschrittspositionen:
  geschriebene Inhalte ersetzen Zukunftsanteile; temporäre Kopien zählen extra.
- Budgetgleichstand akzeptiert, Überschreitung kontrolliert abgewiesen.
- Früher Schnitt nach 1, später nach 19 Formationen: echte Prozessenden,
  frische Prozesse und vollständige Fortsetzung bis Ereignis 20.
- Beide unabhängigen Gesamtvergleiche bestanden: alle 20 Schritte, gesamter
  Kernbeleg, Auswahlbindungen, Feld-/Memoryzustände und Abschluss gleich.
  Nachweise: `early-restore-verification.json`, `late-restore-verification.json`.
- Begrenzte JSON-Serialisierung und Referenzexpansion; kanonische Bytes
  einschließlich negativem Nullwert, Subnormalwert und Unicode unverändert.
- Induzierter Budgetfehler nach nativer Formation: Feld- und Memorybindung
  erhalten, Fortschritt dokumentiert, Worker geschlossen, kein zweiter Abschluss.
  Fehlerbeleg 3.077 Byte, Grenze 4.096. Die Budgetbelegung dieser Fehlerfixture
  ist synthetisch; Formation und Zustandsbindungen sind tatsächlich erzeugt.

## Verbrauch

Alle vollständigen Arme: 20 Audio-, NJ- und visuelle Verarbeitungen,
40 Payloadübergaben. Replay erzeugt keine zusätzliche Memoryerfahrung.

| Arm | Gelesene Containerbytes | Pakete | Video-/Audioframes |
|---|---:|---:|---:|
| Referenz | 18.440 | 2.056 | 801 / 1.255 |
| Früher Restore, kumulativ | 34.832 | 2.064 | 804 / 1.260 |
| Später Restore, kumulativ | 36.768 | 4.000 | 1.559 / 2.441 |

Decodermehrarbeit ist getrennt gebucht, nicht als gleiche Verbrauchsmenge
behauptet. Vor Ergebnisveröffentlichung ergaben noch offene Restreserven
132.165 Byte. Der Ergebnisabschluss gibt 7.057 ungenutzte Logbytes frei;
einschließlich temporärer Ergebniskopie sind dann 125.544 Byte angerechnet.
Deshalb ist `pre_result_reserved_violations` kein verschwiegenes Fehlerereignis.
Die tatsächliche Veröffentlichung wurde auf derselben Basis geprüft.

## Grenzen

Finale physische Istbilanz einschließlich aktiver Referenzdateien, dieses
Berichts und der Bilanzdatei: `closure-balance.json`. Ergebnis/Bericht/Bilanz
teilen unverändert 4.096 Byte; Primärfehlerreserve weiterhin 8.192 Byte.
Die konkrete Veröffentlichung muss passen. Keine Erfolgsgarantie bei
gleichzeitiger Ausschöpfung aller Einzelmaxima; keine Grenzerhöhung.

Synthetischer Codec, echte Rezeptor-/NJ-/Feld-/Memorypfade und Prozesse.
Kein realer Videolauf, keine allgemeine Crash-Recovery. Gates False.
Alte Fehlbefunde bleiben unverändert; -03 hatte keinen Testaufruf, -04 war
nur eine vor dem Test abgelöste Vorbindung. Keine historischen Passzahlen
übernommen und keine alten Testsuiten erneut ausgeführt.
