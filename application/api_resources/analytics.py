from flask_restful import Resource
from application.models import Song, Playlist, SongLikes, SongPlaylist, Album, AlbumSong, Genre, User, Creator
from application.models import Language, many_song_schema, many_album_schema
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import func, distinct
from instances import db, cache, app
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib
import os
from application.contollers import user
import datetime
matplotlib.use('Agg')

@cache.cached(timeout=86400)
def get_plot(df):
    df['Color'] = np.random.choice(list(mcolors.XKCD_COLORS), df.shape[0])

    plt.bar('Genre', 'Rating', color='Color', data=df)
    plt.title('Genre wise ratings', fontdict={'size': 22})
    plt.xlabel('Genre', fontdict={'size': 16})
    plt.ylabel('Rating', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot.jpg'))
    plt.close()

    plt.bar('Genre', 'Views', color='Color', data=df)
    plt.title('Genre wise views', fontdict={'size': 22})
    plt.xlabel('Genre', fontdict={'size': 16})
    plt.ylabel('Views', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot1.jpg'))
    plt.close()

    plt.bar('Genre', 'Count', color='Color', data=df)
    plt.title('Genre wise count of songs uploaded', fontdict={'size': 22})
    plt.xlabel('Genre', fontdict={'size': 16})
    plt.ylabel('Count', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot2.jpg'))
    plt.close()

@cache.cached(timeout=86400)
def get_plot1(df):
    df['Color'] = np.random.choice(list(mcolors.XKCD_COLORS), df.shape[0])

    plt.bar('Language', 'Rating', color='Color', data=df)
    plt.title('Language wise ratings', fontdict={'size': 22})
    plt.xlabel('Language', fontdict={'size': 16})
    plt.ylabel('Rating', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot3.jpg'))
    plt.close()

    plt.bar('Language', 'Views', color='Color', data=df)
    plt.title('Language wise views' ,fontdict={'size': 22})
    plt.xlabel('Language', fontdict={'size': 16})
    plt.ylabel('Views', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot4.jpg'))
    plt.close()

    plt.bar('Language', 'Count', color='Color', data=df)
    plt.title('Language wise count of songs uploaded', fontdict={'size': 16})
    plt.xlabel('Language', fontdict={'size': 16})
    plt.ylabel('Count', fontdict={'size': 16})
    plt.xticks(rotation=80, fontsize=12)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'], 'plot5.jpg'))
    plt.close()

@cache.memoize(timeout=600)
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


@cache.memoize(timeout=86400)
def adminStatistics():
    stats = {}
    song_count = Song.query.count()
    album_count = Album.query.count()
    playlist_count = Playlist.query.count()
    user_count = User.query.filter(User.user_type == 'USER').count()
    creator_count = Creator.query.count()

    last_month = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    month = last_month.strftime("%m")
    year = last_month.strftime("%Y")
    user_last_month = User.query.where(
        func.extract('year', User.created_at) == year).where(
        func.extract('month', User.created_at) == month).count()
    creator_last_month = Creator.query.where(
        func.extract('year', Creator.created_at) == year).where(
        func.extract('month', Creator.created_at) == month).count()
    
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

    query = db.select(Language.name, func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating'), func.count(distinct(Song.id)).label(
        'count'), ).join(Song, Song.language == Language.name, isouter=True).join(SongLikes, SongLikes.song_id == Song.id, isouter=True).group_by(Language.name)
    res5 = db.session.execute(query).fetchall()

    dic = [{'Genre': r[0], 'Views': r[1], 'Rating': r[2], 'Count': r[3]}
           for r in res4]
    df = pd.DataFrame(dic)
    df.fillna(0, inplace=True)
    get_plot(df)

    dic = [{'Language': r[0], 'Views': r[1], 'Rating': r[2], 'Count': r[3]}
           for r in res5]
    df = pd.DataFrame(dic)
    df.fillna(0, inplace=True)
    get_plot1(df)

    stats['song_count'] = song_count
    stats['album_count'] = album_count
    stats['playlist_count'] = playlist_count
    stats['user_count'] = user_count
    stats['user_last_month'] = user_last_month
    stats['creator_count'] = creator_count
    stats['creator_last_month'] = creator_last_month
    stats['total_views'] = res[0] if res else 0
    stats['total_likes'] = res1[0] if res1 else 0
    stats['average_rating'] = res[1] if res else 0
    stats['total_songs_in_albums'] = res2[0] if res2 else 0
    stats['total_songs_in_playlists'] = res3[0] if res2 else 0
    # No of playlist having some songs

    return stats


class AnalyticsResource(Resource):
    @jwt_required()
    @user
    def get(self):
        user_type = get_jwt()['user_type']
        if user_type == 'ADMIN':
            return {"analytics": adminStatistics()}

        if user_type == 'CREATOR':
            creator_id = get_jwt_identity()
            creator = Creator.query.get_or_404(get_jwt_identity())
            if not creator or creator.disabled:
                return {"message": "creator disabled"}, 403
            songs = Song.query.filter(Song.creator_id == creator_id).order_by(
                Song.created_at.desc()).all()
            print(songs)
            albums = Album.query.filter(Album.creator_id == creator_id).order_by(
                Album.created_at.desc()).all()
            return {"analytics": creatorStatistics(creator_id),
                    "songs": many_song_schema.dump(songs),
                    "albums": many_album_schema.dump(albums)}
        return {"message": "unauthorized"}, 403
