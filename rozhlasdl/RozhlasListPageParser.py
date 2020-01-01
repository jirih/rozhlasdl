class RozhlasListPageParser:
    def __init__(self, root):
        self.root = root

    def get_links(self):
        links = []
        for a in self.root.iter('{http://www.w3.org/1999/xhtml}a'):
            if "class" in a.attrib and (
                    "button-play" in a.attrib["class"] or "button-listaction--play" in a.attrib["class"]):
                if "href" in a.attrib:
                    links.append(a.attrib["href"])
        return links
