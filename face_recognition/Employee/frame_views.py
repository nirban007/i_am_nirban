from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from functools import partial

from functions import FaceRecognition  # Import your FaceRecognition class

# Initialize FaceRecognition instance
face_recognition = FaceRecognition(set_entry_hour='10', set_entry_min='00', set_meridian='AM', tol=15)

# Create embeddings for known faces
dir_path = 'D:\\Projects\\who-are-you\\face_recognition\\Employee\\employee_images'
embeddings = face_recognition.create_person_embedding(dir_path)

# Define generator function to continuously capture frames
def generate_frames(face_recognition, embeddings):
    cam_id = 0  # Adjust the camera ID as per your system
    while True:
        # Perform face recognition on camera feed
        frame = face_recognition.recognize_face(embeddings, cam_id)
        
        # Show the frame
        face_recognition.show_frame(frame)
        
        # Yield an empty byte string
        yield b''

# Create a partial function with required arguments pre-filled
generate_frames_partial = partial(generate_frames, face_recognition)

# Define streaming view using the partial function
@gzip.gzip_page
def stream_camera_feed(request):
    return StreamingHttpResponse(generate_frames_partial(embeddings), content_type='multipart/x-mixed-replace; boundary=frame')
