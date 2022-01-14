# User profile process 
import os
from flask import current_app
from PIL import Image

def process_upload_image(upload_img, username):
  file_name = upload_img.filename
  file_extension = file_name.split('.')[-1]
  file_rename = str(username) + '.' + file_extension
  save_path = os.path.join(current_app.root_path, 'static/profile_pics', file_rename)

  load_img = Image.open(upload_img)
  load_img.thumbnail([128, 128])
  load_img.save(save_path)
  
  return file_rename