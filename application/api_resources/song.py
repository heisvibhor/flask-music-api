from flask_restful import Resource, request
from application.models import Song, Playlist, SongLikes, CreatorLikes, Creator, Album, AlbumSong
from application.models import creator_likes_schema, song_schema
from application.delete_file import delete_file
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
import os
from instances import app, db, cache
from sqlalchemy import func, case
import uuid
from .analytics import creatorStatistics


def delete_song(song_id):
    get_song = Song.query.get_or_404(song_id)

    # get_song.albums = []
    # get_song.likes = []

    if get_song.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'], get_song.image))
    if get_song.audio:
        delete_file(os.path.join(app.config['AUDIO_FOLDER'], get_song.audio))

    db.session.delete(get_song)
    db.session.commit()


class SongResource(Resource):
    @jwt_required()
    def get(self):
        # claims = get_jwt()
        # print(current_user.user_type, claims, request.args, get_jwt_identity())

        if request.args.get('song_id'):
            songs_query = db.select(Song,
                                    (func.sum(CreatorLikes.rating * CreatorLikes.rating_count) /
                                     func.sum(CreatorLikes.rating_count)),
                                    func.sum(CreatorLikes.likes).label('likes')
                                    ).join(CreatorLikes, CreatorLikes.song_id == Song.id, isouter=True
                                           ).group_by(Song.id).where(Song.id == request.args.get('song_id'))
            r = db.session.execute(songs_query).fetchone()

            if not r:
                return {"message": "Song not found"}, 404
            return {'song': song_schema.dump(r[0]), 'rating': r[1], 'likes': r[2]}

        else:
            songs_query = db.select(Song,
                                    (func.sum(CreatorLikes.rating * CreatorLikes.rating_count) /
                                     func.sum(CreatorLikes.rating_count)),
                                    func.sum(CreatorLikes.likes).label('likes')
                                    ).join(CreatorLikes, CreatorLikes.song_id == Song.id, isouter=True
                                           ).group_by(Song.id)
            # print(request.args)
            empty = ['', None, 'undefined', 'null']
            if 'title' in request.args and request.args['title'] not in empty:
                songs_query = songs_query.where(
                    Song.title.ilike('%'+request.args.get('title')+'%'))
            if 'language' in request.args and request.args['language'] not in empty:
                songs_query = songs_query.where(
                    Song.language == request.args.get('language'))
            if 'genre' in request.args and request.args['genre'] not in empty:
                songs_query = songs_query.where(
                    Song.genre == request.args.get('genre'))
            if 'creator_id' in request.args and request.args['creator_id'] not in empty:
                songs_query = songs_query.where(
                    Song.creator_id == request.args.get('creator_id'))

            res = db.session.execute(songs_query).fetchall()
            print(res)
            if not res:
                return {"message": "Song not found"}, 404
            an = [{'song': song_schema.dump(
                r[0]), 'rating': r[1], 'likes': r[2]} for r in res]
            return {"data": an}

    @jwt_required()
    def put(self, song_id):
        get_song = Song.query.get_or_404(song_id)
        creator = Creator.query.get_or_404(get_jwt_identity())
        if get_jwt()['user_type'] != 'CREATOR' or creator.id != get_song.creator_id:
            return {"message": "wrong user"}, 403
        
        if not creator or creator.disabled:
            return {"message": "creator disabled"}, 403

        audio = request.files.get('audio')
        image = request.files.get('image')

        if not audio or audio.filename == '':
            audio_filename = None
        else:
            if get_song.audio:
                delete_file(os.path.join(
                    app.config['AUDIO_FOLDER'], get_song.audio))

            audio_filename = 'a' + str(uuid.uuid4()) + \
                '.' + audio.filename.split('.')[-1]
            get_song.audio = audio_filename

        if not image or image.filename == '':
            image_filename = None
        else:
            if get_song.image:
                delete_file(os.path.join(
                    app.config['IMAGE_FOLDER'], get_song.image))

            image_filename = 'a' + str(uuid.uuid4()) + \
                '.' + image.filename.split('.')[-1]
            get_song.image = image_filename

        empty = ['', None, ' ']
        if request.form['title'] not in empty:
            get_song.title = request.form['title']
        else:
            return {"message": "invalid input"}, 406

        if 'lyrics' in request.form:
            get_song.lyrics = request.form.get('lyrics')
        if 'description' in request.form:
            get_song.description = request.form.get('description')
        if 'genre' in request.form:
            get_song.genre = request.form.get('genre')
        if 'language' in request.form:
            get_song.language = request.form.get('language')

        if audio_filename:
            audio.save(os.path.join(
                app.config['AUDIO_FOLDER'], audio_filename))
        if image_filename:
            image.save(os.path.join(
                app.config['IMAGE_FOLDER'], image_filename))

        db.session.add(get_song)
        db.session.commit()

        return {"message": "Updated succesfully", "song": song_schema.dump(get_song)}, 200

    @jwt_required()
    def delete(self, song_id):
        if get_jwt()['user_type'] == 'ADMIN':
            song = Song.query.get_or_404(song_id)
            delete_song(song_id)
            return {"message": 'Deleted succesfully'}, 200
        
        song = Song.query.get_or_404(song_id)
        if not (get_jwt()['user_type'] == 'CREATOR' and get_jwt_identity() == song.creator_id):
            return {"message": "wrong user"}, 403
        creator = Creator.query.get_or_404(current_user.id)
        if not creator or creator.disabled:
            return {"message": "creator disabled"}, 403
        delete_song(song_id)
        return {"message": 'Deleted succesfully'}, 200

    @jwt_required()
    def post(self):
        if get_jwt()['user_type'] != 'CREATOR':
            return {"message": "wrong user"}, 403
        creator = Creator.query.get_or_404(get_jwt_identity())
        if not creator or creator.disabled:
            return {"message": "creator disabled"}, 403

        audio = request.files.get('audio')
        image = request.files.get('image')

        if not audio or audio.filename == '':
            audio_filename = None
        else:
            audio_filename = 'a' + str(uuid.uuid4()) + \
                '.' + audio.filename.split('.')[-1]
        if not image or image.filename == '':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) + \
                '.' + image.filename.split('.')[-1]

        empty = ['', None, ' ']

        new_song = Song(audio=audio_filename, image=image_filename,
                        creator_id=get_jwt_identity())
        if request.form.get('title') in empty:
            return {"message": "invalid input"}, 406
        new_song.title = request.form.get('title')

        if 'lyrics' in request.form:
            new_song.lyrics = request.form.get('lyrics')
        if 'description' in request.form:
            new_song.description = request.form.get('description')
        if 'genre' in request.form:
            new_song.genre = request.form.get('genre')
        if 'language' in request.form:
            new_song.language = request.form.get('language')

        if not (new_song.audio or new_song.lyrics):
            return {"message": "Both audio and lyrics cannot be empty"}, 406

        if audio_filename:
            audio.save(os.path.join(
                app.config['AUDIO_FOLDER'], audio_filename))
        if image_filename:
            image.save(os.path.join(
                app.config['IMAGE_FOLDER'], image_filename))
        cache.delete_memoized(creatorStatistics, get_jwt_identity())
        db.session.add(new_song)
        db.session.commit()

        return {"message": 'Added succesfully', "song": song_schema.dump(new_song)}, 200
