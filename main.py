from flask import *
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from PIL import Image
import os


import cv2
import time
from mtcnn import MTCNN
import lightgbm as lgb  


app = Flask(__name__)

import pymysql

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mental_health'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)



csv_file_path = r'static/student.csv'
df = pd.read_csv(csv_file_path)

def map_values(value):
    if 1 <= value <= 5:
        return 1
    elif 6 <= value <= 10:
        return 2
    elif 11 <= value <= 15:
        return 3
    elif 16 <= value <= 20:
        return 4
    elif 21 <= value <= 25:
        return 5
    else:
        return value

# Apply mapping for anxiety_level and depression
df['anxiety_level'] = df['anxiety_level'].apply(map_values)
df['depression'] = df['depression'].apply(map_values)

# Apply mapping for self_esteem (range 1 to 30)
df['self_esteem'] = df['self_esteem'].apply(lambda x: min(5, max(1, (x-1) // 5 + 1)))

# Assuming you have your data loaded into a DataFrame 'data'
# Features_for_clustering should contain the relevant features for clustering
features_for_clustering = df[['anxiety_level', 'self_esteem', 'mental_health_history', 'depression', 'headache', 'blood_pressure','sleep_quality', 'breathing_problem', 'noise_level', 'living_conditions', 'safety', 'basic_needs', 'future_career_concerns', 'social_support']]

# Scale the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features_for_clustering)




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/")
def user_login():
    return render_template("about.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/TherapistConsultancy")
def therapist():
    return render_template("TherapistConsultancy.html")


@app.route("/book")
def book():
    return render_template("book.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=['POST','GET'])
def login():
    cur = mysql.cursor()
    context = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur.execute("SELECT * FROM users WHERE username = %s and password=%s", (username,password,))
        existing_user = cur.fetchone()
        
        if  existing_user:
            if existing_user[1] == username and existing_user[2] == password:
                user = existing_user[1]
                return redirect(url_for('questionaire'))
            else:
                context['message']="Invalid Details"
                context['category']="danger"
                return render_template("login.html", data=context)
        else:
            context['message']="Invalid Details"
            context['category']="danger"
            return render_template("login.html", data=context)
    cur.close()
    return render_template("login.html", data=context)

@app.route("/index2")
def index2():
    return render_template("index2.html")

@app.route("/about2")
def about2():
    return render_template("about2.html")

@app.route("/TherapistConsultancy2")
def therapist2():
    return render_template("TherapistConsultancy2.html")

@app.route("/profile2")
def profile2():
    return render_template("profile2.html")

@app.route("/contact2")
def contact2():
    return render_template("contact2.html")

@app.route("/registration", methods=['POST','GET'])
def registration():
    cur = mysql.cursor()
    context = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password == confirmPassword:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchall()

            if len(existing_user):
                context['message']="User already exist"
                context['category']="danger"
                return render_template("registration.html", data=context)
            
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.commit()
            
            return redirect(url_for('questionaire'))
        else:
            context['message']="Password mismatch"
            context['category']="danger"
            return render_template("registration.html", data=context)

    cur.close()
    return render_template("registration.html", data=context)


@app.route("/questionaire")
def questionaire():
    return render_template("questionaire.html")

@app.route("/test")
def test():
    return render_template("test.html")

# Logout route
@app.route('/logout')
def logout():
    user = None
    return redirect(url_for('login'))

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json.get('data')
    user_input = [int(value) for value in data]

    
    print(user_input)
        
    # Calculate the average of user inputs
    user_average = sum(user_input) / len(user_input)

    # Convert the average to percentage (assuming the scores are on a scale of 1 to 5)
    user_percentage = (user_average / 5) * 100

    user_cluster_name = (round(user_percentage,2))

    return jsonify({'success': True, 'message': user_cluster_name})

@app.route("/output", methods=['GET'])
def output():
    if request.method == "GET":
        output = (request.args.get('output'))
        print(output)
        return render_template("output.html", output=output)


def load_images_from_folder(folder, label):
    images = []
    labels = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        try:
            img = Image.open(img_path)
            img = img.convert('RGB')  
            img = img.resize((224, 224))  
            img_array = np.array(img)
            images.append(img_array)  
            labels.append(label)
        except Exception as e:
            print(f"Error loading image: {img_path} - {e}")
    return np.array(images), np.array(labels)

# Specify the paths to your dataset folders
autistic_folder = r"static/img/test/Autistic"
nonautistic_folder = r"static/img/test/Non_Autistic"

# Load autistic images and labels
X_autistic, y_autistic = load_images_from_folder(autistic_folder, 1)

# Load nonautistic images and labels
X_nonautistic, y_nonautistic = load_images_from_folder(nonautistic_folder, 0)

# Concatenate the datasets
X = np.concatenate((X_autistic, X_nonautistic), axis=0)
y = np.concatenate((y_autistic, y_nonautistic), axis=0)

# Encode labels to numerical values
label_encoder = preprocessing.LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Flatten the images before creating the LightGBM dataset
X_train_flatten = X_train.reshape(X_train.shape[0], -1)
X_test_flatten = X_test.reshape(X_test.shape[0], -1)

# Define the LightGBM dataset
train_data = lgb.Dataset(X_train_flatten, label=y_train)
test_data = lgb.Dataset(X_test_flatten, label=y_test, reference=train_data)

# Set hyperparameters with adjustments
params = {
    'objective': 'binary',
    'metric': 'binary_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 64,  # Adjusted num_leaves
    'learning_rate': 0.05,
    'feature_fraction': 0.9
}

# Train the LightGBM model
num_round = 10
bst = lgb.train(params, train_data, num_round, valid_sets=[test_data])

@app.route("/face")
def face():

    # Create an MTCNN detector
    detector = MTCNN()

    # Capture video from the default camera (you can replace this with your own image loading logic)
    cap = cv2.VideoCapture(0)

    # Set the duration for which the code should run (in seconds)
    duration = 5
    end_time = time.time() + duration

    print("Scanning for face...")

    # Variables to accumulate autism probabilities
    total_proba = 0.0
    num_faces = 0

    # Read a frame from the camera
    ret, frame = cap.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame using MTCNN
    faces = detector.detect_faces(frame)

    if len(faces) > 1:
        return render_template('face.html', data="multiple faces detected")
    
    
    

    # Process each detected face
    for face in faces:
        x, y, w, h = face['box']
        conf = face['confidence']

        # Extract the face region
        face_roi = frame[y:y + h, x:x + w]

        # Check if the face_roi is not empty
        if not face_roi.size == 0:
            # Preprocess the face image (resize, convert to RGB, flatten)
            face_img = cv2.resize(face_roi, (224, 224))
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            face_img_flatten = face_img.reshape(1, -1)

            # Use the trained LightGBM model to predict the probability
            face_pred_proba = bst.predict(face_img_flatten, num_iteration=bst.best_iteration)

            # Accumulate probabilities and count faces
            total_proba += face_pred_proba[0]
            num_faces += 1

            # Print the result in the terminal
            print(f"Autism: {100 - face_pred_proba[0] * 100:.2f}%")
            # aut = aut.2f
            # Draw a rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Face Detection',frame)


    # Calculate average autism probability
    average_proba = total_proba / num_faces if num_faces > 0 else 0.0
    # print(f"Average Autism Probability: {average_proba*100:.2f}%")
    output = {100-average_proba*100}

    return render_template("face.html", data=output)

if __name__ == "__main__":
    app.run(debug=True)