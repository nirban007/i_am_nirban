<h1 align='center' style=color:#fe5e21;><strong>Who Are You</strong></h1>

<h3 align='center' style=color:#fe5e21;><strong>A face recognition based attendance system.</strong></h3>

## Introduction
This face recognition based attendance system caputes images through your webcam/camera device and puts a box around the detected face with the accuracy and the name of the person. Uses [`insightface`](https://insightface.ai/) library with `buffalo_l` model at the backend

## Project Structure

[`face_recognition`](https://github.com/Tasfiq-K/who-are-you/tree/main/face_recognition): Contains the driver code and the utility functions for the face recognition system

## Usage
To get started, first clone this repo using:
```bash
git clone https://github.com/Tasfiq-K/who-are-you.git
```
 then install the required packages from the [requirements](https://github.com/Tasfiq-K/who-are-you/blob/main/requirements.txt) file. 

Using the command line:
```bash
pip install -r requirements.txt
```
This will install all the required dependencies.

Next, you need to create embedding vectors (if you don't have already) for the people you want detect/recognize through any camera device connected to the machine which should run the code. 

To do that, you can just call the `create_person_embedding` function and pass the directory that contains the folder with the images of the persons. 

To be able to consistent with the code structure, create your directory structure for the images like below.

 suppose the main directory is called `photos` and it has sub-directories named `person_1` and `person_2` which actually contains the images of `person_1` and `person_2`
```bash
photos/
     |
     |___person_1/
     |      |
     |      |___image_1.jpg
     |      |___image_2.jpg
     |      .
     |      .
     |___person_2/
            |
            |___image_1.jpg
            |___image_2.jpg
            .
            .
```
It's a good idea to name the image folders like `person_1`, `person_2` with the actual name of the person whose photos are in those directories.

Now, pass the main directory name in string format to the `create_person_embedding` function and it will automatically create the embeddings and will return a dictionary.

Next, pass the embedding dictionary to `recognize_face` function with the id of the camera that you want to use. This will launch the camera and will be ready for matching the face.