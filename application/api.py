from flask_restful import Api
from flask_restful import current_app as app
# from .api_resources.song import songPlaylistResourse, albumSongSearchResource, songSearchResource
# from .api_resources.artist import artistSearchResource
# from .api_resources.album import albumSearchResource

api = Api(app)
# api.add_resource(songPlaylistResourse, '/api/playlist/<int:playlist_id>/<int:song_id>')
# api.add_resource(albumSongSearchResource, '/api/album/song/search')
# api.add_resource(songSearchResource, '/api/song/search', '/api/song/delete/<int:song_id>')
# api.add_resource(artistSearchResource, '/api/artist/search')
# api.add_resource(albumSearchResource, '/api/album/search', '/api/playlist/delete/<int:album_id>')