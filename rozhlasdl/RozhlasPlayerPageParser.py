from qualifiedTags import DIV, H3, P
from utils import str_to_win_file_compatible


class RozhlasPlayerPageParser:

    def __init__(self, block_track_player_div):
        self.root = block_track_player_div

    def get_mp3_url(self):
        div_player_track = self.root.findall(".//%s[@id='player-track']" % DIV)
        data_id = div_player_track[0].attrib["data-id"]
        return "https://media.rozhlas.cz/_audio/%s.mp3" % data_id

    def get_audio_title(self):
        p = self.root.findall(".//%s/../%s" % (H3, P))
        return str_to_win_file_compatible(p[0].text)

    def get_programme(self):
        h3 = self.root.findall(".//%s" % H3)[0]
        return str_to_win_file_compatible(h3.text)
