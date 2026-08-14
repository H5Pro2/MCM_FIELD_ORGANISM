# 213ZZT - Statischer Behandlungsvertrag der technischen Ausfuehrungsgrenze

## Einordnung

`213ZZT` ist kein Forschungslauf und erhaelt keine Laufnummer. Das Dokument behandelt ausschliesslich den in `213ZZR` beobachteten und durch `213ZZS` statisch abgenommenen technischen Vertragsabbruch. Es autorisiert keine Ausfuehrung, Diagnose oder Systemaenderung.

## Forschungsfrage und Auftrag

Wie ist der gescheiterte und verbrauchte Einzelvertrag zukuenftig methodisch zu dokumentieren und abzugrenzen, ohne aus den gebundenen Beobachtungen eine ungepruefte Ursache abzuleiten oder einen weiteren technischen Zugriff vorzubereiten?

## Verwendete Quellen

- aktueller Uebergabe-Eingang;
- `docs/forschung/213ZZR_G1_POLICYPROBE_EINZELAUFRUF_TECHNISCHER_VERTRAGSABBRUCH.md`;
- `docs/forschung/213ZZS_G1_213ZZR_UNABHAENGIGE_STATISCHE_ABNAHME_UND_KLASSIFIKATION.md`.

Keine externen Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Die beiden Quelldokumente wurden ausschliesslich statisch gelesen. Verwendet wurden nur die bereits dokumentierten Vertrags-, Beobachtungs- und Abnahmefelder. Es erfolgten kein `-PolicyProbe`-Aufruf, keine Policy-Abfrage, kein Registry-Zugriff, keine Diagnose, keine Konfigurationsaenderung, kein Alternativhost, kein Retry, keine Produktionsinventur und kein Realpfadzugriff.

## Durchgefuehrte Schritte

1. Den Status des Einzelvertrags aus `213ZZR` und `213ZZS` abgeglichen.
2. Beobachtete Tatsachen von technischer Interpretation und offenen Ursachen getrennt.
3. Zulaessige kuenftige Verweise auf den technischen Abbruch festgelegt.
4. Unzulaessige Erweiterungen und Wiederverwendungen abgegrenzt.
5. Bedingungen fuer jede moegliche spaetere praktische Behandlung festgelegt.
6. Eine Stopplinie gegen G1- und MCM-Befunduebertragung formuliert.

## Statischer Behandlungsvertrag

### 1. Verbindlicher Status

- `213ZZR` ist ein ausgefuehrter, fehlgeschlagener und verbrauchter Einzelvertrag.
- Sein Ergebnis bleibt `contract_pass=false`.
- Der dokumentierte Vorgang darf weder als offen, wiederholbar noch als teilweise bestanden bezeichnet werden.
- `213ZZS` ist die massgebliche unabhaengige statische Abnahme dieses Vorgangs.

### 2. Zulaessige Dokumentation

Kuenftige Dokumente duerfen folgende gebundene Aussagen referenzieren:

- genau ein Startversuch und genau ein gestarteter Prozess;
- kein Retry und keine Beobachterartefakte;
- freie Final- und Stagingziele vor und nach dem Vorgang;
- leere Standardausgabe, 460 Standardfehlerbytes und Exitcode `1`;
- `contract_pass=false` und fail-closed Vertragsabbruch;
- Vorhandensein der ASCII-Marker `about_Execution_Policies` und `UnauthorizedAccess`;
- enge Klassifikation als Hinweis auf eine mit PowerShell-Ausfuehrungsrichtlinien verbundene nicht autorisierte Zurueckweisung.

Jeder Verweis muss `213ZZR` als Beobachtungsquelle und `213ZZS` als statische Abnahme nennen. Byte- oder Hashwerte duerfen nur unveraendert aus diesen Quellen uebernommen oder statisch reproduziert werden.

### 3. Verbindliche Abgrenzung

Ohne neue, ausdruecklich begrenzte Freigabe duerfen aus dem Vorgang nicht abgeleitet oder behauptet werden:

- Quelle, Scope, Prioritaet oder konkrete Konfiguration einer Richtlinie;
- Wirksamkeit einer bestimmten Benutzer-, Maschinen-, Prozess- oder Gruppenrichtlinie;
- Eignung eines Alternativhosts oder einer Umgehung;
- Funktionsfaehigkeit des nicht erreichten Skriptzweigs;
- Zustand einer Produktionsinventur oder eines Realpfads;
- ein G1-, Feld-, Memory-, Organismus- oder sonstiger MCM-Befund.

### 4. Behandlung in kuenftiger Arbeit

- Forschung und Dokumentation, die den gesperrten Ausfuehrungspfad nicht benoetigen, muessen den Vorgang lediglich als bekannte technische Projektgrenze ausweisen.
- Ein Ergebnis, das Daten aus dem nicht erreichten Skriptzweig voraussetzt, muss als technisch nicht erhoben gekennzeichnet werden. Fehlende Daten duerfen nicht durch Annahmen, synthetische Ersatzwerte oder alte Produktionswerte ersetzt werden.
- Eine erneute Ausfuehrung, Diagnose oder Systemaenderung darf nicht aus `213ZZT` abgeleitet werden. Sie erfordert einen neuen Auftrag mit eigener enger Vorregistrierung und ausdruecklicher Freigabe.
- Bis zu einer solchen Freigabe ist der technische Zweig dokumentarisch geschlossen. Es gibt keinen impliziten Retry und keine automatische Fortsetzung.

### 5. Unveraenderlichkeit der Evidenz

`213ZZR` und `213ZZS` bleiben historische Evidenz. Spaetere technische Erkenntnisse duerfen ihre Beobachtungswerte nicht rueckwirkend umdeuten oder ueberschreiben. Sie koennen nur in einem getrennten Dokument mit eigener Quelle, eigenem Auftrag und klarer zeitlicher Abgrenzung ergaenzt werden.

## Messergebnisse und Gegenbaselines

Diese statische Behandlung erzeugt keine neuen Laufmesswerte. Als gebundene Evidenz gelten ausschliesslich die in `213ZZS` bestaetigten Werte:

- Protokollfelder: `25/25`;
- Startversuche/Prozesse/Retry: `1/1/0`;
- Standardausgabe: `0` Bytes;
- Standardfehler: `460` Bytes;
- Exitcode: `1`;
- Beobachterartefakte: `0`;
- Final- und Stagingziel nach dem Vorgang vorhanden: nein/nein;
- `contract_pass=false`;
- beide zugelassenen ASCII-Marker vorhanden.

Gegenbaseline ist der Erfolgsvertrag aus `213ZZP`, dessen Ausgabe- und Exitbedingungen nicht erfuellt wurden. Sicherheitsbaseline sind genau ein Prozess, kein Retry, keine Artefakte und freie Ziele; diese Bedingungen wurden erfuellt. Die methodische Gegenbaseline fuer `213ZZT` ist jede unzulaessige Erweiterung von einer beobachteten Zurueckweisung zu einer nicht erhobenen Ursachen- oder Systemaussage.

## Beobachtetes Ergebnis

Der technische Vorgang ist vollstaendig dokumentiert, statisch abgenommen und als fehlgeschlagener Einzelvertrag abgeschlossen. Fuer den nicht erreichten Skriptzweig liegen keine erhobenen Ergebnisdaten vor.

## Technische Interpretation

Die bestehende Evidenz reicht fuer die enge Marker-basierte Klassifikation der unmittelbaren Zurueckweisung. Sie reicht nicht fuer eine Ursachenanalyse oder fuer Aussagen ueber eine konkrete Richtlinienkonfiguration. Methodisch ist der Vorgang deshalb als bekannte, derzeit nicht weiter untersuchte technische Ausfuehrungsgrenze zu behandeln.

## Hypothese

Keine neue technische Hypothese wird eingefuehrt. Insbesondere wird keine konkrete Richtlinienquelle oder Umgehungsmoeglichkeit angenommen.

## Offene Frage

Nur bei einem spaeteren, eigenstaendig freigegebenen technischen Auftrag waere zu klaeren, ob und auf welchem zulaessigen Weg die Ausfuehrungsgrenze weiter untersucht werden soll. Diese Frage ist nicht Gegenstand von `213ZZT`.

## Grenzen und nicht gepruefte Annahmen

`213ZZT` prueft keine Laufzeitumgebung und keine Systemkonfiguration. Es veraendert keine Policy und validiert keinen Alternativpfad. Es nimmt nicht an, dass eine spaetere Freigabe erteilt wird oder dass eine technische Diagnose den Pfad oeffnen wuerde. Es liegt kein G1- oder MCM-Befund vor.

## Konkrete Schlussfolgerung

Der gescheiterte Einzelvertrag ist dokumentarisch terminal: Er bleibt verbraucht, nicht bestanden und nicht wiederholbar. Kuenftige Arbeit darf nur die statisch gebundenen Beobachtungen und die enge Marker-basierte Klassifikation verwenden. Nicht erhobene Ursachen, Systemzustaende und fachliche Befunde bleiben offen. Keine Zielabweichung ist erkennbar.

## Vorschlag fuer den naechsten begrenzten Schritt

Als naechstes ist ausschliesslich die unabhaengige statische Abnahme von `213ZZT` sinnvoll. Dabei ist zu pruefen, ob Statusbindung, Quellenpflicht, Evidenzgrenze, dokumentarische Stopplinie und Freigabevorbehalt vollstaendig sind und ob der Vertrag unbeabsichtigt eine Ausfuehrung, Diagnose, Umgehung oder G1-/MCM-Befundarbeit autorisiert. Ein praktischer technischer Schritt wird nicht vorgeschlagen.
