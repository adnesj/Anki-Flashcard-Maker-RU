import os
import requests
from bs4 import BeautifulSoup
import bs4
import urllib.parse
import string
import re
import base64
from gtts import gTTS
from urllib.parse import urljoin
import shutil
from icrawler.builtin import GoogleImageCrawler

hdr= {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}

def handle_word(word):
    mnemonic = ""
    image = ""
    accented_word = ""
    trans = ""
    info = ""
    impf = ""
    impf_trans = ""
    pf = ""
    pf_trans = ""
    etymology = ""
    links = ""
    english_definition = ""
    pronunciation = ""
    wiktionary = f'en.wiktionary.org/wiki/{word}/#Russian'
    anki_formatted = f'{mnemonic};{image};{accented_word};{pronunciation};{trans};{info};{impf};{impf_trans};{pf};{pf_trans};{etymology};{links}'
    
    
    url = f'https://en.wiktionary.org/wiki/{word}#Russian'  # Replace with the actual URL
    # Send an HTTP GET request to the website
    response = requests.get(url, headers=hdr)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the HTML content from the response
        content = response.content
        # Create a BeautifulSoup object with the HTML content
        soup = BeautifulSoup(content, "lxml")
        if soup.find("span", id="Russian"):
            russian_section = soup.find("span", id="Russian")
            h2_element = russian_section.find_parent("h2")
            next_h3 = h2_element.find_next_sibling("h3")
        else:
            print(f'[!] Russian Wiktionary page for "{word}" not found. Creating card with all other fields empty.')
            print(f";;{word};;;;;;;;;")
            return

        while next_h3: # Finds part of speech
            if next_h3.find("span", string=lambda text: text and text.lower() in ["verb", "noun", "adjective", "adverb", "interjection", "postposition", "preposition", "pronoun", "conjunction", "proper noun"]):
                part_of_speech = next_h3.text.replace("[edit]", "")
                break
            next_h3 = next_h3.find_next_sibling("h3")
        else: part_of_speech = False
        if not part_of_speech: # If POS is not in an h3 it might be in an h4
            next_h4 = h2_element.find_next_sibling("h4")
            while next_h4: # Finds part of speech
                if next_h4.find("span", string=lambda text: text and text.lower() in ["verb", "noun", "adjective", "adverb", "interjection", "postposition", "preposition", "pronoun", "conjunction", "proper noun"]):
                    part_of_speech = next_h4.text.replace("[edit]", "")
                    break
                next_h4 = next_h4.find_next_sibling("h4")
        
        if soup.find("a", title="Appendix:Russian pronunciation"):
            a_tag = soup.find("a", title="Appendix:Russian pronunciation")

            # Find the parent of the <a> tag and the next neighbor <span> with class "IPA"
            parent = a_tag.parent
            if parent.find_next_sibling("span", class_="IPA"):
                span_tag = parent.find_next_sibling("span", class_="IPA")

                # Extract the text of the <span> tag
                pronunciation = span_tag.get_text(strip=True)
        if part_of_speech:
            if part_of_speech == "Verb": # Wiktionary part done as far as I can tell, rest still yet to do
                accented_impf = ""
                accented_pf = ""
                if soup.find("i", string="imperfective"): # Handles perfective verb case — gamlen, funkatj på выходить
                    # Handle perfective verb case
                    #! Switch to wiktionary page of impf verb
                    accented_pf = soup.find("strong", class_="Cyrl headword", lang="ru")
                    accented_impf = accented_pf.find_next("a", title=True).find_next("a", title=True)
                    word = accented_impf.text.replace("́", "")
                    handle_word(word)
                elif soup.find("i", string="perfective"): # Handles imperfective verb case
                    accented_impf = soup.find("strong", class_="Cyrl headword", lang="ru")
                    accented_pf = accented_impf.find_next("a", title=True).find_next("a", title=True)
                    
                    # Find the preceding <p> elementµ
                    preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
                    # Find the <ol> element only if the preceding <p> element is found
                    if preceding_p:
                        ol_element = preceding_p.find_next_sibling("ol")
                        if ol_element:
                            english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title)
                    if not english_definition:
                        print("No English definition found.")
                        
                    # Find the preceding <p> element with the etymology
                    etymology_header = russian_section.find_parent("h2").find_next_sibling("h3")
                    if etymology_header: # Finds etymology
                        etymology = etymology_header.find_next_sibling("p").text.replace(";", ":")
                      
                    impf_present_1s = soup.select_one('span[class^="Cyrl form-of lang-ru 1|s|pres|ind-form-of"]').find('a').text
                    impf_present_3s = soup.select_one('span[class^="Cyrl form-of lang-ru 3|s|pres|ind-form-of"]').find('a').text
                    impf_present_3p = soup.select_one('span[class^="Cyrl form-of lang-ru 3|p|pres|ind-form-of"]').find('a').text
                    impf_past_ms = soup.select_one('span[class^="Cyrl form-of lang-ru m|s|past|ind-form-of"]').find('a').text
                    impf_past_fs = soup.select_one('span[class^="Cyrl form-of lang-ru f|s|past|ind-form-of"]').find('a').text  
                    impf_past_ns = soup.select_one('span[class^="Cyrl form-of lang-ru n|s|past|ind-form-of"]').find('a').text
                    if soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('a'):
                        impf_imperative = soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('a').text
                    else: impf_imperative = soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('strong').text
                    pf_present_1s = ""
                    pf_present_3s = ""
                    pf_present_3p = ""
                    pf_past_ms = ""
                    pf_past_fs = ""
                    pf_past_ns = ""
                    pf_imperative = ""
                    pf_word = accented_pf.text.replace("́", "")
                    
                    # Fetch sentence and translation from Openrussian
                    url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                    # Send an HTTP GET request to the website
                    response = requests.get(url)
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Get the HTML content from the response
                        content = response.content
                        # Create a BeautifulSoup object with the HTML content
                        soup = BeautifulSoup(content, "lxml")
                        if soup.find("div", class_="section sentences"):
                            impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                            impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                    
                    url = f'https://en.wiktionary.org/wiki/{pf_word}#Russian'  # Replace with the actual URL
                    # Send an HTTP GET request to the website
                    response = requests.get(url)
                    if response.status_code == 200: # Move to the perfective verb's site
                        # Get the HTML content from the response
                        # Create a BeautifulSoup object with the HTML content
                        
                        content = response.content
                        soup = BeautifulSoup(content, "lxml")
                        pf_present_1s = soup.select_one('span[class^="Cyrl form-of lang-ru 1|s|fut|ind-form-of"]').find('a').text
                        pf_present_3s = soup.select_one('span[class^="Cyrl form-of lang-ru 3|s|fut|ind-form-of"]').find('a').text
                        pf_present_3p = soup.select_one('span[class^="Cyrl form-of lang-ru 3|p|fut|ind-form-of"]').find('a').text
                        pf_past_ms = soup.select_one('span[class^="Cyrl form-of lang-ru m|s|past|ind-form-of"]').find('a').text
                        pf_past_fs = soup.select_one('span[class^="Cyrl form-of lang-ru f|s|past|ind-form-of"]').find('a').text  
                        pf_past_ns = soup.select_one('span[class^="Cyrl form-of lang-ru n|s|past|ind-form-of"]').find('a').text
                        if soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('a'):
                            pf_imperative = soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('a').text
                        else: pf_imperative = soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of"]').find('strong').text
                        
                        # Fetch sentence and translation from Openrussian
                        url = f'https://en.openrussian.org/ru/{pf_word}'  # Replace with the actual URL
                        # Send an HTTP GET request to the website
                        response = requests.get(url)
                        # Check if the request was successful
                        if response.status_code == 200:
                            # Get the HTML content from the response
                            content = response.content
                            # Create a BeautifulSoup object with the HTML content
                            soup = BeautifulSoup(content, "lxml")
                            if soup.find("div", class_="section sentences"):
                                pf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "")
                                pf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text
                        
                            # Start of finding impf audio
                            if True:
                                url = f"https://en.wiktionary.org/wiki/{word}"
                                response = requests.get(url)
                                soup = BeautifulSoup(response.content, "html.parser")
                                audio_player = soup.find("table", class_="audiotable")
                                if audio_player: # Rest of finding wikt audio
                                    # Extract the audio URL
                                    audio_url = audio_player.find("source")["src"]

                                    if audio_url.startswith("//"):
                                        audio_url = "https:" + audio_url

                                    # Send an HTTP GET request to the audio URL
                                    headers = {
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                                    }
                                    audio_response = requests.get(audio_url, headers=headers)

                                    # Determine the file extension from the Content-Type header
                                    content_type = audio_response.headers.get("Content-Type")
                                    extension = audio_url[-3:]

                                    # Decode the URL-encoded filename
                                    decoded_word = urllib.parse.unquote(word)

                                        
                                    # Save the audio file to the specified filepath
                                    word_audio_filename = f'{decoded_word}.{extension}'
                                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                                    with open(filepath, "wb") as file:
                                        file.write(audio_response.content)
                                    
                                    # Print the absolute path of the saved file
                                    abs_path = os.path.abspath(filepath)
                                else: # Safe case generates TTS
                                    decoded_word = word
                                    # Generate TTS audio using gTTS
                                    tts = gTTS(text=word, lang="ru")
                                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                                    word_audio_filename = f'{decoded_word}.mp3'
                                    tts.save(filepath)
                                    abs_path = os.path.abspath(filepath)
                            
                            # Start of finding pf audio
                            if True:
                                url = f"https://en.wiktionary.org/wiki/{pf_word}"
                                response = requests.get(url)
                                soup = BeautifulSoup(response.content, "html.parser")
                                audio_player = soup.find("table", class_="audiotable")
                                if audio_player: # Rest of finding wikt audio
                                    # Extract the audio URL
                                    audio_url = audio_player.find("source")["src"]

                                    if audio_url.startswith("//"):
                                        audio_url = "https:" + audio_url

                                    # Send an HTTP GET request to the audio URL
                                    headers = {
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                                    }
                                    audio_response = requests.get(audio_url, headers=headers)

                                    # Determine the file extension from the Content-Type header
                                    content_type = audio_response.headers.get("Content-Type")
                                    extension = audio_url[-3:]

                                    # Decode the URL-encoded filename
                                    decoded_word = urllib.parse.unquote(pf_word)
                                        
                                    # Save the audio file to the specified filepath
                                    pf_word_audio_filename = f'{decoded_word}.{extension}'
                                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                                    with open(filepath, "wb") as file:
                                        file.write(audio_response.content)
                                    
                                    # Print the absolute path of the saved file
                                    abs_path = os.path.abspath(filepath)
                                else: # Safe case generates TTS
                                    decoded_word = word
                                    # Generate TTS audio using gTTS
                                    tts = gTTS(text=pf_word, lang="ru")
                                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{pf_word}.mp3")
                                    pf_word_audio_filename = f'{decoded_word}.mp3'
                                    tts.save(filepath)
                                    abs_path = os.path.abspath(filepath)
                        
                            
                            if impf != "": # TTS for impf sentence
                                tts = gTTS(text=impf, lang="ru")
                                filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                                impf_audio_filename = f'{word}_impf.mp3'
                                tts.save(filepath)
                                abs_path = os.path.abspath(filepath)
                            else: impf_audio_filename = ""
                            
                            if pf != "": # TTS for pf sentence
                                tts = gTTS(text=pf, lang="ru")
                                filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_pf.mp3")
                                pf_audio_filename = f'{word}_pf.mp3'
                                tts.save(filepath)
                                abs_path = os.path.abspath(filepath)
                            else: pf_audio_filename = ""
                            
                            # Start of finding image
                            url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                            image = ""
                            # Send an HTTP GET request to the website
                            response = requests.get(url, headers=hdr)
                            # Check if the request was successful
                            if response.status_code == 200:
                                # Get the HTML content from the response
                                content = response.content
                                # Create a BeautifulSoup object with the HTML content
                                soup = BeautifulSoup(content, "lxml")
                                if soup.find("img", class_="mimg"):
                                    image_url = soup.find("img", class_="mimg")["src"]
                                    image_response = requests.get(image_url)
                                    # Save the audio file to the specified filepath
                                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                                    image = f'{word}.jpg'
                                    with open(filepath, "wb") as file:
                                        file.write(image_response.content)  
                                else:
                                    print(f"Image for {word} couldn't be retrieved ")

                            url = f'https://en.openrussian.org/ru/{word}'
                        
                        accented_word = f'{accented_impf.text} | {accented_pf.text}'
                        info = f'({impf_present_1s}, {impf_present_3s}, {impf_present_3p} — {impf_past_ms}, {impf_past_fs}, {impf_past_ns} — {impf_imperative} | {pf_present_1s}, {pf_present_3s}, {pf_present_3p} — {pf_past_ms}, {pf_past_fs}, {pf_past_ns} — {pf_imperative})'
                        anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word} [sound:{pf_word_audio_filename}];{pronunciation};to {english_definition.text};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};[sound:{pf_audio_filename}] {pf};{pf_trans};{etymology};{wiktionary} {url}'
                        
                        anki_formatted = anki_formatted.replace('\n', '')
                        
                        #anki_formatted = f'{mnemonic};{image};{accented_impf.text} | {accented_pf.text};to {english_definition.text};;{impf};{impf_trans};{pf};{pf_trans};{etymology};{url};;'
                        
                        
                        file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                        new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare

                        # Read the existing lines from the file
                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()

                        # Check if the new line already exists
                        if any(new_line == line.split(';')[0] for line in lines):
                            print(f"[!] {word} already exists in the file, skipping.")
                        else:
                            # Append the new line to the file
                            with open(file_path, 'a', encoding='utf-8') as file:
                                file.write(anki_formatted + '\n')
                                print(anki_formatted)                       
                    else: # Safe-fix if website does not respond, means wiktionary does not have a page for the perfective verb
                        print(f'[!] Imperfective wiktionary page for "{word}" does not exist.')
                        
                        # Start of finding impf audio
                        if True:
                            url = f"https://en.wiktionary.org/wiki/{word}"
                            response = requests.get(url)
                            soup = BeautifulSoup(response.content, "html.parser")
                            audio_player = soup.find("table", class_="audiotable")
                            if audio_player: # Rest of finding wikt audio
                                # Extract the audio URL
                                audio_url = audio_player.find("source")["src"]

                                if audio_url.startswith("//"):
                                    audio_url = "https:" + audio_url

                                # Send an HTTP GET request to the audio URL
                                headers = {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                                }
                                audio_response = requests.get(audio_url, headers=headers)

                                # Determine the file extension from the Content-Type header
                                content_type = audio_response.headers.get("Content-Type")
                                extension = audio_url[-3:]

                                # Decode the URL-encoded filename
                                decoded_word = urllib.parse.unquote(word)

                                    
                                # Save the audio file to the specified filepath
                                word_audio_filename = f'{decoded_word}.{extension}'
                                filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                                with open(filepath, "wb") as file:
                                    file.write(audio_response.content)
                                
                                # Print the absolute path of the saved file
                                abs_path = os.path.abspath(filepath)
                            else: # Safe case generates TTS
                                # Generate TTS audio using gTTS
                                tts = gTTS(text=word, lang="ru")
                                filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                                word_audio_filename = f'{word}.mp3'
                                tts.save(filepath)
                                abs_path = os.path.abspath(filepath)
                        
                        # Fetch sentence and translation from Openrussian
                        url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                        # Send an HTTP GET request to the website
                        response = requests.get(url)
                        # Check if the request was successful
                        if response.status_code == 200:
                            # Get the HTML content from the response
                            content = response.content
                            # Create a BeautifulSoup object with the HTML content
                            soup = BeautifulSoup(content, "lxml")
                            if soup.find("div", class_="section sentences"):
                                impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                                impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                        
                        if impf != "": # TTS for impf sentence
                            tts = gTTS(text=impf, lang="ru")
                            filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                            impf_audio_filename = f'{word}_impf.mp3'
                            tts.save(filepath)
                            abs_path = os.path.abspath(filepath)
                        else: impf_audio_filename = ""
                        
                        if impf != "": # TTS for pf verb
                            tts = gTTS(text=accented_pf.text.replace("́", ""), lang="ru")
                            filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                            pf_audio_filename = f'{accented_pf.text.replace("́", "")}_impf.mp3'
                            tts.save(filepath)
                            abs_path = os.path.abspath(filepath)
                        else: pf_audio_filename = ""
                        
                        # Start of finding image
                        url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                        image = ""
                        # Send an HTTP GET request to the website
                        response = requests.get(url, headers=hdr)
                        # Check if the request was successful
                        if response.status_code == 200:
                            # Get the HTML content from the response
                            content = response.content
                            # Create a BeautifulSoup object with the HTML content
                            soup = BeautifulSoup(content, "lxml")
                            if soup.find("img", class_="mimg"):
                                image_url = soup.find("img", class_="mimg")["src"]
                                image_response = requests.get(image_url)
                                # Save the audio file to the specified filepath
                                filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                                image = f'{word}.jpg'
                                with open(filepath, "wb") as file:
                                    file.write(image_response.content)  
                            else:
                                print(f"Image for {word} couldn't be retrieved ")
                        
                        accented_word = f'{accented_impf.text} | {accented_pf.text}'
                        info = f'({impf_present_1s}, {impf_present_3s}, {impf_present_3p} — {impf_past_ms}, {impf_past_fs}, {impf_past_ns} — {impf_imperative} | {pf_present_1s}, {pf_present_3s}, {pf_present_3p} — {pf_past_ms}, {pf_past_fs}, {pf_past_ns} — {pf_imperative})'
                        anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word} [sound:{pf_audio_filename}];{pronunciation};to {english_definition.text};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};{pf};{pf_trans};{etymology};{wiktionary} {url}'
                        anki_formatted = anki_formatted.replace('\n', '')
                        file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                        
                        file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                        new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare

                        # Read the existing lines from the file
                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()

                        # Check if the new line already exists
                        if any(new_line == line.split(';')[0] for line in lines):
                            print(f"[!] {word} already exists in the file, skipping.")
                        else:
                            # Append the new line to the file
                            with open(file_path, 'a', encoding='utf-8') as file:
                                file.write(anki_formatted + '\n')
                                print(anki_formatted)
                else: # Handles the case if aspect partner is not found
                    # Find the preceding <p> element
                    preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
                    # Find the <ol> element only if the preceding <p> element is found
                    if preceding_p:
                        ol_element = preceding_p.find_next_sibling("ol")
                        if ol_element:
                            english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title)
                        else:
                            print("No <ol> element found after the preceding <p> element.")
                    else:
                        print("Preceding <p> element not found.")
                    if not english_definition:
                        print("No English definition found.")
                    accented_impf = soup.find("strong", class_="Cyrl headword", lang="ru")
                    impf_present_1s = soup.select_one('span[class^="Cyrl form-of lang-ru 1|s|pres|ind-form-of origin-"]').find('a').text
                    impf_present_3s = soup.select_one('span[class^="Cyrl form-of lang-ru 3|s|pres|ind-form-of origin-"]').find('a').text
                    impf_present_3p = soup.select_one('span[class^="Cyrl form-of lang-ru 3|p|pres|ind-form-of origin-"]').find('a').text
                    impf_past_ms = soup.select_one('span[class^="Cyrl form-of lang-ru m|s|past|ind-form-of origin-"]').find('a').text
                    impf_past_fs = soup.select_one('span[class^="Cyrl form-of lang-ru f|s|past|ind-form-of origin-"]').find('a').text  
                    impf_past_ns = soup.select_one('span[class^="Cyrl form-of lang-ru n|s|past|ind-form-of origin-"]').find('a').text
                    impf_imperative = soup.select_one('span[class^="Cyrl form-of lang-ru 2|s|imp-form-of origin-"]').find('a').text
                    
                    # Fetch sentence and translation from Openrussian
                    url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                    # Send an HTTP GET request to the website
                    response = requests.get(url)
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Get the HTML content from the response
                        content = response.content
                        # Create a BeautifulSoup object with the HTML content
                        soup = BeautifulSoup(content, "lxml")
                        if soup.find("div", class_="section sentences"):
                            impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                            impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                    
                        # Start of finding audio
                    url = f"https://en.wiktionary.org/wiki/{word}"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, "html.parser")
                    audio_player = soup.find("table", class_="audiotable")
                    if audio_player: # Rest of finding wikt audio
                        # Extract the audio URL
                        audio_url = audio_player.find("source")["src"]

                        if audio_url.startswith("//"):
                            audio_url = "https:" + audio_url

                        # Send an HTTP GET request to the audio URL
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                        }
                        audio_response = requests.get(audio_url, headers=headers)

                        # Determine the file extension from the Content-Type header
                        content_type = audio_response.headers.get("Content-Type")
                        extension = audio_url[-3:]

                        # Decode the URL-encoded filename
                        decoded_word = urllib.parse.unquote(word)
                            
                        # Save the audio file to the specified filepath
                        word_audio_filename = f'{decoded_word}.{extension}'
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                        with open(filepath, "wb") as file:
                            file.write(audio_response.content)
                        
                        # Print the absolute path of the saved file
                        abs_path = os.path.abspath(filepath)
                    else: # Safe case generates TTS
                        decoded_word = word
                        # Generate TTS audio using gTTS
                        tts = gTTS(text=word, lang="ru")
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                        word_audio_filename = f'{decoded_word}.mp3'
                        tts.save(filepath)
                        abs_path = os.path.abspath(filepath)
                    
                    if impf != "": # TTS for impf sentence
                        tts = gTTS(text=impf, lang="ru")
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                        impf_audio_filename = f'{word}_impf.mp3'
                        tts.save(filepath)
                        abs_path = os.path.abspath(filepath)
                    else: impf_audio_filename = ""
                    
                    # Start of finding image
                    url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                    image = ""
                    # Send an HTTP GET request to the website
                    response = requests.get(url, headers=hdr)
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Get the HTML content from the response
                        content = response.content
                        # Create a BeautifulSoup object with the HTML content
                        soup = BeautifulSoup(content, "lxml")
                        if soup.find("img", class_="mimg"):
                            image_url = soup.find("img", class_="mimg")["src"]
                            image_response = requests.get(image_url)
                            # Save the audio file to the specified filepath
                            filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                            image = f'{word}.jpg'
                            with open(filepath, "wb") as file:
                                file.write(image_response.content)  
                        else:
                            print(f"Image for {word} couldn't be retrieved ")

                    url = f'https://en.openrussian.org/ru/{word}'
                    
                    accented_word = accented_impf.text
                    info = f'({impf_present_1s}, {impf_present_3s}, {impf_present_3p} — {impf_past_ms}, {impf_past_fs}, {impf_past_ns} — {impf_imperative})'
                    anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word};{pronunciation};to {english_definition.text};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};{pf};{pf_trans};{etymology};{wiktionary} {url}'
                    anki_formatted = anki_formatted.replace('\n', '')
                    file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                    new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare

                    # Read the existing lines from the file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()

                    # Check if the new line already exists
                    if any(new_line == line.split(';')[0] for line in lines):
                        print(f"[!] {word} already exists in the file, skipping.")
                    else:
                        # Append the new line to the file
                        with open(file_path, 'a', encoding='utf-8') as file:
                            file.write(anki_formatted + '\n')
                            print(anki_formatted)
                    
                    file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(anki_formatted + '\n')
            elif part_of_speech == "Noun" or part_of_speech == "Proper noun":
                accented_word = soup.find("strong", class_="Cyrl headword", lang="ru").text
                
                # Find the preceding <p> element with the etymology
                etymology_header = russian_section.find_parent("h2").find_next_sibling("h3")
                if etymology_header: # Finds etymology
                    etymology = etymology_header.find_next_sibling("p").text.replace(";", ":")
                
                preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
                if preceding_p: # Finds english definition
                    ol_element = preceding_p.find_next_sibling("ol")
                    if ol_element:
                        english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title).text
                    else:
                        print("No <ol> element found after the preceding <p> element.")
                else: # Safe case
                    print("Preceding <p> element not found.")
                if not english_definition: # Safe case
                    print("No English definition found.")
                
                if preceding_p.find("span", class_="gender"):
                    gender_animacy = preceding_p.find("span", class_="gender").text
                else: gender_animacy = None
                if soup.select_one('span[class^="Cyrl form-of lang-ru nom|p-form-of "]'):
                    nom_pl = soup.select_one('span[class^="Cyrl form-of lang-ru nom|p-form-of "]').text
                    if soup.select_one('span[class^="Cyrl form-of lang-ru acc|p-form-of"]'): # Some nouns can be either anim or inan, affecting the acc form
                        acc_sg = soup.select_one('span[class^="Cyrl form-of lang-ru acc|s-form-of "]').text
                    else: acc_sg = "Np or Gp"
                    if soup.select_one('span[class^="Cyrl form-of lang-ru acc|p-form-of "]'): # Some nouns can be either anim or inan, affecting the acc form
                        acc_pl = soup.select_one('span[class^="Cyrl form-of lang-ru acc|p-form-of o"]').text
                    else: acc_pl = "Np or Gp"
                    gen_sg = soup.select_one('span[class^="Cyrl form-of lang-ru gen|s-form-of "]').text
                    gen_pl = soup.select_one('span[class^="Cyrl form-of lang-ru gen|p-form-of "]').text
                    ins_sg = soup.select_one('span[class^="Cyrl form-of lang-ru ins|s-form-of "]').text
                    ins_pl = soup.select_one('span[class^="Cyrl form-of lang-ru ins|p-form-of "]').text
                    info = f'{gender_animacy}, N:{accented_word}-{nom_pl}, A:{acc_sg}-{acc_pl}, G:{gen_sg}-{gen_pl}, I:{ins_sg}-{ins_pl}'
                else:
                    info = f'{gender_animacy}, indeclinable noun or sg only'

                # Fetch sentence and translation from Openrussian
                url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                # Send an HTTP GET request to the website
                response = requests.get(url)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("div", class_="section sentences"):
                        impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                        impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                        
                vowels = ['a', 'e', 'i', 'o', 'u']
                uppercase_letters = [chr(letter) for letter in range(ord('A'), ord('Z')+1)]
                if english_definition[0].lower() == 'u'  and english_definition[1].lower() not in vowels and english_definition[2].lower() in vowels: article = "a"
                elif english_definition[0].lower() == 'e'  and english_definition[1].lower() == 'u': article = 'a'
                elif english_definition[0] == 'u' and english_definition[0] in uppercase_letters and english_definition[1] in uppercase_letters: article = 'a'
                elif english_definition[0].lower() == 'y'  and english_definition[1].lower() not in vowels: article = 'an'
                elif english_definition[0].lower() in vowels: article = "an"
                else: article = "a"
                
                # Start of finding audio
                url = f"https://en.wiktionary.org/wiki/{word}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                audio_player = soup.find("table", class_="audiotable")
                if audio_player: # Rest of finding wikt audio
                    # Extract the audio URL
                    audio_url = audio_player.find("source")["src"]

                    if audio_url.startswith("//"):
                        audio_url = "https:" + audio_url

                    # Send an HTTP GET request to the audio URL
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                    }
                    audio_response = requests.get(audio_url, headers=headers)

                    # Determine the file extension from the Content-Type header
                    content_type = audio_response.headers.get("Content-Type")
                    extension = audio_url[-3:]

                    # Decode the URL-encoded filename
                    decoded_word = urllib.parse.unquote(word)
                        
                    # Save the audio file to the specified filepath
                    word_audio_filename = f'{decoded_word}.{extension}'
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                    with open(filepath, "wb") as file:
                        file.write(audio_response.content)
                    
                    # Print the absolute path of the saved file
                    abs_path = os.path.abspath(filepath)
                else: # Safe case generates TTS
                    decoded_word = word
                    # Generate TTS audio using gTTS
                    tts = gTTS(text=word, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                    word_audio_filename = f'{decoded_word}.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                
                if impf != "": # TTS for impf sentence
                    tts = gTTS(text=impf, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                    impf_audio_filename = f'{word}_impf.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                else: impf_audio_filename = ""
                
                # Start of finding image
                url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                image = ""
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("img", class_="mimg"):
                        image_url = soup.find("img", class_="mimg")["src"]
                        image_response = requests.get(image_url)
                        # Save the audio file to the specified filepath
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                        image = f'{word}.jpg'
                        with open(filepath, "wb") as file:
                            file.write(image_response.content)  
                    else:
                        print(f"Image for {word} couldn't be retrieved ")

                url = f'https://en.openrussian.org/ru/{word}'
                
                anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word};{pronunciation};{article} {english_definition};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};{pf};{pf_trans};{etymology};{wiktionary} {url}'
                anki_formatted = anki_formatted.replace('\n', '')
                file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare
                # Read the existing lines from the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                # Check if the new line already exists
                if any(new_line == line.split(';')[0] for line in lines):
                    print(f"[!] {word} already exists in the file, skipping.")
                else:
                    # Append the new line to the file
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(anki_formatted + '\n')
                        print(anki_formatted)
            elif part_of_speech == "Adjective":
                accented_word = soup.find("strong", class_="Cyrl headword", lang="ru").text
                
                # Find the preceding <p> element with the etymology
                etymology_header = russian_section.find_parent("h2").find_next_sibling("h3")
                if etymology_header: # Finds etymology
                    etymology = etymology_header.find_next_sibling("p").text.replace(";", ":")
                
                preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
                if preceding_p: # Finds english definition
                    ol_element = preceding_p.find_next_sibling("ol")
                    if ol_element:
                        english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title).text
                    else:
                        print("No <ol> element found after the preceding <p> element.")
                else: # Safe case
                    print("Preceding <p> element not found.")
                if not english_definition: # Safe case
                    print("No English definition found.")
                
                if soup.select_one('span[class^="Cyrl form-of lang-ru short|m"]'):
                    short_m = soup.select_one('span[class^="Cyrl form-of lang-ru short|m"]').text
                    short_f = soup.select_one('span[class^="Cyrl form-of lang-ru short|f"]').text
                    short_n = soup.select_one('span[class^="Cyrl form-of lang-ru short|n"]').text
                    info = f'{short_m}, {short_f}, {short_n}'
                else: 
                    short_m ="No short forms"
                    short_f = ""
                    short_n = ""
                    info = "No short forms"
                
                # Fetch sentence and translation from Openrussian
                url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("div", class_="section sentences"):
                        impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                        impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                
                # Start of finding audio
                url = f"https://en.wiktionary.org/wiki/{word}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                audio_player = soup.find("table", class_="audiotable")
                if audio_player: # Rest of finding wikt audio
                    # Extract the audio URL
                    audio_url = audio_player.find("source")["src"]

                    if audio_url.startswith("//"):
                        audio_url = "https:" + audio_url

                    # Send an HTTP GET request to the audio URL
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                    }
                    audio_response = requests.get(audio_url, headers=headers)

                    # Determine the file extension from the Content-Type header
                    content_type = audio_response.headers.get("Content-Type")
                    extension = audio_url[-3:]

                    # Decode the URL-encoded filename
                    decoded_word = urllib.parse.unquote(word)
                        
                    # Save the audio file to the specified filepath
                    word_audio_filename = f'{decoded_word}.{extension}'
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                    with open(filepath, "wb") as file:
                        file.write(audio_response.content)
                    
                    # Print the absolute path of the saved file
                    abs_path = os.path.abspath(filepath)
                else: # Safe case generates TTS
                    decoded_word = word
                    # Generate TTS audio using gTTS
                    tts = gTTS(text=word, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                    word_audio_filename = f'{decoded_word}.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                
                if impf != "": # TTS for impf sentence
                    tts = gTTS(text=impf, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                    impf_audio_filename = f'{word}_impf.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                else: impf_audio_filename = ""
                
                # Start of finding image
                url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                image = ""
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("img", class_="mimg"):
                        image_url = soup.find("img", class_="mimg")["src"]
                        image_response = requests.get(image_url)
                        # Save the audio file to the specified filepath
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                        image = f'{word}.jpg'
                        with open(filepath, "wb") as file:
                            file.write(image_response.content)  
                    else:
                        print(f"Image for {word} couldn't be retrieved ")

                url = f'https://en.openrussian.org/ru/{word}' 
                
                anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word};{pronunciation};{english_definition};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};{pf};{pf_trans};{etymology};{wiktionary} {url}'
                anki_formatted = anki_formatted.replace('\n', '')
                file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare
                # Read the existing lines from the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                # Check if the new line already exists
                if any(new_line == line.split(';')[0] for line in lines):
                    print(f"[!] {word} already exists in the file, skipping.")
                else:
                    # Append the new line to the file
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(anki_formatted + '\n')
                        print(anki_formatted)
            else: # Handles all other parts of speech
                accented_word = soup.find("strong", class_="Cyrl headword", lang="ru").text
                
                # Find the preceding <p> element with the etymology
                etymology_header = russian_section.find_parent("h2").find_next_sibling("h3")
                if etymology_header: # Finds etymology
                    etymology = etymology_header.find_next_sibling("p").text.replace(";", ":")
                
                preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
                if preceding_p: # Finds english definition
                    ol_element = preceding_p.find_next_sibling("ol")
                    if ol_element:
                        english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title).text
                if not english_definition: # Safe case
                    print("[!] No English definition found.")
                
                # Fetch sentence and translation from Openrussian
                url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200: # Openrussian sentence scraper
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("div", class_="section sentences"):
                        impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                        impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                
                # Start of finding audio
                url = f"https://en.wiktionary.org/wiki/{word}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                audio_player = soup.find("table", class_="audiotable")
                if audio_player: # Rest of finding wikt audio
                    # Extract the audio URL
                    audio_url = audio_player.find("source")["src"]

                    if audio_url.startswith("//"):
                        audio_url = "https:" + audio_url

                    # Send an HTTP GET request to the audio URL
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                    }
                    audio_response = requests.get(audio_url, headers=headers)

                    # Determine the file extension from the Content-Type header
                    content_type = audio_response.headers.get("Content-Type")
                    extension = audio_url[-3:]

                    # Decode the URL-encoded filename
                    decoded_word = urllib.parse.unquote(word)
                        
                    # Save the audio file to the specified filepath
                    word_audio_filename = f'{decoded_word}.{extension}'
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                    with open(filepath, "wb") as file:
                        file.write(audio_response.content)
                    
                    # Print the absolute path of the saved file
                    abs_path = os.path.abspath(filepath)
                else: # Safe case generates TTS
                    decoded_word = word
                    # Generate TTS audio using gTTS
                    tts = gTTS(text=word, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                    word_audio_filename = f'{decoded_word}.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                
                if impf != "": # TTS for impf sentence
                    tts = gTTS(text=impf, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                    impf_audio_filename = f'{word}_impf.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                else: impf_audio_filename = ""
                
                # Start of finding image
                url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                image = ""
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("img", class_="mimg"):
                        image_url = soup.find("img", class_="mimg")["src"]
                        image_response = requests.get(image_url)
                        # Save the audio file to the specified filepath
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                        image = f'{word}.jpg'
                        with open(filepath, "wb") as file:
                            file.write(image_response.content)  
                    else:
                        print(f"Image for {word} couldn't be retrieved ")

                url = f'https://en.openrussian.org/ru/{word}' 
                
                anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word};{pronunciation};{english_definition};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};;;{etymology};{wiktionary} {url}'
                anki_formatted = anki_formatted.replace('\n', '')
                file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
                new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare
                # Read the existing lines from the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                # Check if the new line already exists
                if any(new_line == line.split(';')[0] for line in lines):
                    print(f"[!] {word} already exists in the file, skipping.")
                else:
                    # Append the new line to the file
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(anki_formatted + '\n')
                        print(anki_formatted)
        else:
            print(f'[!] POS for "{word}" is not listed in script. Creating card with all other fields empty.')
            accented_word = soup.find("strong", class_="Cyrl headword", lang="ru").text
            
            # Find the preceding <p> element with the etymology
            etymology_header = russian_section.find_parent("h2").find_next_sibling("h3")
            if etymology_header: # Finds etymology
                etymology = etymology_header.find_next_sibling("p").text.replace(";", ":")
                
            preceding_p = soup.find("strong", class_="Cyrl headword", lang="ru").find_parent("p")
            if preceding_p: # Finds english definition
                ol_element = preceding_p.find_next_sibling("ol")
                if ol_element:
                    english_definition = ol_element.find("a", href=True, title=lambda title: title and ":" not in title).text
            if not english_definition: # Safe case
                print("[!] No English definition found.")
            
            # Fetch sentence and translation from Openrussian
            url = f'https://en.openrussian.org/ru/{word}'  # Replace with the actual URL
            # Send an HTTP GET request to the website
            response = requests.get(url, headers=hdr)
            # Check if the request was successful
            if response.status_code == 200: # Openrussian sentence scraper
                # Get the HTML content from the response
                content = response.content
                # Create a BeautifulSoup object with the HTML content
                soup = BeautifulSoup(content, "lxml")
                if soup.find("div", class_="section sentences"):
                    impf = soup.find("li", class_="sentence").find("span", class_="ru").text.replace("́", "").replace(";", ":")
                    impf_trans = soup.find("li", class_="sentence").find("span", class_="tl").text.replace(";", ":")
                
                # Start of finding audio
                url = f"https://en.wiktionary.org/wiki/{word}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                audio_player = soup.find("table", class_="audiotable")
                if audio_player: # Rest of finding wikt audio
                    # Extract the audio URL
                    audio_url = audio_player.find("source")["src"]

                    if audio_url.startswith("//"):
                        audio_url = "https:" + audio_url

                    # Send an HTTP GET request to the audio URL
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                    }
                    audio_response = requests.get(audio_url, headers=headers)

                    # Determine the file extension from the Content-Type header
                    content_type = audio_response.headers.get("Content-Type")
                    extension = audio_url[-3:]

                    # Decode the URL-encoded filename
                    decoded_word = urllib.parse.unquote(word)

                        
                    # Save the audio file to the specified filepath
                    word_audio_filename = f'{decoded_word}.{extension}'
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{decoded_word}.{extension}")
                    with open(filepath, "wb") as file:
                        file.write(audio_response.content)
                    
                    # Print the absolute path of the saved file
                    abs_path = os.path.abspath(filepath)
                else: # Safe case generates TTS
                    decoded_word = word
                    # Generate TTS audio using gTTS
                    tts = gTTS(text=word, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.mp3")
                    word_audio_filename = f'{decoded_word}.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                
                if impf != "": # TTS for impf sentence
                    tts = gTTS(text=impf, lang="ru")
                    filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}_impf.mp3")
                    impf_audio_filename = f'{word}_impf.mp3'
                    tts.save(filepath)
                    abs_path = os.path.abspath(filepath)
                else: impf_audio_filename = ""
                
                # Start of finding image
                url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                image = ""
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("img", class_="mimg"):
                        image_url = soup.find("img", class_="mimg")["src"]
                        image_response = requests.get(image_url)
                        # Save the audio file to the specified filepath
                        filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                        image = f'{word}.jpg'
                        with open(filepath, "wb") as file:
                            file.write(image_response.content)  
                    else:
                        print(f"Image for {word} couldn't be retrieved ")

                url = f'https://en.openrussian.org/ru/{word}'
                
            anki_formatted = f'{word};{mnemonic};[sound:{word_audio_filename}] {accented_word};{pronunciation};{english_definition};{info};[sound:{impf_audio_filename}] {impf};{impf_trans};;;{etymology};{wiktionary} {url}'
            anki_formatted = anki_formatted.replace('\n', '')
            file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
            new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare

            # Read the existing lines from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            # Check if the new line already exists
            if any(new_line == line.split(';')[0] for line in lines):
                print(f"[!] {word} already exists in the file, skipping.")
            else:
                # Append the new line to the file
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write(anki_formatted + '\n')
                    print(anki_formatted)
    else: #If wiktionary page does not exist
        print(f'[!] Wiktionary page for "{word}" not found. Creating card with most fields empty.')
        if True:        
            if True:    
                # Start of finding image
                url = f"https://www.bing.com/images/search?q={word}&form=HDRSC3&first=1"
                image = ""
                # Send an HTTP GET request to the website
                response = requests.get(url, headers=hdr)
                # Check if the request was successful
                if response.status_code == 200:
                    # Get the HTML content from the response
                    content = response.content
                    # Create a BeautifulSoup object with the HTML content
                    soup = BeautifulSoup(content, "lxml")
                    if soup.find("img", class_="mimg"):
                        image_url = soup.find("img", class_="mimg")["src"]
                        if requests.get(image_url):
                            image_response = requests.get(image_url)
                            # Save the audio file to the specified filepath
                            filepath = os.path.join("C:\\Users\\Ådne\\AppData\\Roaming\\Anki2\\STANDARD\\collection.media", f"{word}.jpg")
                            image = f'{word}.jpg'
                            with open(filepath, "wb") as file:
                                file.write(image_response.content)  
                    else:
                        print(f"Image for {word} couldn't be retrieved ")

                url = f'https://en.openrussian.org/ru/{word}'
            accented_word = word
                
            anki_formatted = f'{word};{mnemonic};{accented_word};{pronunciation};{english_definition};{info};{impf};{impf_trans};;;{etymology};{wiktionary} {url}'
            anki_formatted = anki_formatted.replace('\n', '')
            file_path = "C:/Users/Ådne/#Python Projects/anki_flashcard_maker/russian_words_anki.txt"
            new_line = anki_formatted.split(';')[0]  # Extract the first part of the line to compare
            # Read the existing lines from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Check if the new line already exists
            if any(new_line == line.split(';')[0] for line in lines):
                print(f"[!] {word} already exists in the file, skipping.")
            else:
                # Append the new line to the file
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write(anki_formatted + '\n')
                    print(anki_formatted)


legges_te_manuelt = "выходить, строить, арендовать"
word_list = ["двор"]
for word in word_list:
    handle_word(word)
