# S2-JG - Architektur- und Kontextzulassungsvertrag

## Status und Zweck

`STATIC_CONTROLLED_PERCEPTUAL_CONTEXT_ADMISSION_CONTRACT_BOUND`

S2-JG konsolidiert den bestaetigten privaten Wahrnehmungs- und Memorypfad und
bindet genau eine naechste Funktion: die vorsichtige, read-only Zulassung eines
bereits beurteilten inneren Wahrnehmungskontextes. Der Vertrag fuehrt keine
neue Memory-Ebene, keine Auswahl einer "besten Erinnerung" und keine
MCM-spezifische Wirkungsbehauptung ein.

Noch nicht freigegeben sind Implementierung, Tests, Runner, Ausfuehrung,
oeffentliche API, Snapshotaenderung, Feldrueckwirkung, Semantik oder
Lernoperation.

## Gebundener Bestand

Der Vertrag ist an den technischen Stand
`91ea7fdd1d0c15e8b24201eb02c74a73db16df60` und folgende unveraenderte
Grundlagen gebunden:

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Atomarer B4-/TSPM-Koordinator | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| Drei-Rollen-Kontextbundle | `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| Zwei-Bereich-Projektion | `tools/_s2gi_private_two_area_context_projection.py` | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` |
| Fuenf-Status-Signalgeber | `tools/_s2ic_private_two_area_conflict_signal.py` | `a99d29379b3f6c7883eeb5f000c1e70fa37e652282a7305820ab823fcc726191` |
| Rezeptorgetreue Aggregatbindung | `tools/_s2jd_private_aggregate_context_binding.py` | `2b063900d76a4974f3ecabf23dc182b8401a3e76a7caa9e1532a36939a99852f` |
| Bestaetigter Fuenf-Status-Befund | `reports/s2jf/s2jf-five-status-confirmation-20260901-01-control/RESULT.md` | `8fa4c38a041e3538e3ccec01d6cb99086c3e0a6c340093632b0c6f9be63cb55b` |

S2-JF bestaetigt alle fuenf Statuswerte fuer real gebildete A/B-Zustaende.
Signalgeber und unabhaengige Direktbaseline stimmen in allen acht Faellen
ueberein. Das ist die funktionale Grundlage von S2-JG, kein Nachweis neuer
Memory-Physik.

## Konsolidierte Architektur

Die verbindliche Daten- und Wirkungsrichtung lautet:

```text
audiovisuelle Weltquelle
-> gemeinsame validierte Rezeptoren
-> gebundener reduzierter Wahrnehmungszustand
   +-> aktueller MCM-Feldpfad
   \-> privater atomarer Memorypfad
       -> A_RECENT
       -> Fast-ausgeloeste, quellgebundene Slow-Aktualisierung
       -> B_STABLE
-> read-only A/B-Kontextbeurteilung
-> kontrollierte Kontextzulassung
```

Der Feld- und der Memoryzweig besitzen denselben rezeptorisch gebundenen
Ursprung. Der Memorypfad liest jedoch keinen Feldsnapshot und wird nicht aus
einem Feldergebnis rekonstruiert. Umgekehrt darf Memory-Atomaritaet einen
bereits entstandenen Feldzustand weder zurueckrollen noch veraendern.

`A_RECENT` enthaelt weiterhin juengste Inhalte, B4-Kurzfolge und die interne
Fast-Spur als getrennte Rollen. `B_STABLE` enthaelt ausschliesslich stabile
Slow-Kandidaten. Die Bildung von B bleibt eine Fast-ausgeloeste,
quellgebundene Slow-Aktualisierung aus der aktuellen Originalexposition. Sie
ist keine Kopie des B4- oder gesamten A-Zustands.

## Funktionsfrage

Gegeben sind eine validierte aktuelle Teilwahrnehmung, eine validierte
read-only A/B-Projektion und genau ein dazugehoeriges qualifiziertes
Fuenf-Status-Signal. Darf fuer den naechsten privaten Wahrnehmungsverbrauch
Kontext bereitgestellt werden, ohne zwischen konkurrierenden Erinnerungen zu
waehlen?

S2-JG beantwortet nur diese Zulassungsfrage. Die Funktion fuellt keine Maske,
berechnet keine neue Aehnlichkeit und waehlt keinen Memorybereich nach Nutzen,
Alter, Support oder Distanz aus.

## Zulaessige Eingaben

Eine spaetere reine Zulassungsfunktion darf ausschliesslich akzeptieren:

1. die bereits validierte maskierte Wahrnehmungsprobe;
2. die bereits validierte S2-GI-Zwei-Bereich-Projektion;
3. das dazugehoerige qualifizierte S2-IC-Fuenf-Status-Signal mit
   rezeptorgetreuer S2-JD-Aggregatbindung;
4. einen atomaren, einmalig verbrauchbaren privaten Owner;
5. ein endliches Ledger fuer Validierung, Tabellenentscheidung und Digest.

Probe, Projektion und Signal muessen dieselben Quellen-, Konfigurations-,
Bundle-, A/B-Zustands- und Vor-/Nachzustandsdigests binden. Die Signalbefunde
muessen zeitlich und digestseitig vor der Zulassungsentscheidung entstanden
sein.

Unzulaessig sind Speicherabfragen, Rezeptoraufrufe, neue Distanzberechnungen,
Zielwerte, Sollstatus, Fallkennungen, Belohnung, Semantik, Rohdaten oder eine
vom Aufrufer angegebene Wunschrolle.

## Verbindliche Entscheidungstabelle

Die Ausgabe besitzt genau eine der beiden obersten Entscheidungen
`ALLOW_CONTEXT` oder `PROCEED_WITHOUT_CONTEXT`. Der urspruengliche
Fuenf-Status-Befund bleibt unveraendert sichtbar.

| Eingangssignal | Entscheidung | Zulaessiger Kontextbezug |
| --- | --- | --- |
| `SINGLE_SOURCE` | `ALLOW_CONTEXT` | Genau der eine bereits als anwendbar belegte Bereich. |
| `CONSISTENT` | `ALLOW_CONTEXT` | Beide anwendbaren Bereiche als ungeordnetes Aequivalenzpaar; keine Einzelrolle wird bevorzugt. |
| `CONFLICT` | `PROCEED_WITHOUT_CONTEXT` | Kein Kontext; der Konflikt bleibt als Grund sichtbar. |
| `NO_CONTEXT` | `PROCEED_WITHOUT_CONTEXT` | Kein Kontext; beide Bereiche sind gueltig abwesend. |
| `NO_APPLICABLE_CONTEXT` | `PROCEED_WITHOUT_CONTEXT` | Kein Kontext; vorhandene Kandidaten sind fuer die aktuelle Probe nicht anwendbar. |

Fuer `SINGLE_SOURCE` ist die einzige anwendbare Rolle keine Rangentscheidung.
Sie folgt vollstaendig aus dem vorgelagerten Signal. Fuer `CONSISTENT` darf
die Zulassung nur die bereits belegte Gleichwertigkeit der maskierten
Ergaenzungen autorisieren. Sie darf weder A noch B zum Gewinner erklaeren,
noch beide Kandidatenwerte verschmelzen. Ein nachgelagerter Verbraucher muss
die identische Ergaenzung verwenden koennen, ohne eine Bereichspraeferenz zu
erfinden.

Bei allen drei `PROCEED_WITHOUT_CONTEXT`-Faellen wird ausschliesslich mit der
aktuellen Wahrnehmung fortgefahren. Es gibt keinen Fallback auf den jeweils
anderen Bereich, keine Abschwaechung des Konflikts und keine Teilzulassung.

## Ausgabeform

Das spaetere private, unveraenderliche Objekt
`ControlledPerceptualContextAdmission` darf hoechstens enthalten:

- Schema- und Vertragskennung;
- `decision` mit genau einem der beiden Werte;
- unveraenderten `source_signal_status`;
- `admitted_roles`: leer, genau eine Rolle oder bei `CONSISTENT` das
  kanonische ungeordnete Paar `A_RECENT`, `B_STABLE`;
- Kandidaten- und Ergaenzungsdigests nur soweit sie bereits im Signal
  validiert sind;
- Probe-, Quellen-, Bundle-, Projektions-, Signal- und Zustandsdigests;
- neutralen Grundcode;
- Owner-Vor- und Endzustand;
- vollstaendiges Ressourcenledger;
- eigenen kanonischen Ergebnisdigest;
- identische Memory- und Feld-Vor-/Nachzustandsdigests.

Verboten sind `BEST_MEMORY`, `selected_area`, Rang, Score, Konfidenz,
Gewichtung, gemischte Kandidatenwerte, semantische Bezeichnungen und ein
neuer gespeicherter Kontextzustand. Bei einem Fehler entsteht kein partielles
Zulassungsobjekt.

## Atomaritaet und Read-only-Grenze

Vor der Entscheidung werden alle Eingaben und ihre Beziehungen vollstaendig
validiert. Erst danach darf lokal ein Kandidat fuer die Ausgabe entstehen.
Die Veroeffentlichung ist atomar:

- Erfolg verbraucht den Owner genau einmal und erzeugt genau ein vollstaendig
  validiertes Zulassungsobjekt;
- jeder Eingabe-, Rollen-, Digest-, Ledger- oder Zustandsfehler setzt den
  Owner auf `FAILED` und erzeugt keine Teilausgabe;
- Owner-Wiederverwendung ist ausgeschlossen;
- Probe, A, B, B4, Fast, Slow, Composite und Feldzustand bleiben bit- und
  digestgleich;
- die Funktion darf weder bilden, konsolidieren, verdrangen, abrufen noch
  eine Memory- oder Feldoperation ausloesen.

Gueltige Abwesenheit und regulare Nichtzulassung sind keine Fehler.
Beschaedigte, fremde, mehrdeutige oder widerspruechliche Evidenz ist dagegen
kein regulaerer Fuenf-Status-Fall und stoppt vollstaendig fail-closed.

## Ressourcenbindung

Die Zulassung bleibt eine endliche Tabellenfunktion. Pro Aufruf gelten
hoechstens:

```text
validierte Probe                         = 1
validierte Zwei-Bereich-Projektion       = 1
validiertes Fuenf-Status-Signal          = 1
Statusentscheidungen                     = 1
Bereichsreferenzen                       <= 2
Kandidatenreferenzen                     <= 2
neue Wahrnehmungs- oder Distanzvergleiche = 0
Speicher-, Rezeptor- oder Feldaufrufe     = 0
Zulassungsobjekte                        = 1 oder 0 bei Fehler
```

Validierungs-, Digest- und Ownerarbeit ist vollstaendig zu zaehlen. Die
Zulassung darf keine Werte duplizieren, die bereits eindeutig durch
Kandidatendigest und Herkunft gebunden sind. Konkrete Byte- und
Operationsgrenzen sind erst mit einer spaeteren Implementierungsentscheidung
zu materialisieren; fehlende Grenzen duerfen nicht durch unbeschraenkte
Container ersetzt werden.

## Nichtzirkularitaet

Der einzige zulaessige Entscheidungsgraph lautet:

```text
Weltquelle -> Rezeptorbeleg -> aktueller Wahrnehmungszustand
                              +-> aktueller MCM-Feldzustand
                              \-> atomarer A/B-Memoryzustand

validierte Probe + validierte A/B-Projektion
-> qualifiziertes Fuenf-Status-Signal
-> ControlledPerceptualContextAdmission
-> spaeterer, gesondert zu bindender Kontextverbrauch
```

Die Zulassung darf ihren Eingangsstatus nicht aus der erwarteten Entscheidung
rekonstruieren. Ein spaeteres Verbraucherresultat darf weder das Signal noch
die Zulassung rueckwirkend begruenden. Evaluationsregeln und Sollwerte liegen
ausserhalb des Funktionspfads.

## Starke Engineeringbaseline

Die staerkste Baseline ist eine unabhaengige direkte Implementierung derselben
fuenfzeiligen Entscheidungstabelle. Sie erhaelt identische validierte Eingaben
und Budgets, darf aber die Zulassungsfunktion oder deren Ergebnis nicht
aufrufen.

Vollstaendige Gleichheit mit dieser Baseline ist der erwartete Befund. Sie
bestaetigt eine transparente und brauchbare Engineeringfunktion, schliesst
aber einen Claim auf neue MCM-Physik oder intelligente Kontextwahl aus. Bei
gleichem Nutzen ist die einfachere Implementierung zu bevorzugen.

## Falsifikation und methodische Ungueltigkeit

Bei vollstaendig gueltiger Beweiskette ist die Funktion falsifiziert, wenn
mindestens eines gilt:

- ein Status wird anders als in der Entscheidungstabelle behandelt;
- `CONFLICT` laesst irgendeinen Kontext zu;
- `NO_CONTEXT` oder `NO_APPLICABLE_CONTEXT` erzeugt eine Kandidatenreferenz;
- `SINGLE_SOURCE` laesst mehr als die eine anwendbare Rolle zu;
- `CONSISTENT` erzeugt Gewinner, Rangfolge, Verschmelzung oder verschiedene
  zugelassene Ergaenzungen;
- der nicht zugelassene Bereich beeinflusst eine spaetere Ausgabe;
- Signalgeber und unabhaengige Tabellenbaseline weichen bei identischen
  gueltigen Eingaben voneinander ab;
- ein Probe-, Memory-, Bundle- oder Feldzustand wird veraendert.

Methodisch ungueltig und nicht fachlich falsifiziert ist ein Versuch bei
fehlender, fremder, widerspruechlicher oder unvollstaendiger Quellen-, Owner-,
Digest-, Status-, Zustands- oder Ledgerbindung. In diesem Fall lautet der
Befund `NOT_EVALUABLE`; es darf kein Funktionsurteil abgeleitet werden.

## Aussagegrenze und naechste Entscheidung

S2-JG bindet eine kontrollierte Zulassungsgrenze zwischen bestaetigter
read-only Kontextbeurteilung und spaeterem Kontextverbrauch. Ein spaeteres
Bestehen wuerde nur zeigen, dass eindeutiger oder gleichwertiger Kontext
zugelassen und Konflikt beziehungsweise Abwesenheit sicher zurueckgehalten
wird.

Nicht gezeigt waeren automatische Relevanzwahl, Semantik, Vorhersage,
Langzeit-Memory, Feldrueckwirkung oder ein MCM-spezifischer Mechanismus. Die
naechste konkrete Freigabe kann unmittelbar eine kleine private reine
Zulassungsfunktion, eine unabhaengige Tabellenbaseline und fokussierte
neutrale Tests betreffen. Eine weitere allgemeine Vertrags- oder
Beleginfrastruktur folgt aus S2-JG nicht.
