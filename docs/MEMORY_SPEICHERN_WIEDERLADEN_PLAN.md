# MEMORY-SPEICHERN-WIEDERLADEN — ANSCHLUSSPLANUNG

Stand: 12.09.2026. Ausschließlich statische Anschlussplanung.
Bezugscommit: `537109994cf777f8d36cda617aafe12226806c25`; der gelesene
Arbeitsbaum enthält zusätzliche geänderte und unversionierte Dateien.
Der Commit allein bindet deshalb nicht den späteren ausführbaren Quellenstand.
Keine historischen Läufe oder Qualifikationen wiederholen.

## Ziel und Abgrenzung

Kann derselbe Grundpfad nach ordentlichem Speichern und tatsächlichem
Prozessende mit unverändertem Feld und Memory identisch weiterarbeiten?
Memory-only-Wiederladen würde Banken erhalten, aber keine identische
Systemfortsetzung belegen. Ein frisches Feld verändert mögliche Folgewirkungen.
Für diesen Vergleich ist deshalb ein vollständiger Systemcheckpoint nötig.
Keine Crash-Recovery, Livequelle, Mediendecoder-Wiederaufnahme oder neue
Memorymechanik. Die abgeschlossenen Medienläufe bleiben unverändert gültig.

## Erforderlicher Inhalt

| Teil | Vollständig zu erhalten |
| --- | --- |
| Memory | B4-Einträge und Formationsindizes; Fast-Vektoren; beide PPB-Prototypbanken; Belegung, Supports, Konsolidierungszähler, letzte Auswahl und Eingangsdigests |
| Fortschreibung | Akzeptierte Formations-/Bankzähler, Eltern-/Zustandsdigests, Konfigurationsbindung, Quellenuhren und letzte Fensterenden |
| Generationen | Aktuelle Geburtsbindungen aller 24 Slots und tatsächliche Transaktionskette; gleiche Slot-ID ist kein Generationsnachweis |
| Feld | Vollständiger nativer Feldsnapshot einschließlich Aktivierung, Nachhall, Layer-/Kontaktzustand und Docks; dazu Wrapperphase, Komponentendigest, Schrittzahl und letztes Zeitende |
| Stream/Sitzung | Manifest, nächste Ordinalzahl, letzter Ereignisdigest, verarbeitete Ereignisse, Feld-/Formations-/Scanversuche, abgeschlossene Rückgaben und zugängliche Präfixbelege |
| Herkunft/Budget | Profil, Codeinventar mit transitiven Abhängigkeiten, Quellenzulassung, Dateihashes, geplante und bereits verbrauchte Lese-/Arbeitsbudgets, Checkpointversion und Integritätsbindung |

Keine Rohpayloads, Locks oder lebenden Owner serialisieren. Ein verbrauchter
Owner wird nicht wieder geöffnet. Der neue Prozess erzeugt neue lokale Objekte;
neue Transaktionsowner gehören ausschließlich zum nächsten gebundenen Ereignis.
Historische Owner-/Consume-Belege bleiben als unveränderliche Herkunft erhalten.

Support ist gesättigte Evidenz, kein Laufzeitzähler. Fast-Ablauf verwendet
`step - last_selected_step >= expire_after_exposures`
([Fast](../mcm_field_organism/_tspm1_private.py), Zeilen 1407–1418), PPB entsprechend
`expire_after_steps` ([PPB](../mcm_field_organism/_ppb1_reference.py), Zeilen 598–599).
Prozesspause und Wanduhr erzeugen keine zusätzlichen Schritte. Weder diese
Zähler noch Quellenuhren, Runtimezeit oder Supports beginnen nach Laden neu.

## Vorhandene und fehlende Anschlüsse

- [Memorycodec](../tools/_s2ob_private_state_evidence.py): `encode()`/`decode()`
  erhalten Binary64-Werte verlustfrei; maximal 5.568 Werte und 98.304 Byte.
  Anschließend vorhandenes `decode_state()` aus
  [NE-Verifikation](../tools/_s2ne_private_run_verification.py), Zeile 28,
  für native Rekonstruktion und Memoryvalidierung verwenden. Kein Pickle.
- [Feld](../mcm_field_organism/shared_mcm_field.py): `snapshot()`,
  `SharedMCMFieldSnapshot.from_json()` und `restore_shared_mcm_field()`
  (Zeilen 866/411/889) existieren. Der kompakte `field_record()` im
  [NG-Anschluss](../tools/_s2ng_private_runtime_comparison.py) enthält dagegen
  nur Bindungen und reicht nicht zur Wiederherstellung.
- [MR](../tools/_s2mr_private_minimal_mcm_runtime.py), Konstruktor Zeile 327:
  verlangt `processed_event_count == 0`. Nötig ist ein explizit versionierter
  Restore-Einstieg für vollständig validierten Streamzustand. Bestehenden
  Frischevalidator nicht lockern; keine privaten Zustandszuweisungen als Umgehung.
- [CallerRuntime](../tools/_s2ob_private_caller_binding.py), Zeile 339:
  initialisiert Feld, Memory, Belegpool und Generationskette leer. Ein eigener
  Restore-Anschluss muss native Zustände und ihre Branch-Referenzen konsistent
  verbinden sowie Präfix, Zähler und Generationen übernehmen. Bereits kodierte
  Zustände nicht erneut durch die native Schreibgrenze des Pools schicken.
- [OC-Sitzung](../tools/_s2oc_private_caller_session.py), `close()` Zeile 235:
  vorzeitiger Abschluss ist INCOMPLETE, kein Speicherpunkt. Nötig ist eine
  gesonderte administrative Unterbrechung unter dem Verarbeitungsschutz:
  vollständiges Ereignis abschließen, Checkpoint atomar publizieren, Instanz
  schließen und Prozessende bestätigen. Kein zweiter vollständiger Laufabschluss.
- [OB-Verifikation](../tools/_s2ob_private_caller_verification.py), Zeile 63,
  erwartet den Nullanfang. Dies bleibt erhalten: vollständiges Präfix plus
  Fortsetzung gemeinsam belegen; zusätzlich die Speicher-/Ladegrenze prüfen.
  Ein alleiniger Digest ohne verfügbare Präfixinhalte genügt nicht.

Das ist ein neuer Lifecycle-Anschluss, keine bereits qualifizierte Bedienung.
Nur ein erfolgreich gespeicherter und ordnungsgemäß beendeter Präfix darf
einmalig fortgesetzt werden. Fehlgeschlagene oder historisch geschlossene
Gesamtläufe werden nicht umgedeutet. Ein Abbruch innerhalb der Speicherung
bleibt ein Fehler; allgemeine Wiederaufnahme nach beliebigen Abstürzen ist offen.

## Neue kurze Vergleichsaufgabe

Neue endliche Aufruferfolge, kein Replay des abgeschlossenen Medienversuchs.
Vor jeder späteren Analyse eine PCM- und eine RGB-Datei mit Pfad, Bytezahl und
Hash fest binden. Wiederverwendete Inhalte werden je Ereignis regulär analysiert.
Die Dateiauswahl und endgültige Zulassung sind noch nicht erstellt.

| Ereignisse | Gebundene Funktion |
| --- | --- |
| 1–4 | Vier vollständige AV-Wahrnehmungen desselben Dateipaars |
| Schnitt nach 4 | Arm U läuft weiter; Arm S speichert, beendet den Prozess tatsächlich und lädt in einem neuen Prozess |
| 5 | Auditiver Teilhinweis aus derselben PCM-Datei, read-only vor einer weiteren Formation |
| 6 | Visueller Teilhinweis aus derselben RGB-Datei, bestehende Cueform, read-only |
| 7 | Erneute vollständige AV-Wahrnehmung, unveränderte Fortschreibung und regulärer Abschluss |

Profil: bestehendes Halbprofil mit NJ genau einmal vor Audiokontaktbildung,
`ALL_BANDS_24`, unveränderte visuelle/Slow-Verarbeitung und Rangumrechnung;
Konfigurationsdigest
`55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`.
Technische IDs werden vorab neu gebunden. Zeiten vollständig aus
`expected_times(ordinal, kind)` (OB, Zeile 90), auch nach Laden Ordinale 5–7,
nicht erneut 1–3. Keine Medien- oder Wandzeit als Ersatz einsetzen.

Beide Arme verwenden dieselbe logische Ereignis-/Konfigurationsbindung für
vergleichbare native Digests, aber getrennte physische Ablagen und Instanzen.
Arm- und Prozesskennungen stehen in der administrativen Vergleichsbindung.
Eine später erforderliche Zulassung muss beide Arme ausdrücklich abdecken;
keine verbrauchte Lauf-ID oder Autorisierung übernehmen.

## Prüfungen und Grenzen

Vor Ereignis 5: native Memorywerte bitgenau, vollständiger Feldsnapshot,
Streamzähler, Zeiten und Generationskette gleich. Nach jedem Folgeereignis:
Eingangsbindungen, Feld-/Memoryzustände, Transaktionen, Generationen, vollständige
Scans und Hypothese/Enthaltung gegen U vergleichen. Administrative
Prozess-/Speicherbelege dürfen sich unterscheiden, funktionale Unterschiede
nicht durch Toleranzen oder ausgelassene Felder verdecken. Hinweise verändern
Memory nicht; Schließen verändert weder Feld noch Memory.

Eine Enthaltung ist technisch gültig. Der Vergleich verlangt Gleichheit,
nicht einen erzwungenen Treffer oder eine bestimmte Stabilisierung. Die kurze
Folge prüft Fortsetzung vorhandener Evidenz, nicht alle Ablauf-/Ersetzungsfälle.
Zähler- und Generationsmanipulationen sind eigene negative Anschlusskontrollen.

Später neutral getrennt prüfen: beschädigte/abgeschnittene Datei, falscher
Digest, inkompatibles Profil/Schema/Code, vertauschte Präfixbindung, falsche
nächste Ordinale, fehlende Referenz, bereits verbrauchter Checkpoint,
Speicher-/Lesefehler und Übergröße. Vor erfolgreicher vollständiger Prüfung
keine Fortsetzung und kein Payloadzugriff; kein stiller Nullzustandsfallback.
Fehler enthalten Phase, Fortschritt und Budgetteilbeträge, ohne Primärfehler
durch CLOSE/INCOMPLETE zu ersetzen.

Geplanter Arbeitsumfang je Arm: sieben Ereignisse, fünf Formationen, zwei
Hinweise; sechs Audioanalysen/NJ-Projektionen, sechs visuelle Analysen,
2.016 Feldkontakte und vier Scanbelege einschließlich Direktbaseline.
Beide Arme zusammen: 14 Ereignisse, zehn Formationen, vier Hinweise,
4.032 Feldkontakte, acht Scanbelege. Arm S analysiert seinen Präfix nach
Wiederladen nicht erneut. Ein Speicherpunkt, ein tatsächliches Prozessende,
ein Wiederladen; keine automatischen Wiederholungen.

Unveränderte OB-Basisgrenzen: Metadaten 65.536, Quellen 174.080,
gemeinsame Zusatzhülle 262.144, Verifikation 262.144 und Gesamt 4.194.304 Byte;
Memoryzustandsbeleg 98.304 Byte. Keine größeren historischen Medienbudgets
automatisch übernehmen. Physische Doppelablagen, Checkpoint, vollständiger
Feldsnapshot, aktive Quellen-/Qualifikationsreferenzen und alternative
Erfolgs-/Fehlerabschlüsse müssen vollständig gemeinsam bilanziert werden.

**Offene Vorbedingung:** Für den vollständigen Feldcheckpoint und den neuen
Lifecycle-Nachweis liegt noch keine konkrete Ausgabehülle mit abgesicherter
Maximalgröße vor. Bestehende Feldserialisierung ist kein Platznachweis.
Vor späterer Qualifikation deren Klassen, Einzelreserven, sämtliche
Fortschrittsalternativen und separat begrenzte Verifikationsarbeit binden.
Bei Überschreitung stoppen, nicht kürzen, umklassifizieren oder Limits erhöhen.

## Nächste Entscheidung

Kleinster Umsetzungsvorschlag: vorhandene Codecs plus ein versionierter
Checkpoint-/Restore-Anschluss an MR und Caller/OC, mit vollständiger
Präfixbindung und unabhängiger Grenzprüfung. Keine neue Speicherregel.
Jetzt wurde ausschließlich Code gelesen und dokumentiert. Implementierung,
Qualifikation und Funktionsversuch bleiben getrennt freizugeben; Gates False.
