# S1-GM: Statische Real-Batch-Adapter-Bindung

Stand: 2026-08-15

Status: `SCHNITTSTELLENKORREKTUR_KEINE_AUSFUEHRUNG`

## Ergebnis

Die reale Batch-Kernkette ist vorhanden und signaturkompatibel:

```text
aktuelles SharedMCMField
-> Batch-zu-Dock-Abbildung
-> lokale Neuroneneingaben
-> Fixed-Adapter-Feldkernel
-> naechstes SharedMCMField
```

Der aktuelle S1-GL-Injektionspfad reicht fuer diese Kette jedoch noch nicht
aus. Er uebergibt nur einen Digesttoken und erhaelt ein synthetisches Receipt.
Der reale Feldkernel gibt dagegen ein neues `SharedMCMField` zurueck. Dieses
Objekt muss explizit an den naechsten Batch und am Armende an den terminalen
Snapshot weitergereicht werden.

## Unzulaessige Abkuerzung

Das Feld darf nicht in einer Closure, einem globalen Dictionary oder einem
bindingbezogenen versteckten Cache gehalten werden. Ebenso darf das frische
S1-GH-Feld nicht in-place als versteckter Laufzustand mutiert und kein
terminaler Snapshot aus einem Digesttoken vorgetaeuscht werden.

## Kleinste notwendige Korrektur

Ein typisierter Live-Field-Carrier muss mindestens tragen:

```text
binding_digest
initial_field_digest
current_field
current_field_digest
completed_batch_count
accounted_source_support_count
actual_field_steps_executed
carrier_digest
```

Die spaetere Batch-Schnittstelle lautet damit:

```text
Fresh Binding + Batch + LiveFieldCarrier
-> LiveFieldCarrierTransition mit naechstem SharedMCMField
```

Die terminale Factory erhaelt denselben vollstaendigen Carrier und darf erst
dann den echten Feldsnapshot in den S1-GI-Output ueberfuehren.

## Einordnung

S1-GL bleibt als synthetische Kontrollflussabnahme gueltig. S1-GM korrigiert
nur die Annahme, ein Digesttoken allein koenne spaeter direkt durch den realen
Batch-Adapter ersetzt werden. Das ist eine begrenzte technische Typenluecke,
keine wissenschaftliche Sackgasse.

Entscheidung:

```text
REAL_BATCH_CHAIN_EXISTS_EXPLICIT_LIVE_FIELD_CARRIER_REQUIRED
```

## Bester naechster Schritt

S1-GN implementiert ausschliesslich den typisierten Live-Field-Carrier und
eine synthetische Carrier-Transition. Feldobjektidentitaet, Digestfortsetzung,
Batchzaehler und Supportbilanz werden geprueft; der reale Batch-Adapter und
Feldkernel bleiben geschlossen.
