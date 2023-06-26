from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, after_this_request
import random, string, json, os, subprocess, shutil, time, threading, schedule

app = Flask(__name__)
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')


last_task_update = 0
task_queue = []

#tasks[id] = json.dumps({'status': status})
def update_task(id, status):
    tasks[id] = json.dumps({'status': status})

@app.route('/api/process', methods=['POST'])
def process():
    #Generate an ID for this request
    #Random string of 10 characters
    id = ''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))

    files = request.files.getlist('files')

    update_task(id, 'Files uploaded')
    #Get the files from the POST request.
    video_file = files[0]
    srt_file = files[1]

    #Make a directory called the ID in the uploads folder
    output_path = os.path.join(os.getcwd(), 'uploads', id)
    os.mkdir(output_path)

    #Write the files to disk
    video_path = os.path.join(output_path, id + '.mp4')
    srt_path = os.path.join(output_path, id + '.srt')

    video_file.save(video_path)
    srt_file.save(srt_path)

    update_task(id, 'Files saved')

    #Get the data from the POST request
    data = json.loads(request.form['data'])

    update_task(id, 'Processing')
    #Run the task in a separate thread
    thread = threading.Thread(target=process_task, args=(data, id))
    thread.start()

        
    #Return the ID to the client
    return json.dumps({'id': id})

def process_task(data, id):
    output_path = os.path.join(os.getcwd(), 'uploads', id)
    video_path = os.path.join(output_path, id + '.mp4')
    srt_path = os.path.join(output_path, id + '.srt')

    #Frame dir doesn't need to be created, it's created by the tagger script
    frames_path = os.path.join(output_path, 'frames')

    output_framerate = data['outputFramerate']
    video_framerate = data['videoFramerate']

    #Format command
    command = 'python3 ' + os.path.join(os.getcwd(), "tagger.py") + ' --video ' + video_path + ' --srt ' + srt_path + ' --framerate ' + output_framerate + ' --framerate-video ' + video_framerate + ' --frames-dir ' + frames_path
    
    print(command)

    update_task(id, 'Processing')
    #Run command, and log output with update_task
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        update_task(id, line.decode('utf-8').rstrip())

    #Zip the frames folder
    update_task(id, 'Compressing frames')
    zip_path = os.path.join(output_path, 'frames.zip')
    shutil.make_archive(zip_path[:-4], 'zip', frames_path)

    #Delete the frames folder
    update_task(id, 'Cleaning up')
    delete_command = 'rm -rf ' + frames_path
    process = subprocess.Popen(delete_command, shell=True)

    #Delete the video and srt files
    os.remove(video_path)
    os.remove(srt_path)

    update_task(id, 'Finished processing')

@app.route("/api/task/<id>", methods=['GET'])
def get_task(id):
    # Check the task exists
    if id not in tasks:
        return json.dumps({'error': 'Invalid task ID'})

    return tasks[id]

@app.route("/api/download/<id>", methods=['GET'])
def download(id):
    #Check the task exists
    if id not in tasks:
        return json.dumps({'error': 'Invalid task ID'})

    #Check the task is finished
    task = json.loads(tasks[id])
    if task['status'] != 'Finished processing':
        return json.dumps({'error': 'Task not finished'})

    #Zip file is in the uploads folder
    zip_path = os.path.join(os.getcwd(), 'uploads', id, 'frames.zip')

    update_task(id, 'Downloaded')
    return send_file(zip_path, as_attachment=True)


#Delete all files in the uploads folder if they're older than 1 hour
FILE_TIMEOUT = 60 * 60
def cleanup():
    for id in os.listdir(os.path.join(os.getcwd(), 'uploads')):
        path = os.path.join(os.getcwd(), 'uploads', id)
        if os.path.isdir(path):
            if time.time() - os.path.getctime(path) > FILE_TIMEOUT :
                shutil.rmtree(path)
schedule.every(30).seconds.do(cleanup)

#Run the cleanup function in a separate thread
def cleanup_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)
thread = threading.Thread(target=cleanup_thread)
thread.start()

if __name__ == '__main__':
    app.run()
