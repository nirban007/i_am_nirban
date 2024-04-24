import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip

from functions import FaceRecognition

def stream_camera_feed(request):
    # Set up camera capture
    cam_id = 0  
    web_cap = cv2.VideoCapture(cam_id)

    # Define generator function to continuously capture frames
    def generate_frames():
        while True:
            success, frame = web_cap.read()
            if not success:
                break

            # Encode frame as JPEG image
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield the frame as bytes
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    # Define streaming view using generator function
    @gzip.gzip_page
    def streamed_response(request):
        return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

    # Return the streaming view
    return streamed_response
