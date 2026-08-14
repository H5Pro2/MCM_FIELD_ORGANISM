# Forschung 031: Ordnung der offenen Luecke aus Forschung 030

## Zweck und Status

Dieses Dokument ordnet ausschliesslich den positiv begrenzten Konzeptstand aus
Forschung 030. Es prueft das Konzept nicht erneut und gibt weder einen
Forschungslauf noch eine Runtime-, Produkt- oder Programmerweiterung frei.

## Offene Luecke

Offen bleibt genau eine Frage:

> Erzeugt dieselbe vollstaendig belegte Audio-Video-Quellenwirkung innerhalb
> derselben Organismuszeit bei zwei verlustfreien, aber unterschiedlich fein
> geteilten Rezeptorabschlussfolgen dieselbe aktuelle lokale Feldantwort?

Betroffen ist nur die vorhandene asynchrone Audio-Video-Rezeptoruebergabe.
Untersucht werden duerften ausschliesslich vorhandene aktuelle Feldgroessen:
Rezeptorprojektion, lokale Ein-Schritt-Probe, Aktivierung und schneller
Nachhall.

Die Frage behauptet keine neue Feldwirkung. Ereigniszahl, Abschlussrate und
technische Zeitteilung sind keine inneren Feldrollen.

## Vorgelagerte Tragfaehigkeitspruefung

Vor jeder Ausfuehrungsfreigabe muss rein technisch und ohne Runtimeaenderung
feststehen, dass die bestehende Runtime beide Folgen tragen kann:

- eine grobe verlustfreie Rezeptorabschlussfolge;
- eine feine verlustfreie Rezeptorabschlussfolge;
- identische Quellenwirkung und identische Organismuszeit in beiden Armen;
- keine Auswahl, Mittelung, Interpolation oder Endpunktreduktion;
- keine Kopplung des Feldfortschritts an die technische Ereigniszahl.

Kann die bestehende Runtime dies nicht leisten, endet der Anschluss hier. Aus
der fehlenden Anschlussfaehigkeit folgt kein Auftrag zur Programmerweiterung.

## Zulaessige passive Baselines

- **Nullarm N:** gleiche Organismuszeit und feste Anatomie; alle Docks bleiben
  vorhanden und tragen genullten kontrollierten Kontakt.
- **Grobarm G:** festgelegte Quellenwirkung in einer groben verlustfreien
  Abschlussfolge.
- **Feinarm F:** dieselbe Quellenwirkung im selben Zeithorizont in einer
  feineren verlustfreien Abschlussfolge.
- **Reproduktion R:** frisch initialisierte identische Wiederholung von G und
  F mit passivem komponentenweisem Vergleich.
- **Permutation P:** identische Werte und Abschlusszeiten bei vertauschter
  Deklarations- oder Iterationsreihenfolge.
- **Technische Nullerklaerung:** Observer, Snapshot, Cache, Serialisierung,
  Schrittteilung und Gleitkommanumerik werden passiv auf eine vollstaendige
  Erklaerung jeder Abweichung geprueft.

Alle Arme muessen dieselbe Organismusuhr, Start- und Endzeit, Dockanatomie,
Geometrie, Gesamtquellenwirkung und vorab festgelegte Beobachtungspunkte
besitzen.

## Harte Ausschluesse

- keine Runtime-, Produkt-, Anatomie- oder Codeaenderung;
- keine neue Zustandsvariable, Kandidatenrolle, Rekurrenz oder Kopplung;
- keine Labels, Bedeutung, Klassen oder Ereignisnamen im Kausalpfad;
- kein Reward, Score, Sollwert, Gewinner oder Zielverhalten;
- keine Memory-, Material-, Organisations- oder Topologieableitung;
- kein Sample-and-Hold, keine Interpolation, Mittelung,
  Ratennormalisierung, Modalitaetsgewichtung oder Zustandsauswahl;
- keine Wiedereroeffnung der durch 021 bis 029 geschlossenen Zweige;
- keine adaptive Wahl von Folgen, Messpunkten, Toleranzen oder Stopplinien;
- kein MINI_DIO-Mechanikimport.

## Abbruchkriterien

Der Fachweg wird ohne positive Aussage beendet, wenn mindestens eine der
folgenden Bedingungen eintritt:

1. Die Runtime-Tragfaehigkeitspruefung kann G und F nicht ohne Erweiterung
   bereitstellen.
2. G und F liefern bei fairer Angleichung dieselbe aktuelle Feldantwort.
3. Eine Differenz wird vollstaendig durch Projektion, lokale
   Ein-Schritt-Wirkung, schnellen Nachhall oder additive Ueberlagerung
   erklaert.
4. Eine Differenz folgt aus Ereigniszahl, Zeitteilung,
   Ausfuehrungsreihenfolge, Observer, Snapshot oder Numerik.
5. Quellenwirkung, Organismuszeit, Anatomie oder bekannte schnelle Zustaende
   koennen nicht vollstaendig angeglichen werden.
6. Eine faire passive Auswertung erfordert eine ausgeschlossene neue Rolle
   oder technische Speicherlogik.

Eine verbleibende numerische Differenz waere zunaechst nur eine ungeklaerte
technische Abweichung. Sie ist kein Nachweis einer neuen Feldwirkung oder
Organisation.

## Medien- und Browsergrenze

Der Fachweg bleibt synthetisch und medienfrei formulierbar. Sollte spaeter
Browserwiedergabe verlangt werden, darf ausschliesslich eine vorhandene Video-,
Kamera- oder Rezeptorschnittstelle direkt verwendet werden. Download, lokale
Mediendatei oder Kopie, Installation, Transcode und dateibasierter
OpenCV-Ersatzpfad bleiben ausgeschlossen. Eine fehlende Anschlussstelle ist
als interner Workflowfehler zu behandeln.

## Organisatorische Entscheidung

Forschung 030 bleibt eine offene, nicht freigegebene Bestandsfrage. Der
naechste moegliche Schritt ist ausschliesslich die separate Bewertung der
Runtime-Tragfaehigkeit. Dieses Ordnungsdokument selbst loest weder Forschung
noch Entwicklung aus.

## Tatsaechlich verwendete Quellen

- aktuelle Uebergabe des MCM-Forschungsleiters;
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`;
- `docs/forschung/029_ORDNUNGSDOKUMENT_KONZEPTABGLEICH_021_BIS_028.md` zur
  Uebernahme der bestehenden Baseline-, Ausschluss- und Mediengrenzen.

MINI_DIO und externe Mechanikquellen wurden nicht verwendet.
