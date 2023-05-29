# Video Frame Metadata Extraction

This Python script is designed to extract metadata from an SRT file and write it to the frames of a video. It utilizes the `ffmpeg` and `exiftool` command-line tools to split the video into frames and write the metadata, respectively.

## Prerequisites

-   Python 3.x
-   `ffmpeg` command-line tool
-   `exiftool` command-line tool

## Usage

1. Ensure that you have Python 3.x installed on your system.
2. Install the required Python dependencies by running the following command:

    ```shell
    pip install argparse
    ```

3. Install `ffmpeg` and `exiftool` on your system. Instructions for installation can be found on the official websites of the respective tools.
4. Download or clone the script to your local machine.

5. Open a terminal or command prompt and navigate to the directory containing the script.

6. Run the following command to execute the script:

    ```shell
    python tagger.py --video <path_to_video> --srt <path_to_srt> [--framerate <framerate>] [--framerate-video <framerate_video>] [--frames_dir <frames_dir>] [--metadata-file <metadata_file>]
    ```

    Replace `tagger.py` with the actual name of the script file.

    #### Parameters

    - `--video`: (required) Path to the video file.
    - `--srt`: (required) Path to the SRT file containing metadata.
    - `--framerate`: (optional) Framerate at which to output the frames. Default is `1`.
    - `--framerate-video`: (optional) Framerate of the input video. Default is `30`.
    - `--frames_dir`: (optional) Path to the directory where the frames will be saved. Default is `'frames/'`.
    - `--metadata-file`: (optional) Path to the metadata image file. Default is `'metadata.jpg'`.

    **Note**: Make sure to replace `<path_to_video>`, `<path_to_srt>`, and other parameters with the actual paths and values.

7. The script will perform the following actions:

    - Parse the SRT file to extract frame numbers, timestamps, and metadata.
    - Split the video into frames using `ffmpeg`.
    - Write the metadata from the metadata image file to the frames using `exiftool`.
    - Write the extracted metadata to the frames using `exiftool`.

8. After the script finishes executing, you will find the frames with the embedded metadata in the specified `--frames_dir` directory.

## Example

Here is an example command to run the script:

```shell
python tagger.py --video input_video.mp4 --srt input_metadata.srt --framerate 2 --framerate-video 30 --frames_dir output_frames --metadata-file metadata.jpg
```

In this example, the script will extract metadata from the `input_metadata.srt` file and embed it into the frames of the `input_video.mp4` video. The frames will be saved in the `output_frames` directory, and the metadata will be written using the `metadata.jpg` file.

The `metadata.jpg` file should be a photo you have taken with the device that captured the video.

Feel free to adjust the parameters according to your specific requirements.
