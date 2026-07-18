# Forschungsreihe des gemeinsamen MCM-Feldes

Dieser Ordner enthält ausschließlich Methodiken, Register und Befunde, die
unter der aktuellen Ein-Feld-Architektur neu entstehen.

Die Reihe verwendet das Präfix `GF`. Alte Versuche werden weder kopiert noch
umbenannt. Ihre zulässige Verwendung regelt die
[Evidenzgrenze](../EVIDENZGRENZE_GEMEINSAMES_MCM_FELD.md).

## Aktueller Stand

- Die technische Audio-Video-Strecke erreicht ein gemeinsames MCM-Feld.
- Die Aufnahmen überlappen real, sind aber noch nicht zustandsgenau zeitgepaart.
- [Technischer Zeitaudit 001](TECHNISCHER_ZEITAUDIT_001.md) zeigt bei realem
  Gerätezugriff null eindeutige 1:1-Zustandspaare und eine starke Abweichung
  zwischen nominaler und tatsächlicher visueller Zustandszeit.
- [Technischer Fensteraudit 002](TECHNISCHER_FENSTERAUDIT_002.md) zeigt, dass
  vorab gemeinsame reale Fenster ausführbar sind, aber weiterhin viele native
  Zustände jedes Docks enthalten und daher noch keinen Feldtakt bilden.
- [Technischer Ereigniszeitaudit 003](TECHNISCHER_EREIGNISZEITAUDIT_003.md)
  zeigt, dass verlustfreier asynchroner Eintritt möglich ist, ein Feldschritt
  je Ereignis die innere Tickzahl aber zu rund 95 % an Audio binden würde.
- [Technische Rateninvarianzprüfung 004](TECHNISCHE_RATENINVARIANZPRUEFUNG_004.md)
  trennt verstrichene Dauer, Ereignisanzahl und irreversibel ausgelassenen
  Weltkontakt mit der bekannten passiven B1-Baseline.
- [Technischer Zeitspannenvertrag 005](TECHNISCHER_ZEITSPANNENVERTRAG_005.md)
  reicht gemessene Dauer optional und atomar an alle Neuronenvorschläge
  weiter, ohne sie zu speichern oder mechanisch auszuwerten.
- [Technische Feldzeitpartition 006](TECHNISCHE_FELDZEITPARTITION_006.md)
  zerlegt einen realen Horizont lückenlos an nativen Abschlussgrenzen und
  weist deren weiterhin bestehende Rezeptorratenabhängigkeit aus.
- [Technische Rezeptorstütze 007](TECHNISCHE_REZEPTORSTUETZE_007.md) trennt
  Audio-Samplefenster, Video-Frameidentität, nominelle Perioden und technische
  Read-Dauer von einer noch unbelegten Weltstütze auf der Organismusuhr.
- Der gemeinsame Feldzustand verwendet bisher eine zustandslose
  Rezeptorprojektion.
- [Technischer asynchroner Docknachbarschaftsaudit 015](TECHNISCHER_ASYNCHRONER_DOCKNACHBARSCHAFTSAUDIT_015.md)
  zeigt, dass lokale Rezeptornachbarschaft in der globalen Abschlussfolge
  ratenabhängig unterbrochen wird.
- [Technische verlustfreie Vorschlagsübergabe 016](TECHNISCHE_VERLUSTFREIE_VORSCHLAGSUEBERGABE_016.md)
  bewahrt vollständige reduzierte Dockfolgen über unterschiedliche
  Vorschlagssegmentierungen, noch ohne Feldverarbeitung.
- [Technische Feldeingangs-Kapazitätsfalsifikation 017](TECHNISCHE_FELDEINGANGS_KAPAZITAETSFALSIFIKATION_017.md)
  zeigt, dass die aktuelle Einzel-Frame- und Skalarschnittstelle solche Folgen
  nicht in einem atomaren Feldvorschlag darstellen kann.
- [Technischer Zeitträger-Architekturabgleich 018](TECHNISCHER_ZEITTRAEGER_ARCHITEKTURABGLEICH_018.md)
  hält Sequenzträger und lokale asynchrone Wirkung wegen ihrer offenen
  Ratenabhängigkeit als Runtimezweige geschlossen.
- [Funktionaler Zeitwirkungsvertrag 019](FUNKTIONALER_ZEITWIRKUNGSVERTRAG_019.md)
  trennt Darstellungsinvarianz von Ordnungszugänglichkeit in einer vollständig
  gestützten synthetischen Kontaktwelt.
- [Passive Zeitrepräsentations-Scheiterkarte 020](PASSIVE_ZEITREPRAESENTATIONS_SCHEITERKARTE_020.md)
  zeigt, dass Segmentanzahl, Endpunkt und zeitgewichteter Mittelwert nicht
  beide Vertragsachsen tragen. Die vollständige bekannte Stützbahn trägt sie
  nur als variable Ground Truth, nicht als freigegebene Runtime.
- [Passive Kompaktzusammenfassungs-Kollision 021](PASSIVE_KOMPAKTZUSAMMENFASSUNGS_KOLLISION_021.md)
  lässt zwei verschiedene Zeitumkehrungen trotz eines festen Bündels aus 13
  üblichen Verlaufskennwerten kollidieren und isoliert fehlende Zeitrichtung.
- [Passiver gerichteter Zeitmoment-Abgleich 022](PASSIVER_GERICHTETER_ZEITMOMENT_ABGLEICH_022.md)
  bewahrt eine gerichtete Zeitprojektion rateninvariant, zeigt aber zugleich
  eine andere Ordnungskollision desselben skalaren Moments.
- [Exakter linearer Zeitprojektions-Nullraum 023](EXAKTER_LINEARER_ZEITPROJEKTIONS_NULLRAUM_023.md)
  zeigt per Rang und Nullität, warum jede feste endliche lineare Bank bei
  ausreichend reicher Geschichte nichttriviale Kollisionen besitzen muss.
- [Funktionaler Geschichtsäquivalenzvertrag 024](FUNKTIONALER_GESCHICHTSAEQUIVALENZVERTRAG_024.md)
  verlangt Geschichtstrennung nur bei kausal verschiedener späterer
  Feldwirkung und verbietet vollständige Archivierung als Forschungsziel.
- [Aktuelle Feldruntime-Geschichtsnullfunktion 025](AKTUELLE_FELDRUNTIME_GESCHICHTSNULLFUNKTION_025.md)
  zeigt nach vollständiger natürlicher Angleichung einschließlich lokaler
  Vorfeldwahrnehmung exakt gleiche Antworten auf dieselbe spätere Probe.
- [Zulässigkeitsvertrag minimale lokale Feldwirkung 026](ZULAESSIGKEITSVERTRAG_MINIMALE_LOKALE_FELDWIRKUNG_026.md)
  erlaubt für `GF_001` ausschließlich aktuelle Rezeptoraufnahme und lokale
  Vorfeldproben, noch ohne Eigenzustand, Nachhall oder Persistenz.
- Eine entwickelte Beziehung, Topologie oder Memorywirkung ist nicht gezeigt.
- `GF_001` ist noch geschlossen.

Die aktuelle Richtung für spätere Persistenz ist im Vertrag
[Organisches Memory des gemeinsamen MCM-Feldes](../architektur/028_ORGANISCHES_MEMORY_DES_GEMEINSAMEN_FELDES.md)
festgehalten. `GF_001` führt davon noch keine Mechanik ein.

## Ablageregel

Für jeden geöffneten Versuch entstehen höchstens:

```text
GF_NNN_METHODIK_<KURZTITEL>.md
GF_NNN_BEFUND_<KURZTITEL>.md
```
