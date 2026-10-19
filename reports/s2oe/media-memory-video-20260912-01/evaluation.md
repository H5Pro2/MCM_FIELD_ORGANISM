# Getrennte Funktionsauswertung

Einmal nach RECORDING_COMPLETE und evaluation_allowed=true gelesen.
Keine erneuten Scans, Rezeptoren, Distanzen oder Verifikation.
Record: 344e8e61004c34e0cb419e04910573a991e32add607043467215a0e9b0669a10.
Verifikation: 8170305ef10b43cd68927264fe9a5e97714bf3f62b944e6c21ef2717e24a41d6.

## Abruf vor erneuter Formation

| Ereignis | Durchlauf/Medienzeit | Modalität | Entscheidung |
| --- | --- | --- | --- |
| 13 | 2 / 1,0 s | Audio | ABSTAIN_INTERNAL_AMBIGUITY |
| 14 | 2 / 1,0 s | Video | ABSTAIN_NO_APPLICABLE_CONTEXT |
| 21 | 2 / 4,0 s | Audio | ABSTAIN_INTERNAL_AMBIGUITY |
| 22 | 2 / 4,0 s | Video | ABSTAIN_NO_APPLICABLE_CONTEXT |

Audio jeweils: 9/9 prüfbare B4-Kandidaten treffen, Fast 1/1 und stabiler
Audio-Slot 1/1 treffen ebenfalls. Die interne A-Mehrdeutigkeit verhindert
eine öffentliche Hypothese. Video jeweils: B4 0/9, Fast 0/1 Treffer;
kein stabiler visueller Kandidat. Primärscan und Direktbaseline stimmen
bei allen vier Entscheidungen überein. Alle Hinweise erhalten den
Memorydigest unverändert; keine Hypothese wird ausgegeben oder angewandt.

## Speicherentwicklung

20 Formationen bestätigt. Fast-Slot 000 entsteht bei e01, danach 19 MATCHED;
Support ab e02 gesättigt bei 2, Konsolidierungszähler am Ende 19.
Audio-PPB-Slot 000 entsteht e02, erhält 18 MATCHED und erreicht e04
Support 3. Diese Generation bleibt bestehen, auch im zweiten Durchlauf.
Visuelle PPB-Slots entstehen e02 bis e05; ab e06 folgen 15 Ersetzungen
zyklisch 000 bis 003. Alle vier verbleiben bei Support 1, ohne stabile
visuelle Abrufspur. B4: neun Belegungen, danach elf Ersetzungen;
am Ende Formationen 12 bis 20. Generationen stammen aus den Transaktionen.
Ein gesättigter Support bedeutet nicht ausgebliebene Aktualisierung.

## Aussagegrenze

Fortgesetzte Speicherbildung auf wiederverwendeter Quelle ist belegt;
ein eindeutiger Wiederabruf bleibt an allen vier Stellen aus. Kandidatentreffer
sind Musteranwendbarkeit, keine Objektidentität. Ohne frischen Vergleichsarm
mit denselben Hinweisen ist ein kausaler Abrufvorteil früherer Wahrnehmung
nicht isoliert. Keine semantischen Labels oder nachträgliche Erfolgsregel.
Abgetasteter Medienfluss, kein vollständiges Videoverständnis.
Die Offline-Prüfung rekonstruiert weder FFT noch Feldtrajektorie oder
die Roh-zu-Halb-Numerik aus fehlenden Rohwerten.
