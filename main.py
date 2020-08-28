from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

import webapp2
import jinja2
import os


from models import Photo_gal, Img, MyUser, Content
from DeleteAction import DiscardGalName, RemoveImg
from FileAction import FileUploader, FileDownloader
from clone import CloneAll, CloneGallery
from NameAction import AddName, RenameGallery, ShowGallery

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class Main(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        header = 'Welcome to Image Section'
        curr_user = users.get_current_user()
        error = str(self.request.get('error'))
        arr = []
        if curr_user:

            url = users.create_logout_url(self.request.uri)
            url_string = 'Logout'
            user_key = ndb.Key('MyUser', curr_user.user_id())
            user = user_key.get()
            if user is None:
                header = 'Welcome to Image Section'
                user = MyUser(id=curr_user.user_id())
                user.put()
                user.emailId = curr_user.email()
                user.put()
            else:
                gallerConst = ndb.Key('Photo_gal', user.emailId)
                data = gallerConst.get()
                if data is not None:
                    if len(data.name):
                        for name in data.name:
                            postCollectionConst = ndb.Key('Content', name + user.emailId)
                            data = postCollectionConst.get()
                            id = 0
                            if data is not None and len(data.content):
                                id = data.content[0]
                            arr.append({
                                "id": id,
                                "gal": name
                            })
                else:
                    arr=[]
        else:
            url = users.create_login_url(self.request.uri)
            url_string = 'login'

        template_values = {
            'url': url,
            'url_string': url_string,
            'user': curr_user,
            'header': header,
            'arr': arr,
            'error': error
        }

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))




app = webapp2.WSGIApplication([
    ('/', Main),
    ('/add_name', AddName),
    ('/gallery', ShowGallery),
    ('/edit_gal_name', RenameGallery),
    ('/delete_gallery', DiscardGalName),
    ('/upload_file', FileUploader),
    ('/download_file', FileDownloader),
    ('/delete_image', RemoveImg),
    ('/duplicate_gallery', CloneGallery),
    ('/duplicate_all', CloneAll)
], debug=True)
