from chirpy.core.response_generator import nlg_helper

from chirpy.response_generators.music.utils import MusicBrainzInterface

@nlg_helper
def get_another_song_by_same_singer(musician_name, cur_song):
    musicbrainz = MusicBrainzInterface()
    top_songs = musicbrainz.get_top_songs_by_musician(musician_name)
    for song in top_songs:
        if song != cur_song:
            return song
