from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, unique=False, default=False)
    genres = db.Column(db.ARRAY(db.String(50)))
    artists = db.relationship("Artist", secondary="association", back_populates="venues")
 


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(50)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, unique=False, default=False)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship("Venue", secondary="association", back_populates="artists")

class Association(db.Model):
    __tablename__ = 'association'
    venue_id = db.Column(db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime())


