# S1AT: Vertrag fuer den passiven C_i-Nullkontakt

## Zweck

Der Vertrag trennt drei Dinge, die im bisherigen Gap-Lauf vermischt waren:

1. Feldnachhall ohne neue Rezeptorframes;
2. C_i-Abschwaechung ohne neue Weltzufuhr;
3. eine optionale Rueckwirkungspruefung unter explizit markierter Intervention.

Der Vertrag ist ein technischer Messvertrag. Er behauptet weder Memory noch
Vergessen.

## Verbindliche Weltgrenze

- Eingabequelle bleibt die kontrollierte synthetische Audio-/Video-Testwelt.
- Im Nullkontakt werden keine neuen Audio- oder Videoframes erzeugt.
- Es gibt keinen Browserzugriff, keine Kamera und kein Mikrofon.
- Die letzte Kontaktaufnahme wird als Snapshot abgeschlossen und eingefroren.
- Jede anschliessende Zustandsaenderung muss als Intervention benannt werden.

## Referenzzustand

Vor dem Nullkontakt werden gespeichert:

```text
S_contact     letzter gemeinsamer MCM-Feldsnapshot
C_contact     letzter C_i-Zustand
world_digest  Digest der kontrollierten Kontaktfolge
```

Rohdaten, Datenbanken oder Embeddings sind keine Memorydarstellung.

## Drei getrennte Arme

### N0: Feldnachhall-Hold

`S_contact` wird ohne weiteren Feldschritt nur beobachtet. C_i wird nicht
fortgeschrieben. Dieser Arm misst ausschliesslich, ob die bestehende
Feldreprasentation waehrend des Wartens unveraendert bleibt.

### N1: Passiver C_i-Abschwaechungstest

Es werden keine neuen Rezeptorframes zugefuehrt. Fuer den isolierten
Substrattest wird die externe Exposition explizit auf `E_i = 0` gesetzt:

```text
dC_i/dt = alpha * (1-C_i^2) * (0-C_i)
```

Das Feld `S_contact` bleibt unveraendert und wird nicht aus C_i aktualisiert.
Damit ist N1 nur ein Eingriff in die technische C_i-Gleichung, kein
Weltkontakt und kein Organismusverhalten.

### N2: Gekoppelter Nullkontakt

Wie N1, aber die aus dem C_i-Schritt berechnete Rueckwirkung wird auf eine
separate Kopie von `S_contact` projiziert. Der eingefrorene Referenzsnapshot
bleibt unveraendert. N2 misst die technische Kopplung, nicht die reine
Abschwaechung.

## Pflichtmessungen

Fuer jede Gap-Laenge `g` werden ausschliesslich aufgezeichnet:

- `max_abs(C_i_g)` und `Linf(C_i_g, C_i_contact)`;
- bei N2 zusaetzlich `Linf(S_g, S_contact)`;
- Digest des eingefrorenen Referenzsnapshots;
- Reproduzierbarkeit bei identischem `world_digest`;
- Vergleich gegen P0 und amplitudenkalibriertes leaky.

Es gibt keine Schwelle, die den Lauf automatisch als Memory, Vergessen oder
Lernen klassifiziert.

## Abbruchbedingungen

Der Lauf wird verworfen, wenn:

- im Nullkontakt neue Rezeptorframes erzeugt werden;
- N0 den Feldsnapshot veraendert;
- N1 trotz `E_i=0` externe Werte bezieht;
- N2 und N1 nicht getrennt protokolliert werden;
- ein technischer Zustand als Memory, Bedeutung, Organisation oder KI
  bezeichnet wird.

## Implementierungsstatus

Der N1-Grundschritt ist im aktuellen API-Pfad als
`advance_ci_null_exposure(...)` implementiert und nutzt explizit `E_i=0`.
N0 bleibt ein unveraenderter Snapshot-Hold und wird ueber Snapshot-Gleichheit
geprueft. Ein vollstaendiger N0/N1-Lauf mit drei Gap-Laengen ist noch nicht
ausgefuehrt.

Der naechste konkrete Schritt ist dieser fokussierte N0/N1-Test mit
deterministischem Snapshot-Digest.

## N0/N1-Testlauf

Der fokussierte Lauf wurde mit `1`, `2` und `4` passiven N1-Schritten
durchgefuehrt. Der N0-Snapshot blieb unveraendert; sein Digest war:

```text
113e58fce0e1b629dbf10b551fee9c9c2c4ea44f00bc1ae63d274cb2371ebf75
```

Die N1-Werte waren in beiden Kontaktvarianten identisch, weil der erste
Kontakt identisch ist:

```text
Schritte  max_abs(C_i)  Abstand zu C_contact  C_i-Digest
1         0.201499497   0.010106547           946c9f343ecb
2         0.191833587   0.019772457           eb7f5a83fc5f
4         0.173769532   0.037836512           6603e8846952
```

Die Abnahme ist eine deterministische Reaktion der expliziten `E_i=0`
Gleichung. Sie darf nicht als biologisches Vergessen oder Memoryleistung
bezeichnet werden.

## N2-Testlauf

N2 wurde mit denselben drei Gap-Laengen auf einer separaten Kopie des
eingefrorenen Aktivierungsvektors ausgefuehrt. Der Referenzsnapshot blieb bei
allen Schritten digest-identisch:

```text
113e58fce0e1b629dbf10b551fee9c9c2c4ea44f00bc1ae63d274cb2371ebf75
```

Die Kopie erhielt nur die technische Rueckwirkung aus dem jeweiligen N1-
Schritt:

```text
Schritte  max_abs(C_i)  Linf Feldkopie zu S_contact  Kopie-Digest
1         0.201499497   0.002526637                 4f05bc68f0f0
2         0.191833587   0.004943114                 0f7ddfe99371
4         0.182594882   0.007252790                 2aa8157ef8e0
```

N2 ist damit als getrennte technische Projektion reproduzierbar. Die
Abweichung befindet sich nur in der Kopie und ist kein veraenderter
Weltkontakt.
