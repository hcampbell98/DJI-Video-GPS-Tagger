# Video Processing App

This is a Flask-based web application for processing video files and generating frames from them. It also provides functionality to download the processed frames as a zip file. The application runs a separate thread to periodically clean up the uploaded files older than 1 hour.

## Prerequisites

-   Python 3.x
-   Flask
-   FFmpeg (for video processing)
-   exiftool
-   argparse

## Installation

1. Clone the repository:

    ```shell
    $ git clone https://github.com/hcampbell98/DJI-Video-GPS-Tagger.git
    $ cd DJI-Video-GPS-Tagger/web_app
    ```

2. Create and activate a virtual environment (optional):

    ```shell
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```

3. Install the required dependencies:

    ```shell
    $ pip install -r requirements.txt
    ```

4. Start the application:

    ```shell
    $ python app.py
    ```

    The application should now be running on `http://localhost:5000`.

## Usage

1. Access the application by visiting `http://localhost:5000` in your web browser.

2. Upload a video file and its corresponding subtitle file (SRT format).

3. Provide additional processing parameters (output framerate, video framerate).

4. Click the "Process" button to initiate the video processing.

5. The application will display the status of the processing task.

6. Once the task is finished, you can download the processed frames as a zip file.

## API Endpoints

-   `POST /api/process`: Initiates the video processing task. Expects a video file and a subtitle file to be uploaded along with additional processing parameters. Returns the ID of the task.

-   `GET /api/task/<id>`: Retrieves the status of a processing task with the specified ID.

-   `GET /api/download/<id>`: Downloads the processed frames as a zip file for a completed task with the specified ID.

## Cleanup Process

The application runs a cleanup process in a separate thread to remove uploaded files that are older than 1 hour. This ensures that the server's storage space is not consumed by unnecessary files. The cleanup process runs every 30 seconds.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
