"""Format verified UF1 archive evidence; no experiment execution."""
import hashlib,json
from pathlib import Path
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
RUN=ROOT/'reports/s2uc/uf1-comparison-20261005-01'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=read(OUT/'verification.json');a=read(RUN/'assessment.json')
assert v['status']=='PASS_ARCHIVE_VERIFICATION' and v['verdict']=='F_VORTEIL_BELEGT'
def d(x):return f'{float(Fraction(x)):.12f}'
def ci(x):return '['+'; '.join(map(d,x))+']'
def table(headers,rows):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows]
primary=v['primary'];main={x['condition']:x for x in a['secondary'] if x['mask']=='Q' and x['orientation'] is None}
lines=['# UF1 Abschluss und unabhängige Archivprüfung','',
'Berichts- und Prüfdatum: 2026-10-14. Forschungsversuch: 2026-10-05. Autor: MCM-KI-Entwickler; Empfänger: MCM KI Projektleiter.',
'', '**Abschluss: PASS_ARCHIVE_VERIFICATION; F_VORTEIL_BELEGT unabhängig bestätigt.** Genau ein vorhandener Forschungsversuch COMPLETE, 32 neue D/N-Paare, 64 Geschichten und 128 Armläufe. Die UF1-Einmalbeauftragung ist VERBRAUCHT. Dieser Abschluss erzeugt keine neue Laufnummer oder Forschungsfreigabe.',
'',f"Einziger Primärkontrast D, U−F auf allen Q-Zielen: **{d(primary['mean'])}**, nominales 95%-Intervall **{ci(primary['ci'])}**. Exakt: {primary['mean']}, [{'; '.join(primary['ci'])}]. Das gesamte Intervall ist positiv: F hat in dieser Aufgabenfamilie weniger Fehler als U.",
'','## Fehlerwerte und ergänzende Befunde','']
lines+=table(['Bedingung','U mittlere MAE','F mittlere MAE','U−F','95%-Intervall','Einordnung'],[[c,d(x['means']['U']),d(x['means']['F']),d(x['mean']),ci(x['ci']),'einziger Primärvergleich' if c=='D' else 'ergänzend, kein zweiter Primärtest'] for c,x in main.items()])
lines+=['', 'Alle 32 D-Paarkontraste sind positiv. In N ist der ergänzende mittlere Kontrast negativ: U hat dort weniger Fehler als F. Die 30 Nebenintervalle und die Interaktion sind nominal und nicht für Mehrfachvergleiche korrigiert; daraus entsteht kein zusätzlicher konfirmatorischer Gesamtsieg.',
f"Explorative Interaktion (D:U−F)−(N:U−F): {d(a['interaction']['mean'])}, 95%-Intervall {ci(a['interaction']['ci'])}.",
'','## Bedeutung für den Erfahrungsmechanismus','',
'**Beobachtung:** U bildet und nutzt begrenzte Verlaufsspuren mit rückgemeldeten Fehlerwerten; die archivierten Ausgaben und Fehlerupdates sind konsistent. In D gewinnt U an 832 Q-Zielen gegen F, verliert an 2323 und ist an 5037 gleich. Seine Gewinnsumme 238,5 wird durch die Schadenssumme 706,25 übertroffen. In N gewinnt U an 2643 Q-Zielen, verliert an 2406 und ist an 3143 gleich; Gewinn 884,25, Schaden 793,75. Technische Funktion und zusätzlicher Vorhersagenutzen sind damit getrennte Aussagen.',
'', '**Technische Interpretation:** Auf der stabilen hinweisabhängigen Zweiwerteaufgabe nutzt die einfache Häufigkeitsregel die bisher beobachteten Alternativen wirksamer als U als Gesamtverfahren. U erreicht hier keinen Vorteil gegenüber dieser passenden Baseline. In D ist die Nettobilanz gegenüber F in jeder U-Verfügbarkeitsklasse negativ, auch bei warmem Kontextabruf V3. Der Abstand lässt sich daher deskriptiv nicht ausschließlich auf fehlende oder kalte Spuren reduzieren. Das ist keine kausale Zerlegung der Fehlerursache.',
'', '**Hypothese:** Die Speicherung alternativer Fortsetzungen samt ihrer empirischen Häufigkeiten und die zur absoluten Fehlerbewertung passende Mehrheitswahl können den D-Vorteil erklären. UF1 isoliert diese Erklärung nicht: F besitzt explizites Vierframe-Phasenwissen, zwei exakte Zweiframe-Hinweisschlüssel und eine andere Speicherrepräsentation. U hält zwei Retained-Vierframespuren und einen Kandidaten mit Fehlerbewertung. Ein Gleichbudget- oder Gleichinformationsvergleich liegt nicht vor. Insbesondere sind U-Zusatzheap und F-Eigenheap keine direkt vergleichbaren Gesamtgrößen; U-Bank allein gegen F-Bank zu stellen wäre irreführend.',
'', '**Grenzen und Nichtnachweis:** F kann je Hinweis nur zwei verschiedene Fortsetzungswerte aufnehmen; ein dritter Wert wäre terminal. In diesen Quellen gibt es nur zwei Hinweise, daher keine F-Hinweisverdrängung. Kein Nachweis für variierende Aufgaben, Audio/Video, allgemeine Kognition, Semantik, Clusterbildung oder feldinterne Memory. Der ergänzende U-Vorteil in N belegt ebenfalls keine allgemeine Überlegenheit. Die Ergebnisse von UH1/UHR1 bleiben eigenständige Befunde mit anderen Quellen und Vergleichsarm H; sie werden weder gepoolt noch kausal mit UF1 verrechnet.',
'','## Unabhängige Prüfungen und Aussagegrenzen des Audits','',
'Das nachgelagerte Skript importiert ausschließlich die Python-Standardbibliothek. Es führt keine Policy, keinen Produktions- oder Referenzprädiktor und keinen Quellengenerator aus. Die Auswertung verwendet nur vorhandene UF1-Archive sowie die vorab gebundenen Dateien.',
'']
lines+=table(['Prüfung','Ergebnis'],[
['Bindungen','PASS: exakter Vorstart-SHA, operative Code-/Vorstartdateien, Vertrags-SHA, Autorisierungsvorlage plus AUTHORIZED_ONCE, archivierter Planhash und 4.690.185 Vorbereitungsbytes'],
['Archivvollständigkeit','PASS: exakt 133 im Versuchsabschluss gebundene Dateien plus closure.json; alle Dateilängen und SHA256; 64 Quellen und 64 Fallarchive'],
['Quellen','PASS: kanonische Bytes, IDs/r/C/o, Katalog, 1024 Frames, Phasen, D-Quoten, N-Randquoten, identische D/N-Fortsetzungsfolgen je Paar, Ziehungszähler und Quellenhashes'],
['F','PASS: 65.536 vollständige Bankzustände aus XOR/zlib-Deltas dekodiert; Schlüssel, Wertebits, Häufigkeiten gegen ausschließlich vergangenes Feedback, Reihenfolge, Stempel, Puffer, Tickets, Ausgabe und Phasen geprüft'],
['F-Fehler','PASS: 32.704 eingefrorene Ausgaben aus Vorzustand gegen archivierte Ziele mit sequenziellem binary64-MAE nachgerechnet; F0/F1/F2 und Zählerdiagnosen geprüft'],
['U','PASS: 32.704 Ausgaben anhand ursprünglicher Frameindices neu bewertet; archivierte Auswahl anhand Fehlerzellen, EC/EP-Updates und Feedbackhistorie rekonstruiert; Profil und Zeitfenster geprüft'],
['Statistik','PASS: alle 320.000 Bootstrapindices gegen SHA-Rezept, 640 Armmittelwerte, 32 Primärpaare, Primärintervall, 30 Nebenbilanzen/-intervalle, 704 Falldiagnosen und explorative Interaktion exakt rational nachgerechnet'],
['Ressourcen','PASS: archivierte Laufzeit-/Speicher-/Exportmessungen und sämtliche Kategoriegrenzen; zusätzlicher Abschluss im Exportbudget'],
['Cleanup','COMPLETE, Workerexit 0, Worker beendet, Cleanup-Marker je Fall, Ziel 1025 rechtszensiert, Resume verboten']])
lines+=['', 'Die Vollständigkeitsprüfung des vorbereiteten Skripts führte zu Ergänzungen ausschließlich an verify_archive.py: vollständige F-Zustandsprüfung gegen Präfixhäufigkeiten, U-Zell-/Auswahl-/Feedbackprüfung, unabhängige Bootstrapindexprüfung, eindeutige Nebenbilanz-/Diagnoseabdeckung, fehlende Primär-/Interaktionsmittelwerte, Fallidentitäten, Plan-/Vorbereitungsbindung und Ressourcenteilgrenzen. Während der Entwicklung wurde der Zugriff auf im Kompaktarchiv nicht enthaltene prior_feedback-Felder durch Rekonstruktion aus Updates und ursprünglichen Frameindices ersetzt; ein Syntaxfehler wurde vor der erfolgreichen Auswertung korrigiert. Diese Prüfskriptkorrekturen veränderten keine gebundenen Versuchsdaten oder Verfahren.',
'', 'Auditgrenze: Die ursprüngliche Quellenrezeptprüfung und die kausale Versiegelung vor dem ersten Policy-Aufruf sind durch den gebundenen Starter und das Manifest belegt; das Audit prüft deren Bindung und die archivierten Quellen, erzeugt aber das Forschungsrezept nicht erneut. Die damals unabhängige U-Lebenszyklusreferenz und der Cleanup sind im gebundenen Lauf belegt; das Audit führt keine zweite U-Zustandsmaschine aus. Prozesspeaks sind archivierte Windows-Job-Messungen, keine heute erneut gemessenen Laufwerte. Die 3600-s-Frist betrifft den damaligen Versuch, nicht die am 14.10. erfolgende nachgelagerte Dokumentation.',
'','## Vollständige ergänzende Vergleiche','',
'Orientierung 0: ungerade Paare; 1: gerade Paare; alle: 32 Paare. Q hat 256, G_all 511, S 255 und Q_X/Q_Y jeweils 128 Ziele je Geschichte. Positive U−F-Werte bedeuten F-Vorteil. Alle Q-Ziele einschließlich Kaltstart zählen. S ist in beiden Armen identisch.', '']
lines+=table(['C','Maske','Orientierung','U','F','U−F','95%-Intervall'],[[x['condition'],x['mask'],'alle' if x['orientation'] is None else x['orientation'],d(x['means']['U']),d(x['means']['F']),d(x['mean']),ci(x['ci'])] for x in a['secondary']])
lines+=['','## Gewinne und Schäden','', 'Perspektive U gegen F: Gewinn=sum(max(F−U,0)), Schaden=sum(max(U−F,0)), Netto=Gewinn−Schaden. Diese Ziel-Summen sind keine Geschichtenmittelwerte. Besser/schlechter/gleich zählen Ziele. Schlechtestes Paar ist der größte Geschichtenmittelwert U−F.','']
lines+=table(['C/Maske/o','Ziele','Gewinn','Schaden','Netto','besser/schlechter/gleich','max. Schaden','schlechtestes Paarmittel'],[[f"{x['condition']}/{x['mask']}/{x['orientation'] if x['orientation'] is not None else 'alle'}",x['count'],d(x['gain']),d(x['harm']),d(x['net']),f"{x['improved']}/{x['worse']}/{x['equal']}",d(x['max_harm']),d(x['worst_mean'])] for x in a['secondary']])
lines+=['', 'Alle Positionen maximalen Schadens stehen verlustfrei in [assessment.json](../uf1-comparison-20261005-01/assessment.json) unter secondary[].maximum_harm_targets als [Paar,Ziel]. Sämtliche 30 Paarlisten, 704 Falldiagnosen und 640 Armmittelwerte bleiben dort vollständig erhalten; die 640 Armmittelwerte stehen zusätzlich in [verification.json](verification.json). Die Positionen wurden unabhängig gegen alle archivierten Ziele geprüft.','', '## Diagnosen auf allen Q-Zielen','',
'V0: keine passende Spur; V1: nur kalte Zellen; V2: warm/Persistenz; V3: warm/Kontext. F0: unbekannt; F1: Gleichstand; F2: strikte Mehrheit. Partitionen überlappen und werden nicht addiert. Leere Gruppen haben keine definierte mittlere Leistung; ihre Summen sind null.','']
lines+=table(['C','Partition','Label','Anzahl','Gewinn','Schaden','Netto','besser/schlechter/gleich','max. Schaden'],[[x['condition'],x['partition'],x['label'],x['count'],d(x['gain']),d(x['harm']),d(x['net']),f"{x['improved']}/{x['worse']}/{x['equal']}",d(x['max_harm']) if x['count'] else 'nicht definiert'] for x in v['diagnosis']])
lines+=['','## Alle Primärpaare','']
lines+=table(['Paar','Orientierung','D: U−F exakt','D: U−F dezimal'],[[r,(r-1)%2,x,d(x)] for r,x in enumerate(primary['pairs'],1)])
lines+=['','## Quellenkontingenzen','', 'D je ungeradem Paar XA/XB/YA/YB=96/32/32/96, je geradem Paar 32/96/96/32. N hat die folgenden tatsächlichen Kontingenzen, ohne erzwungene 64er-Balance. Die vollständigen 64 Quellenhashes und Ziehungszähler stehen in verification.json unter source_tables und im [Manifest](../uf1-comparison-20261005-01/manifest.json).','']
lines+=table(['Paar','Orientierung','N: XA/XB/YA/YB'],[[x['replicate'],x['orientation'],'/'.join(map(str,x['XA_XB_YA_YB']))] for x in v['source_tables'] if x['condition']=='N'])
lines+=['','## Ressourcen und Export','']
resource_rows=[['Workerzeit (s)',v['counts']['engine_seconds'],3540],['Supervisor bis Abschlusswrite (s)',v['supervisor_seconds'],3600],['Job Private Commit (Byte)',v['process_memory']['peak_job_committed_bytes'],536870912],['Prozesspeak (Byte)',v['process_memory']['peak_process_committed_bytes'],'im gemeinsamen Job'],['U Zusatzheap (Byte)',v['maxima']['U']['additional_python_peak'],16384],['F Eigenheap (Byte)',v['maxima']['F']['own_heap_peak'],32768],['F Bank / konservative Numerik (Byte)','4304 / 4712',5120],['U Originalframes / kombinierte Obergrenze','16 / 18','18 / 20'],['U Receipt / UTF-8-Obergrenze (Byte)','778 / 1556','16384 / 32768'],['Vorbereitung (Byte)',4690185,8388608],['Quellen gesamt (Byte)',v['source_bytes'],2097152],['Fallarchive gesamt (Byte)',v['case_total_bytes'],33554432],['Größtes gzip / expandiert (Byte)',f"{v['case_compressed_max']} / {v['case_expanded_max']}",'524288 / 4194304'],['Laufverwaltung (Byte)',v['admin_bytes'],2097152],['Versuchsabschluss (Byte)',v['terminal_bytes'],1048576],['Laufexport (Byte)',v['export_bytes'],'Teil der Gesamtsumme'],['Vorbereitung plus Laufexport (Byte)',v['charged_plus_export_bytes'],67108864]]
lines+=table(['Messgröße','Wert','Grenze'],resource_rows)
lines+=['', 'F besitzt einen Ausgabeslot, keine Receipts und höchstens 384 Byte geliehene Eingangsrohdaten (Objektgraph 1584 Byte). U besitzt bis zu zwei Ausgabeslots. U-Grenzstellenmaxima: 15 Originale, 5760 Originalrohbytes, 15907 Originalobjektbytes, 17183 Basisarmbytes und 20871 insgesamt erreichbare Bytes; Zusatzheap wird separat gemessen. Nullwerte deaktivierter Rohtrace-Spitzen bedeuten nicht Nullspeicher. F konservative Numerik ist eine gebundene Entwurfsobergrenze, kein neu erhobener numerischer Peak.',
'', 'Externe Beobachtermaxima: U-Belege 11021954 Byte, F-Trace 601440 Byte, Eingangsobjekte 458136 Byte, F-Referenzgrenzstelle 798 Byte. Diese Größen gehören zum gemeinsamen Prozessbudget, nicht zur Arm-Memory. Vollständige Phasenspitzen stehen in verification.json/maxima.',
'', 'Die nachgelagerten Prüf-/Berichtsdateien sowie die neu eingefügten Übersichtstexte werden zusätzlich belastet. [export-accounting.json](export-accounting.json) enthält die abschließende Bytebilanz samt 16-KiB-Reserve für Bilanz und Abschluss; die bereits vorhandenen historischen Übersichtstexte werden nicht als neue Kopie belastet. Verwaltungsgrenze 2 MiB und Gesamtgrenze 64 MiB bleiben verbindlich.',
'','## Bindungen und Artefakte','']
lines+=table(['Artefakt','SHA256'],[['Vorstart',v['prestart_sha256']],['Codebindung',v['code_binding_sha256']],['Autorisierung',v['authorization_sha256']],['Quellenmanifest',v['manifest_sha256']],['Versuchsabschluss',v['closure_sha256']],['Vorhandene Auswertung',sha(RUN/'assessment.json')],['Prüfskript',sha(OUT/'verify_archive.py')],['Unabhängige Prüfung',sha(OUT/'verification.json')]])
lines+=['', 'Forschungsarchiv: reports/s2uc/uf1-comparison-20261005-01. Abschlussordner: reports/s2uc/uf1-assessment-20261005-01. [Prüfskript](verify_archive.py), [Prüfergebnis](verification.json), [Abschlussbindung](closure.json). Gebundener Code, Quellen, Matrix, Autorisierung und Versuchsabschluss bleiben unverändert. AUTHORIZED_ONCE in der historischen Autorisierungsdatei wird nicht umgeschrieben: Der vorhandene Versuchsmarker und Abschluss belegen den Verbrauch. Kein Retry, Resume, Ersatzmaterial oder Pooling.',
'','## Begründeter nächster fachlicher Schritt','',
'Vorschlag an den Projektleiter: zunächst einen eng begrenzten Konzeptvertrag für einen Vergleich unter angeglichenem Informationszugang und nachvollziehbar abgeglichenem Gesamtbudget festlegen. Er soll genau die offene Frage trennen, ob U gegenüber der Häufigkeitsspeicherung einen eigenständigen Nutzen aus Verlaufserfahrung gewinnt oder ob der jetzige Abstand durch Aufgabenpassung, Phasenwissen und Speicherung der Alternativen erklärt wird. Die notwendige Angleichung muss vor jeder Implementierung festlegen, welches Phasenwissen beide Verfahren erhalten, welche Originaldaten und Zusatzspeicher zählen und welcher einzelne Kontrast die Erklärung falsifizieren würde. Ist das ohne eine andere Forschungsfrage nicht sinnvoll möglich, soll der Projektleiter die Grenze ausdrücklich festhalten und den nächsten Aufgabenstrukturwechsel begründen.',
'', 'Begründung: Die vorliegende stabile Zweiwerteaufgabe zeigt einen klaren D-Vorteil der einfachen Baseline und einen ergänzenden N-Vorteil von U. Ein weiteres unverändertes Wiederholen liefert keine neue mechanistische Gegenprognose. Deshalb jetzt keine U-Änderung, keine neue Laufserie und kein vorweggenommener Architekturwechsel. Der Folgeauftrag ist in diesem Abschluss ausschließlich vorgeschlagen und wurde nicht ausgeführt.','']
(OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')

summary='''## Aktueller Ergebnisstand: UF1 unabhängig abgeschlossen (2026-10-14)

Der Forschungsversuch vom 2026-10-05 ist COMPLETE; die nachgelagerte Archivprüfung
ist PASS_ARCHIVE_VERIFICATION. F_VORTEIL_BELEGT unabhängig bestätigt:
D: U−F = 0.057098388672; nominales 95%-Intervall [0.054504394531; 0.059814453125].
D-MAE: U 0.186218261719, F 0.129119873047. Ergänzend N: U−F = −0.011047363281,
Intervall [−0.017975616455; −0.003936767578]; kein zweiter Primärtest.
32 neue D/N-Paare, 64 Geschichten, 128 Armläufe. 65.536 F-Zustände,
je 32.704 U-/F-Ausgaben, 640 Armmittelwerte, alle Intervalle und Bilanzen geprüft.
Keine neuen Quellen und keine Policy-Wiederholung im Abschlussaudit.
Supervisor 465.861 s; Job-Peak 204697600 Byte; Ressourcen- und Exportgrenzen eingehalten.

[Ergebnisbericht]({report}), [Archivprüfung]({verification}), [Exportbilanz]({accounting}).
Die UF1-Einmalbeauftragung ist VERBRAUCHT: kein Retry, Resume oder Ersatzmaterial.
Gebundene Verfahren und Archive bleiben unverändert; UH1/UHR1 werden nicht gepoolt.
U zeigt hier keinen D-Vorteil gegenüber F. F hat Phasenwissen und eine andere
Speicherrepräsentation; Ursachen und allgemeine Überlegenheit sind damit nicht belegt.
Nächster Vorschlag: begrenzter Konzeptvertrag für einen Vergleich unter angeglichenem
Informationszugang und nachvollziehbar abgeglichenem Gesamtbudget, mit genau einer
falsifizierbaren Frage zum Nutzen der Verlaufserfahrung. Noch nicht ausgeführt.

'''
overview_bytes={}
for name in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md'):
    path=ROOT/name;text=path.read_text(encoding='utf-8')
    assert '## Aktueller Ergebnisstand: UF1 unabhängig abgeschlossen (2026-10-14)' not in text
    old='## Aktueller Arbeitsstand: UF1 implementiert und neutral qualifiziert (2026-10-05)'
    assert old in text
    link=('../' if name.startswith('docs/') else '')+'reports/s2uc/uf1-assessment-20261005-01/'
    block=summary.format(report=link+'REPORT.md',verification=link+'verification.json',accounting=link+'export-accounting.json')
    replacement=block+old.replace('Aktueller Arbeitsstand','Historischer Vorbereitungsstand')
    text=text.replace(old,replacement,1)
    path.write_text(text,encoding='utf-8')
    overview_bytes[name]=len(replacement.encode())-len(old.encode())

files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.iterdir() if p.is_file() and p.name not in ('export-accounting.json','closure.json')}
audit_bytes=sum(x['bytes'] for x in files.values());overview_charge=sum(overview_bytes.values());reserve=16384
account=dict(status='PASS',date='2026-10-14',preparation_bytes=4690185,research_export_bytes=v['export_bytes'],
    research_admin_bytes=v['admin_bytes'],assessment_files_before_accounting=files,assessment_bytes_before_accounting=audit_bytes,
    overview_new_text_bytes=overview_bytes,overview_new_text_total=overview_charge,accounting_and_closure_reserve=reserve,
    conservative_total_bytes=v['charged_plus_export_bytes']+audit_bytes+overview_charge+reserve,total_limit_bytes=67108864,
    conservative_admin_bytes=v['admin_bytes']+audit_bytes+overview_charge+reserve,admin_limit_bytes=2097152,
    scope='New overview content charged; pre-existing historical overviews are not duplicated research exports.')
assert account['conservative_total_bytes']<=account['total_limit_bytes']
assert account['conservative_admin_bytes']<=account['admin_limit_bytes']
def save(path,data):
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
save(OUT/'export-accounting.json',account)
files['export-accounting.json']={'bytes':(OUT/'export-accounting.json').stat().st_size,'sha256':sha(OUT/'export-accounting.json')}
closure=dict(status='PASS_UF1_ASSESSMENT_COMPLETE',date='2026-10-14',verdict=v['verdict'],files=files,
    research_closure_sha256=v['closure_sha256'],authorization_consumed=True,research_attempts=1,
    new_research_attempts_in_this_assignment=0,policy_replays=0,source_materializations=0,
    overview_files={n:{'sha256':sha(ROOT/n),'new_text_bytes':overview_bytes[n]} for n in overview_bytes},
    proposed_next_step_executed=False)
save(OUT/'closure.json',closure)
assert sum((OUT/n).stat().st_size for n in ('closure.json','export-accounting.json'))<=reserve
print(json.dumps({k:account[k] for k in ('status','conservative_total_bytes','conservative_admin_bytes')},indent=2))
