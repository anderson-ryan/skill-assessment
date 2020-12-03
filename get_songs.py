import json
import os
import requests
from dotenv import load_dotenv

def get_token():
    load_dotenv()
    return os.getenv('ACCESS_TOKEN')


def get_nested_key(doc, names):
    for name in names:
        if doc.get(name):
            doc = doc[name]
        else:
            return None
    return doc


# Raises: requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout
def search(artist, timeout=5):
    with requests.Session() as s:
        s.headers.update({'Authorization': "Bearer %s" % get_token()})
        response = s.get('https://api.genius.com/search', params={'q': artist}, timeout=timeout)
        response.raise_for_status()
        return response.text


# Raises: json.decoder.JSONDecodeError
def parse_artist_id(response, artist):
    response = json.loads(response)

    hits = get_nested_key(response, ['response', 'hits'])
    if type(hits) is list:
        for hit in hits:
            primary_artist = get_nested_key(hit, ['result','primary_artist'])
            if primary_artist and primary_artist.get('name') and primary_artist.get('id'):
                if str(primary_artist.get('name')).lower() == artist.lower():
                    return primary_artist.get('id')

    return None


def get_songs_for_id(id, page_limit=100, timeout=5):
    with requests.Session() as s:
        s.headers.update({'Authorization': "Bearer %s" % get_token()})
        url_base = "https://api.genius.com/artists/%s/songs" % id

        song_list = []
        current_page = 1
        while current_page:
            try:
                response = s.get(url_base, params={'page': str(current_page)}, timeout=timeout)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                return (song_list, "Connection to Genius timed out")
            except requests.exceptions.ConnectionError:
                return (song_list, "Could not connect to Genius")
            except requests.exceptions.HTTPError:
                return (song_list, "HTTP Error %s" % response.status_code)
            else:
                try:
                    songs, next_page = parse_song_response(response.text, id)
                    song_list.extend(songs)

                    if next_page and next_page > current_page and next_page < page_limit:
                        current_page = next_page
                    elif next_page and next_page >= page_limit:
                        return (song_list, 'Reached page limit')
                    else:
                        current_page = None

                except json.JSONDecodeError:
                    return (song_list, 'Malformed response from Genius')
            

        return (song_list, None)


# Raises: json.decoder.JSONDecodeError
def parse_song_response(response, id):
    response = json.loads(response)
    song_list = []
    next_page = None

    songs = get_nested_key(response, ['response', 'songs'])
    if type(songs) is list:
        for song in songs:
            title = song.get('title')
            if title and get_nested_key(song, ['primary_artist', 'id']) == id:
                song_list.append(title)

    page = get_nested_key(response, ['response', 'next_page'])
    if page:
        try:
            next_page = int(page)
        except ValueError:
            return (song_list, None)

    return (song_list, next_page)


if __name__ == "__main__":
    try:
        artist = input("Enter artist's name: ")
        response = search(artist)
        artist_id = parse_artist_id(response, artist)
        if not artist_id:
            print("\nGenius could not find artist: %s" % artist)
        else:
            print("Retrieving song list from Genius. Please wait...")
            songs, error_message = get_songs_for_id(artist_id)

            if error_message:
                if len(songs) > 0:
                    print("\nUnable to retrieve entire song list")
                    print("Reason: %s" % error_message)
                    print(songs)
                else:
                    print("\nUnable to retrieve song list")
                    print("Reason: %s" % error_message)
            else:
                print("")
                print(songs)

    except requests.exceptions.HTTPError as e:
        print("\nError: Bad HTTP request \nError message:")
        print(e)

    except requests.exceptions.ConnectionError as e:
        print("\nError: Unable to connect to Genius \nError message:")
        print(e)
    
    except requests.exceptions.Timeout as e:
        print("\nError: Connection to Genius timed out")

    except json.decoder.JSONDecodeError as e:
        print("\nError: Response from Genius was not a valid JSON document")
    
    except Exception as e:
        print("\nAn unexpected error has occurred \nError message:")
        print(e)