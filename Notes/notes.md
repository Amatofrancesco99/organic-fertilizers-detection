<style>
red { color: Red }
orange { color: Orange }
purple {color: Purple }
green { color: Green }
</style>

# <b>Tesi magistrale - Satellite Data Analysis 🌎</b>

**Argomento:** <i>Identificazione, tramite satellite, di episodi di concimazione</i>

**Tools:** <i>Google Earth Engine</i> (da seguenza di immagini a sequenza di indici significativi, note come features) + 
<i>Python</i> (analisi delle features e costruzione dei modelli di ML)

**F. Amato - F. Dell'Acqua - D. Marzi**

***
***
## <green><b>2 Mar 2023 - 1 incontro</b></green>
L'obiettivo di questa attività di tesi è di combinare il Machine Learning (ML) a dati satellitari. Più nella fattispecie, collegare osservabili (immagini) satellitari ad azioni agricole effettuate sul terreno, in questo caso speicifico episodi di concimazione (vedere che tracce lascia un fenomeno di concimazione sulla banda spettrale).<br>

L'**identificazione degli episodi di concimazione** è importante, nella realtà pratica, per 2 motivazioni principali:
- *identificazione di operazioni di tipo agricolo* (qualcosa che succede dal campo e che vogliamo registrare dal satellite)
- *[direttiva nitrati](#direttiva-nitrati)* (le politiche agricole della commissione europea intendono effettuare controlli da satellite dei nitrati, vale a dire "non concimate quando non è permesso farlo, poiché - se lo fate - aumentate l'inquinamento da nitrati della falda acquifera e dei corsi d'acqua")

L'interesse di questa ricerca è più focalizzato sulla prima motivazione, ossia l'identificazione delle operazioni di concimazione, in quanto una delle operazioni che il campo subisce nell'arco della stagione agricola.

**Questa tesi nasce partendo da un articolo che ha utilizzato un approccio (semplicistico) per risolvere il problema identificato**, ossia: hanno cercato una serie di episodi di presunta concimazione (in una piccola area della Spagna - Università di Oviedo), affermando che se un campo agricolo ha improvvisamente cambiato "colore" (da un immagine alla successiva) allora quello è un episodio di concimazione (é vero?). Tali ricercatori hanno compreso, usando diversi modelli di classificazione ML, che un'episodio di concimazione avviene quando c'é una brusca variazione nella risposta spettrale (calcolando diversi indici). 

Il risultato ottenuto ha senso, ma ha delle limitazioni intrinseche ed è stato impostato in maniera ottimistica (area geografica limitata, è vero che se da un giorno all'altro la risposta spettrale cambia effettivamente ci sia stato un fenomeno di concimazione?).

**Come estendere questa ricerca?**
- utilizzare non solo un'immagine prima e dopo l'evento di concimazione, ma **utilizzare sequenze multi-temporali pre e post concimazione** (dataset più ricco) potrebbe essere anche d'aiuto il periodo dell'anno in cui avviene per poter comprendere se è un fenomeno di concimatuzione o meno
- **ridurre il numero di indici fisici** utilizzati, considerando quelli più utili (un paper di un'università Francese ha compreso quali sono gli indici fisici che sono più correlati ad un evento di concimazione)
- usare **non solo immagini spettrali ma anche radar**
- validare **utilizzando più aree geografiche** (non solo quell'area della Spagna) cosa accade (questo è più un problema per quanto riguarda la disponibilità di quando sono effettivamente state fatti episodi di concimazione - è difficile che un agricoltore ti venga a dire che ha concimato quando in realtà non poteva farlo in quel periodo, non tutti dichiarano di concimare, ...)

**Cosa iniziare a fare?**
Leggere i paper e per quanto riguarda il primo comprendere l'approccio che hanno seguito, eventuali limitazioni e problematiche (e.g. realizzabilità ed usabilità), scaricare magari anche il dataset (se si riesce a leggerlo o se c'è da impazzire). Inoltre si potrebbe cercare se c'è disponibilità di fenomeni accertati di concimazione in altre aree (non necessariamente in Europa). <br><br>

<purple><b>PAPER 1:</b></purple> [Remote sensing for detecting freshly manured fields](Papers/Professor/remote-sensing-for-detecting-freshly-manured-fields.pdf)<br>
Sperimentazione sistematica su un insieme di indici e con un insieme di tecniche di machine learning. Articolo utile per capire il punto da cui partiamo. Ha poco di telerilevamento, perché parte da un approccio basato sui dati piuttosto che sul loro significato, e questo lascia spazio a diversi miglioramenti.

<purple><b>PAPER 2:</b></purple> [Potential of Sentinel-2 Satellite Images for Monitoring Green Waste Compost and Manure Amendments in Temperate Cropland](Papers/Professor/monitoring-green-waste-compost-and-manure-amendments-in-temperate-cropland-Sentinel2.pdf) <br>
Illustra una serie di misure effettuate su campi dedicati alla sperimentazione specifica, e propone alcuni indici basati su dati telerilevati che si presume siano collegati alla concimazione, partendo da considerazioni fisiche.

<purple><b>PAPER 3:</b></purple> [Geospatial Intelligence Against Nitrate
Pollution (GEOINT) Project](Papers/Professor/geospatial-intelligence-against-nitrate-pollution.pdf)<br>
Metodo proposto per l'identificazione della concimazione. Superato, ma da indicazioni utili soprattutto perché è basato sull'interpretazione del dato anziché sull'applicazione ("alla cieca") di una serie di metodi alternativi tra loro per valutare quale funziona meglio.

<purple><b>GOOGLE SCHOLAR </b></purple>(https://scholar.google.com): ricerca di metodi

*** 
### <orange><b>Direttiva Nitrati</b></orange>
La Direttiva Nitrati è una normativa dell'Unione Europea adottata nel 1991 e successivamente rivista nel 1998 e nel 2006, che ha lo scopo di proteggere le acque dall'inquinamento causato dai nitrati di origine agricola.

I nitrati sono composti chimici costituiti da atomi di azoto e di ossigeno (NO3-) che sono presenti naturalmente nel terreno e nell'acqua. Tuttavia, l'uso eccessivo di fertilizzanti e la gestione inadeguata dei rifiuti animali possono aumentare la quantità di nitrati presenti nel suolo e nell'acqua, causando la contaminazione dell'acqua potabile e la proliferazione di alghe nocive nelle acque superficiali.

La Direttiva Nitrati stabilisce un quadro normativo per la protezione delle acque dall'inquinamento da nitrati di origine agricola, stabilendo limiti massimi per l'applicazione di fertilizzanti azotati e imponendo misure preventive e correttive per ridurre la contaminazione da nitrati.

La direttiva impone anche ai paesi membri dell'UE di elaborare piani d'azione per la riduzione dell'inquinamento da nitrati nelle loro aree vulnerabili, che prevedono la limitazione dell'uso di fertilizzanti azotati, la gestione corretta dei rifiuti animali e la promozione di pratiche agricole sostenibili.

***
***
## <green><b>Note sui paper</b></green>

*1. Limitazioni e problemi del primo paper - Spagnoli*

- **Fanno uno train-test split selezionando il 70% dei campi (21) per il train e il restante per il test (9)**. Sarebbe decisamente meglio fare K-Fold cross-validation per valutare le performance
- **Non specificano se abbiano fatto feature selection/reduction sull’intero dataset oppure solo su quello di train**. Se si utilizza l'intero dataset per la selezione delle caratteristiche, si rischia di selezionare anche le caratteristiche irrilevanti o ridondanti, aumentando il rischio di overfitting e diminuendo la capacità di generalizzazione del modello. Inoltre, l'utilizzo dell'intero dataset per la selezione delle caratteristiche può portare ad un aumento del tempo di elaborazione e della complessità
- **Ho notato che nascondono molto il fatto che hanno un recall molto basso** (specialmente per la classe di pixel concimati - 85%) che però diventa alta la media del recall, perché il recall dei pixel non concimati è molto alto (99%). Avrebbe più senso scegliere un modello in cui sia la precision che la recall siano simili per entrambe le classi (ok la media, ma la varianza del recall per le due classi?)...specialmente se si vogliono riconoscere concimazioni illegali
- **La maggior parte degli eventi di concimazione per i diversi campi sono registrati nel periodo tra Febbraio a Maggio** (pochi a Febbraio e la maggior parte a Maggio)
- **I campi si trovano tutti in Spagna e tra l'altro utilizzano solamente solo l’immagine prima e dopo dell’evento di concimazione per quel campo** (loro stessi suggeriscono di usare sequenze temporali), **inoltre usano solo campi in cui è stata effettuata una concimazione** (il modello finale alla fine sarebbe in grado di riconoscere campi dove non c'é mai stata nemmeno una sottoparte concimata - oppure farebbe errori?)
- **Usano tantissime features, senza capire bene perché il modello finale funziona bene con quelle features** (ho il sospetto che molte delle features ridotte siano biased dovute al fatto che i campi si trovano solamente in Spagna). Dunque io preferirei qualcosa di più interpretabile (e magari meno biased), magari facendo ulteriori ricerche per capire se anche in altri paper (ad esempio in USA, per evitare di rimanere ristretti ad una ricerca valida in EU) gli stessi indici individuati dall’università Francese (Exogenous Organic Matter Indexes) sono validi ugualmente (cosa che suggerirebbe di usare molte meno features - e non 128 come quello spagnolo)
<br><br>

*2. Limitazioni e problemi del secondo paper - Francesi*
- **Le uniche colture considerate sono grano, mais e colza** (diverse però da quelle considerati dagli spagnoli, che però hanno usato molte più features)
- Hanno studiato **solamente quello che accade nel periodo tra Giugno e Agosto nella parte a nord della Francia**
- **Non hanno considerato cosa accade ai vari indici quando ad esempio piove molto, o quando passano più di 60 giorni dall'evento di concimazione**, o ancora più importante **in campi in cui non é mai stata fatta una concimazione nel periodo considerato** (i vari indici variano notevolmente anche in periodi particolari dell'anno, dove però non é mai stata fatta una concimazione? Oppure variano solo effettivamente quando c'é stata una concimazione...il terzo paper mostra alcuni contro-esempi utili)

<br><br>

*3. Risultati, limitazioni e problemi del terzo paper - Dell'Acqua & Marzi*
- **L'analisi è limitata a due campi locati nel nord Italia, dove la concimazione è stata fatta sempre nel periodo primaverile-estivo**
- **L'analisi mostra che effettivamente l'EOMI non sia un indice molto affidabile, esso infatti varia di molto in periodi dell'anno dovuti a fenomeni non solo legati a quelli della concimazione stessa** (in cloud filtering necessario)
- **L'effetto della concimazione dipende dal tipo di coltivo, tipi di campi diversi hanno effetti diversi** (anche per quanto riguarda i tempi di visibilità degli effetti di concimazione stessa, cambiano in funzione della tecnica di concimazione usata in funzione del tipo di coltivo) 


*Come si potrebbero unire i risultati dei vari paper, in un'unica soluzione (valida e utilizzabile) che cerchi di ridurre le limitazioni intrinseche di ciascuno?*<br>
Un'idea potrebbe essere quella di trainare i nostri modelli (di ML - non optiamo per DeepL siccome abbiamo troppi pochi campi) usando: 
- **Tutti i campi spagnoli**: per performance K-fold, anziché train e test
- **Molte meno features**: aggiungendo però *[indici radar](#indici-radar-per-rilevare-concimazione)*, per favorire interpretabilità. Osservando inoltre che gli indici individuati dai Francesi sono: 
    - significativi in altri periodi dall'anno, in un'altra area geografica ed in tipi di campi diversi da quelli usati dagli spagnoli
    - **MA** legati anche a fenomeni dovuti non alla sola concimazione e, ancora più importante, **NON** hanno considerato cosa accade ai vari indici in campi in cui non é mai stata fatta una concimazione nel periodo considerato (questo in parte spiega perché usare moltissime features migliora le performance)
- **Sequenze multi-temporali** (ricordiamo che gli effetti della concimazione sui vari indici studiati nel secondo paper si riducono notevolmente man mano che passano giorni dall'evento di concimazione stessa - considerare time slice da 30gg pre e post concimazione). 
- L'obiettivo finale è quello di ottenere **sia precision che recall alti**, dopo di che una volta individuato il modello "migliore" possiamo **valutare come funziona anche nei due campi locati in Italia** (abbiamo una validità maggiore se funziona bene anche in Italia).

*Quali limitazioni rimarrebbero?*<br>
**Geografica:** Un po' meglio che solo quello spagnolo. Chiaramente se funziona bene per i due campi in Italia (nord-Italia) non é detto che funzioni ugualmente bene né in tutta l’Italia, né in Spagna, ne tanto meno in tutto il mondo (alla fine Italia e Spagna son pur sempre in Europa, con un clima molto simile e vicine tra loro). Quindi ci sarebbe da verificare come funziona per altre aree geografiche nel mondo (potrebbe essere un’hint a portare avanti questa attività nel tempo...leggere la parte sotto di come migliorare l'accuratezza).<br>
**Temporale:** L'analisi è limitata a campi in cui la concimazione è stata fatta nel periodo primaverile-estivo.<br>
**Terzo punto *"2. Limitazioni e problemi del secondo paper - Francesi"*** (pag. 3)<br>
**Risoluzione spaziale immagini satellitari**: Metri di terra vengono sintetizzati in una singola misurazione (per ogni banda acquisita dal sensore)<br>

**Come si potrebbero ridurre ulteriormente alcune tra le limitazioni che ancora rimarrebbero?** Se optassimo per l'utilizzo dei satelliti PlanetScope anziché Sentinel avremmo una risoluzione spaziale superiore (ed anche una più alta revisit frequency...potrebbe essere di aiuto per diversi motivi tra cui il fatto che gli EOMI sono sensibili al cloud coverage), ma avremmo meno bande spettrali disponibili (quale opzione converrebbe scegliere?). Inoltre gli spagnoli hanno usato Sentinel...<br>
**Come si potrebbe migliorare ulteriormente l'accuratezza del modello?** Molte cose potrebbero aiutare, ma forse una tra le più importanti potrebbe essere conoscere il periodo dell'anno considerato + il luogo geografico + il tipo di coltivo. Tipicamente tenendo fisso il tipo di coltivo ed il luogo geografico il periodo dell'anno in cui è più probabile che sia fatta una concimazione potrebbe essere imparato dai dati stessi<br>
**Ultima considerazione**: il modello non possiamo trainarlo con i due campi locati in Italia + tutti quelli in Spagna, perché per condurre un’analisi valida dovremmo usare lo stesso numero di campi nelle due aree (altrimenti sarebbe biased a riconoscere la concimazione in Spagna). Ma per fare ciò avremmo solo 4 campi in totale, che sono davvero pochi per poter condurre un’analisi sperimentale valida e che sia statisticamente significativa.<br>

***
### <orange><b>Alcuni indici radar per rilevare concimazione</b></orange>
- *Indice di differenza di backscatter (BSI)*: l'BSI misura la differenza tra il segnale di backscatter delle immagini radar pre- e post-concimazione. Dopo la concimazione, le proprietà elettriche del suolo e delle piante possono cambiare, influenzando la quantità di segnale di backscatter ricevuto dal radar.
- *Indice di variazione temporale della rugosità (TIRS)*: il TIRS è un indice che misura la variazione della rugosità del suolo nel tempo. Dopo la concimazione, il suolo può diventare più uniforme, influenzando il TIRS.
- *Indice di backscatter polarimetrico (PBSI)*: il PBSI è un indice che misura la polarizzazione del segnale di backscatter delle immagini radar. 
- *Indice di backscatter del canale di polarizzazione incrociata (CPBSI)*: il CPBSI è un indice che misura la quantità di segnale di backscatter ricevuto dal canale di polarizzazione incrociata delle immagini radar.

***
***
## <green><b>14 Mar 2023 - 2 incontro</b></green>
**Problema studio spagnoli:** La data di concimazione deve essere nota a priori per poter identificare le aree interessate concimate.
**Nostro obiettivo:** Riconoscere in un lasso temporale le date di concimazione (la percentuale di area concimata di un campo??), utilizzando immagini satellitari (sia Sentinel2: indici ottici, che Sentinel1: indici radar).

**Cosa iniziare a fare?** Dare un occhiata al [dataset Spagnolo](https://data.mendeley.com/datasets/fbvvvf55kp/1), studiare come è fatto.

**ChatGPT prompt:**
"Codice Google Earth Engine & Python che sia in grado di riconoscere in un lasso temporale le date di concimazione e la percentuale di area concimata di un campo - utilizzando immagini satellitari, più specificatamente usando sia Sentinel2 per indici ottici, mentre Sentinel1 per indici radar (usando un filtro per il cloud coverage per le immagini Sentinel2).<br>
Il dataset nel complesso contiene 30 campi agricoli di cui per ognuno abbiamo una sola data di concimazione e la geometria del campo. 
Il train dataset contiene il 70% di campi agricoli totali di cui sappiamo una sola data di concimazione, le coordinate geografiche del campo, l'area del campo.<br>
Per il test dataset abbiamo il restante 30% dei campi agricoli di cui sappiamo solo le coordinate geografiche, l'area del campo.<br>
Calcola le performance usando K-Fold cross validation. La misura di performance è data dalla differenza tra le date effettiva di concimazione e la date individuata dal modello. <br>
Infine, il modello non deve imparare pattern nelle date di concimazione o tra le coordinate e la data di concimazione, ma solamente tra l'evoluzione temporale degli indici fisici e le date di concimazione."

***
***