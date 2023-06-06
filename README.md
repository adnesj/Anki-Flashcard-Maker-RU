# Anki-Flashcard-Maker-RU

A simple script I made to automatically create flashcards for anki by scraping necessary information from Wiktionary, Openrussian, and Bing images. Only works for russian so far, but it would be possible to adapt it to work for any language of your wish. There will be certain words it messes up for, or even crashes, due to inconsistencies in Wiktionary's HTML, which I have not yet bothered to account for, but for the large majority of words it should do whtat it is supposed to. Apologies for the incredibly messily written code, I am not a very good programmer yet.

Add the dictionary form of the words you want to make cards out of to the list at the end of main.py and run in your code editor. This will add a line to the text file russian_words_anki, which can then be imported into anki.

Main file is in main.py, and the setup of my anki cards for this to work in anki_card_template.txt.

Example output:  
отвечать;;[sound:отвечать.ogg] отвеча́ть | отве́тить [sound:ответить.ogg];[ɐtvʲɪˈt͡ɕætʲ];to answer;(отвеча́ю, отвеча́ет, отвеча́ют — отвеча́л, отвеча́ла, отвеча́ло — отвеча́й | отве́чу, отве́тит, отве́тят — отве́тил, отве́тила, отве́тило — отве́ть);[sound:отвечать_impf.mp3] Я отвечаю за его честность, потому что я его хорошо знаю.;I answer for his honesty, for I know him well.;[sound:отвечать_pf.mp3] Она не ответила на мой вопрос.;She made no response to my question.;Inherited from Proto-Slavic *otъvěťati. Synchronically as if from отве́тить (otvétitʹ) +‎ -а́ть (-átʹ).;en.wiktionary.org/wiki/отвечать/#Russian https://en.openrussian.org/ru/отвечать

How it looks in anki:  
![image](https://github.com/adnesj/Anki-Flashcard-Maker-RU/assets/92785260/55298bb3-d2a4-45e2-bc23-c8cb08fc130f)  
![image](https://github.com/adnesj/Anki-Flashcard-Maker-RU/assets/92785260/72be049c-a5a2-487e-a795-65401d60b93c)  
![image](https://github.com/adnesj/Anki-Flashcard-Maker-RU/assets/92785260/1aacd1d6-8933-4bc8-9bd6-e251d16f418d)

