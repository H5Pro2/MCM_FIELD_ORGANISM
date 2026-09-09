# S2-NY: neutrale Empfehlungs-/LOCAL-Qualifikation

## Technischer Abschluss

Lauf-ID: `s2ny-prediction-qualification-20260909-01`.
Genau ein vorregistrierter Aufruf, **30/30 bestanden**, Exit-Code `0`.
Status `S2NY_PREDICTION_QUALIFIED`; kein Retry, kein realer NY-Lauf.

- [Vorregistrierung](preregistration.json): 30 benannte Testgruppen,
  Interpreterumgebung, Quellenhashes, Arbeits- und Beleggrenzen vor Aufruf.
- [Testprotokoll](stderr.txt): alle 30 Testkoerper erreicht und bestanden.
- [Ergebnis](result.json): Digest
  `1f005bdd8e4d91ac88036b7659dcff86690cb99e0935840ff36460fd7c4e42bb`.
- [Vollstaendige neutrale Ergebnishuelle](neutral-envelope.json): 585.190 Byte
  bei unveraendertem Limit 2.097.152 Byte; SHA-256
  `2f49a366340c27f6e92bb612520da1b476b1ba74c6c0e99e479d10868bd4f1b1`.

## Tatsaechlich erreichte Grenzen

1. Fehlerherkunft: nur die beiden unmittelbar vorherigen H1-/H2-Fehler
   derselben Folge mit passenden Freeze-, Ziel-, Stellen- und Scoredigests.
   Fremde Folge, vertauschte Historien, manipulierte Primaer-/Direktwerte,
   falscher Freeze, veraltete und fehlende Fehler typisiert abgewiesen.
2. Zukunftssperre: kein Ziel-Reader ohne unveraenderliche Prognosebindung;
   nachtraegliche Aenderungen werden vor Zielverarbeitung abgewiesen.
   Ab k=3 sind H1/H2/PERSIST/LOCAL und beide Empfehlungen vorher gebunden.
   Identische funktionale Praefixe bleiben bei anderen Quellenkennungen gleich.
3. Enthaltung: k=2 `ABSTAIN_INSUFFICIENT_PREFIX`, Fehlergleichstand
   `ABSTAIN_TIE`; keine Ersatzprognose, `recommended_mae=null`, keine
   fingierte Nullfehlerwertung. Bereits festgelegte Kontrollen bleiben sichtbar.
4. LOCAL: pro Stelle frische Akkumulation aus genau drei Vektoren, keine
   fortgeschriebene Lernhistorie. Nullnenner, Subnormale und Produktunterlauf
   geprueft, nichtendliche/ungueltige Eingaben typisiert abgewiesen.
   Endliche Prognosen ausserhalb [0,1] bleiben ungeclippt.
5. Freeze/Lifecycle: synthetische historiengebundene Eingangs-Payloads
   unveraendert; Manipulation vor Readeraufruf abgewiesen. Keine Owneroeffnung
   oder Updates. Praefix und Fehlerbelege nach Folgenschluss geloescht.
6. Direktrechnung: eigene Prognose-, LOCAL-, MAE- und Empfehlungsarithmetik;
   primäre Helfer im Unabhaengigkeitstest gesperrt. Vollstaendige neutrale
   Belege offline nachgerechnet, fehlende/vertauschte Belege abgewiesen.
7. Auswertung: NEXT_BEST trotz Verlust gegen beide Kontrollen im isolierten
   Auswertertest geprueft. Vollstaendige neutrale Laeufe einschliesslich
   reiner Gleichstaende technisch verifizierbar; D=0 bleibt
   `NUTZEN_NICHT_GEPRUEFT`. Alle 20 Kriterien getrennt, nicht eingetretene
   W-Verlustprognosen regulaer FALSIFIED, keine Gewinn-/Verlustverrechnung.
8. Ressourcen/Abschluss: Arbeitszaehler und vollstaendige Ausgabehülle
   geprueft; Schreibkonflikt `WRITE_CONFLICT` und Groessenueberschreitung
   typisiert. Neutraler Materialisierungsfehler schliesst phasengenau ohne
   fachliche Teilauswertung ab. Auswertung vor Verifikation gesperrt.

Die Suite verwendete zwei vollstaendige synthetische Bestaende und einen
synthetischen Fehlerabschluss. Der echte Adaptertest erzeugte ausschliesslich
fuenf neutrale Null-PCM-Fenster: **5 direkte Analysen und 5 NJ-Projektionen**,
auch hier Prognosen vor den drei Zielerzeugungen. Keine NY-Quellenbytes oder
realen NY-Zielwerte; keine separate Materialisierung. Ein Fenster gleichzeitig,
keine Rohpayloadablage. Keine Memory-, Feld-, Kontext- oder Runtimeaufrufe.

## Bindungen und verbleibende Grenzen

Alle 43 vorgebundenen Datei-SHA-256 waren vor/nach dem Aufruf identisch;
die vollstaendige Liste steht im Ergebnis. Neue Anbindung separat vom
historischen Siegel; bestehende NW/NX-Arithmetik und Generatoren unveraendert.
NY-Plan, Quellenversiegelung und historische NX-Ergebnis-/Verifikationsdatei
blieben unveraendert. Es wurde keine historische Lernkette erneut berechnet.

Der geschlossene private Einstieg liegt in
`tools/_s2ny_private_prediction_run.py`: `run_main_once`, danach separat
`verify_file_once` und `evaluate_file_once`. Der Haupteinstieg verlangt diesen
Qualifikationsbeleg sowie die vorgebundenen Quellen-/Freeze-Belege. Er wurde
hier nur mit geschlossenem Gate auf Ablehnung geprueft, nicht real ausgefuehrt.

Die Zukunftssperre ist eine qualifizierte kontrollierte Aufruffolge, keine
Sandbox gegen beliebigen Pythoncode. Die Offline-Pruefung rechnet gespeicherte
Halbierungen, Prognosen, Fehler und Bindungen nach; ein Digest allein beweist
keine historische CPU-Aufrufordnung. Die neutrale Huellengroesse garantiert
nicht jede reale Serialisierung; das unveraenderte Limit gilt fail-closed.

Noch keine NY-Empfehlungsrichtigkeit oder Verbesserung gegen LOCAL belegt.
Knappe Binary64-Vorteile waeren spaeter mit absoluten MAE/Gewinndifferenzen
zu berichten, keine allgemeine Robustheit. Alle beteiligten Gates `False`;
ME/MI und Systemintegration bleiben gesperrt. Fremde Aenderungen und
Bootstrap sind nicht Bestandteil dieser Arbeit.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Qualifikationsbefunds und der separaten Hauptlaufentscheidung weiter.
