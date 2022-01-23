import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import oauth2
from decouple import config
import sys
from funcy import chunks


# функция для авторизации в Spotify
def autorisation():
    # получение клиент айди приложения из переменных окружения
    client_id = config('CLIENT_ID')
    # получение секретный ключ приложения из переменных окружения
    client_secret = config('CLIENT_SECRET')
    # разрешения нашего приложения
    scope = ('user-library-read, playlist-read-private, playlist-modify-private, playlist-modify-public, user-read-private, user-library-modify, user-library-read')
    # URL, на который переадресуется браузер пользователя после получения прав доступа при получении ключа доступа
    redirect_uri = 'http://localhost:8888/callback/'
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    code = sp_oauth.get_auth_response(open_browser=True)
    # получаем токен
    token = sp_oauth.get_access_token(code, as_dict=False)
    sp = spotipy.Spotify(auth=token)
    # id пользователя Spotify
    username = sp.current_user()['id']
    # возвращаем объект спотифай и пользователя
    return sp, username


# функция, получающая id трека
def get_track_id(query, sp):
    # получаем данные по первому треку из поисковой выдачи Spotify
    track_id = sp.search(q=query, limit=1, type='track')
    # Теперь найдем id первого трека из поисковой выдачи.
    if len(track_id['tracks']['items']) > 0:
        return track_id['tracks']['items'][0]['id']
    return None


def get_music_queries(file_name: str) -> []:
    # открываем файл на чтение
    with open(file_name, 'r', encoding='UTF-8') as file:
        # получаем список по строкам их файла
        new = file.read().split('\n')
        new.reverse()

        output = []
        lenght = len(new)

        if lenght < 3:
            return output

        for i in range(1, lenght, 2):
            track = new[i][11:].split('-')
            output.append(track[1] + " " + track[0])

        return output


def get_list_of_track_ids_by_100(filename, sp):
    # получаем все запросы
    queries = get_music_queries(filename)
    new_spotify_playlist_tracks_id = []
    for query in queries:
        spotify_track_id = get_track_id(query, sp)
        if spotify_track_id is None:
            print(f"Track {query} not found")
        else:
            new_spotify_playlist_tracks_id.append(spotify_track_id)

    return list(chunks(100, new_spotify_playlist_tracks_id))


def transfer(filename):
    # авторизуемся в Spotify
    sp, username = autorisation()
    # создадим в Spotify плейлист с именем (playlist_name)
    create_spotify_playlist = sp.user_playlist_create(username, "TransferMusic")
    # получим id созданного плейлиста
    new_spotify_playlist_id = create_spotify_playlist['id']

    new_spotify_playlist_tracks_id = get_list_of_track_ids_by_100(filename, sp)

    for track_list in new_spotify_playlist_tracks_id:
        # если список треков не пуст
        if len(track_list) > 0:
            # добавляем все песни в плей лист
            add_tracks_in_playlist(new_spotify_playlist_id, track_list, sp)


def add_tracks_in_playlist(playlist_id, tracks_id, sp):
    sp.playlist_add_items(playlist_id, tracks_id)


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except:
        pass

    transfer(filename)
