//Dropzone handler

class Dropzone {
    constructor(dropzoneElement, logger) {
        this.dropzoneElement = dropzoneElement;
        this.logger = logger;

        this.dropzoneElement.addEventListener("dragover", this.handleDragOver.bind(this), false);
        this.dropzoneElement.addEventListener("dragleave", this.handleDragLeave.bind(this), false);
        this.dropzoneElement.addEventListener("drop", this.handleDrop.bind(this), false);
        this.dropzoneElement.addEventListener("click", this.handleClick.bind(this), false);

        this.name = dropzoneElement.getAttribute("data-name");
        this.nameElement = document.createElement("div");
        this.nameElement.classList.add("dropzone-name");
        this.nameElement.innerHTML = this.name;
        this.dropzoneElement.appendChild(this.nameElement);
    }

    handleDragOver(event) {
        event.stopPropagation();
        event.preventDefault();
        this.dropzoneElement.classList.add("dropzone-dragover");
    }

    handleDragLeave(event) {
        event.stopPropagation();
        event.preventDefault();
        this.dropzoneElement.classList.remove("dropzone-dragover");
    }

    handleDrop(event) {
        event.stopPropagation();
        event.preventDefault();
        this.dropzoneElement.classList.remove("dropzone-dragover");
        this.addFile(event.dataTransfer.files[0]);
    }

    handleClick(event) {
        event.stopPropagation();
        event.preventDefault();

        // Open file dialog
        let fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.addEventListener("change", this.handleFileInput.bind(this), false);
        fileInput.click();
    }

    handleFileInput(event) {
        this.addFile(event.target.files[0]);
    }

    addFile(file) {
        let fileElement = document.createElement("div");
        fileElement.classList.add("dropzone-file");
        fileElement.innerHTML = file.name;
        this.dropzoneElement.appendChild(fileElement);

        this.file = file;
        this.dropzoneElement.removeChild(this.nameElement);

        this.logger.log("Added file " + file.name);
    }

    getFile() {
        return this.file;
    }
}

class Logger {
    constructor(element) {
        this.logElement = element;
    }

    log(message, overwrite = false) {
        if (!overwrite) {
            this.logElement.innerHTML = this.logElement.innerHTML + message + "<br>";
        } else {
            //Overwrite last line
            let lines = this.logElement.innerHTML.split("<br>");
            lines[lines.length - 2] = message;
            this.logElement.innerHTML = lines.join("<br>");
        }

        //Scroll to bottom
        this.logElement.scrollTop = this.logElement.scrollHeight;
    }
}

let statusUpdater;
statusHandler = function (id) {
    //Get request to /api/task/<id>
    //Don't wait for response
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/task/" + id, true);
    xhr.timeout = 1000;
    xhr.send();

    //Get the response
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            let response = JSON.parse(xhr.responseText);

            if (response.status === "Finished processing") {
                clearInterval(statusUpdater);

                //Start download but don't leave the page
                let downloadLink = document.createElement("a");
                downloadLink.href = "/api/download/" + id;
                downloadLink.download = "frames.zip";
                downloadLink.click();

                logger.log("Downloading frames.zip");
            }

            logger.log(response.status, response.overwrite);
        }
    };
};

formSubmit = function (form) {
    let files = [];
    for (let dropzone of dropzones) {
        files.push(dropzone.getFile());
    }

    let selectors = form.querySelectorAll(".framerate-selector > input");

    let outputFramerate = selectors[0].value;
    let videoFramerate = selectors[1].value;

    //Upload the files
    let formData = new FormData();
    let i = 0;
    for (let file of files) {
        //The files need names
        formData.append("files", file, "file" + i++);
    }

    let data = {
        outputFramerate: outputFramerate,
        videoFramerate: videoFramerate,
    };

    formData.append("data", JSON.stringify(data));

    logger.log("Uploading files, this may take a while...");
    let xhr = new XMLHttpRequest();

    //Log the progress
    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            let percentComplete = event.loaded / event.total;
            logger.log("Uploaded " + Math.round(percentComplete * 100) + "%", true);
        }
    };

    xhr.open("POST", "/api/process", true);
    xhr.send(formData);

    //Get the response
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            let response = JSON.parse(xhr.responseText);
            if (response.id) {
                logger.log("Processing ID: " + response.id);
                statusUpdater = setInterval(statusHandler, 500, response.id);
            }
        }
    };
};

dropzones = [];
logger = null;

document.addEventListener("DOMContentLoaded", function () {
    //Create logger
    logger = new Logger(document.querySelector(".output"));

    for (let dropzoneElement of document.getElementsByClassName("dropzone")) {
        dropzones.push(new Dropzone(dropzoneElement, logger));
    }
});
