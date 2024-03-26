from flask_restful import Resource, request
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong
from application.models import song_likes_schema, CreatorLikes, creator_likes_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
from sqlalchemy import and_
from instances import db, cache, app
from datetime import date


class SongLikeRateResource(Resource):
    @jwt_required()
    def get(self, song_id):
        Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id,
                                               SongLikes.user_id == get_jwt_identity())).first()
        if not songLike:
            songLike = SongLikes(
                song_id=song_id, user_id=get_jwt_identity(), like=False, rating=0)
            db.session.add(songLike)
            db.session.commit()

        return {"songlike": song_likes_schema.dump(songLike)}

    @jwt_required()
    def put(self, song_id):
        song = Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id,
                                               SongLikes.user_id == get_jwt_identity())).first()
        creator_like = CreatorLikes.query.filter(and_(CreatorLikes.song_id == song_id,
                                                      CreatorLikes.like_date == date.today())).first()
        if not songLike:
            songLike = SongLikes(
                song_id=song_id, user_id=get_jwt_identity(), rating=0)

        if not creator_like:
            creator_like = CreatorLikes(
                creator_id=song.creator_id,
                like_date=date.today(),
                song_id=song_id,
                likes=0)

        if request.form.get('like') == "true" and not songLike.like:
            if creator_like.rating_count:
                creator_like.rating_count += 1
            else:
                creator_like.rating_count = 1
            creator_like.likes += 1
        songLike.like = True if request.form.get('like') == "true" else False

        if request.form.get('rating') and int(request.form.get('rating')) <= 5 and int(request.form.get('rating')) > 0:
            songLike.rating = int(request.form.get('rating'))
            if creator_like.rating_count:
                creator_like.rating_count += 1
            else:
                creator_like.rating_count = 1
            if not creator_like.rating:
                creator_like.rating = songLike.rating
            else:
                creator_like.rating = (creator_like.rating * creator_like.rating_count +
                                       songLike.rating) / (creator_like.rating_count + 1)

        db.session.add_all([creator_like, songLike])
        db.session.commit()

        return {"songlike": song_likes_schema.dump(songLike)}

    @jwt_required()
    def post(self, song_id):
        song = Song.query.get_or_404(song_id)
        songLike = SongLikes.query.filter(and_(SongLikes.song_id == song_id,
                                               SongLikes.user_id == get_jwt_identity())).first()
        creator_like = CreatorLikes.query.filter(and_(CreatorLikes.song_id == song_id,
                                                      CreatorLikes.like_date == date.today())).first()
        if not songLike:
            songLike = SongLikes(
                song_id=song_id, user_id=get_jwt_identity(), rating=0)

        if not creator_like:
            creator_like = CreatorLikes(
                creator_id=song.creator_id,
                like_date=date.today(),
                song_id=song_id,
                likes=0)

        if request.form.get('like') == "true" and not songLike.like:
            if creator_like.rating_count:
                creator_like.rating_count += 1
            else:
                creator_like.rating_count = 1
            creator_like.likes += 1
        songLike.like = True if request.form.get('like') == "true" else False

        if request.form.get('rating') and int(request.form.get('rating')) <= 5 and int(request.form.get('rating')) > 0:
            songLike.rating = int(request.form.get('rating'))
            if creator_like.rating_count:
                creator_like.rating_count += 1
            else:
                creator_like.rating_count = 1
            if not creator_like.rating:
                creator_like.rating = songLike.rating
            else:
                creator_like.rating = (creator_like.rating * creator_like.rating_count +
                                       songLike.rating) / (creator_like.rating_count + 1)

        db.session.add_all([creator_like, songLike])
        db.session.commit()

        return {"songlike": song_likes_schema.dump(songLike)}


@cache.memoize(60)
def add_view(song_id, user_id):
    song = Song.query.get_or_404(song_id)
    creator_like = CreatorLikes.query.filter(and_(CreatorLikes.song_id == song_id,
                                                  CreatorLikes.like_date == date.today())).first()
    if not creator_like:
        creator_like = CreatorLikes(
            creator_id=song.creator_id,
            like_date=date.today(),
            song_id=song_id,
            views=1)
    song.views += 1
    db.session.add_all([song, creator_like])
    db.session.commit()
    return {"message": "Success"}


@app.route("/api/view/<int:song_id>", methods=['GET'])
@jwt_required()
def add_views(song_id):
    return add_view(song_id, get_jwt_identity())
