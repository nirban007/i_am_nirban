import os
import cv2
from functions import FaceRecognition
import psycopg2

def embeddings_database_exists(db_params):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Check if the embeddings table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'embeddings')")
        exists = cursor.fetchone()[0]

        return exists
    except psycopg2.Error as e:
        print("Error while checking embeddings database:", e)
        return False
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def fetch_embeddings_from_database(db_params):
    embeddings_dict = {}
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Fetch embeddings from the database
        cursor.execute("SELECT name, embedding_arr FROM embeddings")
        rows = cursor.fetchall()

        for row in rows:
            name = row[0]
            embeddings = row[1]
            embeddings_dict[name] = embeddings

        return embeddings_dict
    except psycopg2.Error as e:
        print("Error while fetching embeddings from the database:", e)
        return None
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hour = input("Enter Opening Hour (HH): ")
    mins = input("Enter Opening Minutes (MM): ")
    am_pm = input("AM/PM: ")
    photos_dir = os.path.join('D', os.sep, 'Projects', 'who-are-you', 'face_recognition', 'Employee', 'employee_images')
    #D:\Projects\who-are-you\face_recognition\Employee\employee_images
    # Database connection parameters
    db_params = {
        "dbname": "face_rec",
        "user": "postgres",
        "password": "nirban@007",
        "host": "localhost",
    }

    face_rec = FaceRecognition(set_entry_hour=hour, 
                               set_entry_min=mins, 
                               set_meridian=am_pm, 
                               tol=30)

    if embeddings_database_exists(db_params):
        # If embeddings exist in the database, fetch them
        embeddings = fetch_embeddings_from_database(db_params)
    else:
        # If embeddings do not exist in the database, create them and save to the database
        embeddings = face_rec.create_person_embedding(photos_dir)
        # face_rec.save_embedding(embeddings, db_params)

    # print(embeddings)

    try:
        face_rec.recognize_face(embeddings=embeddings, cam_id=0)
    except cv2.error as e:
        print("OpenCV Error:", e)

if __name__ == "__main__":
    main()