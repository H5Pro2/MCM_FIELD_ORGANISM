# FIELD_CHECKPOINT: Anschluss vorbereitet, Qualifikation nicht gestartet

Auftrag `MEMORY-SPEICHERN-WIEDERLADEN`, 12.09.2026.
Bezugscommit weiterhin `537109994cf777f8d36cda617aafe12226806c25` mit
vorhandenem dirty Arbeitsbaum. Historische Dateien und Validatoren unverändert.
Private Klasse `FIELD_CHECKPOINT.v1`, Schutzdeckel 524.288 Byte.

## Vollständige Feldformatrechnung

[Reproduzierbare reine Format-/Budgetrechnung](prepare_checkpoint_budget.py),
ohne Projektimporte, Rezeptoren, Memory- oder Feldfortschreibung:

| Bestandteil | Obere Bytezahl |
| --- | ---: |
| 336 Neuronen einschließlich 1.230 lokaler Samples | 375.337 |
| Beide Docks einschließlich aller Carrier-/Neuronpaare | 39.911 |
| Layer, Dockliste, Offsets, leere periodische Achsen, Schema und Zeitdistribution | 11.332 |
| Vollständige native Feldhülle | **426.580** |
| Schutzdeckel | **524.288** |

Geltung ausschließlich für das fest gebundene schema-1-OB-Feld: Audiozeile
48, Visualgeometrie 12×8×3, feste Feld-/Layer-/Neuronidentitäten,
höchstens 28 Ereignisse, leere Boundary-Kontaktliste des transienten Adapters.
Kein Substrat-/Development-Schemawechsel. Native Floattexte werden konservativ
mit 24 Zeichen plus zwei zusätzlichen Platzhalter-Anführungszeichen bilanziert;
endliche Python-Binary64-Zahltexte benötigen diese zusätzliche Quotehülle nicht.
Carrier-/Geometriekennungen sind mit 80 ASCII-Zeichen abgedeckt,
Feldzeitwerte mit zehn Dezimalstellen, Neuronticks mit zwei.
Die 192.870 Byte bleiben die frühere reine Untergrenze.

Dies ist eine Formatobergrenze unter diesen Bindungen, keine gemessene
Checkpointdatei und kein allgemeiner Größenbeweis für beliebige Feldschemas.
Die fertiggestellte Restore-Prüfung muss diese Formbedingungen ausdrücklich
durchsetzen; eine Digestprüfung allein ersetzt sie nicht.

## Vorbereitung und korrigierter Vorabstopp

Neue, noch unqualifizierte Dateien:

- [Checkpointanschluss](../tools/_memory_checkpoint.py): native Codecs,
  gesonderter Runtime-/Caller-Wiedereinstieg, Präfixprüfung, einmalige
  Consume-Bindung und atomare Veröffentlichung über eine vollständige temporäre
  Datei; historische Einstiege unverändert.
- [16 vorbereitete Kontrollgruppen](../tests/test_memory_checkpoint.py):
  vier neutrale Endpunktereignisse, Unterbrechung nach Ereignis eins;
  zwei Fortsetzungsarme mit tatsächlich getrennten Interpretern vorgesehen.
  **Noch kein Prozessvergleich ausgeführt.** Keine realen Aufruferdateien.
- [Dateigebundener Qualifikationsaufruf](qualify_checkpoint_once.py) mit
  Quelleninventar und Einmalmarkierung. Keine Aufrufmarkierung wurde erzeugt.

Die erste [Vorregistrierung](memory-checkpoint-qualification-20260912-01/preregistration.json)
meldete READY anhand ihrer Gesamt-/Quellenrechnung. Die anschließende
Klassenprüfung zeigte eine ausgelassene Metadatenaddition. READY wird daher
**nicht als gültige Testzulassung verwendet**; die Datei bleibt als Vorabstand
erhalten. [Vorabstopp](memory-checkpoint-qualification-20260912-01/precondition-stop.json).
Der Aufrufcode wurde um diese Prüfung ergänzt, seine vorherige Quellenbindung
ist damit ebenfalls nicht mehr aktuell. Kein Testaufruf, keine Wiederholung.

| Gemeinsame Reserve | Byte |
| --- | ---: |
| Beide neutralen Armbelege | 1.198.072 |
| Checkpoint einschließlich vollständigem Präfix | 725.588 |
| Zusätzlich gezählte temporäre Checkpointdatei | 725.588 |
| Verifikation gemeinsam | 262.144 |
| Quellenanhang des vorbereiteten Standes | 44.330 |
| Zusätzliche Metadaten/Logs | 65.536 |
| Abschluss | 4.096 |
| Gesamt des vorbereiteten Standes | **3.025.354 / 4.194.304** |

Die eingebetteten Metadaten sind bereits in diesen Dateireserven enthalten;
ihre folgende Klassensumme wird **nicht erneut zur Gesamtsumme addiert**:
65.536 Armmetadaten + 32.768 Präfixmetadaten + 32.768 Checkpointadministration
+ 65.536 Qualifikation/Logs + 4.096 Abschluss = **200.704 / 65.536 Byte**.
Die Metadaten-Vorreserve liegt somit **135.168 Byte über der Grenze**.
Dies ist keine gemessene Dateigröße oder notwendige Mindestbelegung.
Die inzwischen geänderte Aufrufdatei verlangt vor einem Start eine aktualisierte
vollständige Quellen- und Größenbindung; die Tabelle ist der erhaltene Vorabstand.

## Gesammelte Restarbeiten

Keine Erhöhung des Feldschutzdeckels erforderlich. Die administrative
Vorreserve ist noch nicht tragfähig: tatsächliche feste Metadatenformen
herleiten und vorhandene gemeinsame Referenzbindung verwenden, statt pauschal
je Beleg 32 KiB zu beanspruchen. Vollständige Erfolgs-/Fehlerformen und temporäre
Dateien weiterhin mitführen; ungezählte Auslagerung ist keine Lösung.

Der neue Anschluss ist derzeit ausdrücklich **NEUTRAL_ENDPOINTS**, nicht die
fertige Aufruferzulassung: reale Materialisierer-/Lesekonten und deren Restore
sind noch anzubinden. Feldformprüfung, Primärfehlerabschluss und gemeinsames
Istledger müssen vervollständigt werden, bevor die vorbereiteten Prüfgruppen
einen vollständigen Anschlussnachweis bilden können. Keine dieser Lücken
wird durch einen Codec-Rundlauf oder historische Passzahlen ersetzt.

Der reale Sieben-Ereignis-Vergleich bleibt gesperrt. Dessen bisherige
konservative Gesamtreserve ist ebenfalls kein fertiger Laufnachweis.
Jetzt erfolgten nur Quelltextvorbereitung und administrative Formatrechnung;
keine Qualifikation, kein nativer Prozesslauf, keine Gateöffnung. Kein Erfolg
und keine technische Gültigkeit des neuen Restore-Anschlusses behauptet.
