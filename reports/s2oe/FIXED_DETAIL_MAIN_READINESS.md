# Detailvergleich: Vorabstopp vor Medienzugriff

Stand 2026-09-12. Ausschließlich statische Anschlussprüfung der erteilten
Einmallauffreigabe. Kein neuer Lauf, keine vergebene oder verbrauchte Lauf-ID,
kein Test und kein Medienzugriff; Gates False.

## Tatsächlich vorhanden

`tools/_s2oe_fixed_detail.py` enthält den versionierten Darstellungsanschluss:
`start()` (Zeile 156), `DetailWorker.view()` und `status()`, geerbtes `close()`,
`validate_evidence()` (Zeile 62), `pack_view()` und `pack_total()` (Zeile 179).
Die 16/16-Qualifikation gilt unverändert für ihren dokumentierten Umfang.

Die `comparison`-Sektion der Vorregistrierung bindet Quelle, zehn Zeitpunkte,
beide Ansichten, Kontrollen und Budgets. Sie ist eine Parameterbindung,
**kein vollständiger, qualifizierter Haupteinstieg**. Meine vorangegangene
Kurzmeldung hat diese Grenze nicht deutlich genug hervorgehoben.

## Fehlende Voraussetzungen des angeforderten Hauptlaufs

1. Kein dateigebundener Einmaleinstieg mit Ausgabeabwesenheit, konsumierter
   Zulassung, vollständiger Quellen-/Qualifikationsprüfung und gemeinsamem
   Erfolgs-/Fehlerabschluss. Das Öffnen des privaten Workers allein erfüllt
   diese Aufgabe nicht.
2. Kein unabhängiger Gesamtverifikator für Reihenfolge, gemeinsame Frameherkunft,
   vollständige 24 Ansichtsergebnisse, Arbeitszähler, Abschluss und Belegbilanz.
   `validate_evidence()` prüft einzelne Rückgaben im produktiven Pfad;
   `pack_total()` prüft Anzahl und Größen, nicht die gesamte Beweiskette.
3. Kein getrennter fachlicher Auswerter mit einer Verifikationssperre. Der
   reale Vergleich darf hierfür nicht die Testmethode als Haupteinstieg verwenden.
4. Die Qualifikationsbilanz ist keine vollständige Erfolgs-/Fehlerbilanz eines
   neuen realen Laufs einschließlich seiner aktiven Qualifikationsabhängigkeiten.

Die vorherige Qualifikation wird weder wiederholt noch rückwirkend erweitert.
Es ist kein neuer Fehler des Rezeptors oder der Memory nachgewiesen.

## Kleinster erforderlicher Abschlussanschluss

Eine schmale dateigebundene Komposition des vorhandenen Workers und Rezeptors
mit bestehenden atomaren Belegwegen; ein unabhängiger lesender Gesamtprüfer;
ein gesperrter separater Berichtsschritt. Gemeinsame Vorbilanz für sämtliche
Erfolgs- und Fehlerformen vor dem einzigen Medienzugriff.

Keine neuen Kennzahlen: räumliche Abdeckung, gespeicherte vollständige Werte
und gebundene K0/K1-Gleichheitskontrollen bleiben der Umfang. Insbesondere
keine nachträglichen zeitlichen L1-Abstände oder Auswahl günstiger Frames.
Ohne gespeicherte RGB-Payloads kann eine Offline-Prüfung die Rezeptormittelwerte
nicht unabhängig aus Pixeln rekonstruieren. Diese numerische Prüfgrenze muss
ausdrücklich von vollständiger Bindungs- und Strukturprüfung getrennt bleiben.

Die notwendige neue Abschlusslogik ist noch nicht implementiert oder neutral
geprüft. Ihre begrenzte Freigabe ist erforderlich, statt sie durch einen
ungeprüften Inline-Hauptaufruf zu ersetzen. Anschließend kann die bereits
gebundene Aufgabe unverändert ausgeführt werden. Kein Wechsel von Quelle,
Rechteck, Schwellen, Arbeitsumfang oder Memorymechanik.
