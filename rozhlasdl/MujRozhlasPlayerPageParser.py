import json
from qualifiedTags import H1


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
        return False # Unsupported at the moment.

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
            urls = list(map(lambda x: x["url"], audiolinks))
            is_multi_urls = len(urls) > 1
            counter = 0
            for url in urls:
                if is_multi_urls:
                    counter += 1
                    urls_and_titles.append((url, "%s %03d" % (title, counter,)))
                else:
                    urls_and_titles.append((url, "%s" % title))
        return urls_and_titles