import json
from qualifiedTags import H1
from log.LoggerFactory import LoggerFactory

LOGGER = LoggerFactory.get(__name__)


class MujRozhlasPlayerPageParser:

    def __init__(self, root, audio_div):
        self.root = root
        self.audio_div = audio_div
        self.json = json.loads(audio_div.attrib["data-player"])

    def get_audio_title(self, use_page_title=False):

        if use_page_title:
            title = self.get_page_name()
            if title is None:
                return None
            return title
        else:
            title = self.json["data"]["series"]["title"]
            return title

    def is_copyright_expired(self):
        return False  # Unsupported at the moment.

    def get_page_name(self):
        for h1 in self.root.iter(H1):
            return h1.text
        return None

    def get_mp3_urls_and_audio_titles(self):
        urls_and_titles = []
        playlist = self.json["data"]["playlist"]
        for playlist_item in playlist:
            title = playlist_item["title"]
            audiolinks = playlist_item["audioLinks"]
            url = None
            download_link_present = False
            for audiolink in audiolinks:
                if audiolink["linkType"] == "download":
                    url = audiolink["url"]
                    download_link_present = True
                    break
            if not download_link_present:
                for audiolink in audiolinks:
                    if audiolink["linkType"] == "ondemand" and audiolink["variant"] == "dash":
                        url = audiolink["url"]
                        download_link_present = True
                        break
            if not download_link_present:
                LOGGER.warning("Link for %s from %s not found." % (title, self.get_page_name(),))
                break

            urls_and_titles.append((url, title))
        return urls_and_titles
