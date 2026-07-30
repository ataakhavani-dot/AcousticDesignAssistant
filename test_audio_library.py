import unittest

from audio_library import AUDIO_GUIDES, get_audio_guides


class AudioLibraryTests(unittest.TestCase):
    def test_gallery_contains_the_complete_audio_catalog(self):
        self.assertEqual(get_audio_guides("gallery"), AUDIO_GUIDES)
        self.assertEqual(len(get_audio_guides("gallery")), 6)

    def test_related_guides_match_each_calculator_topic(self):
        self.assertEqual(
            [guide["title"] for guide in get_audio_guides("rt60")],
            ["RT60 Limits", "Absorption Strategy"],
        )
        self.assertEqual(
            [guide["title"] for guide in get_audio_guides("sbir")],
            ["SBIR Effects", "Monitor Placement"],
        )


if __name__ == "__main__":
    unittest.main()