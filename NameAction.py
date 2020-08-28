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

class AddName(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        gallery_name = str(self.request.get('name'))
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            arr = galleryCollectionConst.get()
            if arr is None:
                new_gallery = Photo_gal(
                    user=obj,
                    name=[gallery_name],
                    id=curr_user.email()
                )
                new_gallery.put()
                self.redirect('/gallery?name=' + gallery_name)
            else:
                insert = True
                arr.name = [str(r) for r in arr.name]
                for i in arr.name:
                    if gallery_name == i:
                        insert = False
                        break
                if insert:
                    arr.name.append(str(gallery_name))
                    arr.put()
                    self.redirect('/gallery?name=' + gallery_name)
                else:
                    self.redirect('/')
        else:
            self.redirect('/login')



class RenameGallery(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        gallery_name = str(self.request.get('oldName'))
        new_gallery_name = str(self.request.get('newgalleryName'))
        if curr_user:
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            if galleryCollectionConst is None:
                self.redirect('/?error=not found')
            else:
                arr = galleryCollectionConst.get()
                update = True
                exists = False
                arr.name = [str(r) for r in arr.name]
                for i in arr.name:
                    if new_gallery_name == i:
                        update = False
                        break
                if update:
                    count = 0
                    for i in arr.name:
                        if gallery_name == i:
                            exists = True
                            arr.name[count] = new_gallery_name
                            break
                        else:
                            count += 1
                    if exists:
                        arr.put()
                        contentCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                        clone = contentCollectionConst.get()
                        new_post = Content(
                            id=new_gallery_name + obj.emailId,
                            gal=arr,
                            content=clone.content)
                        new_post.put()
                        clone.key.delete()
                        self.redirect('/gallery?name=' + new_gallery_name)
                    else:
                        self.redirect('/gallery?name=' + gallery_name + '&error=name not found')
                else:
                    self.redirect('/?error=duplicate name')
        else:
            self.redirect('/login')


class ShowGallery(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        curr_user = users.get_current_user()
        if curr_user:
            url_string = 'Logout'
            url = users.create_logout_url(self.request.uri)
            gallery_name = str(self.request.get('name'))
            error = str(self.request.get('error'))
            curr_user_key = ndb.Key('MyUser', curr_user.user_id())
            obj = curr_user_key.get()
            galleryCollectionConst = ndb.Key('Photo_gal', obj.emailId)
            if galleryCollectionConst is None:
                self.redirect('/?error="gallery does not exist')
            else:
                arr = galleryCollectionConst.get()
                exists = False
                arr.name = [str(r) for r in arr.name]
                for i in arr.name:
                    if i == gallery_name:
                        exists = True
                        break
                if exists:
                    postCollectionConst = ndb.Key('Content', gallery_name + obj.emailId)
                    postCollection = postCollectionConst.get()
                    imageblobId = []
                    if postCollection is not None:
                        imagesGallery = postCollection.content
                        for image in imagesGallery:
                            imageblobId.append({
                                "id": str(image)
                            })
                        template_values = {
                            'header': gallery_name,
                            'url': url,
                            'url_string': url_string,
                            'user': curr_user,
                            'upload_url': blobstore.create_upload_url('/upload_file'),
                            'arr': imageblobId,
                            'error': error
                        }
                        template = JINJA_ENVIRONMENT.get_template('gallery.html')
                        self.response.write(template.render(template_values))
                    else:
                        template_values = {
                            'header': gallery_name,
                            'url': url,
                            'url_string': url_string,
                            'user': curr_user,
                            'upload_url': blobstore.create_upload_url('/upload_file'),
                            'error': error

                        }
                        template = JINJA_ENVIRONMENT.get_template('gallery.html')
                        self.response.write(template.render(template_values))

                else:
                    self.redirect('/')
        else:
            self.redirect('/login')
