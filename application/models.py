from sqlalchemy.orm import Mapped, relationship
from instances import db, ma
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    user_type: Mapped[str] = mapped_column(db.CheckConstraint('user_type in ("USER", "CREATOR", "ADMIN")'),
                                           default="USER")
    playlists: Mapped[list["Playlist"]] = relationship(
        back_populates='user', cascade="save-update")
    language: Mapped[str] = mapped_column(
        db.ForeignKey("language.name"), nullable=False)
    image: Mapped[str] = mapped_column()
    likes: Mapped[list["SongLikes"]] = relationship(
        back_populates='user', cascade="save-update")


class Creator(db.Model):
    id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), primary_key=True, )
    artist: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=db.sql.func.now())
    disabled: Mapped[bool] = mapped_column(default=False)
    policy_violate: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    songs: Mapped[list["Song"]] = relationship(
        back_populates='creator', cascade="save-update")
    albums: Mapped[list["Album"]] = relationship(
        back_populates='creator', cascade="save-update")
    user: Mapped["User"] = relationship()


class SongLikes(db.Model):

    song_id: Mapped[int] = mapped_column(db.ForeignKey(
        "song.id"), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey(
        "user.id"), primary_key=True, nullable=False)
    like: Mapped[bool] = mapped_column(default=False)
    rating: Mapped[int] = mapped_column(default=0)
    song: Mapped["Song"] = relationship(back_populates='likes')  # child
    user: Mapped["User"] = relationship(back_populates='likes')  # parent


class CreatorLikes(db.Model):
    song_id: Mapped[int] = mapped_column(db.ForeignKey(
        "song.id"), primary_key=True, nullable=False)
    creator_id: Mapped[int] = mapped_column(
        db.ForeignKey("creator.id"), nullable=False)
    like_date: Mapped[date] = mapped_column(server_default=db.sql.func.now())
    likes: Mapped[int] = mapped_column(default=0)
    views: Mapped[int] = mapped_column(default=0)
    unlikes: Mapped[int] = mapped_column(default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    rating: Mapped[float] = mapped_column(default=0)


class Song(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[int] = mapped_column(
        db.ForeignKey("creator.id"), nullable=False)
    lyrics: Mapped[str] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=db.sql.func.now())
    audio: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    views: Mapped[int] = mapped_column(default=0)
    genre: Mapped[str] = mapped_column(
        db.ForeignKey("genre.name"), nullable=False)
    language: Mapped[str] = mapped_column(
        db.ForeignKey("language.name"), nullable=False)
    albums: Mapped[list["Album"]] = relationship(secondary='album_song', back_populates='songs',
                                                 primaryjoin="Album.id == AlbumSong.album_id")
    likes: Mapped[list["SongLikes"]] = relationship(
        back_populates='song', cascade="save-update")
    creator: Mapped["Creator"] = relationship(
        back_populates='songs', cascade="save-update")


class Playlist(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=db.sql.func.now())
    image: Mapped[str] = mapped_column()
    songs: Mapped[list["Song"]] = relationship(secondary='song_playlist',
                                               primaryjoin="Playlist.id == SongPlaylist.playlist_id")

    user: Mapped["User"] = relationship(
        back_populates='playlists', cascade="save-update")


class Album(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[int] = mapped_column(
        db.ForeignKey("creator.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=db.sql.func.now())
    image: Mapped[str] = mapped_column()
    songs: Mapped[list["Song"]] = relationship(secondary='album_song', back_populates='albums',
                                               primaryjoin="Album.id == AlbumSong.album_id")

    creator: Mapped["Creator"] = relationship(
        back_populates='albums', cascade="save-update")


class SongPlaylist(db.Model):
    song_id: Mapped[int] = mapped_column(db.ForeignKey(
        "song.id"), primary_key=True, nullable=False)
    playlist_id: Mapped[int] = mapped_column(db.ForeignKey(
        "playlist.id"), primary_key=True, nullable=False)


class AlbumSong(db.Model):
    song_id: Mapped[int] = mapped_column(db.ForeignKey(
        "song.id"), primary_key=True, nullable=False)
    album_id: Mapped[int] = mapped_column(db.ForeignKey(
        "album.id"), primary_key=True, nullable=False)


class Genre(db.Model):
    name: Mapped[str] = mapped_column(primary_key=True)


class Language(db.Model):
    name: Mapped[str] = mapped_column(primary_key=True)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    id = ma.auto_field()
    email = ma.auto_field()
    user_type = ma.auto_field()
    language = ma.auto_field()
    image = ma.auto_field()
    name = ma.auto_field()


class CreatorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Creator
    id = ma.auto_field()
    artist = ma.auto_field()
    created_at = ma.auto_field()
    disabled = ma.auto_field()
    policy_violate = ma.auto_field()
    image = ma.auto_field()
    user = fields.Nested(UserSchema(only=("id", "email", "image")))


class CreatorLikesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CreatorLikes
    song_id = ma.auto_field()
    creator_id = ma.auto_field()
    like_date = ma.auto_field()
    likes = ma.auto_field()
    views = ma.auto_field()
    unlikes = ma.auto_field()
    rating_count = ma.auto_field()
    rating = ma.auto_field()


class SongLikesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SongLikes
    song_id = ma.auto_field()
    user_id = ma.auto_field()
    like = ma.auto_field()
    rating = ma.auto_field()
    song = ma.auto_field()
    user = ma.auto_field()


class SongSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Song
    id = ma.auto_field()
    title = ma.auto_field()
    description = ma.auto_field()
    creator_id = ma.auto_field()
    lyrics = ma.auto_field()
    created_at = ma.auto_field()
    audio = ma.auto_field()
    image = ma.auto_field()
    views = ma.auto_field()
    genre = ma.auto_field()
    language = ma.auto_field()
    creator = fields.Nested(CreatorSchema(only=("id", "artist", "image")))


class PlaylistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Playlist
    id = ma.auto_field()
    title = ma.auto_field()
    description = ma.auto_field()
    user_id = ma.auto_field()
    created_at = ma.auto_field()
    image = ma.auto_field()
    songs = fields.Nested(SongSchema())
    user = fields.Nested(UserSchema(only=("id", "image")))


class AlbumSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Album
    id = ma.auto_field()
    title = ma.auto_field()
    description = ma.auto_field()
    creator_id = ma.auto_field()
    created_at = ma.auto_field()
    image = ma.auto_field()
    songs = fields.Nested(SongSchema())
    creator = fields.Nested(CreatorSchema(only=("id", "image", "artist")))


class SongPlaylistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SongPlaylist
    song_id = ma.auto_field()
    playlist_id = ma.auto_field()


class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre
    name = ma.auto_field()


class LanguageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Language
    name = ma.auto_field()


user_schema = UserSchema()
creator_schema = CreatorSchema()
creator_likes_schema = CreatorLikesSchema()
song_likes_schema = SongLikesSchema()
song_schema = SongSchema()
playlist_schema = PlaylistSchema()
album_schema = AlbumSchema()
song_playlist_schema = SongPlaylistSchema()
genre_schema = GenreSchema()
language_schema = LanguageSchema()

many_user_schema = UserSchema(many=True)
many_creator_schema = CreatorSchema(many=True)
many_creator_likes_schema = CreatorLikesSchema(many=True)
many_song_likes_schema = SongLikesSchema(many=True)
many_song_schema = SongSchema(many=True)
many_playlist_schema = PlaylistSchema(many=True)
many_album_schema = AlbumSchema(many=True)
many_song_playlist_schema = SongPlaylistSchema(many=True)
many_genre_schema = GenreSchema(many=True)
many_language_schema = LanguageSchema(many=True)
