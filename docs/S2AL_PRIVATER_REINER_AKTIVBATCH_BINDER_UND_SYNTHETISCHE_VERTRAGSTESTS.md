# S2-AL: Privater reiner Aktivbatch-Binder

## Umsetzung

S2-AL implementiert den in S2-AK freigegebenen privaten Anschluss in
`mcm_field_organism._ppb1_active_receptor_batch_binding`.

Das Modul enthaelt einen privaten Fehlertyp, drei unveraenderliche private
Wertetypen und die reine Funktion `bind_ppb1_active_receptor_batch`. Die
Funktion bindet Browserweltvertrag, reduzierten Audio-/Videobatch und das
vorhandene PPB-1-Browserprofil in eine digestgebundene Huelle.

Audio und Video bleiben getrennt. Die Huelle haelt die bereits vorhandenen
unveraenderlichen zeitgebundenen Rezeptorframes. Werte werden nicht
transformiert, resampelt, fusioniert oder ergaenzt.

## Synthetische Abnahme

Das fokussierte Modul `tests.test_s2al_private_active_receptor_batch_binding`
wurde vor und nach einer Testverschaerfung ausgefuehrt. Der endgueltige Stand
bestand alle 7 Tests in der von `unittest` gemeldeten Laufzeit von 0,020
Sekunden. Insgesamt wurden 14 Testfaelle ausgefuehrt.

Geprueft wurden der vollstaendige Erfolgsfall, unveraenderliche Ausgaben,
Vertrags-ID und -Digest, Profil- und Geometrieabweichung, ein Quellclockwechsel,
nicht fortschreitende Quell-Endticks sowie die private Exportgrenze. Zwei
vollstaendige Huellen wurden erzeugt; sechs ungueltige Versuche endeten
fail-closed. Ueber beide Laeufe entstanden fuenf vollstaendige Huellen; elf
ungueltige Versuche endeten ohne Ausgabe.

## Grenze

Der Binder ruft weder PPB-1-Zustandsbildung noch read-only Probe, Baseline,
Feld, Produktion, Live-Eingabe oder Dateisystem auf. `current_api.py` und das
Paketwurzelmodul sind unveraendert; es existiert kein oeffentlicher Export.

Der Befund bestaetigt nur die private technische Anschlussfunktion. Er prueft
noch keine Bildung, Stabilisierung, Wiedererkennung oder Feldwirkung eines
Wahrnehmungszustands.

S2-AM soll Implementierung, Digests und Grenzen statisch abnehmen, ohne die
Tests oder die Bindefunktion erneut auszufuehren.

Maschinenlesbarer Receipt:
[S2AL_PRIVATER_REINER_AKTIVBATCH_BINDER_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json](S2AL_PRIVATER_REINER_AKTIVBATCH_BINDER_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json).
