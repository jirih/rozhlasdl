from FileDownloader import FileDownloader
from RozhlasAudioArticlePageParser import RozhlasAudioArticlePageParser
from WebPageParser import WebPageParser
from utils import str_to_win_file_compatible

# pd = PageDownloader(r"https://junior.rozhlas.cz/pohadka-tulacka-hvezdne-obsazene-vypraveni-s-ivou-janzurovou-a-rudolfem-8124985")
# html = pd.download()


# with open("test.html", "w", encoding='utf8') as text_file:
#     text_file.write(html)

with open("test.html", "r", encoding='utf8') as myfile:
    html = myfile.read()

parser = WebPageParser(html)

root = parser.get_root()

p1 = RozhlasAudioArticlePageParser(root)
print(p1.get_audio_title() + ": " + p1.get_mp3_url())
print()

filename = str_to_win_file_compatible(p1.get_audio_title()) + ".mp3"

fd = FileDownloader(r"d:\\Downloads\\rozhlas")
# fd.download(p1.get_mp3_url())
fd.download(p1.get_mp3_url(), filename)
