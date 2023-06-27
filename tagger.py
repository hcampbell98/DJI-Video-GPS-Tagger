import os
from argparse import ArgumentParser
from datetime import datetime

def parse_srt_file(path, framerate, framerate_video):
    with open(path, 'r') as f:
        frame_data = []

        # The SRT file will be formatted as follows

        # 1
        # 00:00:00,000 --> 00:00:00,033
        # <font size="28">SrtCnt : 1, DiffTime : 33ms
        # 2023-05-02 19:40:59.725
        # [iso : 100] [shutter : 1/125.0] [fnum : 170] [ev : 0] [ct : 5289] [color_md : default] [focal_len : 240] [dzoom_ratio: 10000, delta:0],[latitude: 53.578046] [longitude: -1.775009] [rel_alt: 34.600 abs_alt: 137.305] </font>
        #
        # 2
        # etc...

        # We want to extract the frame number, the timestamp, and the data in the square brackets
        # We will store this in a list of dictionaries, where each dictionary represents a frame

        lines = f.readlines()
        for i in range(0, len(lines), int(6 * (framerate_video / framerate))):
            frame = {}
            frame['frame'] = int(lines[i].strip())
            frame['timestamp'] = lines[i+3].strip()

            # The data is in the square brackets, so we split the line by ']' and take the second half
            # We then split this by ' : ' and take the second half
            # This gives us the data we want
            attributes = lines[i+4].split(']')

            for attr in attributes:
                if ': ' in attr:
                    frame[attr.split(": ")[0].replace('[', '').strip()] = attr.split(": ")[1]

            frame_data.append(frame)
        return frame_data

def split_video_into_frames(path_to_video, path_to_frames, framerate):
    # Check if the frames directory exists
    if not os.path.exists(path_to_frames):
        # We first create the directory to store the frames
        os.mkdir(path_to_frames)

        # The command to split the video into frames
        # We use ffmpeg to do this
        # The command will be formatted as follows
        # ffmpeg -i <path_to_video> -r <framerate> <path_to_frames>/frame%04d.jpg
        command = f"ffmpeg -i {path_to_video} -r {framerate} {path_to_frames}/%04d.jpg"

        # We run the command
        os.system(command)

def write_data_to_frame(path_to_frames, frame_data):
    # Get files in the frames directory
    files = os.listdir(path_to_frames)

    for index in range(len(files)):
        file = files[index]

        # Data associated with frame
        data = None
        if index < len(frame_data):
            data = frame_data[index]
        else:
            data = frame_data[-1]

        # The command to write the data to the frame
        # We use exiftool to do this
        ts = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
        cmd = f"exiftool {path_to_frames}/{index+1:04d}.jpg -overwrite_original -GPSLatitude={float(data[',latitude'])} -GPSLongitude={float(data['longitude'])} -GPSAltitude={float(data['rel_alt'].split(' ')[0])} -GPSLatitudeRef=N -GPSLongitudeRef=W -GPSAltitudeRef=0 -DateTimeOriginal=\"{ts.strftime('%Y:%m:%d %H:%M:%S.%f')}\" -ShutterSpeedValue={data['shutter']} -FNumber={data['fnum']} -ExposureCompensation={data['ev']} -ColorTemperature={data['ct']} -FocalLength={data['focal_len']}"
        print("Exif data modified for frame", index+1, "of", len(files))
        
        #Run the command but don't print the output. Needs to work on Windows and Linux
        os.system(cmd + " > /dev/null 2>&1" if os.name == 'posix' else cmd + " > nul 2>&1")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--video', type=str, required=True, help='Path to video')
    parser.add_argument('--srt', type=str, required=True, help='Path to SRT file')
    parser.add_argument('--framerate', type=int, default=1, help='Framerate to output frames at')
    parser.add_argument('--framerate-video', type=int, default=30, help='Framerate of the input video')
    parser.add_argument('--frames-dir', type=str, default='frames/', help='Path to output frames to')
    parser.add_argument('--metadata-file', type=str, default='metadata.jpg', help='Path to metadata image')

    args = parser.parse_args()

    # Parse the SRT file
    frame_data = parse_srt_file(args.srt, args.framerate, args.framerate_video)

    # Split the video into frames
    split_video_into_frames(args.video, args.frames_dir, args.framerate)

    # Write all metadata from metadata file to the frames
    os.system(f"exiftool -overwrite_original -TagsFromFile {args.metadata_file} -all:all {args.frames_dir}")

    # Write the data to the frames
    write_data_to_frame(args.frames_dir, frame_data)

