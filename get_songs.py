import json
import os
import requests
import sys
from dotenv import load_dotenv

def get_token():
    load_dotenv()
    return os.getenv('ACCESS_TOKEN')


# Raises: requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout
def search(artist):
    with requests.Session() as s:
        s.headers.update({'Authorization': "Bearer %s" % get_token()})
        response = s.get('https://api.genius.com/search', params={'q': artist}, timeout=2)
        response.raise_for_status()
        return response.text


# Raises: json.JSONDecodeError
def parse_artist_id(artist, response):
    response = json.loads(response)
    if response.get('response').get('hits'):
        for hit in response['response']['hits']:
            if hit.get('result').get('primary_artist'):
                primary_artist = hit['result']['primary_artist']
                if primary_artist.get('name') and primary_artist.get('id'):
                    if primary_artist['name'].lower() == artist.lower():
                        return primary_artist['id']
    return None


def get_songs_for_id(id, page_limit=100):
    with requests.Session() as s:
        s.headers.update({'Authorization': "Bearer %s" % get_token()})
        url_base = "https://api.genius.com/artists/%s/songs" % id

        song_list = []
        current_page = 1
        while current_page:
            try:
                response = s.get(url_base, params={'page': str(current_page)}, timeout=2)
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


# Raises: json.JSONDecodeError
def parse_song_response(response, id):
    response = json.loads(response)
    song_list = []
    next_page = None

    if response.get('response'):
        response = response['response']

        if response.get('songs'):
            songs = response['songs']
            for song in songs:
                if song.get('primary_artist').get('id') == id:
                    if song.get('title'):
                        song_list.append(song['title'])

        if response.get('next_page'):
            try:
                next_page = int(response['next_page'])
            except ValueError:
                return (song_list, None)

    return (song_list, next_page)


if __name__ == "__main__":
    try:
        artist = input("Enter artist's name: ")
        response = search(artist)
        artist_id = parse_artist_id(artist, response)
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
        print("\Error: Connection to Genius timed out")

    except json.JSONDecodeError as e:
        print("\nError: Response from Genius was not a valid JSON document \nError message:")
        print(e)
    
    except Exception as e:
        print("\nAn unexpected error has occurred \nError message:")
        print(e)