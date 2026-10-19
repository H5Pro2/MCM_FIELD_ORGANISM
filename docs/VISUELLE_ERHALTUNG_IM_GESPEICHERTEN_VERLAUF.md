# Visuelle Erhaltung im gespeicherten Videolauf

Stand 2026-09-12, ausschließlich lesende Einordnung. Kein neuer Lauf,
keine Nachberechnung, kein neuer Scan und keine erneute Verifikation.

## Drei getrennte abgeschlossene Befunde

- Die visuelle Eingangskontrolle bestätigte reproduzierbare vollständige
  Werte und Erhaltung der 32 sichtbaren Werte bei Maskierung.
- `immediate-visual-retrieval-20260912-01` bestätigte den Leerabruf und danach
  den unmittelbaren Abruf einer regulär gebildeten A-Spur aus eingefrorenem
  e03-Eingang. Keine zwischenzeitliche Formation, keine neue Medienmessung.
- `media-memory-video-20260912-01` enthielt dagegen weitere Formationen vor
  den Hinweisen. Seine vier Enthaltungen bleiben unverändert. Unmittelbare
  Abrufbarkeit ist kein Nachweis späterer Erhaltung oder Slow-Stabilisierung.

## Gelesene Belege

Grundlage sind ausschließlich `record.json`, `verification.json` und
`common.json` unter `reports/s2oe/media-memory-video-20260912-01/`.
Die gespeicherten `native.transitions`, `generations.births`, Eingänge,
Zustandsbindungen und Bankbefunde werden hier gegenübergestellt. Die
ursprüngliche Gesamtverifikation wird nicht erneut aufgerufen.

### B4 und relevante Einzelspuren

| Spur | Anlage | Ende der betreffenden PPB-Generation | Ende der B4-Generation | Späterer Hinweis |
| --- | --- | --- | --- | --- |
| e03, Medienzeit 1,0 s | B4 002; visuelle PPB 001 bei e03 | PPB 001 ersetzt bei e07 | B4 002 ersetzt bei e12 | visuell e14 |
| e09, Medienzeit 4,0 s | B4 008; visuelle PPB 003 bei e09 neu ersetzt | PPB 003 erneut ersetzt bei e15 | B4 008 ersetzt bei e20 | visuell e22 |

Die Zahlen bezeichnen Ereignisse, nicht überall Formationsnummern: e13/e14
und e21/e22 sind Hinweise. Beispielsweise ist e15 die 13. Formation.
Eine erneut verwendete Slot-ID erhält eine neue Generation; sie bewahrt
nicht die Herkunft der ersetzten Belegung. Die ursprünglichen B4-Einträge
sind bei den späteren visuellen Hinweisen tatsächlich nicht mehr vorhanden.

### Fast-Fortschreibung

Fast 000 wird bei e01 angelegt und bei allen 19 weiteren Formationen
`MATCHED`. Die Generation bleibt e01; das ist ausdrücklich keine Garantie
unveränderter Werte. Der Support erreicht bei e02 den Sättigungswert 2,
während Werte und Zeitbindung weiterhin aktualisiert werden. Der
Konsolidierungszähler erreicht 19. Kein Fast-Ablauf in dieser Kette.

Die visuelle Fast-Fortschreibung verwendet den Faktor 0,5. Deshalb ist ein
fortgesetzter Fast-Slot kein unveränderliches Archiv der ursprünglichen
Einzelbilder. Ob und wie groß eine bestimmte ursprüngliche Komponente noch
numerisch enthalten ist, wird hier nicht nachberechnet. Die späteren
visuellen Scans belegen bereits: kein sichtbarer Treffer auf den dann
vorhandenen Fast-Kandidaten.

### Visuelle PPB

e01: NO_UPDATE. e02 bis e05: CREATED in 000, 001, 002, 003.
Danach ausschließlich REPLACED:

| Ereignisse | jeweils ersetzte visuelle PPB-Slots |
| --- | --- |
| e06, e07, e08, e09 | 000, 001, 002, 003 |
| e10, e11, e12, e15 | 000, 001, 002, 003 |
| e16, e17, e18, e19 | 000, 001, 002, 003 |
| e20, e23, e24 | 000, 001, 002 |

Kein visueller MATCHED-Übergang; jede neue Belegung hat Support 1. Am Ende
tragen die Slots die Generationen e20, e23, e24, e19. Damit erreicht keine
visuelle Generation den stabilen Support 3. Es fehlen nicht Schreibzugriffe:
Es fehlen passende Wiederzuordnungen zu einer bereits vorhandenen PPB-Spur.

## Entscheidungsregeln und verfügbare Zahlen

Das Halbprofil bindet Fast visuell an mittleren L1-Abstand <=0,2, Update 0,5,
Supportgrenze 2 und Ablauf nach acht nicht erneuerten Expositionen
(`tools/_s2jw_default_live_profile.py`, `_half_components`, Zeilen 179 ff.).
Visuelle PPB unverändert: vier Slots, mittlerer L1-Abstand <=0,01,
Update 0,05, stabil ab Support 3, Ablaufgrenze 64 PPB-Schritte.
Die visuelle Konfigurationsbindung im gespeicherten Zustand ist
`fe8b06bad66204dec3e7c80cb24bb73d740544eba23af9a8c9e1da3d3c5d9fec`.

`mcm_field_organism/_ppb1_reference.py` verwendet `math.fsum` für den mittleren
L1-Abstand (Zeilen 444 ff.). Der Auswahlpfad (Zeilen 590–650) prüft zuerst
Ablauf, dann Matches. Ohne Match folgt ein freier Slot, andernfalls der
älteste `last_selected_step` mit Slot-ID als Tie-Break; Neubelegung setzt
Support 1. Bei MATCHED würden Prototyp und Support fortgeschrieben.

Fast-Sättigung aktiviert im gespeicherten Lauf 19 gemeinsame PPB-Übergänge.
An die PPB geht die aktuelle gebundene Wahrnehmung, nicht automatisch der
gemittelte Fast-Prototyp (`_tspm1_private.py`, Zeilen 2538 ff.; gespeicherte
Relationsprüfung in `_s2ne_private_run_verification.py:_ppb_relations`).
Mit nur 19 PPB-Schritten ist die visuelle Ablaufgrenze 64 nicht erreicht.
Die beobachteten Ersetzungen sind hier daher nicht mit zeitlichem Ablauf
gleichzusetzen. Mehrfaches Schreiben allein erhöht den Support einer
ersetzten Generation nicht.

**Nicht gespeichert:** numerische visuelle Fast- und PPB-Formationsdistanzen
mit Einzeltermen. `verification.json` enthält für Fast nur `fast_rank_digest`,
ausgewählten Matchslot und Übergangsdaten. Die Felder `observed_distance` im
Gesamtrecord gehören zu auditiven Hinweisscans und ersetzen diese Zahlen nicht.
Aus Digests werden keine Distanzen rekonstruiert.

Aus dem validierten Auswahlpfad lässt sich für die jeweiligen bestehenden
Kandidaten ableiten: Fast hat seine gemeinsame Matchbedingung erfüllt;
die visuelle PPB hatte bei CREATED/REPLACED keinen anwendbaren bestehenden
Kandidaten. Das sind relationale Folgerungen (Fast visuell <=0,2; vorhandene
PPB-Kandidaten nicht <=0,01), **keine nachträglich gemessenen Abstände**.
Wie knapp die Grenzen verfehlt wurden und welche Bildbereiche beitragen,
bleibt eine Evidenzlücke. Der visuelle Teilabruf selbst verwendet exakte
Gleichheit auf 32 Positionen, nicht diese Formationsdistanzgrenzen.

## Kleinster vorgeschlagener nächster Nachweis

Falls die numerische Erhaltungsgrenze geklärt werden soll: ausschließlich
den bereits gespeicherten Übergang **e03 → e04** prospektiv für eine spätere
begrenzte Offline-Diagnose binden. Er ist die erste folgende Formation nach
dem jetzt unmittelbar abrufbaren Ziel, nicht ein nach Distanz gewählter Fall.

Nur die originale e04-Wahrnehmung gegen den Fast-Vorzustand und die beiden
damals belegten visuellen PPB-Prototypen e02/e03 vergleichen: drei bereits
regelrelevante 288-Werte-Abstände samt vollständigen Termen und unveränderten
Grenzen. Kandidatenherkunft und B4-Erhaltung separat aus den vorhandenen
Zustandsbelegen führen. Höchstens 864 Differenzen primär und 864 unabhängig,
keine neue Formation, Cuefolge, Medienmessung oder künstliche Wiederholung.
Diese Arbeit ist hier **nur vorgeschlagen, nicht ausgeführt oder freigegeben**.

Sie würde zunächst erklären, warum eine noch vorhandene PPB-Spur keine
Bestätigung erhält, nicht eine Lösung für ihre Erhaltung liefern. Eine
Schwellenänderung, Fokusmechanik oder neue Speicherregel folgt daraus nicht.
Sollten solche Zahlen keine neue fachliche Entscheidung tragen, genügt der
bereits vorliegende Übergangsbefund; kein weiterer Langlauf ist erforderlich.

Gates False. Kontrollversuch geschlossen; historische Belege unverändert.
