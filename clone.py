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

class CloneAll(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        url_string = 'Logout'
        url = users.create_logout_url(self.request.uri)
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            arr = galleryCollectionConst.get()
            if arr is None:
                self.redirect('/')
            else:
                md5s = []
                dups = []
                for name in arr.name:
                    postCollectionConst = ndb.Key('Content', name + obj.emailId)
                    data = postCollectionConst.get()
                    if data is not None:
                        for i in data.content:
                            img = ndb.Key('Img', int(i))
                            data = img.get()
                            imageData = blobstore.BlobInfo(data.blob)
                            if imageData.md5_hash in md5s:
                                dups.append({
                                    "id": i,
                                    "gal": name
                                })
                            else:
                                md5s.append(imageData.md5_hash)
                template_values = {
                    'header': "All",
                    'url': url,
                    'url_string': url_string,
                    'user': curr_user,
                    'arr': dups
                }
                template = JINJA_ENVIRONMENT.get_template('duplicates.html')
                self.response.write(template.render(template_values))
        else:
            self.redirect('/login')


class CloneGallery(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        gallery_name = str(self.request.get('gal'))
        url_string = 'Logout'
        url = users.create_logout_url(self.request.uri)
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            if galleryCollectionConst is None:
                self.redirect('/')
            else:
                arr = galleryCollectionConst.get()
                arr.name = [str(r) for r in arr.name]
                postCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                data = postCollectionConst.get()
                if not len(data.content):
                    self.redirect('/')
                else:
                    md5s = []
                    dups = []
                    for i in data.content:
                        img = ndb.Key('Img', int(i))
                        data = img.get()
                        imageData = blobstore.BlobInfo(data.blob)

                        if imageData.md5_hash in md5s:
                            dups.append({
                                "id": i,
                                "gal": gallery_name
                            })
                        else:
                            md5s.append(imageData.md5_hash)
                    template_values = {
                        'header': gallery_name,
                        'url': url,
                        'url_string': url_string,
                        'user': curr_user,
                        'arr': dups
                    }
                    template = JINJA_ENVIRONMENT.get_template('duplicates.html')
                    self.response.write(template.render(template_values))
        else:
            self.redirect('/login')
