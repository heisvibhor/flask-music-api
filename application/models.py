from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import ForeignKey
from instances import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    user_type = db.Column(db.String, db.CheckConstraint('user_type in ("USER", "CREATOR", "ADMIN")'), default = "USER")
    playlists = db.relationship('Playlist', backref = 'user')
    language = db.Column(db.String, db.ForeignKey("language.name"), nullable=False)
    image = db.Column(db.String)
    likes : Mapped[list["SongLikes"]] = relationship(back_populates='user', cascade="save-update")

class Creator(db.Model):
    __tablename__ = 'creator'
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, )
    artist = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    disabled = db.Column(db.Boolean, default = False)
    policy_violate = db.Column(db.String)
    image = db.Column(db.String)
    songs = db.relationship('Song', backref = 'creator')

class SongLikes(db.Model):
    __tablename__ = "song_likes"
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    song : Mapped["Song"]  = relationship( back_populates='likes') # child
    user : Mapped["User"]  = relationship( back_populates='likes') # parent
    like = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer, default=0)

class Song(db.Model):
    __tablename__ = 'song'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id"), nullable=False)
    lyrics = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    audio = db.Column(db.String)
    image = db.Column(db.String)
    views = db.Column(db.Integer, default=0)
    genre = db.Column(db.String, db.ForeignKey("genre.name"), nullable=False)
    language = db.Column(db.String, db.ForeignKey("language.name"), nullable=False)
    playlists : Mapped[list["Playlist"]] = relationship(secondary='song_playlist', back_populates='songs', cascade="save-update", primaryjoin="Song.id == SongPlaylist.song_id")
    likes : Mapped[list["SongLikes"]] = relationship( back_populates='song', cascade="save-update")
class Playlist(db.Model):
    __tablename__ = 'playlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable = False)
    is_album = db.Column(db.Boolean, default = False)
    description = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    image = db.Column(db.String)
    songs: Mapped[list["Song"]]  = relationship(secondary='song_playlist', back_populates='playlists', primaryjoin="Playlist.id == SongPlaylist.playlist_id")
    
class SongPlaylist(db.Model):
    __tablename__ = "song_playlist"
    song_id = db.Column(db.Integer, ForeignKey("song.id"), primary_key=True, nullable=False)
    playlist_id = db.Column(db.Integer, ForeignKey("playlist.id"), primary_key=True, nullable=False)

class Genre(db.Model):
    __tablename__ = "genre"
    name = db.Column(db.String, nullable = False, primary_key=True)

class Language(db.Model):
    __tablename__ = "language"
    name = db.Column(db.String, nullable = False, primary_key=True)