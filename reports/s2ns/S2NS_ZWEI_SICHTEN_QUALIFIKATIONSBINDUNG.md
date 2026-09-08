# S2-NS: einmalige neutrale Zwei-Sichten-Qualifikation

Vorab-ID: `s2ns-two-view-qualification-20260908-01`.
Genau ein unittest-Aufruf, 24 Testkoerper, failfast; bei Fehler Stopp.
Keine Wiederholung alter Qualifikationen, kein realer NS-Quellenzugriff.

## Anschluss und Grenzen

Neue unveraenderliche Endpoint-, View-, Generation-, Inventory-, Scan- und
Admissionformen. LOWER_24 und UPPER_24 sind eigene Typbindungen; historische
Masken bleiben unveraendert. Eine bereits validierte NJ-Projektion wird nur
partitioniert; kein erneuter Rezeptor- oder NJ-Aufruf. Der Scanner sieht
jeweils nur 24 Cuewerte mit Originalindizes. Beide Scans sind vollstaendig.

A prueft max <= 0.1; Slow prueft historisches sum/24 <= 0.01 je Sicht,
inklusive Grenzen und ohne Toleranz. Konjunktion je belegter Generation vor
A/B-Aufloesung, nicht Abstimmung fertiger Hypothesen. Bestehende oeffentliche
KZ-Entscheidungstabelle wiederverwendet; interne A-/B-Tabelle semantikgleich
ohne Werteergaenzung angebunden. Direktbaseline mit eigener Slottraversierung,
Schnittmenge und Entscheidungstabelle; gemeinsam nur Typen, Bindungsvalidatoren
und kanonische Publikationshilfen, keine produktiven Scan-/Entscheidungshelfer.

Generation bindet Erzeugungs-/Ersetzungsereignis, Geschichte, Bank, Slot,
Prestate, Eingang, erzeugten Slot und Transition. Inventory bindet den
aktuellen Slot-/Wertedigest und den externen Formationsketten-Pruefbeleg.
Diese Stufe prueft Konsistenz gegen das uebergebene Inventory, nicht dessen
Herleitung aus einer realen Formationsgeschichte. Die neutrale Herkunft ist
synthetisch. **Vor einem Hauptlauf fehlt noch der Anschluss an die bereits
unabhaengig geprueften realen Transaktionsketten**, einschliesslich Generation
fortsetzen bei MATCHED, erneuern bei REPLACED und Entfernen freier Slots.
Kein Digest allein ersetzt diesen Herkunftsnachweis.

Weitere verbleibende Laufanschluesse: NS-Materialisierung, geschlossenes
Einmalgate, atomarer Gesamtbeleg und Gesamtverifikation der 31 Ereignisse;
Evaluationsherkunft und urspruengliche Formationswerte aus verifizierten
Belegen statt synthetischer Erwartungsdaten. Hier kein solcher Hauptpfad.

## Vorab festes Inventar

1. Eigene unveraenderliche Sichten, Indexbindung und ungueltige Zahlen.
2. Bindung eines synthetischen gueltigen NJ-Endpunktbelegs ohne NJ-Ausfuehrung.
3. Fehlende zweite oder erste Sicht: gueltige unzureichende Evidenz.
4. Fremder Endpunkt, Quelle/PCM/Rohbindung, Zeit und Profil.
5. Ersetzte Generation bei gleicher Slot-ID und gleichem Inhalt.
6. Fehlende, fremde oder unzulaessige Generationsbindung.
7. Inklusive A-Grenze und benachbarter Binary64-Wert.
8. Zwei Slow-Mittelwerte statt gemeinsamer 48er-Mittelung.
9. Slow-Grenze, Nachbarwert und instabiler Support.
10. Disjunkte Einzeltreffer bestaetigen sich nicht.
11. Gemeinsame Eindeutigkeit trotz zweier Einzelmehrdeutigkeiten.
12. A-Gleichheit und Konflikt anhand aller gespeicherten 48 Werte.
13. Jede Bankmehrdeutigkeit; kein vorzeitiger Scanabbruch.
14. Oeffentliche A/B-Mehrdeutigkeit und Nullzustand.
15. Ein neutraler historischer Halbprofil-ALL-BANDS-Referenzscan fuer LOWER.
16. Verdeckte Werte gelangen nicht in den Einzel-Sichtscan.
17. Technische Verifikation akzeptiert unerwartete gueltige Enthaltung.
18. Zielausschluss kann eine neue Fehlzulassung erzeugen.
19. Oeffentlicher Verlust getrennt von Gewinn; A-/B-Nenner getrennt.
20. Rezeptorvariation gegen originale Formationswerte; PPB-Drift separat,
    uneindeutige/fehlende Referenz null, einseitig sichtbare Variation.
21. Manipulierte Scanvollstaendigkeit, Ergebnis- und Verifikationsbindung.
22. Profil-/Zustandsablehnung, Unveraenderlichkeit, Gates False.
23. Voll belegtes 9/3/8-Inventar, kanonische Ausgabe und Gesamtoberhuelle.
24. Kumulative Budgets, reine Zulassung ohne Ergaenzungswerte.

## Konkrete Ressourcenbindung

Je vollstaendigem Fall/Implementierung: zwei Scans, 40 Slotzeilen, maximal
960 Banddifferenzen, drei Entscheidungen, maximal 144 volle
Kandidatengleichheitsvergleiche. Join und Einzelentscheidungen nutzen dieselben
Termbelege. Native Zustandsvalidatoren bilden keine Memoryformation.

Zusatzverifikation eines Primaer-/Direktpaares: ein unabhaengiger erneuter
Zwei-Sichten-Direktscan, maximal 40 Slotinspektionen/960 Banddifferenzen/
144 Gleichheitsvergleiche. Dazu ein Inventory-/Zustandsvalidierungspass mit
20 Slot-/Generationsbindungen, zwei Sichtvalidierungen und bis zu 80
Scanzeilen-Formpruefungen. Diese Arbeit steht separat im Verifikationsbeleg.
Quellen-/Generationspruefungen vergleichen Bindungen, nicht neue Distanzen.

Fuer einen vollstaendigen Aufruf beider Implementierungen vor Verifikation:
vier Inventoryvalidierungspassagen (Primaer zwei Scans plus Join, Direkt
einmal), 80 native Slotbindungen, sechs Sichtvalidierungen und 40
Join-Scanzeilenpruefungen; die Form-/Digestarbeit ist nicht als L1 verrechnet.

Neutraler Gesamtaufruf separat begrenzt: maximal 192 abgeschlossene
Ausfuehrungsscans/3840 Zeilen/28800 Banddifferenzen, maximal 96 zusaetzliche
Verifikationsscans/1920 Zeilen/28800 Banddifferenzen. Jeweils maximal 4320
Kandidatengleichheitsvergleiche. Ein historischer Referenzscan separat:
20 Zeilen, maximal 480 Differenzen und 48 Gleichheitsvergleiche.
Keine reale NS-Geschichte, keine NS-Payloads, keine Formationen,
Rezeptoranalysen, NJ-Projektionen, Feld- oder Runtimeaufrufe.

Bytegrenzen, vor dem Test fest:

- Sichtscan <= 32768 Byte (bestehende Grenze).
- Resultat aus zwei Scans und drei Zulassungen <= 49152 Byte,
  enger als die bestehende 65536-Byte-Metadatenhuelle.
- Gemeinsames Inventory plus beide Cueformen <= 32768 Byte.
- Zustand <= 98304 Byte; Gesamtbeleg <= 4194304 Byte unveraendert.

Die konkrete maximale JSON-Oberhuelle wird im Test serialisiert: 17
Zustandsplaetze zu 98304 Byte, 15 Fallplaetze mit je 32768 gemeinsamen und
zweimal 49152 Resultatbytes sowie drei Metadatenplaetze zu 65536 Byte,
plus tatsaechliche aeussere JSON-Schluessel und Trennzeichen. ASCII-Padding
ersetzt nur die maximalen Unterbeleggroessen, keine Quellen oder Messwerte.
Daneben wird eine reale kanonische neutrale Vollbelegung mit allen 20 Slots
einschliesslich Primaer, Baseline und separater Verifikation gespeichert.
Damit wird keine universelle RSS-Speichermessung behauptet.

Der reale Plan behaelt 60 Scans/1200 Zeilen/28800 Differenzen/4320
Gleichheitsvergleiche und sein separat gebundenes Offlinebudget. Diese
Qualifikation fuehrt diesen Lauf nicht aus. Gates bleiben False.
