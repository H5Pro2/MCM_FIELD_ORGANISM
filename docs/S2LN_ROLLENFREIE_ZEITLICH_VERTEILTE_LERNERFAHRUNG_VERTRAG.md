# S2-LN - Rollenfreie zeitlich verteilte Lernerfahrung

## Status und Zweck

`S2LN_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-LN bindet den ersten endlichen Funktionslauf ueber den qualifizierten
S2-LM-Wahrnehmungsstrom:

```text
zeitlich geordnete reale AV-Ereignisse
-> gemeinsamer unveraenderlicher Wahrnehmungsbeleg
-> unabhaengige Feld- und Memory-Geschwisterprojektionen
-> zeitlich verteilte Wiederholung und Slow-Verdichtung
-> Verlust aus A_RECENT
-> spaetere auditive und visuelle Teilhinweise
-> read-only Kontext-Hypothese oder Enthaltung
-> getrennte nachgelagerte Nutzenbewertung
```

Dieser Vertrag implementiert und startet nichts. Er fuehrt keine neue
Memorymechanik, keine Feldkopplung, keine automatische Kontextwahl und keine
fachlichen Rollen in den Laufpfad ein.

Ausgangscommit ist
`cd00cd345b455b0b3699133aeb6d1eb595ef2f50`.

## Gebundene technische Quellen

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| kanonische AV-Grenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| zeitgeordneter Feldpfad | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |
| atomare Zwei-Bereich-Memory | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| visueller Teilhinweisscan | `tools/_s2kq_private_partial_cue_retrieval_336.py` | `669e3f7de6957640ed37e79d6608d94d7839d81e959ee1f48d7942526a86e422` |
| auditiver Teilhinweisscan | `tools/_s2kz_private_auditory_partial_cue_retrieval_336.py` | `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b` |
| rollenfreier Stromprozessor | `tools/_s2lm_private_role_free_stream_processor.py` | `210cd182a5ccd8e3043c2bb5efb8668bb3fbc84c42e55a89b3141c8f7d04b750` |
| Default-Live-RGB-Fixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |
| PCM- und AV-Fixtures | `tools/_s2ld_auditory_partial_cue_fixtures.py` | `f6815f7cb0657eff05d230bec0e11d8f8ade6a8487e3c94ece07ca00a08326e6` |
| visuelle Okklusionsfixture | `tools/_s2ks_real_partial_cue_fixtures.py` | `3c643accd5418c44a0a24f6c3afa19ce12261eb32fa0bcd29c8b57047b3b2275` |

Historische Ergebnisdateien liefern weder Zustand noch Kandidaten. Der Lauf
beginnt mit einem frischen Nullfeld und einem frischen leeren Memoryzustand.

## Unveraendertes Profil

Gebunden bleiben:

- visuell `1920 x 1080 RGB8`, `12 x 8 x 3 = 288` Rezeptorwerte;
- auditiv mono `PCM_F32LE`, 48 kHz, 4.800 Samples und 48 Rezeptorwerte;
- genau 336 reduzierte Werte je vollstaendigem AV-Ereignis;
- B4-Kapazitaet 9;
- TSPM-Fast-Kapazitaet 3 und Ablauf nach 8 Expositionen;
- gemeinsamer Fast-Match nur bei Audio `<= 0.2` und Video `<= 0.2`;
- auditive Slow-Kapazitaet 8 bei Schwelle `0.02`;
- visuelle Slow-Kapazitaet 4 bei Schwelle `0.01`;
- PPB-Update `0.05` und Stabilitaet ab Support 3.

Die Schwellen sind bestehende mechanische Grenzen. S2-LN kalibriert sie nicht
als allgemeine Wahrnehmungsmetrik.

## Rollenfreier Ausfuehrungsplan

Der Ausfuehrungspfad kennt ausschliesslich die neutralen Ereignis-IDs
`e01` bis `e18`, deren Typ, Zeit, Quelle und Payloaddigests. Die ersten 16
Ereignisse sind vollstaendige AV-Wahrnehmungen; `e17` ist ein auditiver und
`e18` ein visueller Teilhinweis.

Die fachliche Lesart der Inhalte ist eine getrennte, vorab versiegelte
Auswerterzuordnung:

```text
Lauf:       e01 e02 e03 e04 e05 e06 e07 e08 e09 e10 e11 e12 e13 e14 e15 e16
Auswerter:   T  D1  T  D2  T  D3  T  D4  D5  D6  D7  D8  D9  D1  D2  D3
```

Diese zweite Zeile ist kein Elternbeleg des Ausfuehrungsplans. Insbesondere
duerfen `T`, `D`, `TARGET`, `DISTRACTOR`, Sollstatus und erwarteter Bereich
nicht in Lauf-IDs, Quell-IDs, Pfaden, Ereignissen, Receipts, Fehlertexten oder
Steuerzweigen erscheinen.

Die Lauf-Fixture bindet stattdessen neutrale Inhalts-IDs und konkrete
kanonische RGB-/PCM-Payloaddigests. Gleiches Material bei einer spaeteren
Wahrnehmung erhaelt eine neue Quelle, ein neues Zeitfenster und einen neuen
Quelldigest. Keine alte Ergebnisdatei wird geladen.

Die neutrale Quellenprojektion ist vollstaendig festgelegt:

| neutrale Inhalts-ID | gebundene auditive Rezeptur | gebundene visuelle Rezeptur |
| --- | --- | --- |
| `c00` | vorhandenes PCM `P` | vorhandenes RGB `X` |
| `c01` bis `c09` | vorhandenes PCM `D_FAR` | vorhandenes RGB `D1` bis `D9` positionsgleich |

Der Ausfuehrungsplan verwendet nur `c00` bis `c09`; die Rezepturbezeichnungen
sind ausschliesslich statische Materialisierungsbelege. Die Ereignisbindung
lautet:

```text
e01 c00  e02 c01  e03 c00  e04 c02
e05 c00  e06 c03  e07 c00  e08 c04
e09 c05  e10 c06  e11 c07  e12 c08
e13 c09  e14 c01  e15 c02  e16 c03
```

Vor dem ersten Memoryaufruf muessen die real erzeugten 48- und 288-Werte,
ihre Payload- und Wertedigests sowie fuer jedes ungleiche Paar die bestehende
Fast-AND-Entscheidung gebunden sein. Eine Abweichung stoppt ohne Memoryaufruf;
es gibt keine Ersatzfixture oder Parameteranpassung.

## Quellen und Zeit

Jedes vollstaendige Ereignis besitzt:

- ein neues kanonisches RGB8-Frame und ein ueberlappendes PCM-Fenster;
- getrennte native Video- und Audiouhren;
- eine gemeinsame Feldabschlussgruppe;
- exakt einen vor beiden Armen gebildeten `BoundPerception336V1`;
- einen frischen, genau einmal verwendbaren Ereignis-Owner.

Die 16 AV-Fenster folgen in festen 100-ms-Schritten. Native Fenster derselben
Quelle sind streng monoton. Audio und Video eines Ereignisses sind innerhalb
ihrer gemeinsamen Abschlussgruppe simultan und erhalten keine kuenstliche
Binnenreihenfolge.

`e17` und `e18` liegen auf ihren jeweiligen nativen Uhren strikt nach `e16`.
Gemeinsame Feldzeit ersetzt keine native Rezeptorzeit.

Rohpixel und PCM-Samples sind nur waehrend der Rezeptorreduktion vorhanden.
Hoechstens ein Frame und ein Audiohop werden gleichzeitig gehalten; kein
Rohpayload gelangt in Feld, Memory, Stromzustand, Scan, Hypothese oder
Ergebnisbeleg.

## Erwartete Memoryspur

Die folgende Spur ist ausschliesslich eine Auswertungsvorhersage. Die
Memoryformationen erhalten nur die neutralen 336-Werte-Belege.

| Ereignis | erwartete mechanische Wirkung |
| --- | --- |
| `e01` | neue Fast-Spur fuer den spaeter als T bewerteten Inhalt |
| `e02` | neue getrennte Fast-Spur |
| `e03` | T-Fast-Match; Slow `CREATED`, Support 1 |
| `e04` | neue getrennte Fast-Spur |
| `e05` | T-Fast-Match; Slow `MATCHED`, Support 2 |
| `e06` | neue getrennte Fast-Spur; aeltester Fremdslot wird ersetzt |
| `e07` | T-Fast-Match; Slow `MATCHED`, Support 3 |
| `e08` bis `e10` | getrennte Fremdspuren; T verschwindet aus Fast |
| `e11` bis `e16` | weitere getrennte Fremdspuren; T verschwindet aus B4 |

Nach `e16` muss gelten:

- B4 enthaelt in Bildungsreihenfolge genau `e08` bis `e16`;
- T ist weder in B4 noch in TSPM-Fast vorhanden;
- T ist in auditiver und visueller Slow-Bank stabil mit Support 3;
- kein anderer Inhalt besitzt einen stabilen Slow-Slot;
- die spaeten Inhalte von `e14` bis `e16` sind neue Fast-Spuren und keine
  Updates ihrer laengst ersetzten beziehungsweise abgelaufenen Vorgaenger.

Die zweimal vorkommenden Inhalte D1 bis D3 liegen so weit auseinander, dass
ihre erste Fast-Spur vor der zweiten Wahrnehmung nicht mehr vorhanden ist.
D4 bis D9 erscheinen nur einmal. Damit darf keine Distraktorverdichtung aus
der Ereignisfolge entstehen.

### Slow-Uebergangsintegritaet

Audio und Video werden getrennt aus der tatsaechlichen PPB-Kette abgeleitet:

```text
CREATED  support 1
MATCHED  support 2
MATCHED  support 3
```

Die Prototypen folgen exakt der vorhandenen Binary64-Reihenfolge mit
`update_rate = 0.05`. Bitgleichheit zum ersten Rezeptorvektor wird nicht
vorausgesetzt. Ereignis-, Eingangs-, Support-, Prototyp- und Slotdigests
muessen die Kette vollstaendig binden.

## Unabhaengige Feld- und Memoryzweige

Fuer `e01` bis `e16` entstehen aus demselben Wahrnehmungsbeleg unabhaengige
Geschwisterprojektionen:

- Feld: genau 48 auditive und 288 visuelle Kontakte;
- Memory: genau eine atomare B4-/TSPM-Formation.

Der Feldabschluss haengt nicht vom Memoryergebnis ab. Ein Memoryfehler darf
einen gueltigen Feldkontakt nicht rueckgaengig machen. Ein Feldfehler darf
die unabhaengige Memoryformation nicht unterdruecken. Atomar bleibt nur der
B4-/TSPM-Verbund.

Fuer `e17` und `e18` gilt entsprechend:

- der reale Teilhinweis erzeugt seinen Feldkontakt;
- danach erfolgt ausschliesslich read-only ein vollstaendiger Slotscan;
- ein Scanfehler darf den Feldkontakt nicht rueckgaengig machen;
- der Strom bleibt nach jedem verbrauchten Ereignis-Owner `OPEN`.

Ein technischer Zweigfehler kann den Forschungslauf `NOT_EVALUABLE` machen,
ohne tatsaechlich erfolgte Kontakte oder Formationen umzudeuten.

## Zwei spaetere Teilhinweise

### `e17` - auditiver Teilhinweis

Ein neues echtes PCM-Fenster erzeugt 48 Rezeptorwerte. Der unabhaengige
24/24-Bandplan bindet 24 beobachtete und 24 maskierte Baender. Der Scan liest
vollstaendig `9/3/8` Slots; Produktionsscan und Direktbaseline besitzen
getrennte Owner und hoechstens je 528 Wertvergleiche.

### `e18` - visueller Teilhinweis

Ein neues tatsaechlich okkludiertes RGB8-Frame erzeugt 288 Rezeptorwerte.
Die unabhaengige Positionsmaske bindet 32 beobachtete und 256 maskierte
Positionen. Das vollstaendige Zielbild wird nicht vorher analysiert. Der Scan
liest vollstaendig `9/3/4` Slots; Produktionsscan und Direktbaseline besitzen
getrennte Owner und hoechstens je 800 Wertvergleiche.

Beide Teilhinweise muessen genau einen passenden oeffentlichen Kandidaten aus
`B_STABLE` oder eine mechanisch korrekte Enthaltung ergeben. Es gibt keine
Rangfolge, Verschmelzung, Nearest-Winner-Regel oder crossmodale Auswahl.

## Hypothesenbeleg und Kontextnutzen

Der bestehende S2-LM-Scanbeleg bindet den Hypothesendigest. Fuer S2-LN muss
der einmal erzeugte Scan zusaetzlich einen unveraenderlichen, typisierten
Hypothesenbeleg mit genau den vorgeschlagenen maskierten Werten an das
Ereignisresultat uebergeben:

- auditiv hoechstens 24 Werte;
- visuell hoechstens 256 Werte;
- Bereich ausschliesslich `A_RECENT` oder `B_STABLE`;
- Scan-, Cue-, Masken-/Bandplan-, Memoryvorzustands- und Hypothesendigest;
- keine beobachteten Werte, Zielwerte oder Evaluationsrolle.

Dieser Beleg muss aus demselben urspruenglichen Scanaufruf stammen. Eine
zweite Memoryprobe, eine Rekonstruktion aus dem Digest oder ein versteckter
Adapter-Seiteneffekt ist verboten. Ist der Beleg nicht vollstaendig
materialisierbar, bleibt ein spaeterer Lauf `NOT_EVALUABLE`.

Erst nach abgeschlossenem Ausfuehrungspfad darf der getrennte Auswerter die
maskierten Zielwerte binden und drei fachliche Projektionen vergleichen:

1. `CURRENT_PERCEPTION_ONLY` laesst maskierte Werte unaufgeloest;
2. die S2-LM-Hypothese ergaenzt ausschliesslich maskierte Werte;
3. die unabhaengige Direktbaseline ergaenzt mit demselben Cue und Budget.

Kontextnutzen liegt fuer eine Modalitaet nur vor, wenn die Hypothese den
Rekonstruktionsfehler gegenueber Current-only verringert, beobachtete Werte
unveraendert bleiben und Produktionsscan sowie Direktbaseline fachlich
uebereinstimmen. Die Hypothese wird weder ins Feld noch ins Memory
zurueckgeschrieben.

## Gebundene Arbeitsgrenzen

| Position | Grenze |
| --- | ---: |
| Stromereignisse | 18 |
| vollstaendige AV-Formationen | 16 |
| auditive Rezeptoranalysen | 17 |
| visuelle Rezeptoranalysen | 17 |
| Feldfortschreibungen | 18 |
| atomare Memoryformationen | 16 |
| Produktionsscans | 2 |
| unabhaengige Direktscans | 2 |
| Feldkontakte | `16 * 336 + 48 + 288 = 5.712` |
| Memory-L1-Terme | `16 * 3.552 = 56.832` |
| Scanvergleiche gesamt | hoechstens `2 * 528 + 2 * 800 = 2.656` |
| kumulierte rohe Eingangsbytes | hoechstens `106.080.000` |
| gleichzeitig gehaltene Rohdaten | hoechstens ein RGB-Frame und ein PCM-Hop |

Die spaetere Implementierung verwendet keine Operationsregistry und keinen
append-only Recorder. Fuer die 18 Ereignisse genuegen genau:

- ein unveraenderliches Tupel neutraler Ereignisspezifikationen;
- feste kumulative Zaehler fuer die oben gebundenen Arbeitsklassen;
- ein einziger atomar veroeffentlichter Ergebnisbeleg;
- ein unabhaengiger read-only Verifikator.

Kein Budget darf durch einen vorzeitigen Slotscan oder das Weglassen eines
Arms eingehalten werden. Eine unvollstaendige atomare Ergebnisform ist
`NOT_EVALUABLE` und wird weder fortgesetzt noch ergaenzt.

## Getrennte Auswertung

Der vorab versiegelte Auswertungsplan ist eine unabhaengige Wurzel und kein
Elternbeleg des Ausfuehrungspfads. Erst ein vollstaendiger rollenfreier
Ausfuehrungsbeleg darf mit ihm verbunden werden.

Der Auswerter prueft getrennt:

- zeitlich verteilte Verdichtung von T in beiden Slow-Banken;
- Support 3 und beide PPB-Uebergangsketten;
- Verlust von T aus B4 und Fast nach `e16`;
- Abwesenheit stabiler Distraktorprototypen;
- auditiven und visuellen eindeutigen Teilhinweisabruf;
- Nutzen der beiden getrennten Kontext-Hypothesen;
- Gleichheit mit den unabhaengigen Direktbaselines;
- Feld-/Memory-Geschwisterbindung und Fehlerisolation;
- unveraenderte Memorydigests waehrend beider Teilhinweise;
- unveraenderte Feldzustaende durch Scan, Hypothese und Auswertung.

## Ergebnisregeln

`NOT_EVALUABLE` gilt bei Quellen-, Zeit-, Profil-, Geschwister-, Owner-,
Digest-, Scan-, Hypothesen-, Rohdaten- oder Budgetbruch sowie bei Rollen- oder
Zielwertleck im Laufpfad.

Ein vollstaendiger, technisch gueltiger Lauf ist fachlich falsifiziert, wenn
mindestens eine der folgenden Vorhersagen abweicht:

- T erreicht nicht Support 3 in beiden Slow-Banken;
- T bleibt nach `e16` in A_RECENT oder ein Distraktor wird stabil;
- einer der beiden Teilhinweise liefert nicht den gebundenen eindeutigen
  B_STABLE-Befund;
- der Kontextbeleg verbessert die jeweilige maskierte Wahrnehmung nicht;
- Produktionsscan und Direktbaseline weichen fachlich voneinander ab.

Nur wenn alle technischen und fachlichen Bedingungen gemeinsam gelten, darf
der spaetere Status
`S2LN_ROLE_FREE_DISTRIBUTED_AV_EXPERIENCE_CONFIRMED` lauten.

## Aussagegrenze und naechstes Gate

Ein positives Ergebnis bestaetigt eine begrenzte, zeitlich verteilte und
rollenfreie Online-Erfahrung: Wiederholung und Vergessen entstehen aus der
Ereignisfolge; spaetere Teilhinweise koennen den stabilisierten Inhalt als
getrennte read-only Hypothese nutzbar machen.

Nicht bestaetigt werden Semantik, automatische Maskenerkennung, automatische
Kontextwahl, unbegrenzter Betrieb, Feldlernen oder besondere MCM-Physik. Die
Direktbaselines bleiben die erwartete technische Erklaerung.

Eine spaetere begrenzte Implementierung muss die neutralen RGB-/PCM-Quellen,
Zeitfenster und den typisierten Hypothesenbeleg vor dem ersten Memoryaufruf
vollstaendig materialisieren. Hauptlauf, Runner, Recorder und reale
Memoryausfuehrung bleiben bis zu einer getrennten Freigabe gesperrt.
