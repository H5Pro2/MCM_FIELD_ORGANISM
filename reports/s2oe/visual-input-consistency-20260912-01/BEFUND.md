# Visuelle Eingangskonsistenz: einmaliger Realvergleich

RECORDING_COMPLETE; anschließend genau eine unabhängige read-only
Verifikation EVIDENCE_VALID und eine getrennte Auswertung.
Vier unabhängige Worker, acht visuelle Analysen, keine Memory-/Feldaufrufe.
Quelle unverändert wiederverwendet. Kein Retry oder Parameterwechsel.

| Auswahlzentrum | Referenz-PTS | Wiederholungs-PTS | Zeitbasis |
| --- | ---: | ---: | --- |
| 1,05 s | 31031 | 31031 | 1/30000 |
| 4,05 s | 121121 | 121121 | 1/30000 |

Fensterstarts bleiben 1,0 und 4,0 s. Die PTS wurden beobachtet, nicht
erzwungen; sie stimmen hier auch mit den historischen Referenzen überein.
Native Plane-Bindungen ohne Padding und konvertierte RGB-Hashes stimmen
jeweils überein. Beide vollständigen Rezeptorvergleiche sind bitgleich:
je 288 Werte. In allen vier Vollbild-/Okklusionsvergleichen bleiben die
32 sichtbaren Werte bitgleich. Keine abweichende Position festgestellt.
Alle 2.304 Werte liegen verlustfrei als Binary64-Hex vor.

Gesamter Decoderfortschritt: 33 + 33 + 123 + 123 = 312/400 Frames;
vier ausgewählte Frames. Prozessmaximum 593.944.576 und Jobmaximum
600.514.560 Byte, jeweils unter 1.073.741.824 Byte. Alle Worker geschlossen,
Gates False. Kein Audio-/NJ-Eingang und keine Rohbildablage.
Decoder-Lesemenge 372.251.572 Byte; zusätzliche Vorstart-Hashlesung
83.498.438 Byte. Ursprüngliche MP4 bleibt externer Eingangsbestand.

Die unabhängige Prüfung rekonstruiert die gespeicherten Binary64-Werte
und 704 Gleichheitskomponenten. Native/RGB-Hashes und Rezeptorzustandsdigests
sind Herkunftsbindungen: keine zweite Dekodierung oder Rezeptorrekonstruktion
im Verifikator. Seine Prüfung ersetzt keine nachträgliche Rohbildmessung.

Ergebnis: An diesen zwei Stellen ist die Eingangsfolge reproduzierbar und
die sichtbare Okklusionsprojektion konsistent. Das ist kein allgemeiner
Reproduzierbarkeitsbeweis, keine historische Fehlerursache und kein
Wiedererkennungsnachweis. Die historischen Enthaltungen bleiben unverändert.
Insbesondere wird kein fehlender historischer Einzelwert rückwirkend ergänzt.

Record-SHA-256:
70e59692dcf386472ce2fb6a037d3033f283f53ec55e820844023ffb3a46d27d.
Verifikation-SHA-256:
0cf7dece7f9570055cf788dfaa04aa67790ce44b5f84fb6606eef5ae75a6dffb.
Qualifikation und Profil: ../visual-completion-qualification-20260912-01/
execution-binding.json; Freigabe einmalig durch Analystenübergabe erteilt.
