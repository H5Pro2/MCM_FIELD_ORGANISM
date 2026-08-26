# S1-VL: Privater PPB-1-Rezeptorprofilbinder und dimensionsskalierte synthetische Abnahme

## Auftrag und Grenze

S1-VL setzt den in S1-VK statisch gebundenen Anschluss um. Der Schritt
verbindet den privaten PPB-1-Referenzkern ausschliesslich mit vier bereits
vorhandenen reduzierten Rezeptorgeometrien. Er fuehrt weder Medienquellen
noch den MCM-Feldkern aus.

Zulaessig sind:

- private feste Profilbindungen;
- Ableitung von Geometrie-ID und Traegerfolge aus vorhandenen
  Rezeptorklassen;
- getrennte auditive und visuelle Bankkonfigurationen;
- Fail-Closed-Pruefung der S1-VK-Parameterkorridore;
- synthetische Dimensions-, Kapazitaets- und Aufwandspruefungen.

Nicht Bestandteil sind Feldintegration, `current_api`, Root-Export,
Snapshotumbau, Persistenz, reale Medien, Semantik oder eine Behauptung einer
endogenen Feldursache.

## Implementierte private Rollen

Das Modul
[`_ppb1_receptor_profiles.py`](../mcm_field_organism/_ppb1_receptor_profiles.py)
enthaelt:

- `PPB1ModalityParameters` fuer eine modalitaetseigene Parametergruppe;
- `PPB1ProfileParameters` fuer die getrennte Audio-/Video-Pruefung;
- `PPB1ReceptorProfileBinding` als kanonischen privaten Bindungsrecord;
- `bind_ppb1_receptor_profile` als reinen deterministischen Binder.

Der Binder importiert nur die vorhandenen Rezeptorklassen und den privaten
PPB-1-Kern. Er importiert keine Medienruntime und kein Feldmodul. Die
Parameter werden nicht automatisch aus Ergebnissen gewaehlt.

## Gebundene Profile

| Profil-ID | auditive Traeger | visuelle Traeger | Gesamt |
|---|---:|---:|---:|
| `browser` | 8 | 18 | 26 |
| `controlled` | 12 | 72 | 84 |
| `public-av` | 48 | 240 | 288 |
| `default-live` | 48 | 288 | 336 |

Die Geometrie-IDs und geordneten Traeger werden bei jeder Bindung neu aus
`LogSpectralReceptor`, `BroadbandHearingPath` und
`LocalChannelGridReceptor` abgeleitet. Dadurch bildet das private Modul die
vorhandenen Rezeptoren ab, statt ihre Kennungen als zweite unabhaengige
Quelle zu fuehren.

## Parametergrenze

Der Binder akzeptiert ausschliesslich die in S1-VK festgelegten Korridore:

| Parameter | auditiv | visuell |
|---|---:|---:|
| Kapazitaet | 8 bis 32 | 4 bis 16 |
| Matchschwelle | 0,02 bis 0,25 | 0,01 bis 0,20 |
| Aktualisierungsrate | 0,05 bis 0,50 | 0,05 bis 0,50 |
| Stabilisierung | 3 bis 16 | 3 bis 12 |
| Ablauf nach Bankschritten | 256 bis 8.192 | 64 bis 2.048 |

Unbekannte Profile, nicht endliche Werte, falsche Typen und Werte ausserhalb
dieser Grenzen werden vor der Erzeugung einer Bindung abgelehnt.

## Skalierungsabnahme

Die synthetische Abnahme prueft alle vier Profile bei den unteren und oberen
Korridorgrenzen. Sie materialisiert leere sowie voll belegte private
Bankzustaende und verarbeitet pro Geometrie genau einen synthetischen
`ReceptorContactFrame`.

Fuer `default-live` bei maximaler Kapazitaet werden exakt bestaetigt:

- 6.144 logische Prototypwerte;
- 49.152 Byte als rein mathematisches float64-Nutzlastaequivalent;
- 1.536 auditive Distanzterme pro voll belegtem Audioeingang;
- 4.608 visuelle Distanzterme pro voll belegtem Videoeingang.

Dies sind logische Obergrenzen, keine gemessene Python-Speicher- oder
Laufzeitaussage.

## Testergebnis

Die neue Abnahme besteht mit `14 von 14` Tests. Zusammen mit den 30
PPB-1-Kernpfaden und 18 aktiven Architekturgrenztests bestehen `62 von 62`
fokussierte Tests. Die Kompilierungspruefung fuer Paket und neues Testmodul
ist ebenfalls erfolgreich.

Geprueft werden insbesondere:

- exakte Profilgeometrien und deterministische Digests;
- Annahme beider Korridorenden und Ablehnung ausserhalb der Korridore;
- getrennte Kapazitaeten und korrekte Dimensionsskalierung;
- logische Maximalbudgets und deterministische Vollbankzuordnung;
- Abwesenheit aus Feldsnapshot, Root-Exports und `current_api`;
- fehlende Importe von Feld- oder Medienruntimes.

## Entscheidung

```text
S1_VL_FOUR_EXISTING_RECEPTOR_PROFILES_PRIVATELY_BOUND
S1_VL_GEOMETRY_AND_CARRIERS_DERIVED_FROM_EXISTING_RECEPTORS
S1_VL_S1VK_PARAMETER_CORRIDORS_FAIL_CLOSED
S1_VL_DIMENSION_AND_CAPACITY_BOUNDS_SYNTHETICALLY_ACCEPTED
S1_VL_14_OF_14_NEW_TESTS_PASS
S1_VL_62_OF_62_COMBINED_FOCUSED_TESTS_PASS
S1_VL_NO_PUBLIC_API_SNAPSHOT_FIELD_OR_MEDIA_INTEGRATION
S1_VL_ENGINEERING_BINDING_ONLY_NO_FIELD_CAUSE_FINDING
```

S1-VL bestaetigt, dass der private PPB-1-Kern die vorhandenen reduzierten
Rezeptordimensionen technisch und begrenzt aufnehmen kann. Der Schritt sagt
nicht aus, welche Parameter fachlich geeignet sind oder ob die Bank einen
nuetzlichen spaeteren Wahrnehmungszustand liefert.

## Genau ein naechster Schritt

**Abschlussstand:** Der nachstehend vorregistrierte statische Vertrag wurde
mit S1-VM erstellt. Diese Weiterfreigabe ist verbraucht. S1-VM erlaubt als
naechsten Schritt nur die private Runner- und Adapterimplementierung S1-VN,
noch ohne Ausfuehrung der gebundenen Matrix.

Der einzige fachlich begruendete Anschluss ist:

```text
S1-VM - statischer PPB-1-Parameterwahl-, Baseline- und
        Ausfuehrungsmatrixvertrag
```

S1-VM darf vor jeder weiteren Ausfuehrung nur festlegen:

- eine endliche, getrennte Audio-/Video-Parameterauswahl innerhalb der
  S1-VK-Korridore;
- labelfreie synthetische Faelle fuer Wiederholung, Trennung, Drift,
  Konflikt, Ablauf und Wiederauftreten;
- Metriken fuer Immer-Match, Nie-Match, Slotverbrauch, Fehlersetzung und
  spaetere technische Zuordnung;
- Gegenbaselines aus gleitendem Mittelwert, fester Prototypliste,
  Nachhall/Integrator soweit vergleichbar, Replay und PPB-OFF;
- ein endliches Ausfuehrungsbudget und eindeutige Stoppbedingungen.

S1-VM darf noch keinen Sweep oder Medienlauf ausfuehren und weder Feldkern,
API noch Snapshot aendern.

## Grundlagen

- [S1-VK Rezeptorbindungs- und Skalierungsaudit](S1VK_PPB1_STATISCHER_REZEPTORBINDUNGS_SKALIERUNGS_UND_PARAMETERKORRIDORAUDIT.md)
- [S1-VJ privater PPB-1-Referenzkern](S1VJ_PPB1_PRIVATER_REINER_REFERENZKERN_UND_SYNTHETISCHE_VERTRAGSABNAHME.md)
- [S1-VI PPB-1-Konstruktionsvertrag](S1VI_PPB1_STATISCHER_DATEN_DISTANZ_LEBENSZYKLUS_UND_TESTMATRIXVERTRAG.md)
