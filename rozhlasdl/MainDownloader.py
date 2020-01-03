import re
from os.path import join, isdir

from FileDownloader import FileDownloader
from MyProgressBar import MyProgressBar
from PageDownloader import PageDownloader
from RozhlasAudioArticlePageParser import RozhlasAudioArticlePageParser
from RozhlasAudioSerialPageParser import RozhlasAudioSerialPageParser
from RozhlasListPageParser import RozhlasListPageParser
from WebPageParser import WebPageParser
from qualifiedTags import *
from utils import str_to_win_file_compatible, complete_url, get_subdomain, \
    safe_path_join


def get_audio_div(root):
    for div in root.iter(DIV):
        if "id" in div.attrib:
            div_id = div.attrib["id"]
            if div_id == "file-serial-player":
                return div
            if re.match(r"file-\d+", div_id) and "class" in div.attrib and "audio-article-player" in div.attrib[
                "class"]:
                return div
    return None


def get_audio_type(div):
    if div is None:
        return None
    if "id" in div.attrib:
        div_id = div.attrib["id"]
        if div_id == "file-serial-player":
            return "serial"
        if re.match(r"file-\d+", div_id) and "class" in div.attrib and "audio-article-player" in div.attrib[
            "class"]:
            return "article"
    return None


def get_root_of_page(url):
    pd = PageDownloader(url)
    html = pd.download()
    parser = WebPageParser(html)
    root = parser.get_root()
    return root


class MainDownloader():
    def __init__(self, base_folder, no_duplicates=True):
        self.base_folder = base_folder
        self.no_duplicates = no_duplicates

    def download_audio_serial(self, root, audio_div, folder):
        page_parser = RozhlasAudioSerialPageParser(root, audio_div)

        mp3_urls_and_audio_titles = page_parser.get_mp3_urls_and_audio_titles()
        serial_name = page_parser.get_serial_name()
        serial_folder = join(folder, str_to_win_file_compatible(serial_name))
        if not isdir(serial_folder):
            mkdir(serial_folder)

        for mp3_url, audio_title in mp3_urls_and_audio_titles:
            self.download_mp3(audio_title, serial_folder, mp3_url)

    def download_audio_article(self, audio_div, folder):
        page_parser = RozhlasAudioArticlePageParser(audio_div)

        audio_title = page_parser.get_audio_title()
        if page_parser.is_copyright_expired():
            print("%s: Copyright expired" % audio_title)
            return
        mp3_url = page_parser.get_mp3_url()
        self.download_mp3(audio_title, folder, mp3_url)

    def download_player(self, block_track_player_div, folder):

        h3 = block_track_player_div.findall(".//%s" % H3)[0]
        programme = str_to_win_file_compatible(h3.text)
        folder = safe_path_join(folder, programme)
        p = block_track_player_div.findall(".//%s/../%s" % (H3, P))
        mp3_name = str_to_win_file_compatible(p[0].text)
        filename = mp3_name + ".mp3"
        div_player_track = block_track_player_div.findall(".//%s[@id='player-track']" % DIV)
        data_id = div_player_track[0].attrib["data-id"]
        mp3_url = "https://media.rozhlas.cz/_audio/%s.mp3" % data_id
        fd = FileDownloader(folder, progress_bar=MyProgressBar(), no_duplicates=self.no_duplicates)
        fd.download(mp3_url, filename)

    def download_mp3(self, audio_title, folder, mp3_url):
        if audio_title is not None and mp3_url is not None:
            print(audio_title + ": " + mp3_url)
            filename = str_to_win_file_compatible(audio_title) + ".mp3"
        else:
            filename = None
        fd = FileDownloader(folder, progress_bar=MyProgressBar(), no_duplicates=self.no_duplicates)
        fd.download(mp3_url, filename)

    def download_links(self, root, base_url):
        page_parser = RozhlasListPageParser(root)
        links = page_parser.get_links()
        for link in links:
            self.download_url(complete_url(link, base_url))

    def download_url(self, url):
        print()
        print("Web page: %s" % url)

        subdomain = get_subdomain(url)
        if subdomain == "hledani":
            raise NotImplementedError("Subdomain %s is not supported yet." % subdomain)

        root = get_root_of_page(url)

        if subdomain == "prehravac":
            block_track_player_div = root.findall(".//%s[@id='block-track-player']" % DIV)[0]
            body = root.findall(".//%s" % BODY)[0]
            body_id = body.attrib["id"]
            station = body_id.split('-')[-1]

            folder = safe_path_join(self.base_folder, subdomain)
            folder = safe_path_join(folder, station)

            print("A player web page. Going to download its content, if available.")
            self.download_player(block_track_player_div, folder)

        else:
            audio_div = get_audio_div(root)
            audio_type = get_audio_type(audio_div)
            if audio_type == "article":
                folder = safe_path_join(self.base_folder, subdomain)
                print("Audio type is article. Going to download its content, if available.")
                self.download_audio_article(audio_div, folder)
            elif audio_type == "serial":
                folder = safe_path_join(self.base_folder, subdomain)
                print("Audio type is serial. Going to download all available parts.")
                self.download_audio_serial(root, audio_div, folder)
            else:
                print("Audio type not recognized. Trying to find links to pages with media.")
                self.download_links(root, url)
