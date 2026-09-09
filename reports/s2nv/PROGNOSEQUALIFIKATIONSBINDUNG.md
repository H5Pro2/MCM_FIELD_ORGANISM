# S2-NV: einmalige neutrale Prognosequalifikation

ID `s2nv-prediction-qualification-20260909-01`, genau ein Aufruf, Failfast,
20 Testkoerper, kein Retry. Vor dem Aufruf werden dieses Inventar, alle neuen
Module, Tests, Aufrufskript, historische Helfer, versiegelte Quelldateien und
Umgebung gehasht. Die 16 Quellenqualifikationstests werden nicht wiederholt.

## Unveraenderte Aufgabe und enge Anbindung

LINEAR erhaelt nur die Halbprofilbindung und die letzten zwei tatsaechlich
analysierten Halbvektoren. PERSIST erhaelt nur Profil und letzten Vektor.
Eigene eingefrorene Slottype verhindern zusaetzliche funktionale Felder.
Keine Rezept-, Zeit-, Quellen-, Ziel- oder Kategoriekennung im Vorhersager.
LINEAR berechnet erst `last-previous`, danach `last+d`; PERSIST kopiert.
Keine Rundungstoleranz, Umformung, Gewichte, Quellenanpassung oder Imputation.

Die private PrefixStream-Steuerung besitzt genau fuenf administrative
Quellenbindungen und ruft den Fensteradapter nur in Reihenfolge auf. Ab
Fenster 2 ist eine bereits gebundene Prognose beider Implementierungen
erforderlich. Die kanonischen Prognosebytes werden unveraenderlich vor
Zielfenstererzeugung aufbewahrt; vor und nach dem Adapteraufruf muessen sie
weiterhin exakt mit der Originalbindung uebereinstimmen. Extern gelieferte
Prognosewerte koennen nicht ueber einen Setter installiert werden.

Das naechste Praefix verwendet das reale zuletzt analysierte Ergebnis,
nicht die eigene Prognose. Jeder Strom erhaelt eine frische Steuerung.
Der reale Einstieg verwendet nur den bestehenden unveraenderten Generator,
LogSpectralReceptor.analyze und NJ. Keine rollende Audiopipeline, keine
Kontakt-, Memory-, Feld- oder Runtimefunktion. Es gibt keinen separaten
Eintritt zur Vorabmaterialisierung zukuenftiger NV-Zustaende.

Primar- und Direktprognosen sind vor demselben Ziel gebunden. Die direkte
Arithmetik verwendet keine produktive Vorhersage- oder Fehlerfunktion.
Vorhersagen in `[-1,2]` werden ungeklemmt bewertet, auch ausserhalb `[0,1]`.
Atomare Gesamtdateien verwenden den unveraenderten NU-Dateihelfer, keinen
neuen Recorder. Seine typisierten Ausgabefehler werden lokal auf NV abgebildet.

## Zwanzig Pruefgruppen

1. Geschlossene Eingabeformen, Profil- und Normalformablehnung.
2. Binary64-Subtraktion vor Addition, feste Nachrechnung und Unveraenderlichkeit.
3. Bitkopie einschliesslich Subnormalwert und negativem Nullwert.
4. Prognosen -1 beziehungsweise 2 bleiben ungeclippt und voll im Fehler.
5. Direktbaseline bei gesperrten produktiven Prognose-/Fehlerhelfern.
6. Vorzeitiger beziehungsweise ungebundener Zielzugriff vor Adapteraufruf.
7. Fehlende und doppelte Prognosebindung.
8. Nachtraegliche Aenderung einschliesslich neu berechnetem Digest abweisen.
9. Aenderung waehrend Zielverarbeitung erzeugt keinen veroeffentlichten Fall.
10. Gleiche funktionale Praefixe, andere administrative Quellenidentitaeten.
11. Tatsaechliche Controller-Reihenfolge, Analysezaehler und Lifecycle.
12. Frische Strompraefixe und vollstaendige getrennte Arbeitszaehler.
13. Fuenf kleine konstante neutrale Vollformatfenster ueber echte Analyse/NJ;
    vor jedem neuen Ziel gebundene Prognose, danach gespeicherte Halbierung pruefen.
14. Hash- und Zeitfehler vor Rezeptoraufruf abweisen.
15. Gesamtverifikation, Unveraenderlichkeit, Quellen-/Prognosemanipulation,
    fehlender Strom und unabhaengige Direktnachrechnung.
16. Auswertungssperre, Fortsetzungsgewinne und separat sichtbare Wechselverluste.
17. Gleichstaende: technisch gueltig, Primaerprognose fachlich falsifiziert.
18. Vollstaendige 20-Fenster-/12-Stellen-Huelle plus Codebindungen;
    Byteobergrenze und Ablehnung uebergrosser Ausgabe.
19. Neutraler Dateieinstieg mit atomarem Gesamtbeleg, einmaliger Dateipruefung
    und nachgelagerter Auswertung; historischer Quellenlader ist ersetzt/gesperrt.
20. Phasengenauer technischer Fehlerabschluss, Auswertungssperre,
    geschlossenes Hauptgate und unveraenderliche vorhandene Ergebnisdatei.

Alle Testkoerper sperren die NV-Payloadfunktion und den realen Quellenlader.
Der neutrale Dateieinstieg hat eine synthetische 2099-ID nur im geloeschten
Tempverzeichnis, keine autorisierte reale NV-Lauf-ID. Dessen Gate wird
ausschliesslich fuer diese neutrale Ersatzanbindung im Testprozess geoeffnet
und wieder geschlossen. Es werden keine versiegelten NV-Payloads verwendet.

## Arbeits- und Artefaktgrenzen

Spaeter unveraendert: 20 Generierungen, 20 direkte Analysen, 20 NJ-Projektionen,
je 960 Roh-/Halbwerte. Zwoelf Stellen: je Implementierung 576 Prognose-
Subtraktionen, 576 Additionen, 576 Persistenzkopien sowie 1.152 Fehlerterme,
24 MAE-Summen und zwoelf Gain-Subtraktionen. Beide Implementierungen zusammen
2.304 Fehlerterme. Verifikation separat: 960 Vorwaertshalbierungen, je 1.152
Prognosesubtraktionen/-additionen/Persistenzkopien, 2.304 Fehlerterme, 48
MAE-Summen, 24 Gains. Danach zwoelf Ergebniszuordnungen und sechs Bedingungen.
Alle Arbeitsarten besitzen eigene Zaehler; keine verdeckte Mehrarbeit im
Fehlerbudget. Gates und Systemaufrufe bleiben ausserhalb der neutralen
Temp-Einstiegspruefung geschlossen beziehungsweise Null.

Die Suite verwendet hoechstens drei vollstaendige synthetische Ausfuehrungen,
einen fehlerhaften synthetischen Verlauf und acht zusaetzliche Praefixcontroller.
Nur Pruefung 13 fuehrt echte Sensorarithmetik aus: fuenf direkte neutrale
Analysen und fuenf NJ-Projektionen. Zehn konstante PCM-Fenster entstehen
fuer ihre neutrale Quellenbindung/Verarbeitung, ein weiteres fuer die
Hashabwehr: hoechstens elf Generierungen, 211.200 Byte, ein 19.200-Byte-Fenster
gleichzeitig. Synthetische reduzierte Belege sind keine Rezeptormessungen.

Weitere neutrale Obergrenzen: je 16.384 Prognosesubtraktionen/-additionen,
32.768 Fehlerterme; Offline hoechstens 12.000 Halbierungen, je 16.384
Prognosesubtraktionen/-additionen, 32.768 Fehlerterme, 1.024 MAE-Summen,
512 Gainchecks und 18 strikte Kriterien aus drei Auswertungen. Keine
Vergleiche realer NV-Zustaende. Alle Teilaufrufe behalten die unveraenderten
Produktobergrenzen. Metadaten 65.536, Gesamtbeleg 2.097.152, Verifikations-
und Auswertungsbeleg je 262.144 Byte. Keine nachtraegliche Grenzerhoehung.

## Offline-Grenze und Hauptlauf

Der Verifikator prueft gespeicherte Roh-/Halbwerte samt Hex/Bytes,
Quellen-/Zeit-/Profilbindungen, Vorwaertshalbierungen, Praefixe, Prognosen,
Einzelbandfehler und getrennte Zaehler. Er erzeugt weder PCM noch FFT/NJ
erneut. Rohwerte werden niemals aus Halbwerten rekonstruiert. Ein gepruefter
finaler Beleg beweist allein keine historische CPU-Reihenfolge; dazu bleibt
der hier kontrollierte unveraenderte Aufrufpfad notwendig. Dies ist eine
programmatische Zugriffssperre, keine Sicherheitsgrenze gegen beliebigen
fremden Python-Code im selben Prozess.

Nach Bestehen bleibt der reale Hauptlauf separat gesperrt. Privater Einstieg:
`run_main_once(run_id)`, dann genau einmal `verify_file_once(out)` und nur bei
Erfolg `evaluate_file_once(out)`. Es wird jetzt keine reale Lauf-ID gebunden.
Keine eigenstaendige Rezeptormaterialisierung und kein Vorhersagebefund.
NU, ME/MI, historische Belege, Versiegelung und Bootstrap bleiben unveraendert.
