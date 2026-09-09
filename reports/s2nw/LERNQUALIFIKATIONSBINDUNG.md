# S2-NW: einmalige neutrale Lern-/Prognosequalifikation

Vor Aufruf gebunden: `s2nw-learning-qualification-20260909-01`.
Genau ein Aufruf `python -m reports.s2nw.qualify_learning_once`, darin
ein `unittest -v -f` mit 28 Testkoerpern. Kein Retry. Das Inventar und alle
Quellhashes werden vor dem Testprozess atomar in `preregistration.json`
geschrieben. Kein vorangehender Testlauf oder historischer Testkoerper.

## Umfang

| Tests | Gebundene Pruefung |
| --- | --- |
| 01-05 | Geschlossene Eingaben, exakter Nullzustand, Binary64-Bandreihenfolge, Nullnenner/Unterlauf, unveraenderliche Zustandsform |
| 06-08 | Endliche ungeclippte Prognosen, unveraenderte NV-Baselines, unabhaengiger Direktlerner aus eigenem Nullzustand |
| 09-14 | Zielzugriff und Update vor Beobachtung gesperrt, Prognosemutation, manipulierte Lernkette, vier Updates nach Ziel und Fehlerbindung, vorzeitiges Freeze |
| 15-17 | Zwoelf identische Freeze-Bindungen, frische Testpraefixe, keine Testupdates, administrative Kennungen nicht funktional |
| 18-19 | Quellen-/Zeitfehler vor Analyse, sechs echte neutrale direkte Analysen/NJ-Projektionen mit Prognose vor Zielerzeugung |
| 20-24 | Offline-Nachrechnung, manipulierte Update-/Freezeketten, Auswertungssperre, getrennte Wechselverluste, gueltiger Nullnenner mit negativem Fachbefund |
| 25-28 | Vollstaendige Gesamtbeleggroesse, Arbeitsgrenzen, fehlende/manipulierte Belege, neutraler Einmaleinstieg, phasengenauer Fehlerabschluss und Schreibkonflikt |

Die Tests verwenden eigene konstante Halbvektoren und sechs kleine konstante
PCM-Fixtures. Der neutrale Fit `.5` entsteht nur durch die beobachteten
synthetischen Uebergaenge, nicht durch eine Quellenrezeptvorgabe im Lerner.
Die wirklichen NW-Generatoren und `load_presealed` sind bei der neutralen
Ausfuehrung gesperrt. Test 27 ersetzt nur administrative NW-Anschluesse durch
synthetische Eingaben und ein temporaeres Verzeichnis, keine historische
Hauptfunktion. Die importierten NV-Testhilfen liefern ausschliesslich neutrale
Fensterbelege; kein historischer Test wird erneut ausgefuehrt.

## Arbeits- und Ausgabegrenzen

Pro spaeterem Funktionslauf gelten unveraendert die NW-Plangrenzen:
26 Fenster, vier Updates je Implementierung, 16 Prognosestellen mit drei
Armen; 12 davon bei eingefrorenem Zustand. `work_limits()` bindet Prognose,
Update und Fehlerarbeit separat. `verification_limits()` bindet die
zusaetzliche Offline-Nachrechnung. Nullnenner reduzieren nur die tatsaechlich
ausgefuehrten Divisionen und duerfen keinen technischen Abbruch erzwingen.

Die neutrale Suite umfasst drei vollstaendige synthetische Ausfuehrungen,
einen synthetischen Fehlerabschluss und hoechstens zwoelf zusaetzliche
Praefixkonstruktionen. Sechs echte neutrale Analysen und sechs NJ-Aufrufe;
13 neutrale PCM-Fenstererzeugungen einschliesslich sechs vorgelagerter
Fixturehashes und einer absichtlich falschen Payloadbindung. Zusammen
249.600 Byte erzeugt, maximal 19.200 Byte vollstaendiger PCM-Payload zugleich.
Keine versiegelten NW-Payloads, kein reales NW-Zielmaterialisat.

Konservative Suite-Arbeitsobergrenzen stehen numerisch in der
Preregistrierung; sie sind statische Inventarbudgets, keine behauptete
CPU-Instruktionsmessung. Jeder operative Ablauf prueft seine eigenen
Arbeitszaehler. Gesamtbeleg maximal 2.097.152 Byte, Zustand 4.096 Byte,
Metadaten/Prognosebindung 65.536 Byte, Pruefung/Auswertung je 262.144 Byte.
Test 25 bindet die vollstaendige neutrale Huelle einschliesslich aktueller
Quellhashes und prueft Ueberschreitung ohne Grenzerhoehung.

## Aussagegrenzen

Der kontrollierte Aufrufpfad muss Prognosen vor Erzeugung/Analyse des Ziels
binden, danach erst lernen und vor jeder Testquelle einfrieren. Der reine
arithmetische Updatehelfer besitzt keine eigene Weltzeit; der Aufrufer
erzwingt die Beobachtungsfreigabe. Python-interne Manipulation beliebiger
privater Attribute ist keine Sicherheitsgrenze gegen feindlichen Hostcode.
Die Offline-Pruefung rekonstruiert Zahlen und Zustandsketten aus gespeicherten
Roh-/Halbwerten, beweist allein jedoch nicht die historische CPU-Reihenfolge.

Historische NV-Baselines, Quellenversiegelung, Profile und Belege bleiben
unveraendert. Kein Memory-, Feld- oder Runtimeanschluss. Alle echten
Hauptgates bleiben `False`; ME/MI gesperrt. Erfolg dieser Qualifikation
waere technische Anschlussdeckung, kein realer Lern- oder Transferbefund.
