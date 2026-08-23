# S1-VJ: PPB-1 privater reiner Referenzkern und synthetische Vertragsabnahme

## Freigabe und Grenze

S1-VJ setzt den in S1-VI gebundenen Implementierungsauftrag um. Implementiert
und ausgefuehrt wurden ausschliesslich:

- private unveraenderliche PPB-1-Schemarollen;
- normalisierte mittlere L1-Distanz;
- genau ein atomarer modalitaetseigener Bankschritt;
- kanonische SHA-256-Digests;
- die synthetischen Vertragspfade V01 bis V30;
- relevante Aktivkern-, Export- und Snapshot-Grenztests.

Nicht umgesetzt wurden Feldintegration, Rueckgabeadapter, `current_api`,
Root-Export, Snapshotumbau, reale Audio-/Videoausfuehrung oder Semantik.

## Implementierter privater Kern

Der reine Referenzkern liegt in:

```text
mcm_field_organism/_ppb1_reference.py
```

Das fuehrende `_` kennzeichnet die private Modulgrenze. Das Modul importiert
nur den bestehenden `ReceptorContactFrame` und Python-Standardbibliothek. Es
importiert weder `SharedMCMField` noch den neutralen Feldkern.

Implementiert sind:

| Rolle | Technische Funktion |
|---|---|
| `PPB1BankConfig` | getrennte Bank-, Geometrie-, Kapazitaets- und Lebenszyklusbindung |
| `PPB1PrototypeSlot` | freier oder belegter fester Prototypslot |
| `PPB1BankState` | unveraenderlicher modalitaetseigener Gesamtzustand |
| `PPB1Readout` | privater technischer Schrittreadout |
| `PPB1StepResult` | atomar zusammengehoeriger Poststate und Readout |
| `initial_ppb1_bank_state` | kanonischer leerer Zustand |
| `normalized_mean_l1_distance` | einzige Distanzfamilie |
| `advance_ppb1_bank` | reiner atomarer Bankschritt |

Alle Rollen validieren endliche Werte, technische Kennungen, feste
Dimensionen und kanonische Digests fail-closed.

## Umgesetzter Einzelschritt

Der reine Schritt arbeitet in der in S1-VI gebundenen Reihenfolge:

1. Konfiguration, Vorzustand und Rezeptorframe validieren.
2. Naechste modalitaetseigene Bankschrittnummer bestimmen.
3. Faellige Slots auf einer privaten Arbeitskopie vollstaendig freigeben.
4. Normalisierte mittlere L1-Distanzen berechnen.
5. Kleinste Distanz und bei Gleichstand kleinste Slot-ID waehlen.
6. Ohne Match den kleinsten freien Slot verwenden.
7. Ohne freien Slot den LRU-Slot, bei Gleichstand die kleinste Slot-ID,
   ersetzen.
8. Match konvex aktualisieren und den Stabilitaetszaehler saettigen.
9. Poststate und Readout kanonisieren und validieren.
10. Nur das vollstaendige atomare Ergebnispaar zurueckgeben.

Eingangsframes, Vorzustand und nicht ausgewaehlte Slots werden nicht mutiert.

## Modalitaetstrennung

Audio und Video verwenden getrennte Konfigurationen und Bankzustaende. Ein
Frame mit falscher Modalitaet oder Geometrie wird vor jeder
Zustandsfortschreibung abgelehnt.

Vergessen wird nur durch akzeptierte Schritte derselben Bank fortgeschrieben.
Der bestandene Pfad V25 verwendet einen real belegten visuellen Bankzustand
und zeigt, dass vier anschliessende auditive Bankschritte dessen Digest nicht
veraendern.

## Rohdaten- und Metadatengrenze

Prototypslots speichern nur die fest dimensionierten verdichteten
Rezeptorwerte, einen saettigenden Unterstuetzungszaehler und die letzte
modalitaetseigene Bankschrittnummer.

Nicht gespeichert werden:

- Audio-Samples oder Bildframes;
- Eingangs-Snapshot-ID;
- Quellfenster im Prototyp;
- Liste frueherer Rezeptorframes;
- Replayzeiger;
- Woerter, Objekt- oder Klassenlabels.

Clock und letztes Fensterende liegen nur einmal im Bankzustand zur
Reihenfolgenvalidierung. Vergessen verwendet keine System- oder Wandzeit.

## Ausgefuehrte 30-Pfade-Matrix

Ausgefuehrt wurde:

```powershell
python -m unittest tests.test_ppb1_reference -v
```

Finales Ergebnis:

```text
Ran 30 tests
OK
```

Die Matrix deckt ab:

- V01 bis V08: Schema und Fail-Closed;
- V09 bis V14: Distanz und deterministische Zuordnung;
- V15 bis V19: Bildung, Aktualisierung und Stabilisierung;
- V20 bis V25: Kapazitaet, Vergessen und Wiederverwendung;
- V26 bis V30: Reproduzierbarkeit, PPB-OFF und Oberflaechengrenzen.

## Transparente Fixturekorrekturen

Die erste Matrixausfuehrung bestand mit `28 von 30` Pfaden. Zwei
Testfixtures bildeten ihre registrierte Prueffrage nicht korrekt ab:

1. **V24:** Die erste Fixture waehlt den zu pruefenden Slot unmittelbar vor
   dem erwarteten Vergessen erneut aus und setzte damit dessen Altersstand
   korrekt zurueck. Die korrigierte Zwei-Slot-Folge laesst den Zielslot
   tatsaechlich faellig werden und prueft seine Neubelegung im selben Schritt.
2. **V30:** Die erste Fixture wertete einen durch den Test selbst geladenen
   privaten Submodulnamen in `dir(mcm_field_organism)` als oeffentlichen
   Export. Die korrigierte Pruefung bindet die tatsaechlichen oeffentlichen
   Oberflaechen: Paket-`__all__`, `current_api`, Root-Lazy-Exports und
   Snapshotfelder.

Beide Korrekturen veraenderten weder die S1-VI-Funktionsregel noch die
Referenzkernlogik. Danach bestand die unveraenderte 30-Pfade-Zielmatrix
vollstaendig.

## Aktivkern- und Oberflaechenregression

Zusaetzlich ausgefuehrt wurde:

```powershell
python -m unittest `
  tests.test_active_engineering_surface_boundary `
  tests.test_active_field_state_contract -v
```

Ergebnis:

```text
Ran 18 tests
OK
```

Die kombinierte Schlussausfuehrung bestand mit:

```text
48 von 48 Tests
```

Bestaetigt sind:

- keine PPB-1-Rolle in `current_api`;
- kein Root-Lazy-Export;
- kein Feldsnapshotfeld;
- keine Aenderung des aktiven Feldzustandsvertrags;
- keine Aktivierung geschlossener Forschungszweige;
- bitgleicher PPB-OFF-Vertragsdigest.

## Technische Abnahme

```text
S1_VJ_PRIVATE_PPB1_REFERENCE_KERNEL_IMPLEMENTED
S1_VJ_IMMUTABLE_CONFIG_SLOT_STATE_READOUT_IMPLEMENTED
S1_VJ_NORMALIZED_MEAN_L1_IMPLEMENTED
S1_VJ_ATOMIC_MODALITY_SPECIFIC_STEP_IMPLEMENTED
S1_VJ_ASSIGN_UPDATE_STABILIZE_FORGET_REPLACE_IMPLEMENTED
S1_VJ_CANONICAL_DIGESTS_IMPLEMENTED
S1_VJ_REGISTERED_30_OF_30_PATHS_PASS
S1_VJ_ACTIVE_BOUNDARY_18_OF_18_TESTS_PASS
S1_VJ_COMBINED_48_OF_48_TESTS_PASS
S1_VJ_NO_CURRENT_API_ROOT_EXPORT_OR_SNAPSHOT_ROLE
S1_VJ_NO_FIELD_INTEGRATION_NO_REAL_MEDIA_RUN
S1_VJ_ENGINEERING_COMPONENT_NOT_FIELD_CAUSE_FINDING
```

S1-VJ nimmt den privaten synthetischen PPB-1-Referenzkern technisch ab. Der
Befund gilt nur fuer die gebundene synthetische Viertraeger-Testwelt und die
private reine Kernfunktion.

Nicht belegt sind Eignung fuer reale auditive oder visuelle
Rezeptordimensionen, sinnvolle Produktionsparameter, Laufzeit- oder
Speicherbudget, Feldrueckgabe oder eine Memory-Funktion des Feldkerns.

## Genau ein naechster Schritt

Der einzige fachlich begruendete Anschluss ist:

```text
S1-VK - statischer PPB-1-Rezeptorbindungs-, Skalierungs- und
        Parameterkorridoraudit
```

S1-VK darf ausschliesslich die vorhandenen realen auditiven und visuellen
Rezeptorgeometrien, Traegerdimensionen, moegliche private Konfigurationen,
Speicher-/Laufzeitobergrenzen und getrennte Parameterkorridore auditieren.

Noch nicht zulaessig sind Adapterimplementierung, Feldintegration,
`current_api`, Snapshotumbau, reale Medienausfuehrung oder semantische
Auswertung.

## Projektgrundlagen

- [S1-VI Daten-, Distanz-, Lebenszyklus- und Testmatrixvertrag](S1VI_PPB1_STATISCHER_DATEN_DISTANZ_LEBENSZYKLUS_UND_TESTMATRIXVERTRAG.md)
- [S1-VH statischer PPB-1-Engineeringvertrag](S1VH_PPB1_STATISCHER_ENGINEERING_FUNKTIONS_SICHERHEITS_UND_INTEGRATIONSVERTRAG.md)
- [Privater PPB-1-Referenzkern](../mcm_field_organism/_ppb1_reference.py)
- [Synthetische PPB-1-Vertragstests](../tests/test_ppb1_reference.py)
- [Aktiver Rezeptorvertrag](../mcm_field_organism/receptor_contract.py)
- [Aktivkern-Konsolidierungsabschluss](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md)
