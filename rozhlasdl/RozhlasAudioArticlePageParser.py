# -*- coding: utf-8 -*-
import re

from qualifiedTags import DIV, A, H1

# pattern = re.compile("https://.*rozhlas.cz/.*/[0-9a-f]{8}([0-9a-f]{24})?\\.mp3(\\?.*)?")
pattern = re.compile("https://.*(rozhlas|radio).cz/.*\\.(mp3|flac)(\\?.*)?")


def get_other_part_audio_title(part):
    for div in part:
        if "class" in div.attrib:
            klass = div.attrib["class"]
            if klass == "filename__text":
                return div.text
    return None


def get_mp3_url_from_element(element):
    for a in element.iter(A):
        if "href" in a.attrib:
            href = a.attrib["href"]
            result = pattern.match(href)
            if result is not None:
                return href


class RozhlasAudioArticlePageParser:

    def __init__(self, root, audio_div):
        self.root = root
        self.audio_div = audio_div
        self.other_parts = self.get_other_parts()

    def get_mp3_url(self):
        return get_mp3_url_from_element(self.audio_div)

    def get_audio_title(self, number=1, use_page_title=False):
        if use_page_title:
            title = self.get_serial_name()
            if title is None:
                return None
            return self.add_number_if_has_other_parts(number, title)
        else:
            for div in self.audio_div.iter(DIV):
                if "aria-labelledby" in div.attrib:
                    aria_labelledby = div.attrib["aria-labelledby"]
                    if aria_labelledby == "titulek audia":
                        text = div.text
                        return self.add_number_if_has_other_parts(number, text)
            return None

    def add_number_if_has_other_parts(self, number, text):
        if self.has_other_parts():
            return "%02d %s" % (number, text)
        else:
            return text

    def is_copyright_expired(self):
        for div in self.audio_div.iter(DIV):
            if "class" in div.attrib:
                klass = div.attrib["class"]
                if "audio-rights-expired" in klass:
                    return True
        return False

    def get_other_parts(self):
        parts = []
        for div in self.root.iter(DIV):
            if "class" in div.attrib:
                klass = div.attrib["class"]
                if "wysiwyg-asset" in klass and "asset-type-audio" in klass:
                    parts.append(div)
        return parts

    def has_other_parts(self):
        return len(self.other_parts) != 0

    def get_mp3_urls_and_audio_titles_of_other_parts(self):
        urls_and_titles = []

        if self.has_other_parts():
            number = 2
            for part in self.other_parts:
                url = get_mp3_url_from_element(part)
                title = self.get_audio_title_from_element(part, number)
                urls_and_titles.append((url, title))
                number += 1

        return urls_and_titles

    def get_serial_name(self):
        for h1 in self.root.iter(H1):
            return h1.text
        return None

    def get_audio_title_from_element(self, element, number=0):
        for div in element.iter(DIV):
            if "class" in div.attrib:
                klass = div.attrib["class"]
                if klass == "filename__text":
                    text = div.text
                    return self.add_number_if_has_other_parts(number, text)
        return None
