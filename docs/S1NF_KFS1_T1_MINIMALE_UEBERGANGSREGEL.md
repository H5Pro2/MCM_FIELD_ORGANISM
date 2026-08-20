# S1-NF KFS-1/T1 minimale Uebergangsregel

## Status

S1-NF waehlt genau eine minimale lokale Uebergangsregel fuer `KFS-1`:

```text
KFS1-T1_LOCAL_TARGET_REFRACTORY
```

Die Regel ist jetzt mathematisch festgelegt, aber noch nicht implementiert
oder ausgefuehrt. Sie besitzt keine frei waehlbare Rate, keinen angepassten
Schwellenwert und keine Runtime- oder Feldrueckwirkung.

S1-NF prueft noch keine KFS-1-Wirkung. Der Schritt bindet nur eine konkrete
Regel, die als Naechstes isoliert implementiert und verworfen werden kann.

## Lokale Eingangsbeobachtung

KFS-1/T1 verwendet die bereits vorhandene kanonische, symmetrische
Kantenbeteiligung aus den aktuellen schnellen Feldwerten der beiden
Kantenenden:

```text
p = ((S_i - S_j) / 2)^2
```

Gebundener Bereich:

```text
S_i, S_j in [-1, 1]
p in [0, 1]
```

Die Beobachtung ist invariant gegen Vertauschung der Kantenenden und
gemeinsame Vorzeichenumkehr. Bei gleichen Endwerten gilt exakt `p = 0`.

KFS-1/T1 liest dafuer nur den aktuellen lokalen S-Wert. H, Rohdaten, Labels,
Reward, Zielwerte, Readout, globale Nachbarschaft und Ergebniswissen sind
keine Eingaben. Die Beobachtung ist dieselbe wie in der registrierten
S1-HK-/DTS-1-Gegenbaseline; eine spaetere Differenz muss daher aus der neuen
Uebergangsregel und nicht aus einer anderen Eingangsmetrik stammen.

## Vorzustand

Fuer genau eine Kante sei der gueltige Vorzustand:

```text
C = endliche registrierte Kapazitaet
f = free
b = bound
r = blocked
C = f + b + r
```

Alle Werte sind endlich und nichtnegativ. `C` stammt aus der bereits
gebundenen Anatomie und ist kein in S1-NF anpassbarer Parameter.

## Zielbelegung

Die aktuelle lokale Zielbelegung ist:

```text
target = C * p
```

Damit wird keine Bedeutung oder Sollvorgabe eingefuehrt. `target` bezeichnet
nur den Anteil der lokalen Kapazitaet, den die aktuelle Kantenbeteiligung
innerhalb dieser Regel beanspruchen kann.

## Gebundene Regel

### Positiver lokaler Kontakt

Fuer `p > 0` gilt:

```text
wenn b < target:
    bind = min(f, target - b)
    block = 0

wenn b > target:
    bind = 0
    block = b - target

wenn b = target:
    bind = 0
    block = 0

release = 0
```

Ein positiver Kontakt kann somit freie Ressource bis zur lokalen Zielbelegung
binden oder eine ueber der Zielbelegung liegende Bindung in `blocked`
ueberfuehren. Bereits blockierte Ressource wird unter positivem Kontakt nicht
freigegeben.

Bei `b < target` bindet die aktuelle Kantenbeobachtung die
`LOCAL_CONTACT_OBSERVATION`. Bei `b > target` bindet dieselbe aktuelle
Kantenlage als reduzierte Zielbelegung eine getrennte
`LOCAL_BOUND_COMPLETION_OBSERVATION`. Die Beobachtung waehlt keinen
nachtraeglichen Ergebnistyp; das Rollenpaar folgt ausschliesslich aus
Vorzustand und `target`.

### Exakter lokaler Nullkontakt

Fuer `p = 0` gilt:

```text
bind = 0
block = b
release = r
```

Der Nullkontakt verschiebt die bisherige gebundene Ressource nach `blocked`
und gibt nur die bereits vor diesem Ereignis blockierte Ressource frei. Neu
blockierte Ressource darf nicht im selben Ereignis freigegeben werden.

Wenn `b` und `r` beide positiv sind, werden aus derselben lokalen Nullprobe
zwei getrennte passive Beobachtungsbelege abgeleitet:
`LOCAL_BOUND_COMPLETION_OBSERVATION` fuer den Eintritt von `b` in `blocked`
und `LOCAL_BLOCKED_RELEASE_OBSERVATION` fuer die Freigabe des vorbestehenden
`r`. Die zugehoerigen Bruttotransfers bleiben einzeln sichtbar.

`p = 0` ist der bereits gebundene exakte Nullfall der lokalen Beobachtung und
kein nachtraeglich gewaehlter Schwellenwert.

## Atomare Nachzustandsbildung

Der Nachzustand wird ausschliesslich aus dem geschlossenen Vorzustand und den
drei Transfers gebildet:

```text
f_next = f - bind + release
b_next = b + bind - block
r_next = r + block - release
```

Die Transfers werden kanonisch in dieser Reihenfolge protokolliert:

1. `LOCAL_CONTACT_BIND` oder `LOCAL_REFRACTORY_ENTRY`, falls der jeweilige
   Transfer positiv ist;
2. `LOCAL_REFRACTORY_RELEASE`, falls `release` positiv ist;
3. andernfalls die zutreffenden Stillstandsrollen.

`LOCAL_BOUND_RELEASE` bleibt in KFS-1/T1 gesperrt. Gebundene Ressource muss
zuerst in `blocked` uebergehen und kann erst in einem spaeteren Nullkontakt
freigegeben werden.

## Direkte technische Prognosen

KFS-1/T1 bindet vor Implementierung folgende Gegenprognosen:

1. Frischer Nullfall: Bei `f=C`, `b=r=0` und `p=0` bleibt das Ledger bitgleich.
2. Kontaktbindung: Bei freier Kapazitaet und `p>0` steigt `bound` hoechstens
   bis `C*p`.
3. Wiederholung: Gleicher Kontakt bei bereits erreichter Zielbelegung erzeugt
   keinen weiteren Transfer.
4. Refraktaerer Eintritt: Der erste Nullkontakt nach Bindung verschiebt
   `bound` nach `blocked`, gibt diese neu blockierte Ressource aber noch nicht
   frei.
5. Verzoegerte Freigabe: Erst ein weiterer Nullkontakt gibt die zuvor
   blockierte Ressource nach `free` zurueck.
6. Kontakt waehrend Blockierung: Ein positiver Kontakt gibt `blocked` nicht
   frei und kann nur die bereits freie Restkapazitaet binden.
7. Zustandsintervention: Derselbe aktuelle Wert `p` kann bei verschiedenen
   gueltigen `free/bound/blocked`-Vorzustaenden unterschiedliche Transfers
   erzeugen.
8. Lokalitaet: Der Vorzustand einer anderen Kante darf keinen Transfer auf
   der geprueften Kante veraendern.

Diese Prognosen betreffen nur das Ressourcenledger. Eine spaetere
Feldaufnahmeaenderung ist damit noch nicht prognostisch gebunden.

## Abgrenzung zu Gegenbaselines

| Gegenbaseline | Abgrenzende T1-Prognose |
|---|---|
| Fixed Adapter | gleicher aktueller S-Zustand kann wegen verschiedener lokaler Ledger unterschiedliche Transfers erzeugen |
| Gain oder feste Kante | besitzt keinen endlichen `free/bound/blocked`-Umsatz und keine verzoegerte Freigabe |
| schneller Leaky-Nachhall | monotone passive Abklingung bildet nicht automatisch den gebunden-zu-blockiert-zu-frei-Pfad ab |
| einfacher Integrator/Saettigung | akkumuliert, besitzt aber ohne Zusatzrollen keine getrennte refraktaere Freigabe |
| Replay/Puffer | T1 liest keine vergangene Sequenz und gibt keine Folge erneut aus |
| globale Normalisierung | andere Kanten beeinflussen die lokale T1-Regel nicht |
| bestehendes DTS-1 | verwendet dieselbe Beteiligungsmetrik, aber kontinuierliche frei waehlbare Bindungs-, Umsatz- und Erholungsraten statt der parameterfreien diskreten T1-Regel |

Die bestehende DTS-1-Implementierung ist eine verpflichtende strukturelle
Gegenbaseline. Wenn sie alle T1-Ledgerprognosen und eine spaetere Feldwirkung
innerhalb der vorregistrierten Toleranz vollstaendig reproduziert, besitzt T1
keine eigene technische Evidenzachse und wird als redundanter Kandidat
gestoppt oder als diskrete DTS-1-Baseline umklassifiziert.

## Parametergrenze

S1-NF erlaubt:

- die bereits anatomisch registrierte Kapazitaet `C`;
- die aktuelle lokale Beobachtung `p`;
- den gueltigen lokalen Vorzustand `f/b/r`;
- exakte endliche Arithmetik innerhalb des spaeter gebundenen Zahlenformats.

S1-NF verbietet:

- Bindungs-, Umsatz-, Erholungs- oder Leckraten;
- angepasste Schwellenwerte;
- Zeitkonstanten oder Alterszaehler;
- stochastische Auswahl;
- Optimierung, Parametersuche oder Ergebnisanpassung;
- globale Normierung oder Nachbarvergleich;
- H, Labels, Reward, Zielwerte, Rohdaten oder Readout als Regeleingang.

## Verwerfungsbedingungen

KFS-1/T1 wird vor jeder Feldkopplung verworfen oder zurueckgestuft, wenn:

- die reine Regel eine negative, nicht endliche oder nicht erhaltene Bilanz
  erzeugt;
- Transfer und Nachzustand nicht deterministisch aus demselben Vorzustand und
  demselben `p` folgen;
- neu blockierte Ressource im selben Nullkontakt wieder freigegeben wird;
- positiver Kontakt blockierte Ressource freigibt;
- eine andere Kante oder globale Groesse fuer den lokalen Schritt noetig ist;
- eine freie Rate, Schwelle oder Ergebnisanpassung erforderlich wird;
- die Regel auf Fixed Adapter, einfachen Leaky-Nachhall oder einfachen
  Integrator reduziert werden kann;
- die bestehende DTS-1-Gegenbaseline die gebundenen T1-Prognosen vollstaendig
  reproduziert und keine spaetere eigene Feldgegenprognose formulierbar ist.

## Aussagegrenze

S1-NF waehlt eine technische Uebergangsregel. Es gibt noch keine
Implementierung, keinen Feldlauf, keine Feldrueckwirkung, keinen
Funktionsbefund und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-NG, ausschliesslich als reine isolierte
Implementierung von KFS-1/T1 fuer genau eine Kante und eine einmalige
fokussierte Abnahme der acht direkten Ledgerprognosen. Die Implementierung
darf keine Feldklasse, keinen Runner und keine bestehende DTS-1-Dynamik
importieren. Runtimeintegration, Mehrkantenlauf, Feldrueckwirkung,
Parametersuche und Funktionsentscheidung bleiben gesperrt.
