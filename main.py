import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
from tqdm import tqdm
import pyttsx3
import os
import subprocess

# The parameters for setting up the pyttsx3 engine.
engine = pyttsx3.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('rate', 170)
engine.setProperty('voice', voices[1].id)

blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']

BOOK_TO_CONVERT = "Books/(Expanse 2) Corey, James S A - Caliban's War.epub"
AUDIO_TITLE = "Final/Expanse 2 - Caliban's War - James SA.wav"

path = "Chapters"
mergelist_path = "batchlist.txt"


def chap2text(chap):
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output


def thtml2ttext(thtml):
    output = []
    for html in thtml:
        text = chap2text(html)
        output.append(text)
    return output


def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    ttext = thtml2ttext(chapters)
    return ttext


def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)

    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def chapters_to_audio(chapters):
    print(f"Converting chapter by chapter as a .mp3 file.")
    num = 0
    for ch in tqdm(chapters):
        num = num + 1
        engine.save_to_file(ch, f'Chapters/Chapter_{num}.mp3')
        engine.runAndWait()


def create_mergelist():
    with open(mergelist_path, 'w') as mergelist:
        for file in sorted(os.listdir(path), key=lambda x: int(x.split("_")[1].split(".")[0])):
            if file.endswith('.mp3'):
                mergelist.write("file '{}'\n".format(os.path.join(path, file)))


def concatenate_audio():
    create_mergelist()

    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "batchlist.txt", "-c", "copy", AUDIO_TITLE])


def cleanup_temp_mp3():
    print(f"Deleting the temp files!")

    dir_name = "Chapters/"
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".mp3"):
            os.remove(os.path.join(dir_name, item))

    print(f"Deletion of temp files successful in Chapters.")


if __name__ == '__main__':
    txt = epub2text(BOOK_TO_CONVERT)
    output = ''
    bar = IncrementalBar('Countdown', max=len(txt))
    language = 'en'
    num = 0

    txt = filter(lambda test: test.strip(), txt)

    chapterList = []

    for i in txt:
        chapterList.append(i)

    # Turns each text chapter into a mp3
    chapters_to_audio(chapterList)

    # Combines each mp3 into a big one!
    concatenate_audio()

    # Deletes the temporary .mp3 files
    cleanup_temp_mp3()
