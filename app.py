#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf.csrf import CSRFProtect
import datetime
from forms import VenueForm, ArtistForm, ShowForm
from forms import *
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data_areas = []

    # Get areas
    areas = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # Iterate over each area
    for area in areas:
        data_venues = []

        # Get venues by area
        venues = Venue.query.filter_by(
            state=area.state).filter_by(city=area.city).all()

        # Iterate over each venue
        for venue in venues:
            # Get upcoming shows by venue
            upcoming_shows = db.session.query(Show).filter(
                Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

            # Map venues
            data_venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows)
            })

        # Map areas
        data_areas.append({
            'city': area.city,
            'state': area.state,
            'venues': data_venues
        })

    return render_template('pages/venues.html', areas=data_areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    # Prepare search data
    search_term = request.form['search_term']
    search = "%{}%".format(search_term)

    # Get venues
    venues = Venue.query.with_entities(
        Venue.id, Venue.name).filter(Venue.name.match(search)).all()

    # Iterate over each venue
    data_venues = []

    for venue in venues:
        # Get upcoming shows by venue
        upcoming_shows = db.session.query(Show).filter(
            Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

        # Map venues
        data_venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    # Map results
    results = {
        'venues': data_venues,
        'count': len(venues)
    }

    return render_template('pages/search_venues.html', results=results, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # Get venue
    data_venue = Venue.query.filter(Venue.id == venue_id).first()

    # Get the upcoming shows of this venue
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    if len(upcoming_shows_query) > 0:
        # data_upcoming_shows = []

        upcoming_shows = []

        for show in upcoming_shows_query:

            artist = Artist.query.filter(
                Artist.id == show.artist_id).first()

            upcoming_shows.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(show.start_time),
            })

        # Add shows data
        data_venue.upcoming_shows = upcoming_shows
        data_venue.upcoming_shows_count = len(upcoming_shows)

    # Get the past shows of this venue
    past_shows_query = db.session.query(Show).join(Show.venues).filter(
        Show.venue_id == int(venue_id)).filter(Show.start_time < datetime.now()).all()

    if len(past_shows_query) > 0:

        past_shows = []

        # Iterate over each past show
        for show in past_shows_query:

            artist = Artist.query.filter(Artist.id == show.artist_id).first()

            # Map past shows
            past_shows.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(show.start_time),
            })

        # Add shows data
        data_venue.past_shows = past_shows
        data_venue.past_shows_count = len(past_shows)

    return render_template('pages/show_venue.html', venue=data_venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    error = False

    form = VenueForm()

    if form.validate_on_submit():
        # TODO: modify data to be the data object returned from db insertion
        # Get data
        name = request.form.get('name')

        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        website_link = request.form.get('website_link')
        seeking_talent = True if 'seeking_talent' in request.form else False
        seeking_description = request.form.get('seeking_description')

        try:
            # Create model
            venue = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                genres=genres,
                image_link=image_link,
                facebook_link=facebook_link,
                website_link=website_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description,
            )

            # Update DB
            db.session.add(venue)
            db.session.commit()

        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        # TODO: on unsuccessful db insert, flash an error instead.

        # Show banner
        if error:
            flash(
                'An error occurred. Venue '
                + name
                + ' could not be listed.',
                'danger'
            )
            abort()

        # on successful db insert, flash success
        if not error:
            flash(
                'Venue '
                + name
                + ' was successfully listed!',
                'success'
            )

        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')

    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False

    try:
        Venue.query.filter_by(id=int(venue_id)).delete()
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        return render_template('errors/500.html', error=str(e))
    finally:
        db.session.close()

    # Show banner
    if error:
        flash(
            'An error occurred. Venue could not be deleted.',
            'danger'
        )
        abort()

    if not error:
        flash(
            'Venue was successfully deleted!',
            'success'
        )

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data_artists = []

    # Get artists
    artists = Artist.query.with_entities(
        Artist.id, Artist.name).order_by('id').all()

    # Iterate over each artist
    for artist in artists:
        # Get upcoming shows
        upcoming_shows = db.session.query(Show).filter(
            Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()

        # Map artists
        data_artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    return render_template('pages/artists.html', artists=data_artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    # Prepare search data
    search_term = request.form['search_term']

    search = "%{}%".format(search_term)

    # Get artists
    artists = Artist.query.with_entities(
        Artist.id, Artist.name).filter(Artist.name.match(search)).all()

    # Iterate over each artist
    data_artists = []

    for artist in artists:
        # Get upcoming shows
        upcoming_shows = db.session.query(Show).filter(
            Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()

        # Map artists
        data_artists.append({'id': artist.id, 'name': artist.name,
                            'num_upcoming_shows': len(upcoming_shows)})

    # Map data
    results = {'data': data_artists, 'count': len(artists)}

    return render_template('pages/search_artists.html', results=results, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    # Get artist
    data_artist = Artist.query.filter(Artist.id == artist_id).first()

    # Get the upcoming shows of this artist
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    if len(upcoming_shows_query) > 0:

        upcoming_shows = []

        # Iterate over each upcoming show
        for show in upcoming_shows_query:

            venue = Venue.query.filter(Venue.id == show.venue_id).first()

            # Map upcoming shows
            upcoming_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(show.start_time),
            })

        # Add shows data
        data_artist.upcoming_shows = upcoming_shows
        data_artist.upcoming_shows_count = len(upcoming_shows)

        # Get the past shows of this venue
        past_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

        if len(past_shows_query) > 0:

            past_shows = []

            # Iterate over each past show
            for show in past_shows_query:

                venue = Venue.query.filter(Venue.id == show.venue_id).first()

                # Map past shows
                past_shows.append({
                    'venue_id': venue.id,
                    'venue_name': venue.name,
                    'venue_image_link': venue.image_link,
                    'start_time': str(show.start_time),
                })

            # Add shows data
            data_artist.past_shows = past_shows
            data_artist.past_shows_count = len(past_shows)

    return render_template('pages/show_artist.html', artist=data_artist)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # TODO: populate form with fields from artist with ID <artist_id>

    # Request data
    artist = Artist.query.filter(Artist.id == artist_id).first()

    # Fill form
    form = ArtistForm()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm()

    if form.validate_on_submit():
        error = False

        # Get data
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        seeking_venue = True if 'seeking_venue' in request.form else False
        seeking_description = request.form['seeking_description']

        try:
            # Request artist by id
            artist = Artist.query.get(artist_id)

            # Update artist data
            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.genres = genres
            artist.image_link = image_link
            artist.facebook_link = facebook_link
            artist.website_link = website_link
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description

            # Update DB
            db.session.commit()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(
                'An error occurred. Artist '
                + name
                + ' could not be updated.',
                'danger'
            )
            abort()

        if not error:
            flash(
                'Artist '
                + name
                + ' was successfully updated!',
                'success'
            )

        return redirect(url_for('show_artist', artist_id=artist_id))

    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_artist.html', form=form)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>
    # Request data
    venue = Venue.query.filter(Venue.id == venue_id).first()

    # Fill form
    form = VenueForm()
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm()

    if form.validate_on_submit():
        error = False

        # Get data
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        seeking_talent = True if 'seeking_talent' in request.form else False
        seeking_description = request.form['seeking_description']

        try:
            # Request venue by id
            venue = Venue.query.get(venue_id)

            # Update venue data
            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.phone = phone
            venue.genres = genres
            venue.image_link = image_link
            venue.facebook_link = facebook_link
            venue.website_link = website_link
            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description

            # Update DB
            db.session.commit()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        # Show banner
        if error:
            flash(
                'An error occurred. Venue '
                + name
                + ' could not be updated.',
                'danger'
            )
            abort(400)

        if not error:
            flash(
                'Venue '
                + name
                + ' was successfully updated!',
                'success'
            )

        return redirect(url_for('show_venue', venue_id=venue_id))

    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_venue.html', form=form)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    error = False

    form = ArtistForm()

    if form.validate_on_submit():
        # Get data
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website_link = request.form['website_link']
        seeking_venue = True if 'seeking_venue' in request.form else False
        seeking_description = request.form['seeking_description']

        try:
            # Create model
            artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                image_link=image_link,
                facebook_link=facebook_link,
                website_link=website_link,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description,
            )

            # Update DB
            db.session.add(artist)
            db.session.commit()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        # TODO: modify data to be the data object returned from db insertion

        # on successful db insert, flash success
        if not error:
            flash(
                'Artist '
                + name
                + ' was successfully listed!',
                'success'
            )
        # flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

        # Show banner
        if error:
            flash(
                'An error occurred. Artist '
                + name
                + ' could not be listed.',
                'danger'
            )
            abort()

        return render_template('pages/home.html')

    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    show_data = []

    # Get data
    shows = db.session.query(
        Venue.name,
        Artist.name,
        Artist.image_link,
        Show.venue_id,
        Show.artist_id,
        Show.start_time
    ).filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

    # Map data
    for show in shows:
        show_data.append({
            'venue_name': show[0],
            'artist_name': show[1],
            'artist_image_link': show[2],
            'venue_id': show[3],
            'artist_id': show[4],
            'start_time': str(show[5])
        })

    return render_template('pages/shows.html', shows=show_data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm()
    #  validate
    if form.validate_on_submit():

        error = False

        # Get data
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        try:
            # Create model
            show = Show(
                artist_id=artist_id,
                venue_id=venue_id,
                start_time=start_time,
            )

            # Update DB
            db.session.add(show)
            db.session.commit()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        # on successful db insert, flash success
        # flash('Show was successfully listed!')
        if not error:
            flash(
                'Show was successfully listed!',
                'success'
            )
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # Show banner
        if error:
            flash(
                'An error occurred. Show could not be listed.',
                'danger'
            )
            abort()

        return render_template('pages/home.html')

    else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
