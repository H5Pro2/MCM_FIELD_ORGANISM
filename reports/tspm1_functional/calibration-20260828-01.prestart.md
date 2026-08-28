# Ausfuehrungsstand vor der L1-Bestaetigung

Basis: `14cc788`, unveraenderter Kalibrierungsplan. Quellen werden als Bytes
und SHA-256 vor Qualifikation und Untersuchung aufgezeichnet. Neu sind nur
der private Evaluator/Recorder `tools/_visual_l1_calibration_probe.py` und
`tests/test_visual_l1_calibration_probe.py`. Keine Kern- oder Altschwellenkorrektur.

Genau acht kleine fokussierte Tests: Entwicklungsbindung/Bruchwert,
inklusive Schwelle, Altabrufparitaet/Ties, unveraenderte Inputs/Rueckgabe,
relationale Ergebnisbindung, fachliche Fehler, unvollstaendige Aufzeichnung,
Quellbindung/alte Sperren. Guards verhindern Rezeptor-, Bildungs-, Matrix-
und Bestaetigungsrezeptaufrufe waehrend dieser Tests. Die fuenf bereits
bestandenen Rezeptorregressionen werden nicht nochmals ausgefuehrt.

Nur bei acht bestandenen Tests: ein Versuch `calibration-20260828-01`,
56 Bildanalysen, acht Bildungen, 48 identische Probeinputs fuer zwei Regeln,
96 Abrufe und 320 verkettete Start-/Ergebnisrecords. Frische Bank je Episode.
L1-ALT nutzt den unveraenderten Originalabruf; L1-KAL dieselben L1-/Tie-Regeln
mit dem exakten Python-Bruchausdruck 44/765. Kein Lernen dieser Schwelle.

Der Startbeleg bindet Entwicklungsbelege, neue Eingaben, Quellen, Qualifikation,
Schwelle und Einmallauffreigabe vor der ersten Bildanalyse. Die exklusive
Erzeugung des Laufverzeichnisses verbraucht die Freigabe, auch bei Fehlern.
Keine Wiederholung, Teilfortsetzung oder Ersatzfaelle. Alle alten Einstiegssperren
bleiben erhalten. Kein geschlossener Plattformcode wird ausgefuehrt.

Funktionale Budgets werden je Ereignis gespeichert; Rezeptor, Kontrollarbeit,
Recordpruefung und IO bleiben getrennt. Zusaetzliche live L1-Validierung:
26 Terme je Abruf. Nachpruefungen lesen nur Aufzeichnungen und rechnen deren
Konsistenz nach; sie erzeugen keine erneuten Rezeptor-/Speicher-/Abrufbefunde.
Prozesslaufzeit wird separat gemessen, Prozess-RAM-Spitze nicht erhoben.

K1-K3 zaehlen primaer, G1 ausschliesslich diagnostisch. Fachliche Fehler
bleiben Ergebnisse; technische Bindungsfehler oder unvollstaendige Belege
machen den Lauf nicht auswertbar. Keine universelle Stromausfallgarantie.
