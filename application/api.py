from flask_restful import Api
from flask_restful import current_app as app
from .api_resources.playlist import PlaylistResource, PlaylistSongResource
from .api_resources.interaction import SongLikeRateResource
from .api_resources.song import SongResource
from .api_resources.interaction import *
from .api_resources.home_page import HomePageResource
from .api_resources.analytics import AnalyticsResource
from .api_resources.album import AlbumResource, AlbumSongResource
from .api_resources.creator import CreatorResource
from .api_resources.user import UserResource
from .api_resources.lang_genre import LanguageResource, GenreResource

api = Api(app)
api.add_resource(PlaylistSongResource, '/api/playlist/<int:playlist_id>/<int:song_id>')
api.add_resource(SongResource, '/api/song', '/api/song/<int:song_id>')
api.add_resource(SongLikeRateResource, '/api/like_rate/<int:song_id>')
#"/api/view/<int:song_id>"
api.add_resource(AlbumResource, '/api/album', '/api/album/<int:album>')
api.add_resource(PlaylistResource, '/api/playlist', '/api/playlist/<int:playlist_id>')
api.add_resource(HomePageResource, '/api/home')
api.add_resource(AnalyticsResource, '/api/analytics')
api.add_resource(AlbumSongResource, '/api/album/<int:album>/<int:song_id>')
api.add_resource(CreatorResource, '/api/creator')
api.add_resource(UserResource, '/api/user')
api.add_resource(LanguageResource, '/api/language')
api.add_resource(GenreResource, '/api/genre')

