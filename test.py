import unittest
import get_songs

class TestGetSongs(unittest.TestCase):

    def test_sum(self):
        self.assertIsNotNone(get_songs.get_token(), "Cannot find access token. Should be in .env file with name ACCESS_TOKEN")

if __name__ == '__main__':
    unittest.main()
