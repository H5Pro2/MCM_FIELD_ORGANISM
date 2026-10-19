# Checkpointvergleich: NOT_EVALUABLE

Genau ein Dateieinstieg für `media-restart-real-20260913-02`, Exitcode 1.
Repository-HEAD `537109994cf777f8d36cda617aafe12226806c25` plus die im
Manifest gebundenen lokalen Quellen. Bindungs-SHA-256:
`f784f066b9802117c44db52626bd0cae306abe5a0d5567af94ea8f49ade52282`.
Autorisierung separat in `../media-restart-real-20260913-02-binding/authorization.json`;
SHA-256 `f6df838faefef90728e73078a9b2c7acbeca6fc26c380d63e14b378cff2b77a5`.
Der Einstieg prüfte Bindungen, unveränderte Code-/Quellenbelege,
Ausgabeabwesenheit und vollständige Budgetvorbindung vor dem Medienstart.

## Erreichter Fortschritt

- Referenz, PID 16968: 20 Ereignisse, 20 Audioanalysen/NJ-Projektionen und
  20 visuelle Analysen; beide EOF erreicht. Letzter Video-PTS 800800,
  Audioende Sample 1282048. Regulär geschlossen, Gates False.
- Suspend19, PID 19320: 19 Ereignisse und jeweils 19 Audio-/NJ-/Visual-
  Verarbeitungen. Checkpoint gespeichert, gelesen und gemäß bestehendem
  Anschluss geprüft; Prozess geordnet geschlossen, Gates False.
- Restore20, PID 27336: Checkpoint genau einmal konsumiert. Zustand mit
  19 Ereignissen wiederhergestellt; keine zusätzliche MCM-Formation.
  Ereignis 20 und die EOF-Abschlüsse dieses Arms nicht erreicht.

## Primärfehler und Aussagegrenze

`restore20/failure.json` ist der maßgebliche, 2.347 Byte große Fehlerbeleg:
`DECODER_TIMEOUT`, Phase `MATERIALIZATION`, completed=19. Letzte bestätigte
Workerphase: VIDEO / packet_decode. Gebundene Anfragegrenze: 30 Sekunden.
Der äußere `REAL_CHILD_FAILED` und `REAL_STAGE_FAILED` in `restore20.stderr`
sind Folgefehler, keine Ersatzursache. Keine nähere numerische Ursache belegt.

Null Gesamtverifikationen, null Funktionsauswertungen. Die vorgesehenen
Prüfungen wurden wegen des technischen Abbruchs nicht aufgerufen.
Fortsetzungsgleichheit bleibt ungeprüft; kein negativer Memorybefund.
Kein Retry, keine Code-, Parameter-, Grenz- oder Quellenänderung.

## Verbrauch und Grenzen

| Gesicherter Stand | Gelesene Bytes | Pakete | Videoframes | Audioframes |
|---|---:|---:|---:|---:|
| Referenz einschließlich EOF | 333.993.752 | 2.057 | 801 | 1.252 |
| Vergleich bis Suspend19 | 327.529.918 | 1.948 | 758 | 1.186 |

Diese getrennten Konten dürfen nicht als zwei Verbräuche derselben
Vergleichsarmgrenze summiert werden. Der Restorefehler übernimmt den
Suspendstand als `prior`. Seine zusätzlichen regulären/Replay-Zähler stehen
auf null, aber `read_counters_complete=false` und die äußere
`frame_evidence_complete=false`: zusätzliche tatsächliche Arbeit und
Gesamtlesemenge einschließlich Replay sind nicht vollständig nachgewiesen.
Das innere `restart_work.frame_evidence_complete=true` ersetzt diese fehlende
Workerüberlieferung nicht. Null ist hier kein gemessener Nullverbrauch.

Restore: Peak Job Commit 604.663.808, Peak Process Commit 598.093.824 Byte,
jeweilige Grenze 1.073.741.824 Byte. Keine Speichergrenzmeldung;
Worker geschlossen, Exitcode 1. Nach Prozessende keine zugehörigen
Medienprozesse mehr vorhanden. Die qualifizierten finally-Pfade setzen
beide Gates False; kein normaler Restore-Prozessabschlussbeleg vorhanden.

`balance.json` zählt alle realen Laufdateien und aktiven externen Referenzen,
einschließlich dieser Dokumentation und der separaten Autorisierung.
Nicht verbrauchte Reserven bleiben separat sichtbar. Einzige Budgetänderung
ist das vorab qualifizierte private Belegprofil; keine Systemkapazitätserhöhung.

Quelle unverändert wiederverwendet: `17138816-uhd_3840_2160_30fps.mp4`,
83.498.438 Byte, SHA-256
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Der Decoder prüft den Quellenhash vor Analyse. Keine separate Voranalyse.
Historische Läufe und Befunde unverändert; diese Lauf-ID ist verbraucht.
