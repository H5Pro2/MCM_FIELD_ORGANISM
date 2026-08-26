# S2-AR: Privater atomarer Aktivbatch-Bildungsverbraucher

## Umsetzung

S2-AR implementiert den in S2-AQ freigegebenen privaten Besitzer und den
atomaren Bildungsverbraucher in
`mcm_field_organism._ppb1_active_batch_formation_consumer`.

Eine Besitzerinstanz bindet genau eine vorregistrierte Autorisierung. Eine
vollstaendige Vorpruefung erfolgt vor dem ersten Lebenszyklusaufruf. Eine
reine Vorpruefungsablehnung veraendert den Besitzer nicht; ein korrigierter
Aufruf bleibt moeglich. Nach Versuchsbeginn endet der Besitzer zwingend als
`CONSUMED` oder `FAILED`.

Ein privater nichtblockierender Lock verhindert, dass ein gleichzeitiger oder
rekursiver Aufruf einen weiteren Lebenszyklusaufruf startet. Die Garantie gilt
nur fuer eine Besitzerinstanz. Globale oder prozessuebergreifende Einmaligkeit
wird nicht behauptet.

## Bildungsweg

Der Verbraucher nutzt fuer jedes gebundene Rezeptorframe ausschliesslich
`advance_s1wq_perceptual_state`. Audio und Video besitzen getrennte frische
PPB-1-Bankzustaende. Die Frames werden nach der gebundenen gemeinsamen
Feldzeit geordnet, ohne die Reihenfolge innerhalb einer Modalitaet zu
veraendern.

Jeder Schritt erzeugt ein privates Receipt, das Frameprovenienz, Eingabe,
Vor- und Nachzustand sowie den bestehenden Lebenszyklusdatensatz bindet. Nur
wenn beide Modalitaeten vollstaendig verarbeitet und alle Digests unveraendert
sind, werden Ergebnis und `CONSUMED`-Besitzerzustand gemeinsam sichtbar. Bei
einem technischen Fehler bleibt kein Teilresultat sichtbar.

## Synthetische Abnahme

Das fokussierte Testmodul wurde vor und nach einer internen
Ergebnisvalidierungsverschaerfung ausgefuehrt. Beide Ausfuehrungen bestanden;
der finale Stand bestand alle 9 Tests in 0,043 Sekunden. Insgesamt wurden 18
Testfaelle ausgefuehrt.

Geprueft wurden Erfolg, unveraenderte Vorpruefungsablehnung, korrigierter
Folgeaufruf, terminale Wiederholungsablehnung, technischer Fehlversuch,
Konkurrenzablehnung, unveraenderlicher Besitzer-Snapshot und die privaten
API-, Snapshot- und Feldgrenzen.

## Grenze

S2-AR implementiert nur private technische Bildungsinfrastruktur. Probe,
Baseline, Wiedererkennungsvergleich, Feldwirkung, Produktion, Live-Eingabe und
oeffentliche API bleiben unberuehrt. Der Befund ist kein Nachweis eines
funktionalen Vorteils und kein Memory-Befund.

Der naechste Schritt ist S2-AS: ein statischer Audit von Implementierung,
Digests, Atomaritaet und Grenzen ohne erneute Ausfuehrung.

Maschinenlesbarer Receipt:
[S2AR_PRIVATER_ATOMARER_AKTIVBATCH_BILDUNGSVERBRAUCHER_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json](S2AR_PRIVATER_ATOMARER_AKTIVBATCH_BILDUNGSVERBRAUCHER_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json).
