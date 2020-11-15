# -*- coding: utf-8 -*-
class RozhlasListPageParser:
    def __init__(self, root, follow_image_links=False):
        self.root = root
        self.follow_image_links = follow_image_links

    def get_links(self):
        links = []
        for a in self.root.iter('{http://www.w3.org/1999/xhtml}a'):
            if "class" in a.attrib and (
                    "button-play" in a.attrib["class"]
                    or "button-listaction--play" in a.attrib["class"]
                    or (self.follow_image_links and "image-link" in a.attrib["class"])):
                if "href" in a.attrib:
                    links.append(a.attrib["href"])
        return links
