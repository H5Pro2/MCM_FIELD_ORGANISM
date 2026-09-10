# S2-OA: einmaliger Hauptlauf technisch abgebrochen

Lauf-ID: `s2oa-continuous-runtime-20260910-01`.
Genau ein `run_main_once`-Aufruf, danach genau eine unabhaengige read-only
Verifikation in einem separaten Python-Prozess. Kein Retry, keine Korrektur,
keine weiteren Tests oder Analysen. Keine Funktionsauswertung.

## Technischer Befund

Status **NOT_EVALUABLE**. Fehler bei `e01`, Quelle `oa-e01-visual`,
Phase `NJ_CONTACT`, Klasse `S2LMStreamError`, Code `OA_TECHNICAL_ERROR`.
Die Phase umfasst hier die Bindung eines visuellen Hinweises; sie belegt
weder eine ausgefuehrte NJ-Projektion noch einen numerischen Normalformfehler.
Der genaue verletzte Vertrag ist durch diesen Beleg nicht lokalisiert.

Vorher wurden Qualifikationen, administrative Referenzen, historische
Versiegelung, Quellen-, Profil-, Code- und Umgebungsbindungen geprueft.
Die Materialisierung erreichte genau einen hashbestaetigten RGB-Payload und
eine zurueckgekehrte visuelle Analyse. Die nachfolgende Ereignisbindung
scheiterte; kein vollstaendiges Ereignismaterialisat wurde veroeffentlicht.

| Zaehler | Erreicht | Gebunden |
| --- | ---: | ---: |
| Payloads hashbestaetigt | 1 | 48 |
| Direkte Audioanalysen | 0 | 22 |
| NJ-Projektionen | 0 | 22 |
| Visuelle Analysen | 1 | 26 |
| Vollstaendig materialisierte Ereignisse | 0 | 28 |
| Runtimeereignisse / Formationen | 0 / 0 | 28 / 20 |
| Feldkontakte / Scanbelege | 0 / 0 | 8544 / 16 |

Keine Runtime initialisiert, kein Memory-/Feldzustand fortgeschrieben.
Letzter Runtime-Snapshot und finaler Snapshot sind null. Deshalb war kein
Runtime-close aufzurufen. Haupt-, Neutral- und Quellengate sind False.
Rohpayload nicht gespeichert; keine Deduplizierung oder Ersatzquelle.
Die beiden Python-Aufrufe endeten mit Exit-Code 0: Das bestaetigt die
Belegerzeugung, nicht einen erfolgreichen Systemlauf.

## Belege und Aussagegrenze

[Gesamt-/Fehlerbeleg](record.json), [Aufrufbeleg](invocation.json),
[read-only Pruefbeleg](verification.json).
Ergebnisdigest:
`143ec9db2643475345ca2b9900151172ffd67ff21bff4b64a30e28b50627f180`.
Verifikationsdigest:
`c948df447ff726842807bb6b94a425977dc56bd7b80cc53e7250c157415e1baf`.
Der Verifikator akzeptiert die Fehlerform, Status bleibt NOT_EVALUABLE,
`evaluation_allowed=false`. Kein zweiter Verifikationsaufruf.

q01 wurde nicht bis zum Abruf erreicht; q02, q03, q04, q05, q06, q07 und
q08 wurden nicht verarbeitet. Es gibt keine Hypothesen oder Enthaltungen
als fachliche Ergebnisse. Saemtliche vorhergesagten Uebergaenge f01..f20,
Stabilisierung, B4-Verdraengung, Fast-Ablauf, visueller B-Abruf und Slow-
Ersetzung sind in diesem Lauf ungeprueft. Insbesondere kein q05-Beleg und
keine aktuelle q07-Verfuegbarkeit; keine Aussage zu gleicher Slot-ID und
neuer Generation aus diesem realen Lauf. Fruehere neutrale Qualifikationen
bleiben mit ihrem eigenen Umfang unveraendert erhalten.

## Tatsaechliche Artefaktbilanz beim Laufabschluss

Historischer Stand vor dem untenstehenden statischen Nachtrag. Bytes
kanonischer Dateien bzw. des damaligen Abschlussberichts, kein Prozesspeak:

| Klasse / Datei | Byte |
| --- | ---: |
| Referenzierte administrative und Qualifikationsmetadaten | 47135 |
| record.json | 3131 |
| invocation.json | 321 |
| Dieser Abschlussbericht | 4253 |
| Metadaten zusammen, Grenze 65536 | 54840 |
| Vollstaendige historische Quellenartefakte | 162321 |
| NJ-/Formations-/Generationszusatzbelege | 0 |
| Gemeinsame Zusatzhuelle, Grenze 262144 | 162321 |
| Administrative Vorverifikation | 1580 |
| verification.json plus verification.claim | 275 |
| Verifikation zusammen, Grenze 262144 | 1855 |
| Auswertung | 0 |
| Gesamt einschliesslich Referenzen/Abschluss, Grenze 4194304 | 219016 |

Die vollen kuenftigen Reserven bleiben unveraendert. Historische Dateien
werden voll mitgezaehlt, nicht rueckwirkend als budgetkonform umgedeutet.
Keine fachliche Teilauswertung oder Umdeutung des technischen Abbruchs.

RUECKMELDUNG ERFORDERLICH: Analystenentscheidung ueber eine eng begrenzte
statische Klaerung der visuellen Ereignisbindung vor der Runtime. Keine
Korrektur oder weitere Ausfuehrung aus diesem Bericht ableiten.
ME/MI gesperrt, Prognosezweig ruhend; historische Belege und Bootstrap
unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung des technischen
Abbruchbelegs und der Entscheidung ueber die lokale Vertragsklaerung weiter.

## Statischer Nachtrag: visuelle e01-Ereignisbindung

Stand 2026-09-10. Ausschliesslich vorhandenen Code, Plan, Qualifikations-
und Fehlerbeleg gelesen. Keine Imports, Tests, Projektfunktionsaufrufe,
Payloadregeneration, Rezeptorwiederholung oder erneute Verifikation.
Nur dieser Bericht wurde ergaenzt; keine neue Lauf-ID.

### Erste statisch belegbare Vertragsverletzung

Die versiegelte Plan-ID ist `e01`, Ordinalzahl `1`, Ereignistyp
`PARTIAL_VISUAL_CUE`. Der Materialisierer uebergibt diese ID unveraendert
an `bind_input`; dieser uebergibt sie unveraendert an den LM-Builder:
[Materialisierer:190](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2oa_private_main_binding.py:190),
[Bindung:81](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2oa_private_runtime_binding.py:81).

Dessen erste Pruefung ist `_identifier(event_id, "event_id")`:
[Builder:96](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2lm_private_role_free_stream_processor.py:96).
Die Grammatik `^[a-z][a-z0-9-]{7,95}$` verlangt insgesamt 8 bis 96 Zeichen
([Definition:23](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2lm_private_role_free_stream_processor.py:23)).
`e01` hat drei Zeichen. Diese Uebergabe verletzt den Vertrag deterministisch.
Der Code wuerde hier `S2LMStreamError` mit Grund `event_id differs` werfen
(LM:43-49), noch vor Ordinal-, Typ-, Digest- und Payloadpruefung.
Dies ist eine technische ID-Bindungsluecke, kein Wahrnehmungs- oder Memorybefund.

### Pfad und weitere Eingangsbedingungen

1. `LocalChannelGridReceptor.analyze` liefert einen `VisualReceptorState`
   mit 288 lokalen RGB-Kanalmitteln, Profil `VisualGridConfig()`, Index 2
   (finite_video_path.py:191-217). `from_visual_receptor_state` bildet daraus
   einen `ReceptorContactFrame`: `visual.receptor.2`, `video.frame`, [2,3).
   Der Kontaktvalidator prueft Identitaeten, Zeitintervall, eindeutige Carrier,
   Werteform/Normalform und gleiche Carrier-/Wertezahl
   (receptor_contract.py:61-92,212-224).
2. Der Materialisierer erzeugt einen exakten `OrganismTimedReceptorFrame`
   mit OA-Felduhr `s2oa-continuous-field-clock` und [66666666,100000000).
   Erst danach setzt er `NJ_CONTACT` (main_binding.py:185-190). Die gespeicherte
   Phase schliesst bei diesem Codepfad eine zuvor geworfene Ausnahme in
   Kontaktkonversion oder Timed-Frame-Konstruktion aus. Die konkreten
   visuellen Werte sind im Fehlerbeleg dennoch nicht enthalten.
3. `bind_input` verlangt die unveraenderte Halbprofilkonfiguration, Ordinal
   1..28, den exakten Modalitaetsbesatz und Quelldigests. Fuer e01 sind
   `raw_audio=None`, `pcm_digest=None`, ein visueller Frame und dessen
   RGB-Payloadhash vorgesehen. Der versiegelte Hash lautet
   `830042ca17af96f000d69cb56deed1c4507454d69c8461301eedb28ec8dc6d38`.
   Der Kontaktpfad verlangt dieselben nativen/gemeinsamen Fenster sowie
   Profilgeometrie und Carrierreihenfolge (runtime_binding.py:40-53;
   _s2jw_default_live_av_pairing.py:82-102). Dafuer ist kein statischer
   Widerspruch in e01 erkennbar. NJ liegt allein im Audiozweig und wird
   fuer diesen rein visuellen Hinweis nicht aufgerufen (Zeilen 55-60).
4. Die Quelle ist vor Analyse auf Positionen 0..31 okkludiert. Grid,
   Kanalanordnung und Okklusionszellen stimmen mit dem Rezeptor ueberein.
   `bind_input` verlangt Nullwerte an 32..287 und erzeugt ein exaktes
   `MaskedMemoryCue336V1`: 288 Tupelpositionen, beobachtete Werte 0..31,
   sonst `None`. Der KQ-Validator prueft Maskenplan, Wertebereich [0,1],
   Zeiten und Digests (_s2kq_private_partial_cue_retrieval_336.py:412-441).
   Die hier moeglichen OA-/KQ-/Pairing-Fehler sind nicht pauschal LM-Fehler.
   Keine neue numerische Pruefung der historischen Werte wurde vorgenommen.
5. `S2LOFieldInputV1` enthaelt genau diesen zeitgebundenen visuellen Frame,
   Feldschritt [0,100000000) und den Cue-Digest. Das kuerzere visuelle
   Kontaktfenster wird nicht auf den Feldschritt verschoben. Die Operation
   ist der visuelle Cue, kein auditiver oder vollstaendiger AV-Beleg.
   Quellenbeleg: Digest aus Schema, `nj=None`, RGB-Hash und Halbprofil.
   Wahrnehmungs-, Feldprojektions- und Operationsdigest erhalten denselben
   Cue-Digest (runtime_binding.py:69-83). Damit sind die uebrigen LM-Felder
   konstruktiv vorgesehen; ihre LM-Pruefungen folgen erst der ungueltigen
   ID. `ng.pack_input` liegt wiederum danach und ist auf diesem Pfad mit
   `e01` nicht erreichbar. Es liegt kein Erfolg dieser spaeteren Pruefung vor.

### Konkrete Qualifikationsluecke

Die bestandene Hauptanschlussqualifikation
`s2oa-main-binding-qualification-20260910-01` verwendete als erstes Ereignis
ebenfalls einen visuellen Cue, dasselbe Profil, dieselben Fenster, dieselbe
Maske und denselben Materialisierungs-/Bindungspfad. Ihre Quellen waren
neutral-nullwertig; ihre ID war jedoch `neutral-oa-01`, nicht `e01`:
[Testfixture:32](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2oa_private_main_binding.py:32).
Diese 13-stellige ID erfuellt die LM-Grammatik. Historische Bindungen wurden
zwar lesend geladen, fuer den funktionalen Aufruf aber durch den neutralen
Plan ersetzt (Test:73-96). Die reale kurze Plan-ID erreichte dabei nicht
den LM-Builder. Die 14/14 bleiben fuer die geprueften Eingaben gueltig;
sie qualifizieren diese konkrete Plan-ID-Uebergabe nicht. Der weitere
Unterschied Nullbild/realer okkludierter Inhalt ist kein Beleg eines
numerischen Fehlers und wird nicht zur Ursache erklaert.

### Historische Attribution und engste Korrekturrichtung

Bewiesen ist die statische ID-Vertragsverletzung auf dem gebundenen Pfad.
Sie passt zur protokollierten Klasse und Phase. Nicht gespeichert wurden
jedoch Originalfehlermeldung, Ausloesestelle oder Zwischenargumente;
der Handler behaelt nur Klasse und generischen Code (main_binding.py:277-288).
`event_id differs` ist deshalb hier eine Ableitung aus Code, kein Zitat der
historischen Exception. Fuer eine unmittelbar belegte historische Zuordnung
fehlt mindestens der originale Pruefgrund oder die symbolische Ausloesestelle.
Eine erneute Rezeptoranalyse ist zum Nachweis der ID-Luecke nicht erforderlich.

Moegliche engste Korrekturrichtung, noch nicht umgesetzt oder qualifiziert:
versiegelte Plan-ID erhalten und eine explizite versionierte technische
Runtime-ID-Bindung einfuehren. Sie muss Planwurzel, Plan-ID und Ordinal mit
der LM-konformen ID verbinden. Nicht nur am Erzeuger umbenennen: Die derzeit
identische ID verlangenden Anschlusspruefungen muessen dieselbe Bindung
pruefen (main_binding.py:204; main_verification.py:46). Keine globale
Lockerung der LM-Grammatik, keine neue Quellenversiegelung. Eine spaetere
neutrale Kontrolle muss die reale kurze Plan-ID an dieser Grenze enthalten.
Weitere Anschlussfolgen waeren im freizugebenden Korrekturumfang zu pruefen;
dieser Nachtrag behauptet keine Hauptlauffaehigkeit nach einer Einzelaenderung.

Der historische Status bleibt **NOT_EVALUABLE**. Ergebnis-, Aufruf- und
Verifikationsdateien unveraendert; keine funktionale Teilauswertung.
Gates False, weiterer Hauptlauf gesperrt; ME/MI gesperrt, Prognosezweig ruht.

Dokumentarische Bilanz nach Nachtrag (Dateigroessen, keine erneute
Belegverifikation): Bericht 12023 Byte; Metadaten 62610 Byte;
Gesamt mit unveraenderten Referenzen 226786 Byte. Zusatzhuelle 162321 Byte
und Verifikationsbelege 1855 Byte unveraendert. Urspruengliche Grenzen gelten.

RUECKMELDUNG ERFORDERLICH: Entscheidung ueber die eng begrenzte technische
ID-Bindung oder einen gezielten Diagnosebeleg. Keine Ausfuehrungsfreigabe.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zur belegten
Plan-/Runtime-ID-Luecke und ihrer bislang ungeprueften Uebergabe weiter.
