# S1-HC: Reale Einmaltoken-Factory

Stand: 2026-08-15

Status: `PROZESSLOKALE_EINMALTOKEN_FACTORY_SYNTHETISCH_ABGENOMMEN`

## Umsetzung

S1-HC implementiert die dritte Komponente des S1-GZ-Plans. Die Factory nimmt
nur eine bereits durch S1-HB gebundene S1-GW-Autorisierung an und prueft sie
erneut gegen das exakte Gate und S1-GY-Ziel.

Das Token bindet:

- Autorisierungs- und externen Origin-Digest;
- Run, Gate, Binding, Batch und Carrier;
- maximal einen Adapteraufruf und einen Feldschritt;
- einen prozesslokalen Zustand `issued`, `consumed` oder `retired`.

Eine Autorisierung kann im selben Prozess nur einmal ein Token erzeugen. Das
Token kann weder kopiert, tiefkopiert, serialisiert noch nachtraeglich
umgebunden werden. Erfolg verlangt vorherigen Verbrauch; Erfolg und Fehler
beenden das Token dauerhaft.

## Strikte Grenze

Die Tests verwenden neue, synthetisch verifizierte S1-HB-Ereignisse. Dadurch
entstehen nur kurzlebige Testtokens. Das aktuelle `ok weiter` ist keine
Freigabe und erzeugt kein Produktionstoken. Die Factory besitzt keinen
Adapter-, Kernel-, Transition- oder Persistenzzugriff.

Entscheidung:

```text
REAL_SINGLE_USE_TOKEN_FACTORY_IMPLEMENTED_SYNTHETICALLY_VALIDATED
```

Dies ist technischer Integrationsfortschritt, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-HD implementiert die atomare Receipt-Factory als private Hilfsgrenze. Sie
darf ein S1-GV-Receipt nur aus einem bereits verbrauchten S1-HC-Token und den
vorher/nachher am Adapterrand aufgenommenen Belegen versiegeln; sie darf den
Adapter selbst noch nicht aufrufen.
