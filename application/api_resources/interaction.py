from flask_restful import Resource, request
from flask import jsonify
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong
from application.models import playlist_schema, song_likes_schema, creator_schema, song_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
from sqlalchemy import and_
from instance import db, cache, app
class SongLikeRateResource(Resource):
    @jwt_required()
    def get(song_id):
        Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id, 
                                               SongLikes.user_id == get_jwt_identity()))
        if not songLike:
            songLike = SongLikes(song_id = song_id, user_id = get_jwt_identity(),like = False, rating = 0)
            db.session.add(songLike)
            db.session.commit()
            
        return {"songlike": song_likes_schema.dump(songLike)}
        
    @jwt_required()
    def put(song_id):
        Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id, 
                                               SongLikes.user_id == get_jwt_identity()))
        if not songLike:
            songLike = SongLikes(song_id = song_id, user_id = get_jwt_identity(), rating = 0)

        songLike.like = True if request.args.get('like')=="true" else False
        if request.args.get('rating') and request.args.get('rating')<=5 and request.args.get('rating')>0:
            songLike.rating = request.args.get('rating') 
        db.session.add(songLike)
        db.session.commit()
            
        return {"songlike": song_likes_schema.dump(songLike)}
    @jwt_required()
    def post(song_id):
        Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id, 
                                               SongLikes.user_id == get_jwt_identity()))
        if not songLike:
            songLike = SongLikes(song_id = song_id, user_id = get_jwt_identity(), rating = 0)

        songLike.like = True if request.args.get('like')=="true" else False
        if request.args.get('rating') and request.args.get('rating')<=5 and request.args.get('rating')>0:
            songLike.rating = request.args.get('rating') 
        db.session.add(songLike)
        db.session.commit()
            
        return {"songlike": song_likes_schema.dump(songLike)}
    
@cache.memoize()
def add_view(song_id, user_id):
    song = Song.query.get_or_404(song_id)
    song.views += 1
    db.session.add(song)
    db.session.commit()
    return {"message": "Success"}

@app.route("/api/view/<int:song_id>")
def add_views(song_id):
    return add_view(song_id, get_jwt_identity())