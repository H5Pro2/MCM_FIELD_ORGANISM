# ZW1: Ressourcenplan der gebundenen Forschungsvorbereitung

2026-10-18. Vollständige Zahlen und Grenzen: resource-plan.json.

Fester Forschungsumfang: 16 Paare, 32 Geschichten, genau 64 Policy-Arme mit
64 Live-Referenzen und 64 Archivrekonstruktionen, keine zusätzlichen Messarme.
16 unabhängige Paar-Quellenrekonstruktionen prüfen beide Bedingungen, also
32 Bedingungsquellen; eine unabhängige Interaktions-Statistikreferenz.

Neue tatsächliche neutrale Ausführung: 28 Arme zu je 96 Frames, 28 bestandene
Live-Referenzen, 24 bestandene Arm-Archivreferenzen. Die zwei fehlerhaften
B-Archive wurden vor erfolgreicher semantischer Rekonstruktion abgewiesen.
Der Fristfall erzeugte nur vier Arme; der Quellenfehler keinen. Diese Prüfungen
kommen nicht zusätzlich zur späteren Forschungsserie hinzu. Das abgenommene
Neutralpaket hatte separat 16 Arme; kumulativ sind es 44 kurze neutrale Arme,
keine Forschungsarme. Quellenprimitive wurden zusätzlich nur unter neutralem
Namensraum geprüft; kein vollständiger 1024-Frame-Policyfall wurde ausgeführt.

Gemessener größter gemeinsamer Supervisor-/Worker-Jobpeak: 66441216 Bytes
(rund 63,36 MiB). Alle fünf Jobmessungen unter 536870912 Bytes. Eine Bedingung
wird gemessen/protokolliert, unabhängig archivgeprüft und freigegeben, bevor die
nächste beginnt. Zwischen Bedingungen bleiben nur kompakte Fehlerreihen und
höchstens vier bereits geschlossene Armobjekte bis zur Paarquittung; danach
werden auch diese freigegeben. Es gibt keinen Bestand von 64 lebenden Armen
oder parallel gehaltenen A/B-Archiven.

Lineare Zeitprojektion aus 96 Frames: 1993,69 s für 32 Geschichten.
Planung Faktor acht plus 600 s Quellen/Statistik/Verwaltung: 16550 s,
zuzüglich 3600 s Abschlussreserve innerhalb 57600 s Gesamtgrenze.
Workergrenze bleibt 54000 s. Die neutrale Fristprobe verwendet ausschließlich
für diesen Fehlerfall 30 s; der Forschungsmodus hat keine verkürzte Frist.

Lineare Größen pro Geschichte: gzip 170432 Bytes, encoded 885643,
dictionary 833579, nodes 17984, edges 94827, indices 10187; Observer etwa
4858998 Bytes. Recordmaximum gemessen 16781 Bytes, 14 Collections.
32 Archive linear etwa 5453824 Bytes, unter der 32-MiB-Gesamtgrenze.
32 mal individuelles gzip-Limit ergeben höchstens 16 MiB; Quellen maximal
32 mal 32 KiB = 1 MiB innerhalb der 2-MiB-Gesamtgrenze.

Diese Werte sind Planungen, keine Vollgrößenqualifikation. Kurze Quellen
enthalten keine langen Erhaltungszeugen. Der lineare Mechanismenwert 598 Bytes
ist deshalb keine zulässige Speicherzusage; ER1 beobachtete bis 64087 Bytes
Mechanismen und 4947590 Bytes Observer. Für den Gesamtjob ist insbesondere
ER1s realer Peak 432316416 Bytes (412,29 MiB) zu berücksichtigen. Bis zum
512-MiB-Limit liegen nur 104554496 Bytes (99,71 MiB); das ist keine garantierte
freie Reserve. Neue Wiederkehrmuster, Kompression und Python-Transienten können
den Peak verändern. Keine lineare Extrapolation des neutralen Jobpeaks.

Alle bisherigen Policy-/Codec-/Dateisystemgrenzen bleiben aktiv und werden
in prestart.json gebunden. Keine Erhöhung aufgrund gleicher Armzahl.
Bei Grenzverletzung technischer Abbruch ohne Urteil aus Teilpaaren.
Die reservierte 16-KiB-Terminaldatei bleibt auch bei erschöpftem normalem
Schreibbudget verfügbar. Das absichtliche Budgetfüllartefakt des Negativtests
zählt zur Vorbereitung, nicht als erlaubte Überschreitung einer Forschungsserie.

Der zukünftige Vollgrößenlauf bleibt unbewiesen; dieser Auftrag erzeugt weder
Forschungsberechtigung noch Forschungsquellen. Eine Entscheidung zum Start
ist separat erforderlich und wird durch diese Planung nicht ersetzt.
