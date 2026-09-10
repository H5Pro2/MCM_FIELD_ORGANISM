# MCM_FIELD_ORGANISM

Ein Forschungsprojekt für audiovisuelle Wahrnehmung, ein dynamisches MCM-Feld
und eine davon getrennte Zwei-Bereich-Memory. Der bisherige Kern kann
Wahrnehmungen aufnehmen, begrenzt speichern, vergessen und anhand von
Teilhinweisen getrennte Kontexthypothesen oder eine Enthaltung ausgeben.

## Aktueller Stand

**S2-OB ist als begrenzter Eingangsnachweis abgeschlossen:** sieben Ereignisse aus
bereitgestellten PCM-/RGB-Dateien, vier Formationen und drei korrekte Hinweisentscheidungen.

**S2-OA ist abgeschlossen: Der fortgesetzte Grundpfad funktioniert im geprüften Umfang.**

- Eine Runtime ohne Rücksetzung: **28 Ereignisse, 20 AV-Formationen und 8.544 Feldkontakte**.
- **Alle acht Hinweisentscheidungen** entsprechen den Erwartungen.
- Stabilisierung, Verdrängung, Ablauf und visuelle Slot-Ersetzung sind bestätigt.
  Eine wiederverwendete Slot-ID erhält eine neue Generation; alte Abrufbelege
  begründen keine aktuelle Verfügbarkeit.

Der Lauf ist technisch vollständig. Sein historischer Gesamtstatus bleibt
**`FALSIFIED`**: 13 Supportvorhersagen des Auswerters waren falsch.
Die produktive Fortschreibung sättigt diese Evidenzzähler regelkonform.
Das erfordert weder eine Produktkorrektur noch einen Wiederholungslauf.

## So arbeitet der Grundpfad

**Audio/Video → Rezeptoren → gemeinsame Wahrnehmungsbindung → getrennte Feld- und Memoryzweige**

Die private Audio-Halbprojektion (NJ) wird genau einmal angewandt.
Feld und Memory erhalten dieselben kanonischen Wahrnehmungswerte.

- **Feld:** verarbeitet Wahrnehmungskontakte unabhängig vom Memoryzweig.
- **`A_RECENT`:** begrenzte jüngere Inhalte in B4 und Fast.
- **`B_STABLE`:** getrennte stabilisierte auditive und visuelle Inhalte.
- **Teilhinweise:** lesen Memory ohne Änderung und liefern eine Hypothese
  oder Enthaltung. Hypothesen werden nicht angewandt.
- **Abschluss:** gebundener Snapshot und reguläres `close()`.

## Grenzen und nächster Schritt

Der ausführbare OA-Forschungsrunner ist noch an seinen Korpus, seine
Ereignisfolge und Belegprüfung gebunden. Er ist **kein allgemeiner Eingang
für beliebige Audio-/Videoströme**.

OB ist neutral qualifiziert (**30/30**) und in einer kurzen Dateifolge bestätigt.
Allgemeiner Dauerbetrieb und B-Abruf nach Verdrängung sind damit nicht geprüft.
Nächster Anschluss: einzelne Aufrufe an dieselbe offen bleibende Runtime,
weiterhin mit endlichem Manifest. Bisher nur statisch geklärt, nicht implementiert.
Livequellen, neue Speicherregeln und Hypothesenanwendung bleiben ausgeschlossen.

NW/NX belegen begrenzten gelernten Vorhersagenutzen; die spätere
Historienempfehlung rechtfertigt keine Integration. Der Prognosezweig ruht.
Allgemeine Quellenidentität, Semantik und autonomes Handeln sind nicht nachgewiesen.

## Weiterführende Dokumentation

- [Ereignisweiser Aufruferanschluss: vorhandener Kern und fehlender Zugang](AKTUELLER_FORSCHUNGSWEG.md#statische-anschlussklärung-ereignisweise-aufrufe)
- [Aktiver Grundpfad, Module und verbleibende OA-Kopplung](AKTUELLER_FORSCHUNGSWEG.md#aktuell-oa-geschlossen-grundpfad-statisch-zugeordnet)
- [OA-Laufabschluss und Supporteinordnung](AKTUELLER_FORSCHUNGSWEG.md#abgeschlossener-oa-lauf-02-technischer-und-fachlicher-einzelbefund)
- [Privater Runtimekern S2-MR](tools/_s2mr_private_minimal_mcm_runtime.py)

Die vollständigen Forschungsbefunde und historischen Grenzen stehen im
Forschungsweg und in den verlinkten Belegen, nicht als Laufjournal in dieser README.
