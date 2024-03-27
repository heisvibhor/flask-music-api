from flask_restful import Resource, request, marshal_with, fields
from flask import jsonify
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong
from application.models import playlist_schema, song_likes_schema, creator_schema, song_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
import os
from instances import app, db
import uuid
from application.contollers import user
from application.delete_file import delete_file

class PlaylistSongResource(Resource):
    @jwt_required()
    @user
    def post(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.get_or_404(song_id)

        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist or playlist.user_id != get_jwt_identity():
            return {"message": "Song already exists or Invalid user"}, 406

        playlist.songs.append(song)
        db.session.add(playlist)
        db.session.commit()

        return {'song': song_schema.dump(song)}
    
    @jwt_required()
    def delete(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist and playlist.user_id == get_jwt_identity():
            db.session.delete(songplaylist)
            db.session.commit()
            return {"message": "Success"}, 200
        else:
            return {"message": "Invalid"}, 400
        
def delete_playlist(playlist_id):
    get_playlist = Playlist.query.get_or_404(playlist_id)
    
    get_playlist.songs = []
    if get_playlist.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_playlist.image))

    db.session.delete(get_playlist)
    db.session.commit()


class PlaylistResource(Resource):
    @jwt_required()
    def post(self):
        image = request.files.get('image')
        form = request.form

        if not image or image.filename=='':
            image_filename = None
        else:
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        
        empty = ['', None, ' ']

        playlist = Playlist(user_id = get_jwt_identity()) 

        if 'title' in form and form.get('title') not in empty :
            playlist.title = form.get('title')
        else:
            return {"message": "Invalid title"}, 400
        
        playlist.description = form.get('description') if form.get('description') not in empty else None

        if image_filename:
            playlist.image = image_filename
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                    
        db.session.add(playlist)
        db.session.commit()

        return {"message": "Success", "playlist": playlist_schema.dump(playlist)}

    @jwt_required()
    def put(self, playlist_id):
        image = request.files.get('image')
        playlist = Playlist.query.get_or_404(int(playlist_id))
        if get_jwt_identity() != playlist.user_id:
            return {"message": "Invalid user"}, 406
        empty = ['', None, ' ']

        if request.form.get('title') not in empty :
            playlist.title = request.form['title'] 

        if not image or image.filename=='':
            image_filename =  None
        else:
            if playlist.image:
                delete_file(os.path.join(app.config['IMAGE_FOLDER'] , playlist.image))
            
            image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
            playlist.image = image_filename
        
        playlist.description = request.form['description'] if request.form['description'] not in empty else None

        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                    
        db.session.add(playlist)
        db.session.commit()

        return {"playlist": playlist_schema.dump(playlist), "message": "Success"}
    
    @jwt_required()
    def delete(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        if get_jwt_identity()!= playlist.user_id :
            return jsonify({"message": "wrong user"}), 403
        delete_playlist(playlist_id)
        return {"message": "Success"}

    @jwt_required()
    @user
    def get(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        if get_jwt_identity()!= playlist.user_id :
            return jsonify({"message": "invalid user"}), 403
        return {"playlist": playlist_schema.dump(playlist)}
        
    