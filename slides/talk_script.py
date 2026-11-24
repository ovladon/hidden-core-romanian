"""Textul prezentarii scurte (romana si engleza), folosit de make_talk.py (notele vorbitorului) si de script_doc.py."""

SLIDES = [
    (1, "The Hidden Core of Romanian", "0:30",
     "Bună ziua. Sunt Vlad Belciug și vă prezint o lucrare scrisă împreună cu Elena Pelican, de la Universitatea „Ovidius” din Constanța. "
     "Imaginea din dreapta este o bucată reală din DEX: fiecare săgeată arată că un cuvânt apare în definiția altuia. "
     "Până la final o să vedeți ce înseamnă culorile.",
     "Good morning. I am Vlad Belciug, and this is joint work with Elena Pelican, from “Ovidius” University of Constanța. "
     "The picture on the right is a real piece of the DEX: each arrow shows that one word occurs in the definition of another. "
     "By the end of the talk you will know what the colours mean.",
     "Arată spre rețea."),
    (2, "Look up copac. Then look up arbore.", "0:50",
     "Să facem un experiment simplu. Căutăm copac în DEX. Definiția se termină cu: arbore, pom. "
     "Căutăm arbore. Definiția se termină cu: copac, pom. Fiecare cuvânt ne trimite la celălalt. "
     "Dacă nu știm deja măcar unul dintre ele, dicționarul nu ne poate ajuta. Undeva, cercul trebuie rupt de un cuvânt pe care îl știm deja.",
     "Let us try a simple experiment. We look up copac, ‘tree’, in the DEX. The definition ends with: arbore, pom. "
     "We look up arbore. Its definition ends with: copac, pom. Each word sends us to the other. "
     "If we do not already know one of them, the dictionary cannot help. Somewhere, the circle has to be broken by a word we already know.",
     "Arată săgețile, apoi pauză scurtă după ultima frază."),
    (3, "How many words must you already know?", "0:30",
     "De aici vine întrebarea lucrării: câte cuvinte trebuie să știm dinainte pentru ca dicționarul să ne poată explica toate celelalte? "
     "În științele cognitive, aceasta este problema ancorării simbolurilor. Pentru dicționarele englezești a fost măsurată în 2016. "
     "Pentru română nu o măsurase nimeni.",
     "This is the question of the paper: how many words must we know in advance, so that the dictionary can explain all the others? "
     "In cognitive science this is the symbol grounding problem. It was measured for English dictionaries in 2016. "
     "Nobody had measured it for Romanian.",
     "Lasă întrebarea să stea pe ecran o secundă înainte să vorbești."),
    (4, "Every dictionary has a hidden core", "1:15",
     "Răspunsul are o formă. Dacă desenăm dicționarul ca o rețea și urmărim definițiile, apar straturi. "
     "La margine sunt cuvintele care nu definesc niciun alt cuvânt, ca arici sau topor: le putem învăța oricând, la sfârșit. "
     "Ce rămâne este nucleul, Kernel: cuvintele din care sunt definite toate celelalte, ca pom sau câine. "
     "Iar în centru este setul minim, MinSet: cel mai mic set de cuvinte pe care trebuie să le știm dinainte, ca apă, om, a fi. "
     "Spunem că structura e ascunsă pentru că nicio intrare din dicționar nu o arată; apare numai când citim toate definițiile împreună.",
     "The answer has a shape. If we draw the dictionary as a network and follow the definitions, layers appear. "
     "At the edge are words that define no other word, like arici ‘hedgehog’ or topor ‘axe’: we can always learn them last. "
     "What remains is the Kernel: the words from which all the others are defined, like pom ‘fruit tree’ or câine ‘dog’. "
     "At the centre is the MinSet: the smallest set of words we must know in advance, like apă ‘water’, om ‘man’, a fi ‘to be’. "
     "We call this structure hidden because no single entry shows it; it appears only when all definitions are read together.",
     "Mergi din exterior spre centru pe cercuri."),
    (5, "We read the whole DEX as a network", "1:00",
     "Ce am făcut: am luat toate definițiile DEX-ului, ediția a doua, singura pe care dexonline o distribuie integral, sub licență liberă. "
     "Peste 65 de mii de definiții au dat o rețea de peste 600 de mii de legături. "
     "Un sfert din formele din definiții sunt ambigue: sare poate fi substantiv sau verb. Un model de limbaj a ales lema potrivită; "
     "l-am verificat și am refăcut totul și fără el. Apoi am aplicat exact aceeași procedură pe dicționare din alte unsprezece limbi. "
     "Mărimea setului minim e foarte greu de calculat exact, așa că o încadrăm între două limite demonstrate matematic.",
     "We took every definition of the DEX, second edition, the only edition that dexonline distributes in full, under an open licence. "
     "More than 65,000 definitions gave a network of more than 600,000 links. "
     "A quarter of the word forms in definitions are ambiguous: sare can be a noun, ‘salt’, or a verb, ‘jumps’. A language model chose the right lemma; "
     "we checked it, and we recomputed everything without it. Then we applied exactly the same procedure to dictionaries of eleven other languages. "
     "The size of the MinSet is very hard to compute exactly, so we place it between two mathematically proven bounds.",
     "Treci de la stânga la dreapta pe cele trei cifre."),
    (6, "A third is Kernel. A tenth must be known first.", "0:50",
     "Primul rezultat. O treime din DEX este nucleu. Și aproape un cuvânt din zece trebuie știut dinainte: între 6.193 și 6.325 de cuvinte. "
     "În dicționarele englezești studiate înainte, nucleul are 7 până la 12 la sută, iar setul minim în jur de 1 la sută. "
     "Dar acolo procedura a fost alta, așa că am făcut comparația corect.",
     "First result. A third of the DEX is Kernel. And almost one word in ten must be known in advance: between 6,193 and 6,325 words. "
     "In the English dictionaries studied before, the Kernel is 7 to 12 percent and the MinSet about 1 percent. "
     "But they were processed differently, so we made a fair comparison.",
     "Pauză după fiecare cifră mare."),
    (7, "The DEX is about twice as circular", "1:15",
     "Iată comparația corectă, cu aceeași procedură pentru toate dicționarele. Comparăm cât din nucleu trebuie știut dinainte, "
     "pentru că această măsură nu depinde de mărimea dicționarului. În celelalte limbi: între 10 și 17 la sută. În DEX: 28. Aproape dublu. "
     "Nu este un efect al limbilor romanice: italiana, spaniola, portugheza și franceza au între 10 și 15. "
     "Și nu este un efect al tipului de dicționar: WordNet, care nu este un Wiktionary, are 14 la sută, iar DEX-ul trecut prin exact același program își păstrează valoarea.",
     "Here is the fair comparison, with the same procedure for every dictionary. We compare the share of the Kernel that must be known first, "
     "because it does not depend on the size of the dictionary. In the other languages: 10 to 17 percent. In the DEX: 28. Almost twice as much. "
     "It is not a Romance effect: Italian, Spanish, Portuguese and French have 10 to 15. "
     "And it is not the type of dictionary: WordNet, which is not a Wiktionary, has 14 percent, and the DEX run through exactly the same program keeps its value.",
     "Arată bara portocalie, apoi grupul limbilor romanice."),
    (8, "Words that define each other", "1:00",
     "De ce? Pentru că în DEX foarte multe cuvinte se definesc unul prin altul: 8.761 de perechi. Arbore și copac, amabil și binevoitor, primejdie și risc. "
     "În imagine, săgețile groase sunt astfel de perechi, în jurul cuvântului copac. Fiecare pereche e un cerc mic, deci unul dintre cele două cuvinte trebuie să fie în setul minim. "
     "Sunt mai ales sinonime. Nu sunt greșeli; definirea prin sinonim este o tehnică legitimă, dar are acest cost.",
     "Why? Because in the DEX very many words are defined by each other: 8,761 pairs. Arbore and copac, amabil and binevoitor, ‘kind’, primejdie and risc, ‘danger’ and ‘risk’. "
     "In the picture, the thick arrows are such pairs around the word copac. Each pair is a small circle, so one of its two words must be in the MinSet. "
     "Most of them are synonyms. They are not mistakes; defining by synonym is a legitimate technique, but it has this cost.",
     "Arată săgețile groase din rețea."),
    (9, "The core is linguistically real", "1:00",
     "Este acest nucleu real din punct de vedere lingvistic, sau doar un artefact matematic? Metoda nu a văzut nicio listă de cuvinte de bază; a folosit numai definițiile. "
     "Și totuși, în nucleu găsim 98 la sută din lista Swadesh, cele circa două sute de sensuri de bază folosite în lingvistica comparată, "
     "și 94,5 la sută din fondul principal lexical al lui Graur, din 1954. La întâmplare ne-am fi așteptat la 33 la sută.",
     "Is this core linguistically real, or only a mathematical artefact? The method never saw a list of basic words; it used the definitions alone. "
     "Yet the Kernel contains 98 percent of the Swadesh list, the two hundred or so basic meanings used in comparative linguistics, "
     "and 94.5 percent of Graur’s fundamental lexical stock, from 1954. By chance we would expect 33 percent.",
     "Accent pe „never saw these lists”."),
    (10, "Two cores in one dictionary", "0:50",
     "Nucleul are însă două fețe. Una este moștenită: cuvintele lui Graur, apă, om, casă, mână, foc, pâine, mai ales latinești și slave. "
     "Cealaltă este nucleul de lucru al dicționarului, cuvintele cu care sunt scrise definițiile: acțiune, rezultat, persoană, mai ales împrumuturi savante franceze. "
     "Un exemplu: Graur a lăsat cuvântul arbore în afara fondului principal; DEX-ul îl folosește în 157 de definiții, aproape de două ori mai des decât copac.",
     "But the Kernel has two faces. One is inherited: Graur’s words, apă, om, casă, mână, foc, pâine, mostly Latin and Slavic. "
     "The other is the working core of the dictionary, the words its definitions are written with: acțiune, rezultat, persoană, mostly learned French loanwords. "
     "One example: Graur left arbore out of the fundamental stock; the DEX uses it in 157 definitions, almost twice as often as copac.",
     "Stânga, apoi dreapta, apoi exemplul de jos."),
    (11, "What the results can be used for", "0:40",
     "La ce folosesc rezultatele? Lexicografilor: o listă de 8.761 de perechi care se definesc reciproc, de revizuit. "
     "Profesorilor: un vocabular de bază pentru predarea limbii române și pentru dicționarele pentru cursanți. "
     "Și tehnologiei limbajului: o rețea publică a definițiilor românești și un program care se poate aplica oricărui dicționar.",
     "What can the results be used for? For lexicographers: a list of 8,761 mutually defined pairs to review. "
     "For teachers: a core vocabulary for teaching Romanian and for learner’s dictionaries. "
     "For language technology: an open network of Romanian definitions, and a program that works on any dictionary.",
     "Trei puncte, fără grabă."),
    (12, "Take-home", "0:30",
     "Pe scurt: o treime din DEX este nucleu, iar un cuvânt din zece trebuie știut dinainte. "
     "Raportat la nucleu, DEX-ul este de două ori mai circular decât dicționarele altor unsprezece limbi, pentru că definește des prin sinonime. "
     "Și nucleul, găsit numai din definiții, conține aproape toată lista Swadesh. Datele și codul sunt publice. "
     "Mulțumim voluntarilor dexonline și vă mulțumesc pentru atenție.",
     "In short: a third of the DEX is Kernel, and one word in ten must be known in advance. "
     "Relative to its Kernel, the DEX is twice as circular as dictionaries of eleven other languages, because it often defines by synonyms. "
     "And the Kernel, found from definitions alone, contains almost the whole Swadesh list. The data and the code are public. "
     "We thank the dexonline volunteers, and thank you for your attention.",
     "Rămâi pe acest slide în timpul întrebărilor."),
]

QA = [
    ("De ce ediția a doua și nu DEX 2009 sau 2016?",
     "E singura ediție pe care dexonline o distribuie integral, sub licența GNU GPL. Edițiile ulterioare nu pot fi redistribuite, iar exportul public păstrează doar primele 23 de caractere din fiecare definiție. Programul nostru se poate aplica imediat unei ediții noi, dacă textul ei devine disponibil pentru cercetare. (Slide B1)",
     "Why the second edition and not DEX 2009 or 2016?",
     "It is the only edition that dexonline distributes in full, under the GNU GPL. The later editions cannot be redistributed, and the public dump keeps only the first 23 characters of each definition. Our program can be applied to a newer edition as soon as its text is available for research. (Slide B1)"),
    ("Wiktionary nu e un dicționar academic. Comparația e corectă?",
     "Aceleași reguli pentru toate dicționarele, o măsură care nu depinde de mărime și două controale: WordNet, care nu e Wiktionary, are 14%, în intervalul celorlalte; iar DEX-ul trecut prin exact același program își păstrează valoarea. DEX-ul e la 7,4 abateri standard de media celorlalte. (Slide B2)",
     "Wiktionary is not an academic dictionary. Is the comparison fair?",
     "Same rules for every dictionary, a measure that does not depend on size, and two controls: WordNet, which is not a Wiktionary, has 14%, within the range of the others; and the DEX run through exactly the same program keeps its value. The DEX lies 7.4 standard deviations above the mean of the others. (Slide B2)"),
    ("Cât ne putem baza pe modelul de limbaj?",
     "Are o sarcină îngustă: alege lema dintre candidați numerotați. Un model mai puternic e de acord în 87% din cazuri, iar majoritatea dezacordurilor sunt alegeri defensabile. Mai important, concluziile rămân aceleași fără niciun model, cu două reguli simple. (Slide B3)",
     "How far can we trust the language model?",
     "It does a narrow task: choosing the lemma among numbered candidates. A stronger model agrees in 87% of cases, and most disagreements are defensible choices. More importantly, the conclusions stay the same without any model, with two simple rules. (Slide B3)"),
    ("De ce numai primul sens?",
     "Așa au procedat și studiile pe dicționarele englezești, deci cifrele se pot compara. Analiza pe toate sensurile e următorul pas, pentru versiunea extinsă a lucrării.",
     "Why only the first sense?",
     "This is what the studies of English dictionaries did, so the figures can be compared. The analysis of all senses is the next step, for the extended version of the paper."),
    ("Ține de DEX sau de lexicografia românească în general?",
     "Nu putem încă decide. Wiktionary-ul românesc seamănă cu DEX-ul, dar copiază 70% din definiții din el. Avem nevoie de dicționare mai vechi, independente de DEX, ca Șăineanu sau Scriban; lucrăm cu dexonline în acest sens. (Slide B4)",
     "Is this the DEX, or Romanian lexicography in general?",
     "We cannot decide yet. The Romanian Wiktionary resembles the DEX, but 70% of its definitions are copied from it. We need older dictionaries independent of the DEX, such as Șăineanu or Scriban; we are working with dexonline on this. (Slide B4)"),
    ("Setul minim nu e unic. Ce înseamnă atunci „cuvintele din MinSet”?",
     "Mărimea setului minim e una singură; seturile de această mărime sunt multe. Noi analizăm unul dintre ele. Nucleul, în schimb, e unic, iar rezultatele despre vocabularul de bază se sprijină în primul rând pe el.",
     "The MinSet is not unique. What do ‘MinSet words’ mean?",
     "The size of the MinSet is unique; there are many sets of that size. We analyse one of them. The Kernel, in contrast, is unique, and the results on basic vocabulary rely mainly on it."),
    ("Ce legătură are cu felul în care învață copiii?",
     "Pentru engleză s-a arătat că nucleul conține cuvintele învățate mai devreme. Pentru română nu există încă norme de vârstă de achiziție la această scară, așa că nu am putut testa direct.",
     "What does this have to do with how children learn words?",
     "For English it has been shown that Kernel words are learned earlier. For Romanian there are no age-of-acquisition norms at this scale yet, so we could not test it directly."),
    ("Lista lui Graur e veche și scrisă într-un anumit context. De ce o folosiți?",
     "O tratăm ca pe o ipoteză istorică a unui expert, nu ca pe un etalon, exact cum o descria și Graur însuși. O comparăm și cu lista Swadesh, care e independentă de ea; ambele duc la aceeași concluzie.",
     "Graur’s list is old and written in a particular context. Why use it?",
     "We treat it as a historical expert hypothesis, not as a gold standard, as Graur himself described it. We also compare with the Swadesh list, which is independent of it; both lead to the same conclusion."),
    ("Orice dicționar e circular. Ce e nou?",
     "Da, orice dicționar e circular; întrebarea e cât. Noi am măsurat asta pentru prima dată pe un dicționar românesc întreg și am arătat, cu aceeași procedură, că DEX-ul e de circa două ori mai circular decât dicționarele altor unsprezece limbi, și de ce.",
     "Every dictionary is circular. What is new?",
     "Yes, every dictionary is circular; the question is how much. We measured it for the first time on a whole Romanian dictionary and showed, with the same procedure, that the DEX is about twice as circular as dictionaries of eleven other languages, and why."),
]
