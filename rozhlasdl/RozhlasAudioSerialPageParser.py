# -*- coding: utf-8 -*-
import re

pattern = re.compile("https://.*rozhlas.cz/.*/[0-9a-f]{32}\\.mp3(\\?.*)?")


def _get_mp3_url(li):
    for a in li.iter('{http://www.w3.org/1999/xhtml}a'):
        if "href" in a.attrib:
            href = a.attrib["href"]
            result = pattern.match(href)
            if result is not None:
                return href


def _get_audio_title(li):
    part = 0
    for div in li.iter('{http://www.w3.org/1999/xhtml}div'):
        if "part" in div.attrib:
            part = int(div.attrib["part"])

    filename = ""
    for div in li.iter('{http://www.w3.org/1999/xhtml}div'):
        if "class" in div.attrib:
            klass = div.attrib["class"]
            if "filename__text" in klass:
                if "title" in div.attrib:
                    filename = div.attrib["title"]
                else:
                    filename = div.text

    return "%02d %s" % (part, filename)


class RozhlasAudioSerialPageParser:

    def __init__(self, root, audio_div):
        self.root = root
        self.audio_div = audio_div
        self.lis = self._get_lis()

    def _get_lis(self):
        lis = []
        for li in self.audio_div.iter('{http://www.w3.org/1999/xhtml}li'):
            for a in li.iter('{http://www.w3.org/1999/xhtml}a'):
                if "href" in a.attrib:
                    href = a.attrib["href"]
                    result = pattern.match(href)
                    if result is not None:
                        lis.append(li)
        return lis

    def get_mp3_urls_and_audio_titles(self):
        urls_and_audio_titles = []
        for li in self.lis:
            url_and_audio_title = (_get_mp3_url(li), _get_audio_title(li))
            urls_and_audio_titles.append(url_and_audio_title)
        return urls_and_audio_titles

    def get_serial_name(self):
        for h1 in self.root.iter('{http://www.w3.org/1999/xhtml}h1'):
            return h1.text
