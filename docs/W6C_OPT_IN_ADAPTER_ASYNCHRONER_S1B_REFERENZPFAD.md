# W6-C: Opt-in Adapter fuer den asynchronen S1-B-Referenzpfad

Stand: 2026-08-09

Entscheidung: `S1B_ASYNCHRONOUS_OPT_IN_ADAPTER_TECHNICALLY_ACCEPTED`

Arbeitsart: technische Implementierung und Abnahme

Runtimeaenderung: ja, ausschliesslich additive opt-in Referenzoberflaeche

Formaler Forschungslauf: nein

Browser oder Medienausfuehrung: nein

## Entwicklungsfrage

Kann der in W6-B statisch zugelassene S1-B-Referenzpfad an bereits reduzierte
asynchrone Audio-/Video-Rezeptorsequenzen angeschlossen werden, ohne den
neutralen Standardpfad zu veraendern oder Medienlogik in L einzufuehren?

## Implementierter Anschluss

`mcm_field_organism/s1b_asynchronous_field_runtime.py` stellt bereit:

- `run_s1b_asynchronous_field(...)` als ausdruecklichen opt-in Einstieg;
- `S1BAsynchronousFieldRun` als kompaktes technisches Ergebnis;
- `S1BAsynchronousFieldRuntimeError` als harte Adaptergrenze.

Der Adapter akzeptiert nur:

1. ein bereits aufgebautes gemeinsames MCM-Feld;
2. bereits reduzierte `ReceptorTimeSequence`-Objekte;
3. explizite Feld-, Nachhall- und L-Naturparameter;
4. vorhandene Organismuszeitschritte.

Er liest keine Rohpixel, PCM-Daten, Browserpayloads, Dateinamen,
Modalitaetsbedeutungen, Labels, Observerwerte oder Versuchsergebnisse.

## Zustands- und Fortsetzungsgrenze

Ein bisher neutrales Schema-1-Feld erhaelt beim ausdruecklichen Einstieg genau
ein neutrales, ko-lokales L nach dem festen S1-B-Vertrag. Ein vorhandenes
Schema-3-Feld wird nur bei identischem Vertrag fortgesetzt. Abgewiesen werden:

- gleichzeitiger M- und L-Zustand;
- Wechsel des L-Naturvertrags waehrend einer Fortsetzung;
- unvollstaendige oder doppelte Quellstuetzen;
- Ereignisse ausserhalb des vorgegebenen Zeithorizonts;
- ungueltige Feld-, Nachhall- oder Dissipationskonfigurationen.

Die Ereignisuebergabe bleibt dieselbe wie in der neutralen asynchronen
Runtime. Nur der atomare transiente Feldschritt wird im opt-in Arm durch
`advance_s1b_reciprocal_shared_field_transient()` ausgefuehrt.

## API-Trennung

`current_api.py` enthaelt nun drei getrennte Exportgruppen:

```text
CURRENT_CONTROLLED_FIELD_EXPORTS = neutraler aktiver Standardpfad
F3_REFERENCE_EXPORTS             = vorhandener F3-Referenzpfad
S1B_REFERENCE_EXPORTS            = neuer opt-in S1-B-Referenzpfad
```

Die neutrale Kernliste wurde nicht um L-Funktionen erweitert.
`advance_audio_video_receptor_sequences()` bleibt unveraendert und neutral.
Ohne expliziten Aufruf von `run_s1b_asynchronous_field()` wird S1-B nicht
aktiviert.

## Technische Abnahme

Fokussiert geprueft wurden:

1. exakte Gleichheit der S/H-Feldprojektion zwischen neutraler Runtime und
   S1-B-Nullarm;
2. neutral verbleibendes L im Nullarm;
3. aktiver, digestwirksamer Schema-3-L-Zustand nach Weltkontakt;
4. Invarianz gegen aequivalente Teilung derselben Ereignisgeschichte;
5. bitgleiche Fortsetzung nach Schema-3-Snapshot und Restore;
6. Abweisung einer M/L-Mischung;
7. Abweisung eines L-Vertragswechsels;
8. unveraenderte S1-B-Bestandstests;
9. unveraenderte neutrale asynchrone Runtime;
10. API-Manifest sowie bestehende API- und AV-Verbraucher.

Insgesamt bestanden 53 gezielte technische Tests. Zusaetzlich kompilierten
Adapter und Testmodul fehlerfrei. Es wurde kein Browser, Runner oder formaler
Forschungslauf gestartet.

## Ergebnis

```text
reduzierte Rezeptorsequenz nach S1-B:       angeschlossen
neutraler Standardpfad veraendert:          nein
L automatisch im neutralen Feld angelegt:  nur im opt-in Arm
Schema-3-Fortsetzung:                       bitgleich bestaetigt
S/H-Nullarm:                                exakt bestaetigt
Zeitteilungsinvarianz:                      bestaetigt
Medien- oder Browserlogik in L:             nein
Memory- oder Feldzeitbefund:                nein
```

Entscheidung: `S1B_ASYNCHRONOUS_OPT_IN_ADAPTER_TECHNICALLY_ACCEPTED`.

## Aussagegrenze

W6-C belegt ausschliesslich, dass die bestehende lineare reziproke
Zweizeitenmechanik technisch am aktuellen reduzierten Weltkontaktpfad
betrieben werden kann. Ein von null verschiedener L-Wert ist noch keine
Praegung, Erinnerung, Rekonstruktion, Feldzeit, Organisation oder KI.

Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W6-D registriert vor jeder weiteren Ausfuehrung eine minimale kausale
Zweistufenpruefung. Eine identische kontrollierte Rezeptorgeschichte bildet
die erste Stufe; eine spaetere identische Probe bildet die zweite. Verglichen
werden aktiver S1-B-Arm, Nullarm, L-Neutralisierung und L-Tausch. Festgelegt
werden nur technische Trajektorien, Differenzen und Stopplinien. Der Test darf
weder Wiedererkennung noch Memory als erwartetes Ergebnis voraussetzen.
