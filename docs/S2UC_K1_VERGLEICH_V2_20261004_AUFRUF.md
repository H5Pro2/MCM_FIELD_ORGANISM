# U/K1-Vergleich: ausführbarer, noch nicht freigegebener Start

Die Hülle ist implementiert und mit neutralen Ersatzdaten qualifiziert. Dieser
Text ist keine Einmallauffreigabe. Der Forschungslauf wurde nicht gestartet;
F1–F8 wurden nicht materialisiert. Die frühere Aufrufspezifikation vom03.10.
ist hinsichtlich des fehlenden Executors überholt.

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.

Nur Bindungen prüfen, ohne Quellenmaterialisierung oder Replay:

```powershell
& C:\Python314\python.exe -m tools.s2uc_k1_compare check
```

Der tatsächlich implementierte Vergleichsbefehl für die spätere Einmalfreigabe:

```powershell
& C:\Python314\python.exe -m tools.s2uc_k1_compare run --authorization C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\S2UC_K1_VERGLEICH_V2_20261004_AUTORISIERUNG.json
```

Die Autorisierungsdatei existiert absichtlich noch nicht. Ihre vollständig
gebundene Vorlage ist `S2UC_K1_VERGLEICH_V2_20261004_AUTORISIERUNG_VORLAGE.json`.
Erst die separate Beauftragung darf die operative Datei mit exakt dem erwarteten
Inhalt und Status `AUTHORIZED_ONCE` erzeugen. Die Vorlage selbst hat
`PENDING_SEPARATE_AUTHORIZATION` und wird vom Start abgelehnt.

Gebundene Vorstartdatei: `S2UC_K1_VERGLEICH_V2_20261004_VORSTARTBINDUNG.json`.
SHA256: `c35c1146ebb6c6884d761a52fb50aa15df39f9d39f821e6b329103a76446f9b9`.
Sie bindet Codebindung und verlustfrei komprimierte neutrale Belege. Die
Codebindung bindet ihrerseits sämtliche eingefrorenen Python-Dateien aus K1,
die neue Hülle, Interpreter, Quellbeschreibungen, vorhandene T1-Quellbytes und
Provenienz, feste Reihenfolge, Masken und Kriterien. Keine neue T1-Generierung.

Fester Zielordner: `reports/s2uc/k1-comparison-20261004-01`.
Er wird exklusiv reserviert; bestehende Ergebnisse werden nie überschrieben.
Auch ein ungültiger Start hinterlässt dort einen terminalen Beleg und darf
nicht durch Löschen oder automatischen Neustart wiederholt werden. Eine
Kollision mit einem vorhandenen Ordner erzeugt einen separaten Ablehnungsbeleg.

Exakt16 bekannte T1-Fälle plus F1–F8, jeweils frisches U und K1 mit eigener
Referenz;1.792 Eingangspositionen,3.584 Aufnahmen,3.584 Referenzfortschreibungen
und872 bewertete Ziele je Variante. Sämtliche Quellen werden erst im freigegebenen
Worker materialisiert und vor dem ersten Policyaufruf gemeinsam versiegelt.
T1 wird aus den gespeicherten Quellen gelesen; F wird nach der festen Formel
erzeugt. Die letzte Prognose jedes Falls bleibt zensiert.

Grenzen:3.600s einschließlich Vorstart und Abschluss; Workerfrist spätestens
nach3.540s;60s Abschlussreserve. Vorbereitung maximal8MiB. Export einschließlich
Vorbereitung und1MiB Abschlussreserve maximal64MiB. Feste Dateikappen ergeben
maximal61,75MiB:24 Quellen à160KiB,48 Armergebnisse à512KiB,24 Fallauswertungen
à1MiB,1MiB übrige Verwaltungsdateien,8MiB Vorbereitung und1MiB Abschluss.
Eine Verletzung führt zu NOT_EVALUABLE, niemals zu verkleinerten Fallmengen.

Vier getrennte Urteile: Technik, Mechanismus, Gesamtnutzen und Schaden.
624 T1-Ziele bleiben primär;324 Diagnoseziele sind nur eine Zusatzgruppe.
52 Übergänge einschließlich20 Kontrollen und die vier unveränderten G_w-Masken
bleiben erhalten. Keine Optimierung, Verlängerung oder Wiederholung nach Ergebnis.
