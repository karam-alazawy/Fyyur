#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declarative_base
import sys
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
Base = declarative_base()
date = datetime.now()


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  city_state=db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  data = []
  for city,state in city_state:
    venue=Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.city==city,Venue.state==state).all()
    data.append({
    "city": city,
    "state": state,
    "venues": venue
  })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  q=request.form['search_term']
  venues=Venue.query.with_entities(Venue.name,Venue.id).filter(Venue.name.ilike(f"%{q}%")).all()
  count=Venue.query.filter(Venue.name.ilike(f"%{q}%")).count()
  response={
    "count": count,
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):


  venue=Venue.query.get(venue_id)
  upcoming_shows_data=[]
  upcoming_shows_count=0
  upcoming_shows_query = db.session.query(Association).with_entities(Association.artist_id,Association.venue_id,Association.start_time,Artist.name,Artist.image_link).join(Artist ,Artist.id==Association.artist_id).filter(Association.venue_id==venue_id,Association.start_time>=datetime.now()).all()  
  for upcoming_show in upcoming_shows_query:
    upcoming_shows_count+= 1
    dateStr = upcoming_show.start_time.strftime("%d %b, %Y")
    upcoming_shows_data.append({
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.name,
      "artist_image_link": upcoming_show.image_link,
      "start_time": dateStr
    })


  past_shows_data=[]
  past_shows_count=0
  past_shows_query = db.session.query(Association).with_entities(Association.artist_id,Association.venue_id,Association.start_time,Artist.name,Artist.image_link).join(Artist ,Artist.id==Association.artist_id).filter(Association.venue_id==venue_id,Association.start_time<datetime.now()).all()  
  for past_show in past_shows_query:
    past_shows_count+= 1
    dateStr = past_show.start_time.strftime("%d %b, %Y")
    past_shows_data.append({
      "artist_id": past_show.artist_id,
      "artist_name": past_show.name,
      "artist_image_link": past_show.image_link,
      "start_time": dateStr
    })
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if not form.validate():
    abort(400) 
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    website = request.form['website_link']
    facebook_link = request.form['facebook_link']
    seeking_talent=True if request.form.get('seeking_talent') else False
    new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=facebook_link,genres=genres,website=website,seeking_talent=seeking_talent)
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    abort(500)



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    x = Venue.query.get(venue_id)
    db.session.delete(x)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  q=request.form['search_term']
  artists=Artist.query.with_entities(Artist.name,Artist.id).filter(Artist.name.ilike(f"%{q}%")).all()
  count=Artist.query.filter(Artist.name.ilike(f"%{q}%")).count()
  response={
    "count": count,
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist=Artist.query.get(artist_id)
  upcoming_shows_data=[]
  upcoming_shows_count=0
  upcoming_shows_query = db.session.query(Association).with_entities(Association.artist_id,Association.venue_id,Association.start_time,Venue.name,Venue.image_link).join(Venue ,Venue.id==Association.venue_id).filter(Association.venue_id==artist_id,Association.start_time>=datetime.now()).all()  
  for upcoming_show in upcoming_shows_query:
    upcoming_shows_count+= 1
    dateStr = upcoming_show.start_time.strftime("%d %b, %Y")
    upcoming_shows_data.append({
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.name,
      "venue_image_link": upcoming_show.image_link,
      "start_time": dateStr
    })

  past_shows_data=[]
  past_shows_count=0
  past_show_query = db.session.query(Association).with_entities(Association.artist_id,Association.venue_id,Association.start_time,Venue.name,Venue.image_link).join(Venue ,Venue.id==Association.venue_id).filter(Association.venue_id==artist_id,Association.start_time<datetime.now()).all()  
  for past_show in past_show_query:
    past_shows_count+= 1
    dateStr = past_show.start_time.strftime("%d %b, %Y")
    past_shows_data.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.name,
      "venue_image_link": past_show.image_link,
      "start_time": dateStr
    })
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if not form.validate():
    abort(400) 
  error = False
  try:
    artist=Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = request.form.getlist('genres')
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.seeking_venue = True if request.form.get('seeking_venue') else False
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    abort(500)
 

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if not form.validate():
    abort(400) 
  error = False
  try:
    venue=Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.genres = request.form.getlist('genres')
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = True if request.form['seeking_talent'] else False
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    abort(500)
 


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if not form.validate():
    abort(400) 
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    genres = request.form.getlist('genres')
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    seeking_description = request.form['seeking_description']
    seeking_venue=True if request.form.get('seeking_venue') else False
    new_artist = Artist(name=name,city=city,state=state,genres=genres,phone=phone,image_link=image_link,facebook_link=facebook_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    abort(500)
 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]
  shows=db.session.query(Artist,Association,Venue).with_entities(Association.start_time,Association.venue_id,Venue.name.label('vname'),Association.artist_id,Artist.name,Artist.image_link).filter(Association.artist_id==Artist.id,Association.venue_id==Venue.id).all()  
  for show in shows:
    dateStr = show.start_time.strftime("%d %b, %Y")
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.vname,
    "artist_id": show.artist_id,
    "artist_name":  show.name,
    "artist_image_link": show.image_link,
    "start_time": dateStr
  })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  if not form.validate():
    abort(400) 
  error = False
  try:
    artist_id=request.form['artist_id']
    venue_id=request.form['venue_id']
    start_time=request.form['start_time']
    new_association = Association(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_association)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    abort(400)

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
