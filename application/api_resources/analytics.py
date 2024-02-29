from flask_restful import Resource
from application.models import Song, Playlist, SongLikes, SongPlaylist, Creator, Album, AlbumSong, Genre
from application.models import playlist_schema, song_schema, CreatorLikes, album_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, get_jwt
from sqlalchemy import and_, func, distinct, case
from instances import db, cache, app
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib
import os
matplotlib.use('Agg')


def get_plot(df):
    df['Color'] = np.random.choice(list(mcolors.XKCD_COLORS), df.shape[0])

    plt.bar('Genre', 'Rating', color='Color', data=df)
    plt.title('Genre wise ratings')
    plt.xlabel('Genre')
    plt.ylabel('Rating')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot.jpg'))
    plt.close()

    plt.bar('Genre', 'Views', color='Color', data=df)
    plt.title('Genre wise views')
    plt.xlabel('Genre')
    plt.ylabel('Views')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot1.jpg'))
    plt.close()

    plt.bar('Genre', 'Count', color='Color', data=df)
    plt.title('Genre wise count of songs uploaded')
    plt.xlabel('Genre')
    plt.ylabel('Count')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot2.jpg'))
    plt.close()


@cache.memoize(timeout=84600)
def creatorStatistics(creator_id):
    stats = {}
    song_count = Song.query.where(Song.creator_id == creator_id).count()
    album_count = Album.query.where(
        Album.creator_id == creator_id).count()
    query = db.select(func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating')).join(
        SongLikes, SongLikes.song_id == Song.id, isouter=True).where(Song.creator_id == creator_id)
    res = db.session.execute(query).first()

    query = db.select(func.count(SongLikes.like).label('likes')).join(
        Song, SongLikes.song_id == Song.id).where(Song.creator_id == creator_id, SongLikes.like == True)
    res1 = db.session.execute(query).first()

    query = db.select(func.count(Album.id)).join(
        AlbumSong).where(Album.creator_id == creator_id)
    res2 = db.session.execute(query).first()

    query = db.select(func.count(distinct(Playlist.id))).join(
        SongPlaylist).join(Song).where(Song.creator_id == creator_id)
    res3 = db.session.execute(query).first()

    stats['song_count'] = song_count
    stats['album_count'] = album_count
    stats['total_views'] = res[0] if res else 0
    stats['total_likes'] = res1[0] if res1 else 0
    stats['average_rating'] = res[1] if res else 0
    stats['songs_in_album'] = res2[0] if res2 else 0
    stats['playlist_with_songs'] = res3[0] if res3 else 0
    # No of playlist having some songs
    return stats


# @cache.memoize(timeout=84600)
def adminStatistics():
    stats = {}
    song_count = Song.query.count()
    album_count = Album.query.count()
    playlist_count = Playlist.query.count()

    query = db.select(func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label(
        'rating')).join(SongLikes, SongLikes.song_id == Song.id, isouter=True)
    res = db.session.execute(query).first()

    query = db.select(func.count(SongLikes.like).label(
        'likes')).where(SongLikes.like == True)
    res1 = db.session.execute(query).first()

    # Total Number of songs in playlist
    query = db.select(func.count(Playlist.id)).join(SongPlaylist)
    res3 = db.session.execute(query).first()

    query = db.select(func.count(Album.id)).join(AlbumSong)
    res2 = db.session.execute(query).first()

    query = db.select(Genre.name, func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating'), func.count(distinct(Song.id)).label(
        'count'), ).join(Song, Song.genre == Genre.name, isouter=True).join(SongLikes, SongLikes.song_id == Song.id, isouter=True).group_by(Genre.name)
    res4 = db.session.execute(query).fetchall()

    dic = [{'Genre': r[0], 'Views': r[1], 'Rating': r[2], 'Count': r[3]}
           for r in res4]
    df = pd.DataFrame(dic)
    df.fillna(0, inplace=True)
    get_plot(df)

    stats['song_count'] = song_count
    stats['album_count'] = album_count
    stats['playlist_count'] = playlist_count
    stats['total_views'] = res[0] if res else 0
    stats['total_likes'] = res1[0] if res1 else 0
    stats['average_rating'] = res[1] if res else 0
    stats['total_songs_in_albums'] = res2[0] if res2 else 0
    stats['total_songs_in_playlists'] = res3[0] if res2 else 0
    # No of playlist having some songs

    return stats





class AnalyticsResource(Resource):
    @jwt_required()
    def get(self):
        user_type = get_jwt()['user_type']
        if user_type == 'ADMIN':
            return {"analytics": adminStatistics()}

        if user_type == 'CREATOR':
            creator_id = get_jwt_identity()
            songs = Song.query.filter(Song.creator_id == creator_id).order_by(
                Song.created_at.desc()).all()
            albums = Album.query.filter(Album.creator_id == creator_id).order_by(
                Album.created_at.desc()).all()
            return {"analytics": creatorStatistics(creator_id),
                    "songs": song_schema.dump(songs),
                    "alubms": album_schema.dump(albums)}
        return {"message": "unauthorized"}, 403
