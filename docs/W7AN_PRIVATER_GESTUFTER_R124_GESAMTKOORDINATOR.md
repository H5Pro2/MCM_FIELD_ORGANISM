# W7-AN: Privater gestufter R1/R2/R4-Gesamtkoordinator

## Entscheidung

`W7AN_PRIVATE_STAGED_R124_PRIMARY_REVERSE_COORDINATOR_PASSED`

Der private Gesamtkoordinator ist implementiert. Er startet selbst keine
Phase bei seiner Erzeugung und fuehrt pro `advance()`-Aufruf genau eine
Kindphase aus.

## Rollenfolge

Die sechs Aufloesungsdurchgaenge sind unveraenderlich geordnet:

```text
Primaer:         R1 -> R2 -> R4
Gegenlauf:       R4 -> R2 -> R1
```

Jeder Durchgang besitzt sechs Phasen. Der Koordinator bindet damit genau 36
Fortschritte und das bekannte Gesamtinventar von 1.254 Integrationen.

## P0-Einmaligkeit

Der Koordinator akzeptiert nur den kanonischen W7-AI-P0-Digest
`8b1945...771f5`. Jeder Kindexecutor erhaelt dasselbe P0-Referenzobjekt per
Identitaet. Eine Kopie, Neumaterialisierung oder aufloesungsbezogene P0-
Variante wird nicht erzeugt.

## Primaer- und Gegenlaufbindung

Ein Primaerresultat wird erst nach allen sechs Kindphasen gespeichert. Das
Primaer-R1 muss zusaetzlich den real nachgewiesenen gestuften Digest
`60be9b3c...16edc` reproduzieren.

Im Gegenlauf wird jedes vollstaendige Aufloesungsresultat mit dem
zugehoerigen Primaerdigest verglichen. Eine Abweichung setzt einen terminalen
Stopp; der Koordinator kann danach nicht weiterlaufen.

## Fehlervertrag

- Ein Kindphasenfehler erzeugt keinen Koordinatorbeleg.
- Der globale Phasenstand wird bei einem Kindfehler nicht erhoeht.
- Pro Aufruf kann hoechstens ein Kindphasenbeleg entstehen.
- Erst der 36. Beleg kann `coordinator_completed = true` setzen.
- Ein 37. Aufruf wird verworfen.
- Alle Zwischenobjekte bleiben im Arbeitsspeicher.

## Technische Pruefung

Der schnelle relevante W7-AN-Verbund besteht:

```text
29 tests, OK
```

Geprueft sind Rollenfolge, 36 Einzelschritte, P0-Objektidentitaet,
Kindfehlerstabilitaet, kanonische R1-Bindung, Gegenlaufgleichheit,
terminaler Mismatch-Stopp und fehlende oeffentliche Exporte. Die
Kindexecutoren wurden fuer diese Tests injiziert. Anschliessend wurde der
Koordinator mit allen 36 realen Phasen erfolgreich ausgefuehrt.

## Globale Finalisierung

Nach 36 bestandenen Phasen besitzt der Koordinator drei Primaer- und drei
Gegenlaufresultate. Der inzwischen implementierte reine Finalizer bindet
daraus Starttrennung, Substepordnung, R1-Kompatibilitaet und den bestehenden
Gesamtcontainerdigest, ohne eine weitere Integration auszufuehren.

## Aussagegrenze

Der Koordinator wurde mit allen 36 Phasen real ausgefuehrt. Primaer- und
Gegenlaufdigests waren fuer R1/R2/R4 gleich. Daraus folgen dennoch keine
Konvergenz, Feldfunktion, Memory, Feldzeit, Organisation, Semantik oder KI.
