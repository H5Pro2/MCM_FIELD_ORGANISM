# S2-AQ: Statischer Besitzer-Abnahme- und Materialisierbarkeitsaudit

## Ergebnis

S2-AQ nimmt die S2-AP-Besitzerkorrektur statisch ab. Der S2-AO-Blocker ist auf
Vertragsniveau geschlossen. Es verbleibt kein statischer Blocker fuer eine
private Implementierung des Besitzers und des bestehenden PPB-1-Verbrauchs.

Die Garantie bleibt eng: genau ein terminaler Versuch pro Besitzerinstanz.
Globale, prozessuebergreifende oder ueber mehrfach erzeugte Besitzer hinweg
geltende Einmaligkeit wird nicht behauptet.

## Konkurrenzverhalten

Der spaetere Besitzer kann mit einem privaten Lock materialisiert werden, der
nicht zum kanonischen Zustandsdigest gehoert. `consume_once` versucht diesen
Lock am Methodeneingang nichtblockierend zu erwerben und haelt ihn bis zur
Ablehnung oder zum terminalen Commit.

Ein gleichzeitiger oder rekursiver zweiter Aufruf erhaelt `OWNER_BUSY` und
fuehrt keinen PPB-1-Lebenszyklusschritt aus. Ein spaeterer Aufruf nach
`CONSUMED` oder `FAILED` erhaelt `OWNER_TERMINAL`, ebenfalls vor jedem
Lebenszyklusschritt. Dadurch ist weder Warten noch ein Reentranz-Deadlock fuer
die Ablehnung erforderlich.

## Vorpruefung und terminaler Versuch

Typen, Digests, frische Vorzustaende und Zeitplan werden vor Versuchsbeginn
geprueft. Eine Vorpruefungsablehnung laesst den Besitzer digestgleich auf
`AUTHORIZED/0/0/0`; danach darf genau ein korrigierter Aufruf folgen.

Nach bestandener Vorpruefung wird der Versuch vor dem ersten PPB-1-Schritt auf
eins gesetzt. Ein vollstaendiger Erfolg endet als `CONSUMED/1/1/1`. Ein
erwarteter technischer Fehler endet als `FAILED/1/0/1`, ohne sichtbares
Bankteilresultat. Eine Wiederherstellung nach Prozessabbruch oder
`BaseException` wird fuer diesen privaten In-Memory-Besitzer nicht behauptet.

## Implementierungsgrenze

Die spaetere Implementierung ist auf
`mcm_field_organism._ppb1_active_batch_formation_consumer` begrenzt. Sie darf
nur private Fehler-, Snapshot-, Schrittreceipt-, Ergebnis- und Besitzertypen,
eine private Factory sowie synthetische Vertragstests enthalten.

Es werden ausschliesslich die bestehenden Funktionen
`initial_ppb1_bank_state` und `advance_s1wq_perceptual_state` verwendet. Neue
PPB-1-Regeln, Parameter, API- oder Paketexporte, Snapshot, Produktion,
Live-Pfad, Probe, Baselines und Feld bleiben gesperrt.

## Naechster Schritt

S2-AR kann nach separater Freigabe genau diesen privaten Besitzer, den
atomaren Verbraucher und die neun gebundenen synthetischen Testrollen
implementieren. Ein bestandener Verbraucher waere nur technische
Bildungsinfrastruktur und noch kein funktionaler Speicher- oder Memory-Befund.

Maschinenlesbarer Audit:
[S2AQ_STATISCHER_KORRIGIERTER_BILDUNGSVERBRAUCHER_BESITZER_ABNAHME_KONKURRENZ_UND_MATERIALISIERBARKEITSAUDIT_V1.json](S2AQ_STATISCHER_KORRIGIERTER_BILDUNGSVERBRAUCHER_BESITZER_ABNAHME_KONKURRENZ_UND_MATERIALISIERBARKEITSAUDIT_V1.json).
