from qualifiedTags import DIV, UL, H3, A
from utils import find_elements_with_attribute_equal_to


def get_boxes(box_elements):
    return map(lambda x: RozhlasSearchPageParser.Box(x),
               find_elements_with_attribute_equal_to(box_elements, UL, "class",
                                                     "box-article-archive box-audio-archive"))


class RozhlasSearchPageParser(object):
    def __init__(self, root):
        box_results = find_elements_with_attribute_equal_to(root, DIV, "id", "box-results")
        if len(box_results) == 0:
            return

        self.boxes = list(get_boxes(box_results[0]))

    def get_hrefs(self):
        return map(lambda x: x.get_href(), self.boxes)

    class Box(object):
        def __init__(self, root):
            a_s = root.findall(".//%s/%s" % (H3, A))
            if len(a_s) > 0:
                self.href = a_s[0].attrib["href"]

        def get_href(self):
            return self.href
