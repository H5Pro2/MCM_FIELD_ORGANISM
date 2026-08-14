# S1-AB: Minimale Substrat-Zielarchitektur vor einer Implementierung

Stand: 2026-08-10

Status: `STATISCHER_ENTWURF_KEINE_IMPLEMENTIERUNGSFREIGABE`

## Zweck

Dieses Dokument verkleinert die offene Memory-Frage auf eine technisch
pruefbare Zielrolle. Es beschreibt keine fertige MCM-Memory-Mechanik und
uebernimmt keine menschliche Gehirnarchitektur.

Die menschliche Gedaechtnisforschung dient nur als Funktionsvergleich:
Wiederholung, zeitweise Stabilitaet, Abschwaechung, Interferenz und spaetere
Reaktivierung. Diese Begriffe sind noch keine Befunde im MCM-Projekt.

## Realistische Zielrolle

Gesucht ist ein begrenztes lokales Substrat, dessen spaetere Feldreaktion
durch normale Feldteilnahme veraendert werden kann:

```text
kontrollierte audiovisuelle Welt
-> Rezeptorsequenz
-> gemeinsames MCM-Feld
-> lokale Substratkonfiguration
-> spaetere veraenderte Feldreaktion
```

Die Zielrolle ist kleiner als menschliches episodisches Gedaechtnis. Sie setzt
weder Episodenobjekte noch Bedeutungen, Labels, Ziele oder eine innere
Sprache voraus.

## Was ein Kandidat leisten muesste

Ein zulaessiger Kandidat muss vor einer Runtime-Implementierung statisch
begruenden:

1. **Lokale Ursache:** Eine vorhandene Feldgroesse veraendert die lokale
   Substratkonfiguration durch denselben normalen Feldpfad. Es gibt keinen
   separaten Speicherbefehl.
2. **Endliche Kapazitaet:** Die Konfiguration ist begrenzt und besitzt eine
   fachlich begruendete Bilanz oder Dissipation.
3. **Rueckwirkung:** Die veraenderte Konfiguration beeinflusst spaetere
   Feldschritte ueber denselben gekoppelten Mechanismus.
4. **Wiederholungsabhaengigkeit:** Unterschiedliche Kontaktgeschichte darf
   unterschiedliche spaetere Reaktionen erzeugen, ohne einen
   Wiederholungszaehler vorzuprogrammieren.
5. **Abschwaechung oder Ueberlagerung:** Normale weitere Feldteilnahme darf
   eine alte Wirkung vermindern oder durch eine andere Konfiguration
   ersetzen, ohne Reset oder Loeschkommando.
6. **Nichtinhaltlichkeit:** Der Kandidat speichert keine Rohmedien,
   Datenbankeintraege, Embeddings oder vorgegebene Episoden als Memory.

Fehlt eine dieser Begruendungen, bleibt die Substratlinie geschlossen.

## Menschliche Analogie: erlaubt und nicht erlaubt

Erlaubt ist die Verwendung menschlicher Funktionen als abstrakte
Vergleichsachsen:

```text
Wiederholung       -> zunehmende historische Unterscheidbarkeit
Nichtbenutzung     -> abnehmende spaetere Wirkung
Aehnlicher Hinweis -> moegliche Reaktivierung
Neue Geschichte    -> Interferenz oder Umorganisation
```

Nicht erlaubt ist die direkte Behauptung, damit menschliches Erinnern,
Erleben, Gefuehl oder Bewusstsein nachzubauen. Ebenso unzulaessig waere es,
die vier Vergleichsachsen als feste Phasenmaschine zu implementieren.

## Episodisches Modell als Gegenbaseline

Ein expliziter episodischer Speicher kann als technische Gegenbaseline
verwendet werden. Er darf dabei klar markiert werden als:

```text
expliziter Datenspeicher != feldveraendertes MCM-Substrat
```

Die Baseline kann zeigen, welche Leistung durch direktes Speichern erreichbar
ist. Sie darf nicht als Nachweis fuer MCM-Memory oder als versteckte
Implementierung in die aktive Architektur uebernommen werden.

## Vorlaeufige Messordnung

Erst nach bestandenem Wiedereroeffnungstor duerfte ein Kandidat gegen die
folgenden kontrollierten Verlaeufe geprueft werden:

1. einmaliger Kontakt gegen wiederholten Kontakt;
2. gleiche Endaufnahme bei unterschiedlicher Vorgeschichte;
3. Kontaktpause mit anschliessender identischer Probe;
4. konkurrierende Folgegeschichte gegen unveraenderte Folgegeschichte;
5. Kandidat gegen F3, Leaky-Spur, Hysterese und expliziten Episodenspeicher.

Der technische Erfolgswert waere zunaechst nur eine reproduzierbare
geschichtsabhaengige spaetere Feldreaktion. Das waere noch kein Memory-Claim.

## Entscheidungslinie

Diese Zielarchitektur ist erreichbar als Forschungs- und Engineeringfrage,
aber nicht aus der bestehenden F3/CONST-V-Mechanik automatisch ableitbar.
F3/CONST-V bleibt Referenzarm. Eine neue Gleichung, Variable oder Runtime
wird erst zugelassen, wenn ein konkreter Kandidat die Anforderungen aus S1-AA
und S1-Y vollstaendig beantwortet.

```text
statischer Kandidat
-> Baselineabgrenzung
-> Zulassungsentscheidung
-> erst danach Implementierung
```

## Quellen im Projekt

- `docs/S1Y_ARCHITEKTURENTSCHEID_F3_ABSCHLUSS_UND_SUBSTRATLUECKE.md`
- `docs/S1AA_OPERATIVER_ENTWICKLUNGSANSCHLUSS_NACH_SUBSTRATSTOPP.md`
- `docs/FUNKTIONALER_ANFORDERUNGSRANG_MEMORY_LEBENSZYKLUS.md`
- `docs/RICHTUNGSENTSCHEID_SUBSTRAT_VOR_MEMORYBEFUND.md`

## Bester naechster Schritt

Als naechstes wird kein Speicher implementiert. Stattdessen wird fuer genau
eine moegliche lokale Substratrolle eine statische Kandidatenmatrix erstellt:
Ursache, Endlichkeit, Rueckwirkung, Interferenz, Gegenbaselines und Nullpfad.
Bei einer offenen Zelle bleibt die Implementierung gesperrt.
