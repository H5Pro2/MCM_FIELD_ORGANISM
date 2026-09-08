# S2-NS: statischer Zeitbindungsblocker vor Laufanbindung

Stand 2026-09-08. Ausschliesslich lesender Anschlussbefund, kein neuer Lauf
und keine verbrauchte Qualifikations-ID. Keine Produkt-/Testkorrektur.

## Erste deterministisch widerspruechliche Bindung

Der unveraenderte NS-Plan bindet fuer Ereignis n das Audiofenster
`[(n-1)*4800,n*4800)` und den Snapshotindex `n-1`.
Dies steht nicht nur im Dokument, sondern auch im versiegelten
`execution-plan.json` als `auditory.endpoint_snapshot_index`.

NJ verlangt dagegen ausdruecklich:

```text
start == snapshot_index * 480
end == start + 4800
```

| Ereignis | Versiegelter Index | Versiegeltes Fenster | Von NJ bei diesem Index verlangter Start |
| --- | ---: | --- | ---: |
| e01 | 0 | [0,4800) | 0 |
| e02 | 1 | [4800,9600) | 480 |

Damit ist e02 die erste Verletzung genau dieser Zeitrelation. Fuer eine
ansonsten gueltige direkte Uebergabe des gebundenen Rohzustands wuerde NJ
`S2NJProjectionError` mit Code `SOURCE_TIME_INVALID` ausloesen. Die Pruefung
liegt vor der Energievalidierung und vor der Halbierung. Dies ist eine
statische Folgerung, keine beobachtete Exception eines neuen NS-Laufs.
Andere moegliche Quellen-/Rezeptorfehler sind damit weder ausgeschlossen
noch untersucht; auch die Rezeptorgueltigkeit von e01 ist nicht behauptet.

## Gelesene Stellen

- `docs/S2NS_STATISCHER_PLAN_AUDITIVE_ZWEI_SICHTEN_BESTAETIGUNG.md:120`:
  native Fenster und Snapshotindex n-1.
- `tools/_s2ns_private_source_binding.py:84`: dieselbe Ereignisbindung.
- `tools/_s2ns_private_preseal_verification.py:37`: die lesende Pruefung
  verlangt exakt dieses Tupel; es ist kein frei austauschbares Metadatum.
- `tools/_s2nj_private_auditory_output_projection.py:66`: feste Zeitrelation.
- `tools/_s2nj_private_auditory_output_projection.py:138`: Aufruf dieser
  Pruefung am tatsaechlichen Rohzustand vor der Projektion.
- `tests/test_s2ns_private_two_view.py:124`: die neutrale Logikpruefung
  verwendet einen gueltigen synthetischen NJ-Beleg mit Index 20 und Start
  9600; sie reproduziert nicht die versiegelte NS-Ereigniszeit.

Betroffene unveraenderte Ausfuehrungswurzel:
`reports/s2ns/s2ns-source-preseal-20260908-01/execution-plan.json`,
kanonischer Digest
`bd21e9e5f564e3a11dc2bb0a3dcb40d92a6a5336e863fa10a57c2eb86aa92816`.
Die bereits gespeicherte Quellenbindung ist damit nicht nachtraeglich
fehlgeschlagen; sie hat den vorgegebenen Plan konsistent versiegelt.
Die notwendige Kompatibilitaet dieses Plans mit NJ war noch nicht bewiesen.

## Konsequenz und engste offene Entscheidung

Unveraenderte Uebernahme des versiegelten Snapshotindex und unveraenderte
NJ-Zeitvalidierung sind ab e02 nicht gemeinsam erfuellbar. Weder NJ lockern
noch die historischen Planwurzeln ueberschreiben. Insbesondere den explizit
als Snapshotindex versiegelten Wert nicht still als andere Ordinalzahl
umdeuten.

Als kleinste zu entscheidende Anschlusskorrektur kommt eine **neue explizite
Indexbindung** in Betracht: die historische NS-Endpunktordinalbindung
unveraendert referenzieren und davon getrennt den fuer NJ erforderlichen
nativen Hopindex `window_start_sample // 480 = 10*(n-1)` binden.
Diese Anpassung benoetigt eine ausdrueckliche Entscheidung zur bisherigen
Snapshotvorgabe. Sie darf weder zusaetzliche Analysen/Hops ausloesen noch
Fenster, PCM-Bytes, Reihenfolge, Profil oder Vergleichsregeln veraendern.
Sie wurde hier nicht implementiert und ersetzt keine neue Freigabe.

Die Quellen-, Formationsketten- und Gesamtlaufimplementierung sowie der
einmalige Anschluss-Qualifikationsaufruf wurden nicht begonnen. Keine
Payloadregeneration, Rezeptor-/NJ-/Memory-/Feld-/Runtimeaufrufe, Tests,
Distanzberechnungen oder erneute Verifikation. Keine neuen Laufartefakte.
Gates unveraendert False; historische 14/14- und 24/24-Befunde bleiben
unveraendert in ihrem jeweiligen Umfang gueltig. Versiegelung, fremde
Aenderungen und Bootstrap unberuehrt.

RUECKMELDUNG ERFORDERLICH: Soll die minimale, getrennt versionierte
NS-Ordinal-/NJ-Hopindexbindung freigegeben werden? Erst danach kann die
beauftragte Laufanbindung ohne diesen deterministischen Widerspruch
implementiert und einmal neutral qualifiziert werden.
