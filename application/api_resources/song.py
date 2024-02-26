from flask_restful import Resource, request, marshal_with, fields
from flask import jsonify
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong
from application.models import playlist_schema, song_likes_schema, creator_schema, song_schema
from application.delete_file import delete_file
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
import os
from instances import app, db
from sqlalchemy import func, case
import uuid

def delete_song(song_id):
    get_song = Song.query.get_or_404(song_id)

    get_song.playlists = []
    get_song.likes = []
    
    if get_song.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_song.image))
    if get_song.audio:
        delete_file(os.path.join(app.config['AUDIO_FOLDER'] , get_song.audio))

    db.session.delete(get_song)
    db.session.commit()

class SongResource(Resource):
    @jwt_required()
    # @marshal_with(songQueryFields)
    def get(self):
        claims = get_jwt()

        print(current_user.user_type, claims, request.args, get_jwt_identity())
        
        if request.args.get('song_id'):
            songs_query = db.select(Song, 
                                    func.avg(SongLikes.rating).label('rating'), 
                                    func.sum(case((SongLikes.like, 1) , else_=0)).label('likes')
                                    ).join(SongLikes , SongLikes.song_id == Song.id,isouter=True
                                           ).group_by(Song.id).where(Song.id==request.args.get('song_id'))
            r = db.session.execute(songs_query).fetchone()
            
            if not r:
                return {"message": "Song not found"}, 404
            return {'song': song_schema.dump(r[0]), 'rating':r[1], 'likes': r[2]}
            
        else:
            songs_query = db.select(Song, 
                                    func.avg(SongLikes.rating).label('rating'), 
                                    func.sum(case((SongLikes.like, 1) , else_=0)).label('likes')
                                    ).join(SongLikes , SongLikes.song_id == Song.id,isouter=True
                                           ).group_by(Song.id)

            if 'title' in request.args:
                songs_query = songs_query.where(Song.title.ilike('%'+request.args.get('title')+'%'))
            if 'language' in request.args:
                songs_query = songs_query.where(Song.language==request.args.get('language'))
            if 'genre' in request.args:
                songs_query = songs_query.where(Song.genre==request.args.get('genre'))
            if 'creator_id' in request.args:
                songs_query = songs_query.where(Song.creator_id==request.args.get('creator_id'))

            res = db.session.execute(songs_query).fetchall()
            print(res)
            if not res:
                return {"message": "Song not found"}, 404
            an = [{'song': song_schema.dump(r[0]), 'rating':r[1], 'likes': r[2]} for r in res]
            return {"data": an}

    @jwt_required()
    def put(self, song_id):
        if get_jwt()['user_type'] != 'CREATOR':
            return jsonify({"message": "wrong user"}), 403
        creator = Creator.query.get_or_404(get_jwt_identity())
        if creator.disabled:
            return jsonify({"message": "user disabled"}), 403

        get_song = Song.query.get_or_404(song_id)

        audio = request.files['audio']
        image = request.files['image']

        if audio.filename=='':
            audio_filename = None
        else:
            if get_song.audio:
                delete_file(os.path.join(app.config['AUDIO_FOLDER'] , get_song.audio))
            
            audio_filename = 'a' + str(uuid.uuid4()) +'.' + audio.filename.split('.')[-1]
            get_song.audio = audio_filename

        if image.filename=='':
            image_filename =  None
        else:
            if get_song.image:
                delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_song.image))
            
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
            get_song.image = image_filename
        
        empty = ['', None, ' ']

        if request.form['title'] not in empty :
            get_song.title = request.form['title'] 
        else :
            return jsonify({"message": "invalid input"}), 406
        
        if 'lyrics' in request.form:
            get_song.lyrics = request.form.get('lyrics')
        if 'description' in request.form:
            get_song.description = request.form.get('description')
        if 'genre' in request.form:
            get_song.genre = request.form.get('genre')
        if 'language' in request.form:
            get_song.language = request.form.get('language')

        if audio_filename:
            audio.save(os.path.join(app.config['AUDIO_FOLDER'] , audio_filename))
        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

        db.session.add(get_song)
        db.session.commit()
 
        return jsonify({"message": 'Updated succesfully'}), 200

    @jwt_required()
    def delete(self, song_id):
        song = Song.query.get_or_404(song_id)
        if get_jwt()['user_type'] != 'ADMIN' and not (get_jwt()['user_type'] == 'CREATOR' and get_jwt_identity()== song.creator_id)  :
            return jsonify({"message": "wrong user"}), 403
        creator = Creator.query.get_or_404(current_user.id)
        if creator.disabled:
            return jsonify({"message": "user disabled"}), 403

        delete_song(song_id)

        return jsonify({"message": 'Deleted succesfully'}), 202
    
    @jwt_required()
    def post(self):
        if get_jwt()['user_type'] != 'CREATOR':
            return jsonify({"message": "wrong user"}), 403
        creator = Creator.query.get_or_404(current_user.id)
        if creator.disabled:
            return jsonify({"message": "user disabled"}), 403

        audio = request.files['audio']
        image = request.files['image']

        if audio.filename=='':
            audio_filename = None
        else:
            audio_filename = 'a' + str(uuid.uuid4()) +'.' + audio.filename.split('.')[-1]
        if image.filename=='':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        
        empty = ['', None, ' ']

        new_song = Song(audio = audio_filename, image = image_filename)
        if request.form.get('title') in empty :
            return jsonify({"message": "invalid input"}), 406
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
            return jsonify({"message": "Both audio and lyrics cannot be empty"}), 406

        if audio_filename:
            audio.save(os.path.join(app.config['AUDIO_FOLDER'] , audio_filename))
        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

        db.session.add(new_song)
        db.session.commit()

        return jsonify({"message": 'Added succesfully', "song": song_schema.dump(new_song)}), 200