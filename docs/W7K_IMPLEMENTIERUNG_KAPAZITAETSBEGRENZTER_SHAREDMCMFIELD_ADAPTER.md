# W7-K: Implementierung des kapazitaetsbegrenzten SharedMCMField-Adapters

Stand: 2026-08-09

Entscheidung: `CAPACITY_LIMITED_SHAREDMCMFIELD_ADAPTER_IMPLEMENTED`

Arbeitsart: additive opt-in Runtimeimplementierung

Browser oder Forschungslauf: nein

## Implementierter Umfang

Neu implementiert wurde:

```text
mcm_field_organism/capacity_limited_mcm_f3_runtime.py
```

Das Modul kapselt die bestehende K2/F3-Runtime und setzt W7-G als einzige
alternative Kopplungsableitung ein. Es bietet getrennte opt-in Funktionen
fuer kontinuierliche und ereignisausgerichtete transiente Fortschreibung.

Der Adapter fuehrt keine zweite SSPRK-Implementierung ein. Schnelles S-Feld,
H-Nachhall, F0-Diffusion, Dissipation, Rezeptorgrenzen, Ereignisausrichtung,
Schrittgrenze und Commit stammen weiterhin aus `mcm_f3_runtime.py`.

## Additive Runtimepruefstelle

`mcm_f3_runtime.py` besitzt jetzt den privaten optionalen Parameter:

```text
_stage_validator = None
```

Bei `None` bleibt der vorhandene Pfad unveraendert. Bei expliziter Belegung
wird der Validator auf isolierten, nicht schreibbaren Vektorkopien aufgerufen:

- nach der bestehenden Eingangsvalidierung;
- nach jeder der drei SSPRK-Stufen;
- nach transienten Punktkontakten;
- unmittelbar vor Commit.

Der Validator darf keinen Zustand zurueckgeben. Fehler brechen vor Commit ab.
Der W7-K-Adapter bindet dort ausschliesslich `M_i <= C_site` und passive
Kapazitaetsdiagnosen.

## P0

Der P0-Nullarm bleibt der vorhandene exakte schnelle Feldpfad und durchlaeuft
keine SSPRK-Stufe. Der Adapter prueft den M-Vektor vor und nach dem
Basisaufruf. M bleibt exakt unveraendert; S/H und der gesamte resultierende
Snapshot sind identisch mit dem bisherigen P0-Runtimepfad.

## Konfiguration und Fortsetzung

`MCMCapacityLimitedRuntimeContract` bindet unveraenderlich:

```text
equation_id = w7k.capacity-limited-shared-mcm-field.v1
site_capacity
```

Die kanonische Konfiguration besitzt einen SHA-256-Digest. Nach dem ersten
abgeschlossenen Feldintervall liefert der Adapter eine separate
`MCMCapacityLimitedContinuationBinding` aus Snapshotdigest und
Konfigurationsdigest.

Ein bereits abgeschlossenes Feld kann nur mit dieser Bindung fortgesetzt
werden. Fehlende, geaenderte oder zu einem anderen Snapshot gehoerende
Bindungen werden vor der ersten Integrationsstufe abgewiesen. Ein aus Schema 2
wiederhergestelltes Feld akzeptiert dieselbe Bindung und erzeugt dieselbe
Fortsetzung wie der ununterbrochene Pfad.

Die Bindung wird nicht in `SharedMCMFieldSnapshot` gespeichert. Es gibt keine
Schemaaenderung und keinen neuen dynamischen Organismuszustand.

## Technische Diagnosen

Das Adapterergebnis kapselt das unveraenderte `MCMF3AdvanceResult` und fuegt
nur nichtpersistente skalare Rollen hinzu:

- Anzahl der Kapazitaetsvalidierungen;
- maximale lokale Masse;
- minimale freie Ortskapazitaet;
- maximale Kapazitaetsueberschreitung;
- Konfigurationsdigest.

Diese Werte werden nicht in die Feldentwicklung zurueckgeschrieben.

## Abnahme

Die W7-K-Tests pruefen:

- exakte P0-Gleichheit und unveraendertes M;
- aktive S/H/M-Grenzen, Gesamtmasse und Commitvalidierung;
- transiente Ereignis- und Kapazitaetsgrenzen;
- identische ununterbrochene und wiederhergestellte Fortsetzung;
- Ablehnung fehlender oder geaenderter Fortsetzungsbindung;
- Ablehnung eines ueberbelegten Eingangszustands vor Runtimecommit;
- nicht schreibbare Validatorvektoren und Rueckgabeverbot;
- deterministische Wiederholung und n/2n/4n-Verfeinerung;
- fehlenden Export aus `current_api`.

Der technische Verbund aus W7-K, bestehender K2/F3-Runtime, W7-I, W7-G und
allen vier `current_api`-/Architekturverbrauchersuiten besteht mit:

```text
56 tests, OK
```

## Unveraenderte Grenzen

Unveraendert blieben:

- `SharedMCMFieldSnapshot` und alle Schemata;
- die Default-K2/F3-Kopplung;
- `mcm_field_organism.__init__` und `current_api`;
- Browser-, Video-, Audio- und Rezeptoradapter;
- Reports und Forschungslaeufe.

W7-K belegt technische Integrationsfaehigkeit und lokale
Kapazitaetsinvarianz. Es belegt keine Praegung, Verdichtung, funktionale
Loesung, Wiederverwendung, Feldzeit, inneren Kontext, Memory, Organisation,
Semantik, Selbstregulation oder KI.

## Naechster Schritt

W7-L soll vor jeder Forschungsausfuehrung einen statischen Funktions- und
Gegenbaselinevertrag fuer die neue Runtime binden. Kandidat, unveraenderte
K2/F3-Referenz, Neutralisierungsarme, Wiederverwendungsprobe und harte
Stopplinien muessen vorab feststehen.
