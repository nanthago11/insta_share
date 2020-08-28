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


class FileUploader(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        gallery_name = str(self.request.get('gal'))
        blobInfo = blobstore.BlobInfo(upload.key())
        fname = blobInfo.filename
        curr_user = users.get_current_user()
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
                for i in arr.name:
                    if gallery_name == i:
                        exists = True
                        break
                if exists:
                    postCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                    postCollection = postCollectionConst.get()
                    img = Img(
                        fname=str(fname),
                        blob=upload.key())
                    imkey = img.put()
                    if postCollection is None:
                        new_post = Content(
                            id=gallery_name + obj.emailId,
                            gal=arr,
                            content=[str(imkey.id())])
                        new_post.put()
                        self.redirect('/gallery?name=' + gallery_name)
                    else:
                        postCollection.content.append(str(imkey.id()))
                        postCollection.put()
                        self.redirect('/gallery?name=' + gallery_name)
                else:
                    self.redirect('/')
        else:
            self.redirect('/login')


class FileDownloader(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        id = int(self.request.get_all('index')[0])
        img = ndb.Key('Img', int(id))
        data = img.get()
        self.send_blob(data.blob)

