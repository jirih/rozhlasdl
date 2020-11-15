# -*- coding: utf-8 -*-
import re
import time
from os.path import join

from FileDownloader import FileDownloader
from MyProgressBar import MyProgressBar
from PageDownloader import PageDownloader
from RozhlasAudioArticlePageParser import RozhlasAudioArticlePageParser
from RozhlasAudioSerialPageParser import RozhlasAudioSerialPageParser
from RozhlasException import RozhlasException
from RozhlasListPageParser import RozhlasListPageParser
from RozhlasPlayerPageParser import RozhlasPlayerPageParser
from RozhlasSearchPageParser import RozhlasSearchPageParser
from WebPageParser import WebPageParser
from log.LoggerFactory import LoggerFactory
from qualifiedTags import *
from utils import str_to_win_file_compatible, complete_url, get_subdomain, \
    safe_path_join, find_elements_with_attribute_containing, find_elements_with_attribute_equal_to

LOGGER = LoggerFactory.get(__name__)


def get_audio_div(root):
    for div in root.iter(DIV):
        if "id" in div.attrib:
            div_id = div.attrib["id"]
            if div_id == "file-serial-player":
                return div
            if re.match(r"file-\d+", div_id) and "class" in div.attrib and "audio-article-player" in div.attrib[
                "class"]:
                return div
            if re.match(r"file-\d+", div_id) and "class" in div.attrib and "file-audio" in div.attrib[
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
        if re.match(r"file-\d+", div_id) and "class" in div.attrib and "file-audio" in div.attrib[
            "class"]:
            return "fileaudio"
    return None


def get_root_of_page(url):
    pd = PageDownloader(url)
    html = pd.download()
    parser = WebPageParser(html)
    root = parser.get_root()
    return root


class MainDownloader():
    def __init__(self, base_folder, no_duplicates=True, follow_next_pages=False, fake_download=False, max_next_pages=3,
                 progress_bar_enabled=True, use_page_title=False, kindness=0, follow_image_links=False):
        self.base_folder = base_folder
        self.no_duplicates = no_duplicates
        self.follow_next_pages = follow_next_pages
        self.fake_download = fake_download
        self.max_next_pages = max_next_pages
        self.follow_image_links = follow_image_links
        self.progress_bar_enabled = progress_bar_enabled
        self.use_page_title = use_page_title
        self.kindness = kindness
        self.something_downloaded = False
        self.downloaded_urls = []
        self.downloaded_audios_counter = 0

    def download_audio_serial(self, root, audio_div, folder):
        page_parser = RozhlasAudioSerialPageParser(root, audio_div)

        mp3_urls_and_audio_titles = page_parser.get_mp3_urls_and_audio_titles()
        serial_name = page_parser.get_serial_name()
        serial_folder = join(folder, str_to_win_file_compatible(serial_name))

        for mp3_url, audio_title in mp3_urls_and_audio_titles:
            self.download_mp3(audio_title, serial_folder, mp3_url)

    def download_audio_article(self, root, audio_div, folder):
        page_parser = RozhlasAudioArticlePageParser(root, audio_div)

        audio_title = page_parser.get_audio_title(use_page_title=self.use_page_title)
        if page_parser.is_copyright_expired():
            LOGGER.warning("%s: Copyright expired." % audio_title)
            return
        mp3_url = page_parser.get_mp3_url()

        if page_parser.has_other_parts():
            LOGGER.info("%s: More parts detected." % audio_title)
            serial_name = page_parser.get_serial_name()
            folder = join(folder, str_to_win_file_compatible(serial_name))

        if mp3_url is None:
            LOGGER.warning("%s: No audio file found." % audio_title)
            return
        else:
            self.download_mp3(audio_title, folder, mp3_url)

        if page_parser.has_other_parts():
            mp3_urls_and_audio_titles_of_other_parts = page_parser.get_mp3_urls_and_audio_titles_of_other_parts()
            for mp3_url, audio_title in mp3_urls_and_audio_titles_of_other_parts:
                LOGGER.debug("%s: %s " % (audio_title, mp3_url))
                self.download_mp3(audio_title, folder, mp3_url)

    def download_player(self, block_track_player_div, folder):
        page_parser = RozhlasPlayerPageParser(block_track_player_div)

        audio_title = page_parser.get_audio_title()
        programme = page_parser.get_programme()
        mp3_url = page_parser.get_mp3_url()

        self.download_mp3(audio_title, safe_path_join(folder, programme), mp3_url)

    def download_mp3(self, audio_title, folder, mp3_url):
        if mp3_url is None:
            raise RozhlasException("MP3 URL not given! Probably problem with parsing.")
        if audio_title is not None and mp3_url is not None:

            LOGGER.debug("%s: %s" % (audio_title, mp3_url))
            filename = str_to_win_file_compatible(audio_title) + ".mp3"
        else:
            filename = None
        if self.something_downloaded:
            #LOGGER.debug("Waiting %d seconds." % self.kindness)
            time.sleep(self.kindness)
        fd = FileDownloader(folder, progress_bar=MyProgressBar() if self.progress_bar_enabled else None,
                            no_duplicates=self.no_duplicates, fake_download=self.fake_download)
        not_skipped = fd.download(mp3_url, filename)
        if not_skipped:
            self.downloaded_audios_counter += 1
        self.something_downloaded = True

    def download_links(self, root, base_url):
        page_parser = RozhlasListPageParser(root, self.follow_image_links)
        links = page_parser.get_links()
        for link in links:
            self.download_url(complete_url(link, base_url))

        LOGGER.debug("All links found on %s has been processed." % base_url)

        if self.follow_next_pages:
            ul_pagers = root.findall(".//%s[@class='pager']" % UL)
            if len(ul_pagers) == 0:
                return
            ul_pager = ul_pagers[0]
            current_page_number = int(
                find_elements_with_attribute_containing(ul_pager, LI, "class", "pager__item--current")[0].text)
            if current_page_number > self.max_next_pages:
                LOGGER.info("Maximal number of pages to follow from %s reached." % base_url)
                return

            li_pager_item_next = find_elements_with_attribute_containing(ul_pager, LI, "class", "pager__item--next")
            if len(li_pager_item_next) == 0:
                return
            a_link_to_next = li_pager_item_next[0].findall(".//%s[@href]" % A)
            if len(a_link_to_next) == 0:
                return

            LOGGER.info("Following next (%d) page on %s." % (current_page_number + 1, base_url))
            self.download_url(complete_url(a_link_to_next[0].attrib["href"], base_url))

    def download_search(self, root, base_url):
        page_parser = RozhlasSearchPageParser(root)
        if page_parser.boxes is None or len(page_parser.boxes) == 0:
            LOGGER.warning("No results found for a search page %s." % base_url)
        else:
            for href in page_parser.get_hrefs():
                self.download_url(href)
        LOGGER.debug("All links found on %s has been processed." % base_url)
        if self.follow_next_pages:
            pager = root.findall(".//%s[@id='box-listovani']" % DIV)
            if len(pager) == 0:
                return
            pager = pager[0]
            current_page_number = int(
                pager.findall(".//%s" % B)[0].text)

            if current_page_number > self.max_next_pages:
                LOGGER.info("Maximal number of pages to follow from %s reached." % base_url)
                return

            a_links_to_next = find_elements_with_attribute_equal_to(pager, A, "id", "sipka_right")
            if len(a_links_to_next) == 0:
                return

            LOGGER.info("Following next (%d) page on %s." % (current_page_number + 1, base_url))
            self.download_url(complete_url(a_links_to_next[0].attrib["href"], base_url))

    def download_url(self, url):
        LOGGER.info("Web page: %s" % url)
        if url in self.downloaded_urls:
            LOGGER.debug("Web page %s has been already processed" % url)
            return
        else:
            self.downloaded_urls.append(url)

        subdomain = get_subdomain(url)

        if self.something_downloaded:
            #LOGGER.debug("Waiting %d seconds." % self.kindness)
            time.sleep(self.kindness)
        root = get_root_of_page(url)
        self.something_downloaded = True

        if subdomain == "prehravac":
            body = root.findall(".//%s" % BODY)[0]
            if "mode-live" in body.attrib["class"]:
                raise NotImplementedError("Live mode not supported.")

            block_track_player_div = root.findall(".//%s[@id='block-track-player']" % DIV)[0]

            body_id = body.attrib["id"]
            station = body_id.split('-')[-1]

            folder = safe_path_join(self.base_folder, subdomain)
            folder = safe_path_join(folder, station)

            LOGGER.info("A player web page. Going to download its content, if available.")
            self.download_player(block_track_player_div, folder)

        elif subdomain == "hledani":
            self.download_search(root, url)

        else:
            audio_div = get_audio_div(root)
            audio_type = get_audio_type(audio_div)
            if audio_type == "article" or audio_type == "fileaudio":
                folder = safe_path_join(self.base_folder, subdomain)
                LOGGER.info("Audio type is article. Going to download its content, if available.")
                self.download_audio_article(root, audio_div, folder)
            elif audio_type == "serial":
                folder = safe_path_join(self.base_folder, subdomain)
                LOGGER.info("Audio type is serial. Going to download all available parts.")
                self.download_audio_serial(root, audio_div, folder)
            else:
                LOGGER.warning("Audio type not recognized. Trying to find links to pages with media.")
                self.download_links(root, url)

    def get_stats(self):
        return len(self.downloaded_urls), self.downloaded_audios_counter
