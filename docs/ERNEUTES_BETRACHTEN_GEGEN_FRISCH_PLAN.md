# Erneutes Betrachten gegenüber einem frischen System

Ursprünglich statischer Vorschlag vom 19.09.2026. Durch die nachfolgende
ausdrückliche Analystenübergabe sind Vorbindung, minimale Implementierung und
genau eine neutrale Qualifikation freigegeben. Kein realer Vergleichslauf.
Die ursprüngliche [gemeinsame Budgetvorprüfung](../reports/ERFAHRUNGSVERGLEICH_VORBINDUNG_20260919.md)
war nicht tragfähig. Eine nachfolgende ausdrückliche Entscheidung gibt nun
`EXPERIENCE_COMPARISON_24M_V1` für die gemeinsame Nachweisablage frei:
25.165.824 Byte gesamt, 3.145.728 Metadaten, 524.288 Quellen,
786.432 Zusatzhülle, 262.144 Verifikation. Keine Änderung der Einzelbelege,
Memorykapazität oder Decoderlimits. Qualifikation und späterer Lauf samt
temporärer Publikationskopie werden gemeinsam reserviert.
Der Checkpointzweig ist geschlossen; für diesen Vergleich sind weder
Speichern/Wiederladen noch weitere Neustartversuche nötig.

## Offene Frage und Vorbefunde

Verändert eine zusätzliche frühere Betrachtung bei identischen aktuellen
Eingaben den read-only Abruf gegenüber einem erst jetzt gestarteten System?
Gespeicherte Zustände und mehr Support allein sind noch kein Abrufnutzen.

Der abgeschlossene `media-memory-video-20260912-01` bildete Memory, aber seine
vier Hinweise enthielten sich: Audio wegen interner Mehrdeutigkeit, Video
ohne passenden Kandidaten. Es fehlte der frische Vergleichsarm.
`immediate-visual-retrieval-20260912-01` zeigte dagegen Leerabruf und danach
einen eindeutigen A-Abruf unmittelbar nach einer Formation. Dafür wurden
eingefrorene e03-Werte verwendet; das belegt keine Erhaltung über den Verlauf.
Der Checkpointvergleich belegt Fortsetzungsgleichheit, nicht Erfahrungsnutzen.

## Kleinster Vergleichsvorschlag

Dieselbe bereits untersuchte lokale MP4 und der historische Ausschnitt
[0, 5) Sekunden; keine neue günstige Medienwahl. Zehn feste AV-Auswahlen:
100-ms-Audiofenster ab 0; 0,5; ...; 4,5 Sekunden und jeweils der letzte Frame
am oder vor dem Fenstermittelpunkt. Original-PTS, Zeitbasis und bestehende
versionierte Runtimezeitbindung erhalten. Der Bestand ist nicht unabhängig.

- Erfahrener Arm: zehn Formationen aus einer ersten Betrachtung, danach
  dieselbe Folge erneut mit erhaltenem Memory; insgesamt 20 Formationen.
- Frischer Arm: zu Beginn der Vergleichsphase eigener Nullzustand; nur die
  zehn Formationen dieser Phase. Er lernt währenddessen regulär mit und wird
  nicht vor jeder Kontrolle künstlich zurückgesetzt.
- Beide Arme erhalten in der Vergleichsphase dieselben einmal gemeinsam
  gewonnenen, unveränderlichen Wahrnehmungen; getrennte Runtime-, Feld-,
  Memory- und Ownerinstanzen. Keine Übernahme erfahrener Zustände in den
  frischen Arm, keine Gleichheit der Feldtrajektorien voraussetzen.
- Bei Medienzeit 1,0 und 4,0 Sekunden jeweils Audiohinweis, visueller Hinweis,
  dann AV-Formation. Beide Hinweise read-only vor Aktualisierung, Hypothesen
  unangewandt. Bestehende Masken, Halbprofil, Regeln und Direktbaselines behalten.

Damit vorläufig 24 Ereignisse im erfahrenen und 14 im frischen Arm, insgesamt
30 Formationen und acht Hinweise über zwei getrennte Instanzen. Kein einzelner
Arm überschreitet 20 Formationen, zwei auditive oder sechs visuelle Hinweise.
Vor einer Implementierung sind die gemeinsamen Operations-, Quellen- und
Belegbudgets und die identische aktuelle Zeitbindung ausdrücklich zu prüfen;
eine passende Ereigniszahl allein ist keine technische Zulassung.

## Sichtbare Bewertung

Für jede der vier Kontrollstellen beide Entscheidungen nebeneinander zeigen:
Hypothese oder Enthaltung, A-/B-Bereich, tatsächlich passende Kandidaten,
Slotgeneration und belegte Herkunft. Änderungen und Stabilisierung separat
darstellen. Keine semantischen Namen oder Behauptung einer Objektidentität.

Ein möglicher Nutzen ist eine zusätzliche eindeutige, zur vorgebundenen
Wahrnehmungsherkunft passende Hypothese im erfahrenen Arm. Eine beliebige
zusätzliche Zulassung zählt nicht als Erfolg. Hypothesen aus anderen
Spuren, Mehrdeutigkeit, Verluste und fehlender Unterschied werden einzeln
berichtet und nicht gegen Gewinne verrechnet. Die gemeinsame Quellenherkunft
ist eine experimentelle Zuordnung, kein vom System erkannter Gegenstand.
Gleiche Enthaltungen oder zusätzliche Konkurrenz sind reguläre Gegenbefunde.

Noch zu binden: konkrete Manifeste, skalierte Modalitäts-/Runtimezeiten,
vollständige Ressourcenbilanz und Ergebnisanzeige aus den vorhandenen
Schrittbelegen. Keine neue Memoryregel, Auswahlheuristik oder Livequelle.
Die engste Aussage wäre ein kausaler Einfluss der zusätzlichen Betrachtung
auf diese vier Abrufe, keine allgemeine Lern- oder Robustheitsaussage.
