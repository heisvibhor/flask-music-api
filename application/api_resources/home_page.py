from flask_restful import Resource
from application.models import Song, Playlist, SongLikes,  Album
from application.models import many_playlist_schema, song_schema, CreatorLikes, many_album_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
from sqlalchemy import func, case
from instances import db, cache
from application.contollers import user
class HomePageResource(Resource):
    @jwt_required()
    @user
    def get(self):
        return self.getter(current_user.language, current_user.id)
    @cache.memoize(timeout=300)
    def getter(self, language, id):
        base_query = db.select(Song, 
                                    (func.sum(CreatorLikes.rating * CreatorLikes.rating_count)/func.sum(CreatorLikes.rating_count)), 
                                    func.sum(CreatorLikes.likes).label('likes')
                                    ).join(CreatorLikes , CreatorLikes.song_id == Song.id,isouter=True
                                           ).group_by(Song.id).order_by(case(
        (Song.language == language, 0),
        else_ = 1
        )).limit(10)

        data = {}
        query = base_query.join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Song.id).order_by(func.avg(CreatorLikes.rating * CreatorLikes.rating_count).desc())
        data['top_rated'] = [{'song': song_schema.dump(r[0]), 'rating':r[1], 'likes': r[2]} for r in db.session.execute(query).all()]
        # print(data['top_rated'])
        query1 = base_query.order_by(Song.views.desc())
        data['top_views'] = [{'song': song_schema.dump(r[0]), 'rating':r[1], 'likes': r[2]} for r in db.session.execute(query1).all()]

        query2 = base_query.order_by(Song.created_at.desc()).order_by(Song.views)
        data['recently_added'] = [{'song': song_schema.dump(r[0]), 'rating':r[1], 'likes': r[2]} for r  in db.session.execute(query2).all()]

        query3 = Album.query.order_by(Album.created_at.desc()).limit(10)
        data['albums'] = many_album_schema.dump(query3.all())

        query4 = Playlist.query.order_by(Playlist.created_at.desc()).filter(Playlist.user_id == id)
        data['playlists'] = many_playlist_schema.dump(query4.all())
        return data