from flask_restful import Resource, request, marshal_with, fields
from flask import jsonify
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong
from application.models import album_schema, song_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
import os
from application.delete_file import delete_file
from instances import app, db, cache
from sqlalchemy import func, case
import uuid
from .analytics import creatorStatistics
class AlbumSongResource(Resource):
    @jwt_required()
    def post(self, album_id, song_id):
        album = Album.query.get_or_404(album_id)
        song = Song.query.get_or_404(song_id)

        albumSong = AlbumSong.query.filter(AlbumSong.album_id == album_id, AlbumSong.song_id == song_id).first()
        if albumSong or album.user_id != get_jwt_identity():
            return {"message": "Invalid user or song"}, 406

        album.songs.append(song)
        db.session.add(album)
        db.session.commit()

        return {'song': song_schema.dump(song)}
    
    @jwt_required()
    def delete(self, album_id, song_id):
        album = Album.query.get_or_404(album_id)
        albumSong = AlbumSong.query.filter(AlbumSong.album_id == album_id, AlbumSong.song_id == song_id).first()
        if albumSong and album.user_id == get_jwt_identity():
            db.session.delete(albumSong)
            db.session.commit()
            return {"message": "Success"}, 202
        else:
            return {"message": "Invalid"}, 401
        
           
def delete_album(album_id):
    get_album = Album.query.get_or_404(album_id)
    
    get_album.songs = []
    if get_album.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_album.image))

    db.session.delete(get_album)
    db.session.commit()


class AlbumResource(Resource):
    @jwt_required()
    def post(self):
        image = request.files['image']
        form = request.form

        if image.filename=='':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        
        empty = ['', None, ' ']

        album = Album(creator_id = get_jwt_identity()) 

        if 'title' in form and form.get('title') not in empty :
            album.title = form.get('title')
        else:
            return {"message": "Invalid title"}, 400
        
        album.description = form.get('description') if form.get('description') not in empty else None

        if image_filename:
            album.image = image_filename
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
        cache.delete_memoized(creatorStatistics, get_jwt_identity())
        db.session.add(album)
        db.session.commit()

        return {"message": "Success", "album": album_schema.dumps(album)}

    @jwt_required()
    def put(self, album_id):
        image = request.files['image']
        album = Album.query.get_or_404(int(album_id))
        if get_jwt_identity() != album.creator_id:
            return {"message": "Invalid user"}, 406
        empty = ['', None, ' ']

        if request.form.get('title') not in empty :
            album.title = request.form['title'] 

        if image.filename=='':
            image_filename =  None
        else:
            if album.image:
                delete_file(os.path.join(app.config['IMAGE_FOLDER'] , album.image))
            
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
            album.image = image_filename
        
        album.description = request.form['description'] if request.form['description'] not in empty else None

        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                    
        db.session.add(album)
        db.session.commit()

        return {"message": "Success", "album": album_schema.dumps(album)}
    
    @jwt_required()
    def delete(self, album_id):
        album = Album.query.get_or_404(album_id)
        if get_jwt_identity()!= album.creator_id or get_jwt()['user_type'] != 'ADMIN':
            return jsonify({"message": "wrong user"}), 403
        delete_album(album_id)
        return {"message": "Success"}

    @jwt_required()
    def get(self):
        if request.args.get('album_id'):
            album = Album.query.get_or_404(int(request.args.get('album_id')))
            if get_jwt_identity()!= album.creator_id :
                return jsonify({"message": "invalid user"}), 403
            return {"album": album_schema.dump(album)}
        
        query = Album.query.filter(Album.creator_id == get_jwt_identity())
        if request.args.get('title'):
            query = query.filter(Album.title.ilike(f'%{request.args.get("title")}%'))
        if request.args.get('creator_id'):
            query = query.filter(Album.creator_id == request.args.get('creator_id'))

        res = query.all()
        if not res:
            return jsonify({"message": "not found"}), 404
        return {"album": album_schema.dump(res)}