from google.appengine.ext import ndb


class MyUser(ndb.Model):
    emailId = ndb.StringProperty()


class Photo_gal(ndb.Model):
    user = ndb.StructuredProperty(MyUser, repeated=False)
    madeAt = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.StringProperty(repeated=True)


class Img(ndb.Model):
    fname = ndb.StringProperty(repeated=False)
    blob = ndb.BlobKeyProperty(repeated=False)


class Content(ndb.Model):
    content = ndb.StringProperty(repeated=True)
    gal = ndb.StructuredProperty(Photo_gal, repeated=False)
    madeAt = ndb.DateTimeProperty(auto_now_add=True)
