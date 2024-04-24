from datetime import datetime, timedelta
from insightface.app import FaceAnalysis
import numpy as np
import cv2
import gc
import tqdm
from collections import defaultdict
import os
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
from django.core.files.base import ContentFile

from employeez_info.models import ImageModel




class FaceRecognition:

    """
    Class for Recognizing the faces.
    """

    def __init__(self, set_entry_hour, set_entry_min, set_meridian, tol, model_name='buffalo_l', ):
       
        """Arguments: model_name: str: pass the model that should be used for inference, default 'buffalo_l'
           Returns: None"""

        # from insightface.model_zoo import get_model
        # self.model_name = model_name
        self.set_entry_hour = set_entry_hour
        self.set_entry_min = set_entry_min
        self.set_meridian = set_meridian
        self.tol = tol
        self.set_entry_time = self.set_entry_hour + ":" + self.set_entry_min + ":" + "00"
        self.time_format = "%I:%M:%S %p"
        self.office_entry_time = datetime.strptime(f"{self.set_entry_time} {self.set_meridian}", self.time_format)
        self.today = datetime.today().strftime("%d-%m-%Y")

        self.app = FaceAnalysis(name=model_name, allowed_modules=['detection', 'recognition'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        self.dir_name = 'Attendance'
        self.file_name = f"{self.dir_name}_{self.today}.csv"
        self.db_params = {
            "dbname": "face_rec",
            "user": "postgres",
            "password": "nirban@007",
            "host": "localhost",
        }


    def create_person_embedding(self, dir_path,
                                infer_from_filepath=True,
                                person_name=None):
        """
        creates vector embeddings for the photos inside the passed filepath
        Args:
            dir_path: Location of the directory containing photos directories
            infer_from_filepath: if the photo directory has the name of the person in the photos, then it will be infered from the filepath and keep the person_name as None
            person_name: explicit naming for the person, if the directory naming is unstructured. Make infer_from_filepath=False when using this argument.
        returns: A dictionary item containing person's name with their embedding
        """

        # if person_name:
        #     name = person_name

        # else:
        #     infer_name = filepath.split("/")

        #     if infer_name[0] != "":
        #         name = filepath.split("/")[0]
        #     else:
        #         name = filepath.split("/")[-2]



        known_embedding = defaultdict()
        # person_dict = defaultdict()

        dir_list = os.listdir(dir_path)
        # embedding_list = []

        for key, dir_name in enumerate(dir_list):

            embedding_list = []

            file_list = os.listdir(os.path.join(dir_path, dir_name)) # get the image names as list

            for file_loc in tqdm.tqdm(file_list[:10]): # iterate over the images
                image = cv2.imread(f"{dir_path}/{dir_name}/{file_loc}") # load the image
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (224, 224))

                face = self.app.get(image)
                embedding = face[0]['embedding'] # get the embeding vector

                embedding_list.append(embedding)

            known_embedding[dir_name.title()] = np.array(embedding_list)
            # person_dict[key] = dir_name.title()
            
            gc.collect()
        
        # embedding_arr = np.array(embedding_list).reshape(-1, 10, 512)
        # To know if it's done, comment out if everything works well

        print("Embedding done...\n")
        self.save_embedding(known_embedding)

        return known_embedding
    
    def save_embedding(self, embeddings):
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        try:
            # Create a table to store embedding information
            cursor.execute('''CREATE TABLE IF NOT EXISTS embeddings (id SERIAL PRIMARY KEY, name TEXT, embedding_arr TEXT)''')

            for name, embedding_array in embeddings.items():
                embedding_str = "[" + ", ".join(map(str, embedding_array)) + "]"
                cursor.execute('''INSERT INTO embeddings (name, embedding_arr) VALUES (%s, %s)''', 
                               (name, embedding_str))

            conn.commit()
            print("Embeddings saved successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while working with PostgreSQL:", error)
        finally:
            cursor.close()
            conn.close()

    
    def recognize_face(self, embeddings, cam_id, save_dir='captured'):
        thresh = 30
        web_cap = cv2.VideoCapture(cam_id)

        while True:
            success, frame = web_cap.read()
            imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            process_start = datetime.now()

            faces = self.app.get(imgS)
        
            if faces:
                for face in faces:
                    left, top, right, bottom = face['bbox']
                    curr_embd = face['embedding'].reshape(1, -1)

                    for name, known_embedding in embeddings.items():
                        similarity_score = cosine_similarity(known_embedding, curr_embd)
                        max_similarity = np.max(similarity_score) * 100

                        if max_similarity >= thresh:
                            cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (255, 0, 0), 2)
                            cv2.putText(frame, f"{name} {max_similarity:.2f}% Match", (int(left), int(top) - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                        
                            process_end = datetime.now()
                            shifted_entry = self._calculte_shifted_entry(process_start, process_end)
                            
                            self._mark_attendance(name, shifted_entry)
                            self._save_image(save_dir, frame, shifted_entry)
                        else:
                            # If face is unrecognized, show the frame
                            self.show_frame(frame)

            self.show_frame(frame)

    def show_frame(self, frame):
        cv2.imshow('webcam', frame)
        cv2.waitKey(1)


    def _make_dir(self, path):
        
        os.mkdir(path)

        return

    def _make_file(self):
        import csv

        current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory path
        dir_path = os.path.join(current_dir, '..', self.dir_name) # create a path with one directory up

        # if the directory doesn't exist, make directory 

        if not os.path.exists(dir_path):
            self._make_dir(dir_path) 
        
        file_path = os.path.join(dir_path, self.file_name) # construct the csv file location
        
        if not os.path.exists(file_path):
            with open(file_path, mode='w', newline='') as f:
                data = [['name', 'date', 'timeOfEntry', 'status']]
                writer = csv.writer(f)
                writer.writerows(data)
        
        return file_path
    
    def _save_image(self, path, image, marked_time):
        try:
            # Convert marked_time to a string representation for the filename
            marked_time_str = marked_time.strftime("%Y%m%d%H%M%S")

            # Ensure the 'captured' directory exists
            os.makedirs(path, exist_ok=True)

            # Create a new instance of the ImageModel
            new_image = ImageModel()

            # Set the marked time
            new_image.marked_time = marked_time

            # Save the image data in PNG format
            image_filename = f"frame_{marked_time_str}.png"  # Change file extension to PNG
            image_path = os.path.join(path, image_filename)
            cv2.imwrite(image_path, image)  # Save image using OpenCV in PNG format

            # Set the image attribute to the path of the saved image
            new_image.image = os.path.join('captured', image_filename)

            # Save the ImageModel instance
            new_image.save()
            print("Image saved to database successfully.")
        except Exception as e:
            print(f"Error saving image to database: {e}")


        
    
    def _status(self, entry_time):
        # print("Entry time: ", self.set_entry_time)
        # print(f"Type: {type(self.set_entry_time)}")
        # office_entry_time = datetime.strptime(f"{self.set_entry_time} {self.set_meridian}", self.time_format)
        tol_time = self.office_entry_time + timedelta(minutes=self.tol)
        
        if entry_time.time() < self.office_entry_time.time():
            return "Early"
        
        if entry_time.time() >= self.office_entry_time.time() and entry_time.time() <= tol_time.time():
            return "On Time"
        
        return "Late"
    
    def _calculte_shifted_entry(self, start_time, end_time):

        elapsed_time = end_time - start_time
        shifted_entry = end_time - elapsed_time

        return shifted_entry

        
    def _mark_attendance(self, name, entry_time):

    # """
    # Mark the attendance of the entered person and update data in the database
    # Args: 
    #     name [str]: name/id of the entered person
    #     start_time: [datetime]: Time when the detection process begins
    #     end_time [datetime]: Time at completing the recognizing process
    # """
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            cursor.execute("""CREATE TABLE IF NOT EXISTS attendance(
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            entry_date DATE NOT NULL,
                            entry_time TIME NOT NULL, 
                            status TEXT NOT NULL)""")

            # Check if the person's ID already exists in the table
            cursor.execute("SELECT id FROM attendance WHERE name = %s", (name,))
            row = cursor.fetchone()
        
            if not row:
                # Person's ID does not exist, insert a new record
                # Calculate status
                status = self._status(entry_time)

                # Execute SQL query to insert attendance information into the database
                cursor.execute("""INSERT INTO attendance (name, entry_date, entry_time, status) 
                                  VALUES (%s, %s, %s, %s)""",
                               (name, entry_time.date(), entry_time.strftime("%I:%M %p"), status))

                conn.commit()
                print("Attendance marked successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while marking attendance:", error)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
     
        return
