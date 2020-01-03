import re


class RozhlasAudioArticlePageParser:
    # pattern = re.compile("https://.*rozhlas.cz/.*/[0-9a-f]{8}([0-9a-f]{24})?\\.mp3(\\?.*)?")
    pattern = re.compile("https://.*rozhlas.cz/.*\\.mp3(\\?.*)?")

    def __init__(self, root):
        self.root = root

    def get_mp3_url(self):
        for a in self.root.iter('{http://www.w3.org/1999/xhtml}a'):
            if "href" in a.attrib:
                href = a.attrib["href"]
                result = self.pattern.match(href)
                if result is not None:
                    return href

    def get_audio_title(self):
        for div in self.root.iter('{http://www.w3.org/1999/xhtml}div'):
            if "aria-labelledby" in div.attrib:
                aria_labelledby = div.attrib["aria-labelledby"]
                if aria_labelledby == "titulek audia":
                    return div.text
        return None

    def is_copyright_expired(self):
        for div in self.root.iter('{http://www.w3.org/1999/xhtml}div'):
            if "class" in div.attrib:
                klass = div.attrib["class"]
                if "audio-rights-expired" in klass:
                    return True
        return False
