# S2-NG: Statische Runtime-Anbindung einer fest gebundenen auditiven A-Regel

## Status und Grenze

Nur Anbindungsplan, Quellenstand `6fb6b9a`. Keine Implementierung, Tests,
Quellenmaterialisierung, Distanzanalyse oder Runtimeausfuehrung. Keine neue
Lauf-ID; diese wird erst fuer einen separat freigegebenen Vergleich gebunden.

S2-NF bleibt unveraendert abgeschlossen: unter realer Konkurrenz
`N=5,D=4,R=4,L=0`, darunter drei tatsaechlich variierte Hinweise.
Eine Fehlzulassung nach Zielentfernung wurde verhindert. Die Partialaddition
verliert aber ihre Zielanwendbarkeit; mangels richtigem Referenzabruf ist
dort `D=0`, Erhaltung nicht geprueft. Kein weiterer NF-Lauf oder Ersatzreiz.
Das ist keine allgemeine Verlustfreiheit und keine neue Lernregel.

## Kleinste vorhandene Anschlussstelle

`MinimalMCMRuntime336` in `tools/_s2mr_private_minimal_mcm_runtime.py`
nimmt bereits einen `RoleFreePerceptionStreamProcessor` entgegen. Dessen
Konstruktor besitzt getrennte `auditory_scan`-/`auditory_baseline`-Adapter.
Deshalb bleiben S2-MR, S2-LM, bestehende Defaultadapter und ihre APIs
unveraendert. Keine neue Memoryebene und kein Monkeypatching.

Spaeter genuegt eine kleine private Komposition zweier Audioadapterpaare:

| Vorab festgelegter Arm | Auditive A-Anwendbarkeit in B4/Fast |
| --- | --- |
| HISTORICAL_SUM_L1_24 | `sum(delta_i in Reihenfolge 0..23) / 24 <= 0.2` |
| ALL_BANDS_24 | `max(delta_i fuer 0..23) <= 0.2` |

Beide verwenden unveraendert `tools/_s2ne_private_auditory_transfer.py::retrieve`
und die unabhaengige `direct_retrieve` aus
`tools/_s2ne_private_direct_and_verification.py`. Die Referenz delegiert
bereits an S2-KZ und bleibt historisches Binary64-`sum`, NICHT
`statistics.mean`. Keine dritte Regel, Rundung, Gewichtung oder neue Schwelle.

Die Adapter reichen `AuditoryCueOperationV1`, State und Bandplan unveraendert
weiter. Aus `arm.evidence` entsteht `StreamScanResultV1`; sein Receiptbezug
bindet `arm.arm_digest` und damit die Regelidentitaet. Vollstaendige Scanbelege
bleiben fuer Verifikation und Kandidatenbewertung erhalten. Hypothesen
behalten die vorhandene exakte visuelle/auditive Typunion.

Regel-ID, Bandplan, Memorykonfiguration und Implementierungshashes werden
unveraenderlich vorab an Adapter und Runtime-`component_binding_digest`
gebunden. Widersprueche scheitern vor Ereignisverarbeitung. Kein
Regelparameter am Hinweis, Wechsel, Fallback oder Kombinieren der Regeln.

## Unveraenderte Geschwisterzweige

Auditory-Slow behaelt `sum(delta_i)/24 <= 0.02`. Vollstaendige 9/3/8-Scans,
A-Aufloesung, volle 48-Werte-Kandidatengleichheit und A/B-Entscheidung bleiben
gleich, ohne B-Vorrang. Dasselbe gilt fuer visuelle S2-KQ-Adapter/Baseline,
Rezeptoren, Quellenzeiten, S2-LO-Feld- und atomaren S2-JW-Memoryadapter.
Nur Formationen schreiben Memory; Hinweise sind read-only. Feldkontakt
bleibt von Memory-/Scanfehlern unabhaengig. Keine Hypothesenanwendung,
Vervollstaendigung, Rueckwirkung oder Sequenz-/Praegungsmechanik.

## S2-MT: Wiederverwendbar als begrenzter Transfervergleich

Die bestehende skalierte Quellenwurzel wird unveraendert uebernommen:
Plandigest `3b749837273f9cfb1af4ac50659881c48a4a113384d65999dc90e922b46fd26c`.
Faktor `0.989912331104279` mit der vorhandenen Float32-Bindung `e56a7d3f`
und unveraenderter Multiplikationsfolge. Kein erneutes Siegel oder Quellenentwurf.
Der bereits gespeicherte `presealed_source_plan` in Lauf 05 ist die
Quellenreferenz; keine alten Memoryzustaende oder Hypothesen werden geladen.
Auswertungsrollen aus alten Belegen werden nicht in den Runtimepfad uebernommen.

Literale Formationsfolge e01..e20:

```text
n00 n01 n02 n00 n01 n02 n00 n01 n02 n00 n01
n03 n04 n05 n06 n07 n08 n09 n10 n11
```

Teilhinweise e21..e28: n00 Audio/Video, n01 Audio/Video, n02 Audio/Video,
n12 Audio/Video. Die neutralen Ereignisspezifikationen, die Feldclock
`s2mt-transfer-field-clock`, nativen Cue-Uhren, Zeitwerte und Masken bleiben
unveraendert. Im spaeteren Lauf nur einmal gemeinsame Materialisierung;
Payloadhashes vor Rezeptoraufrufen pruefen, Rohdaten danach verwerfen.
Beide Arme erhalten exakt dieselben unveraenderlichen Materialisate.

`_materialize_events` und `_build_event` sind wiederverwendbar. Der alte
Haupteinstieg bindet dagegen Lauf 05 und einen Prozessor: nicht aufrufen,
umetikettieren oder patchen. Eine kleine Vergleichskomposition verwendet
die Bausteine. Quellen-/Form-/Zeitpruefungen bleiben verpflichtend;
erwartete Treffer oder bessere Konkurrenztrennung sind kein Startgate.

Zwei vorab gebundene, getrennte Runtimeinstanzen, je Budget 28, erhalten
jeweils frische Nullfelder und frische Memoryzustaende, getrennte Adapter-
und Ownerobjekte. Beide durchlaufen dieselben 20 Formationen und acht
Hinweise, dann jeweils `close()`. Kein State-Sharing oder Ergebnis des
einen Arms als Eingabe des anderen. Feld-/Memorykomponenten muessen an den
korrespondierenden Ereignissen identisch bleiben; armgebundene Runtime-
und Receiptgesamtdigests muessen gerade nicht identisch sein.

Umfang pro Arm: 28 Ereignisse, 20 Formationen, 8.064 Feldkontakte,
acht Primaer- und acht Direktbaseline-Scans. Gesamt: 56 Runtimeereignisse,
40 Formationen, 16.128 Feldkontakte, 32 Scans; davon 16 auditive und
16 visuelle. Quellenmaterialisierung wird nicht je Arm wiederholt.
Limits: Audioarm <32.768 Byte, Runtime-Step <65.536 Byte, atomarer Gesamtbeleg
innerhalb der vorhandenen 4-MiB-Obergrenze. Keine Recorderplattform; eine
read-only Gesamtpruefung, danach getrennte Auswertung. Serialisierung und
Scanbudgets gehoeren zur neutralen Kompositionsqualifikation.

## Bewertung ohne verdeckten Erfolgsvorbehalt

Nur der Auswerter kennt n00/n01 als stabile Ziele, n02 als instabile Spur
und n12 als unbekannte Kontrolle. Erwartung bleibt Support 3/3/2 in beiden
Slow-Banken, Verlust aller drei Lerninhalte aus A und unveraenderte visuelle
Ergebnisse. Die historischen Lauf-05-Hypothesen/Enthaltungen sind lediglich
Vergleichsbefunde; die neue Referenz wird real ueber dieselbe Runtime ausgefuehrt.

Alle acht Hinweise, beide Regelarme und jeweils ihre Direktbaseline bleiben
vollstaendig auswertbar. Pro auditivem Hinweis aufzeichnen:

- alle B4-/Fast-/Slow-Treffermengen, Kandidaten-/Slotdigests und Statistikwerte;
- neuer korrekter Abruf, bisher richtiger und erhaltener/verlorener Abruf;
- Zielkandidat anwendbar/nicht anwendbar je Bank, getrennt von Gesamtzulassung;
- Fehlzulassungen, interne/oeffentliche Mehrdeutigkeit und andere Enthaltung.

Ein ausgeschlossener Zielkandidat bei schon enthaltender Referenz ist kein
verlorener richtiger Abruf, bleibt aber sichtbar. Gewinne, Verluste und
verhinderte Fehlzulassungen nicht saldieren.

N/D/R/L nach Modalitaet und belegter Konkurrenz ausweisen; `D=R+L`.
Historisch hatte S2-MT **null korrekte auditive Referenzabrufe**. Bleibt das
so, ist auditive Erhaltung hier **ERHALTUNG_NICHT_GEPRUEFT**. Visuelle
Kontrolltreffer duerfen diesen Nenner nicht auffuellen. Ein Nutzen waere
ein neu korrekter auditiver Abruf ohne neue Fehlzulassung; sein Ausbleiben
ist ein regulaerer negativer Transferbefund, keine Quellenunverfuegbarkeit.

Der Verifikator akzeptiert jede erlaubte, gueltig gebundene Enthaltung.
Er prueft Vollstaendigkeit, Quellen, Regeln, Baselines, Lifecycle und
Read-only-Zustaende ohne Rezeptor-, Memory- oder Abrufwiederholung.
Fachliche Vorhersageverfehlungen verbleiben ausschliesslich beim Auswerter;
Quellen-, Bindungs-, Ressourcen- oder Ausfuehrungsfehler sind NOT_EVALUABLE.

## Lesend gebundene Anschlussdateien

| Datei | SHA-256 |
| --- | --- |
| tools/_s2mr_private_minimal_mcm_runtime.py | da7699b6ef2a17c3b241f257a8aa9c954439e8a2b5cc37dab2a372a7691cf49f |
| tools/_s2lm_private_role_free_stream_processor.py | 84c5650f7f52fe13eb0b8248ab73656dbb67f17fbdd93b2dfc520bacfec7e127 |
| tools/_s2ne_private_auditory_transfer.py | b3370f21888cba0614f039b51f8c730c582fc38470c04c7a0f288c688530445e |
| tools/_s2ne_private_direct_and_verification.py | f61af9ab518c82e97a3fe96e3ba43e7fe0318f01899156070bb181d929c81c27 |
| tools/_s2mx_private_scaled_transfer_sources.py | 56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674 |
| reports/s2mt/s2mt-presealed-transfer-runtime-20260906-05/result.json | 2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f |

Lauf 05 bleibt S2MT_FUNCTION_FALSIFIED; fruehere technische Abbrueche und
S2-NF bleiben unveraendert. Wiederverwendung prueft technische Uebertragung,
keine unabhaengige Generalisierung oder allgemeine Produktreife.

RUECKMELDUNG ERFORDERLICH: Freigabe der kleinen privaten Komposition und
neutralen Qualifikation. Ein spaeterer Hauptvergleich benoetigt zusaetzlich
eine eigene Lauf-ID und separate Einmallauffreigabe. Alle Gates bleiben False.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser schmalen
Runtime-Anbindung und gegebenenfalls ihrer privaten Implementierung weiter.
