from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

import webapp2
import jinja2
import os


from models import Photo_gal, Img, MyUser, Content

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class DiscardGalName(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        gallery_name = str(self.request.get('gal'))
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            if galleryCollectionConst is None:
                self.redirect('/')
            else:
                arr = galleryCollectionConst.get()
                exists = False
                arr.name = [str(r) for r in arr.name]
                updatedCollection = []
                postCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                data = postCollectionConst.get()
                if len(data.content):
                    self.redirect('/gallery?name=' + gallery_name + '&error=cannot delete gallery with images')
                else:
                    for i in arr.name:
                        if gallery_name == i:
                            exists = True
                            break
                        else:
                            updatedCollection.append(i)
                    if exists:
                        arr.name = updatedCollection
                        arr.put()
                        self.redirect('/')
                    else:
                        self.redirect('/?error=nonempty')
        else:
            self.redirect('/login')


class RemoveImg(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        gallery_name = str(self.request.get('gal'))
        image_id = str(self.request.get('imageId'))
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            if galleryCollectionConst is None:
                self.redirect('/')
            else:
                arr = galleryCollectionConst.get()
                exists = False
                arr.name = [str(r) for r in arr.name]
                updatedCollection = []
                postCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                data = postCollectionConst.get()
                if not len(data.content):
                    self.redirect('/?error=image does not exist')
                else:
                    for i in data.content:
                        if str(image_id) == str(i):
                            exists = True
                        else:
                            updatedCollection.append(i)
                    if exists:
                        data.content = updatedCollection
                        data.put()
                        self.redirect('/gallery?name=' + gallery_name)
                    else:
                        self.redirect('/?error=image does not exist')
        else:
            self.redirect('/login')

