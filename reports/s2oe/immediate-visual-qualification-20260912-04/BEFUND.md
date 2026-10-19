# Präsentationszeitbindung neutral qualifiziert

`immediate-visual-qualification-20260912-04`: genau ein Aufruf, **22/22**
bestanden; alle 22 Testkörper erreicht. Die bisherigen 18 Gruppen wurden
beibehalten und um vier Präsentationsprüfungen ergänzt. Kein Retry.

## Herkunft und Präsentation

Version `s2oe.frozen-presentation.v1` bindet drei eigene Präsentations-IDs:
Leerhinweis [9,10), Formation [14,15), Wiederhinweis [15,16) auf `video.frame`.
Die Sitzungsfenster sind getrennt gebunden: [300000000,333333333),
[466666666,500000000), [500000000,533333333) ns. Die AV-Formation enthält
Audio [19200,24000) auf `audio.sample`, Sitzung [400000000,500000000).
Das sind Präsentationen gespeicherter Werte, keine neuen Messungen.

Der vollständige historische Eingang bleibt unverändert erhalten. Jeder
Präsentationsbeleg bindet Eltern-SHA, historischen Ereignisdigest, vollständige
historische Framebindung und vollständige Wertedigestbindung. Neue Zeit- und
Präsentationsdigests ersetzen keine historischen Digests. Die Formation
verwendet neue Kontakt-Snapshot-IDs; der Cue bindet den neuen Präsentationsdigest
und erhält ausschließlich 32 sichtbare Werte, der Rest bleibt None.

Die neuen Tests bestätigen unveränderte Herkunft/Wertebindung, unterschiedliche
Präsentations-IDs und Digests, Ablehnung fremder Herkunft, veralteter nativer
Wiederhinweiszeit und widersprüchlicher Sitzungszeit. Zeitmanipulationen werden
auch mit neu berechnetem Manipulationsdigest abgewiesen. Die bestehenden
nativen Validatoren wurden nicht geändert. Ihre historische Ablehnung der
alten Cuezeit bleibt im 17/18-Fehlbefund erhalten; keine Umdeutung dieses Laufs.

## Tatsächlich erreichte native Kontrolle

Ein synthetischer AV-Eingang wurde regulär rekonstruiert und geformt.
Leerabruf: ABSTAIN_NO_CONTEXT. Unmittelbarer Wiederabruf: ADMIT_SINGLE_CONTEXT.
Primär- und Direktbaseline stimmen in den geprüften Entscheidungs-,
Kandidatenzahl- und Zustandsdigestfeldern überein. Hinweise erhalten Memory
unverändert; die tatsächliche Formation liegt zwischen den beiden Abrufen.
Keine direkte Slotbefüllung, keine Hypothesenanwendung.

Eine synthetische NJ-Projektion nur zum Aufbau der neutralen Fixture; keine
NJ-Projektion im eingefrorenen Kontrollpfad. Eine Formation, vier vollständige
Scans. Null Medien-/Rezeptor-/Feldaufrufe. Zustands-, Formations-, Scan- und
393.216-Byte-Gesamthüllengrenzen wurden im nativen Test tatsächlich geprüft.
Die einzelnen nativen Serialisierungsgrößen wurden nicht separat gespeichert;
der Befund behauptet deshalb nur das geprüfte Einhalten dieser Grenzen.

## Bilanz und Quellenstand

Vorbilanz **2.127.565 / 4.194.304 Byte**. Qualifikationsmetadatenreserve
98.304 / 131.072, Quelleninventar 10.027 / 174.080, gemeinsame Zusatzreserve
14.123 / 262.144, Verifikationsreserve 262.144. Die eigene historische
Eingangsbelegklasse enthält den vollständigen Elternrecord mit 1.359.778 Byte.
Reale Sitzungsmetadaten bleiben auf 65.536 Byte begrenzt.

Inventar vor/nach identisch:
`d29484a68d0a492e187d8c84d752e6d91c7d664ada6f34d2f7e1ed5287960825`.
Präregistrierung:
`bf81aa4a3559a5e8649db43b1f4d8c85c9dcd11e93c8d55823568d3016348a44`.
Vollständiges Log 2.674 / 65.536 Byte; keine Kürzung oder Verpackung.
Die vollständige Istbilanz steht in `final-balance.json`.
Vorbereitung: einmaliger administrativer Elternlesezugriff, 1.359.778 Byte;
null Zugriffe auf den realen Elternrecord im Test.

## Grenze

Kein realer e03-Abrufbefund. Diese Qualifikation belegt die geprüfte neutrale
Rekonstruktions-/Formations-/Präsentationskomposition, nicht einen neuen
Medienpfad oder allgemeine Wiedererkennung. Ein realer Einmaleinstieg mit
Publikation, unabhängiger Gesamtverifikation und eigener finaler Laufbindung
ist damit nicht automatisch freigegeben. Gates False; reale Kontrolle gesperrt.
