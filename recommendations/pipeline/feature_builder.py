import numpy as np


class FeatureBuilder:

    @staticmethod
    def build(song):

        return np.array([
            song.tempo or 0.0,
            song.energy or 0.0,
            song.danceability or 0.0,
            song.loudness or 0.0,
            song.valence or 0.0,
            song.acousticness or 0.0,
        ], dtype="float32")
