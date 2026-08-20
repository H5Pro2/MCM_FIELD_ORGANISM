# S1-OP G2/D3 Zweischritt-F2-Komposition: Funktions- und Falsifikationsvertrag

## Status

S1-OP bindet ausschliesslich Funktion, kausale Reihenfolge und
Falsifikationsbedingungen fuer eine spaetere reine Zweischrittkomposition aus
den akzeptierten S1-OM-Projektions- und S1-OO-Commitschnittstellen. Der
Schritt bindet noch kein Schema, keine neue Registry, keine Implementierung
und keinen Testlauf.

Entscheidung:

```text
G2_D3_TWO_FRESH_CONTINUATION_PROJECTION_COMMIT_COMPOSITION_FUNCTION_AND_FALSIFICATION_BOUND
```

## Technisches Ziel

Die spaetere Komposition soll genau eine Frage pruefen:

```text
Kann ein vollstaendig ausgewaehlter erster D3-Zielzustand als einzige
Zustandsquelle eines zweiten, kausal anschliessenden F2-Schritts dienen?
```

Die Komposition darf dafuer weder einen Betrag noch einen Projektions-,
Commit- oder Validierungsbeleg als Folgeeingang verwenden. Sie darf keinen
Fortsetzungszaehler im D3-Zustand anlegen.

Die geplante reine Oberflaeche ist:

```text
compose_g2_d3_two_step_continuation(
    first_boundary_raw_bytes,
    second_boundary_raw_bytes,
    initial_d3_raw_bytes,
    formation_enabled,
    sequence_registry,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TwoStepCompositionResult
```

S1-OP implementiert diese Funktion nicht.

## Funktionsprognose

Fuer genau zwei lokale Fortsetzungen mit aktivierter Formation gilt die
technische Prognose:

```text
initial C0:
U=0.5, C=0.0

erster vollstaendiger Projektions-/Commitschritt:
m1=0.25
-> Mixed: U=0.25, C=0.25

zweiter vollstaendiger Projektions-/Commitschritt:
m2=0.125
-> Second: U=0.125, C=0.375
```

`free=0.5`, `blocked=0.0` und `capacity=1.0` bleiben in beiden Schritten
unveraendert. Der Aggregatprojektionsdigest bleibt ebenfalls unveraendert.

Diese Prognose prueft nur die technische Komponierbarkeit. Sie ist kein
Nachweis einer eigenstaendigen Kandidatenfunktion und kein Befund zur
hypothetischen MCM-Memory.

## Zwei symmetrische Kontrollketten

S1-OP bindet genau zwei spaetere Kontrollen:

```text
OP_V_XXX:
X[0] -> X[1] -> X[2]

OP_V_YYY:
Y[0] -> Y[1] -> Y[2]
```

In beiden Ketten bildet die erste Grenze die geschlossenen Ordinale `0/1`
und die zweite Grenze die geschlossenen Ordinale `1/2` ab. Die zweite Grenze
darf nicht erneut `0/1` verwenden.

Die beiden Orientierungen duerfen unterschiedliche Grenz-, Kontakt- und
Belegdigests besitzen. Ihre vollstaendigen D3-Zielbytes muessen nach jedem
Schritt bitidentisch sein, weil Orientierung nicht im D3-Record gespeichert
wird.

## Gebundene erste Grenzen

Die erste X- und Y-Grenze bleiben exakt die akzeptierten S1-OC-Bytes:

```text
X/X boundary input digest
= c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c

Y/Y boundary input digest
= 2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b

source anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f
```

Beide verwenden C0 als Originalquelle und erzeugen nach Projektion und
Commitauswahl exakt Mixed:

```text
Mixed D3 input digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

Mixed anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c
```

## Gebundene zweite X-Grenze

Die zweite X-Grenze traegt:

```text
prior_orientation = X
current_orientation = X
prior_interval_ordinal = 1
current_interval_ordinal = 2
prior_interval_closed = true
current_interval_closed = true

prior_contact_digest
= 0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15

current_contact_digest
= 17b667729869347fa7ae06607bf8088ae91e457287cb2d75ed572e11fa276097

source_d3_anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c

boundary_record_digest
= 7d499f00806f6a7e9afea9119aad09b5a74b736881a7a93bd61142fcce8e8ab0

boundary input digest
= 6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a
```

## Gebundene zweite Y-Grenze

Die zweite Y-Grenze traegt:

```text
prior_orientation = Y
current_orientation = Y
prior_interval_ordinal = 1
current_interval_ordinal = 2
prior_interval_closed = true
current_interval_closed = true

prior_contact_digest
= d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356

current_contact_digest
= d44980de014a1b20ffd0fbbf8de1fac867d3ed225394f33ca244d0ee142ff801

source_d3_anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c

boundary_record_digest
= b9756269da497da0c64a0e63e5a64f1c98497118b4ad9f61f74eafcd0786d9c0

boundary input digest
= dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32
```

## Gebundener Endzustand

Beide Kontrollketten muessen exakt dieselben finalen D3-Bytes erzeugen:

```text
capacity = 1.0
free = 0.5
bound_unconfigured = 0.125
bound_configured = 0.375
blocked = 0.0

resource_account_digest
= 95568070519f29b65e34a4c06d681f150e81776b2bae4dfac60b132276df1f52

aggregate_projection_digest
= bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e

anatomy_record_digest
= efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681

D3 input digest
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab
```

## Verbindliche Kompositionsreihenfolge

Die spaetere reine Funktion muss exakt abarbeiten:

```text
1. API-Typen und exakte Registries pruefen
2. ersten Vorschlag aus erster Grenze und initialem C0 intern projizieren
3. ersten Vorschlag mit C0 als Source und Current atomar auswaehlen
4. vollstaendige erste Commitbytes als einziges Zwischen-D3 uebernehmen
5. zweiten Vorschlag aus zweiter Grenze und diesen Zwischenbytes projizieren
6. zweiten Vorschlag mit denselben Zwischenbytes als Source und Current auswaehlen
7. vollstaendige zweite Commitbytes als finales Ergebnis ausgeben
8. alle transienten Projektions- und Commitobjekte verwerfen
9. hoechstens einen passiven Sequenzbeleg ausgeben
```

Der Vorschlag jedes Schritts stammt aus der reinen Projektionsfunktion. Die
Commitfunktion rekonstruiert ihn trotzdem erneut aus ihren Originalbytes.
Projektionsbelege werden nicht an die Commitfunktion uebergeben.

## Atomare Schrittgrenze

Schritt 2 darf erst beginnen, wenn Schritt 1 einen gueltigen
`PROJECTED_COMMITTED`-Status und exakt die Mixed-Bytes geliefert hat. Ein
Preview, ein Projektionsbeleg oder ein fehlgeschlagener Commit ist kein
Zwischenzustand.

Falls irgendeine Voraussetzung des ersten Schritts scheitert:

```text
second projection calls = 0
second commit calls = 0
final_d3_raw_bytes = not_computable
```

Falls der zweite Schritt scheitert, bleiben die ersten Commitbytes nur ein
lokales verworfenes Zwischenresultat. Die Kompositionsfunktion publiziert
weder Mixed noch einen Teilzustand.

## Kausale Grenzbindung

Die zweite Grenze muss gleichzeitig zwei Beziehungen erfuellen:

```text
second.prior_contact_digest = first.current_contact_digest
second.source_d3_anatomy_record_digest = first committed anatomy_record_digest
```

Eine zweite Grenze mit korrekter Orientierung, aber alter C0-Quelldigest ist
ungueltig. Ebenso ist eine korrekt auf Mixed gebundene Grenze mit erneutem
Ordinalpaar `0/1` fuer diese Zweischrittkomposition ungueltig.

Die D3-Zielbytes speichern weder Kontaktordinale noch Orientierungen. Diese
Kausalbeziehung bleibt ausschliesslich in den transienten Grenzinputs und im
passiven Sequenzbeleg nachvollziehbar.

## Fail-Closed-Bedingungen

Die Komposition muss ohne finale Zustandsbytes stoppen, wenn:

- ein Eingabetyp oder eine Registry nicht exakt gebunden ist;
- die erste oder zweite Grenze ungueltig ist;
- die zweite Prior-Kontaktdigest nicht der ersten Current-Kontaktdigest
  entspricht;
- die zweite Grenze nicht den ersten Commitrecord als D3-Quelle bindet;
- der erste Commit nicht exakt Mixed liefert;
- der zweite Commit nicht exakt Second liefert;
- ein Schritt `NO_CHANGE_COMMITTED`, `STALE_SOURCE` oder einen Fehlerstatus
  liefert;
- ein Betrag oder Beleg als Folgeeingang benoetigt wird;
- ein anderer Zustand als die ersten Commitbytes in Schritt 2 gelangt;
- X- und Y-Kette verschiedene D3-Zwischen- oder Endbytes erzeugen;
- ein Teilzustand vor vollstaendig erfolgreichem Schritt 2 sichtbar wird;
- eine O3-, Feld-, Runner-, Medien-, Netzwerk- oder I/O-Oberflaeche erreicht
  wird.

Ein Fehler wird nicht durch Wiederholung, Reparatur oder alternative
Parameter umgangen.

## Gegenbaseline- und Aussagegrenze

Die Zweischrittkomposition bildet eine deterministische konservative
Zahlenfolge. Ein angepasster zustandsbehafteter Adapter kann dieselbe Folge
abbilden. Die Komposition schliesst deshalb keine Gegenbaseline und belegt
keine eigene Abschwaechungs-, Interferenz-, Freigabe- oder
Wiederverwendungsfunktion.

S1-OP ist nur ein technischer Lebenszyklusvertrag fuer die weitere
Entwicklung einer hypothetischen MCM-Memory. Es gibt keinen Feldlauf, keine
O3-Rueckwirkung und keine Runtimepublikation.

## Naechster erlaubter Schritt

S1-OQ darf ausschliesslich API-Schema, Sequenzregistry, Vertragsdigest,
Phasen, Einzelcodes und passive Belegrollen fuer diese exakt zweistufige
Komposition binden.

S1-OQ darf keine Produktions- oder Testimplementierung, keinen Testlauf,
keine Runtimepublikation, keine O3-Auswertung und keinen Feld-, Transfer-
oder Runnerpfad ausfuehren.
