import unittest
import get_songs
import json

class TestGetSongs(unittest.TestCase):

    def test_token(self):
        self.assertIsNotNone(get_songs.get_token(), "Cannot find access token. Should be in .env file with name ACCESS_TOKEN")


    def test_get_nested_key(self):
        test1 = {'key1': {'key2': {'key3': 4}}}
        self.assertEqual(4, get_songs.get_nested_key(test1, ['key1', 'key2', 'key3']), "Case where keys exist")
        self.assertIsNone(get_songs.get_nested_key(test1, ['key2']), "Case where keys do not exist")

    def test_parse_artist_id(self):
        test1 = '{"test": 0}'
        self.assertIsNone(get_songs.parse_artist_id(test1, 'artist'), "Case where pre-loop response format is wrong")
        test2 = '{"response": {"hits": 1}}'
        self.assertIsNone(get_songs.parse_artist_id(test2, 'artist'), "Case where hits is not an array")
        test3 = '{"response": {"hits": [{"result": {"test": 1}}]}}'
        self.assertIsNone(get_songs.parse_artist_id(test3, 'artist'), "Case where inner-loop response format is wrong")
        test4 = '{"response": {"hits": [{"result": {"primary_artist": {"name": "artist", "id": 10}}}]}}'
        self.assertEqual(10, get_songs.parse_artist_id(test4, 'artist'), "Case where first hit is a match")
        test5 = '{"response": {"hits": [{"test": 0},{"result": {"primary_artist": {"name": "artist", "id": 10}}}]}}'
        self.assertEqual(10, get_songs.parse_artist_id(test4, 'artist'), "Case where second hit is a match")
        test6 = '{"response": {"hits": [{"test": 0},{"result": {"primary_artist": {"name": "test", "id": 10}}}]}}'
        self.assertIsNone(get_songs.parse_artist_id(test6, 'artist'), "Case where name doesn't match")
        test7 = "test"
        with self.assertRaises(json.decoder.JSONDecodeError):
            get_songs.parse_artist_id(test7, 'artist')

    def test_parse_song_response(self):
        test1 = '{"test": 0}'
        result1, result2 = get_songs.parse_song_response(test1, 10)
        self.assertEqual([], result1, "Case where pre-loop response format is wrong")
        self.assertIsNone(result2, "Case where pre-loop response format is wrong")
        test2 = '{"response": {"songs": 1}}'
        result1, result2 = get_songs.parse_song_response(test2, 10)
        self.assertEqual([], result1, "Case where songs is not an array")
        self.assertIsNone(result2, "Case where songs is not an array")
        test3 = '{"response": {"songs": [{"title": "test"}]}}'
        result1, result2 = get_songs.parse_song_response(test3, 10)
        self.assertEqual([], result1, "Case where song has no id")
        self.assertIsNone(result2, "Case where song has no id")
        test4 = '{"response": {"songs": [{"title": "test", "primary_artist": {"id": 10}}]}}'
        result1, result2 = get_songs.parse_song_response(test4, 10)
        self.assertEqual(["test"], result1, "Case where song has correct id")
        self.assertIsNone(result2, "Case where song has correct id")
        test5 = '{"response": {"songs": [{"title": "test", "primary_artist": {"id": 9}}, {"title": "test2", "primary_artist": {"id": 10}}]}}'
        result1, result2 = get_songs.parse_song_response(test5, 10)
        self.assertEqual(["test2"], result1, "Case where second song has correct id")
        self.assertIsNone(result2, "Case where second song has correct id")
        test6 = '{"response": {"songs": [{"title": "test", "primary_artist": {"id": 10}}, {"title": "test2", "primary_artist": {"id": 10}}]}}'
        result1, result2 = get_songs.parse_song_response(test6, 10)
        self.assertEqual(["test", "test2"], result1, "Case where two songs have correct id")
        self.assertIsNone(result2, "Case where two songs have correct id")
        test7 = '{"response": {"songs": [{"title": "test", "primary_artist": {"id": 10}}, {"title": "test2", "primary_artist": {"id": 10}}], "next_page": "b"}}'
        result1, result2 = get_songs.parse_song_response(test7, 10)
        self.assertEqual(["test", "test2"], result1, "Case where next_song is not an int")
        self.assertIsNone(result2, "Case where next_song is not an int")
        test8 = '{"response": {"next_page": 2}}'
        result1, result2 = get_songs.parse_song_response(test8, 10)
        self.assertEqual([], result1, "Case with correct next_song")
        self.assertEqual(2, result2, "Case with correct next_song")
        test9 = '{"response": {"songs": [{"title": "test", "primary_artist": {"id": 10}}, {"title": "test2", "primary_artist": {"id": 9}}], "next_page": 2}}'
        result1, result2 = get_songs.parse_song_response(test9, 10) 
        self.assertEqual(["test"], result1, "Case with proper response")
        self.assertEqual(2, result2, "Case with proper response")
        
if __name__ == '__main__':
    unittest.main()
