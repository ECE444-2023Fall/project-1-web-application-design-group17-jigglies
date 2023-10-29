document.addEventListener("DOMContentLoaded", function() {
    const dropZone = document.querySelector(".flex.flex-col.w-full.p-8");
    const fileInput = document.getElementById("file-upload");
    const uploadText = document.getElementById("upload-text");
    const imagePreview = document.getElementById("image-preview");
    const uploadIcon = document.getElementById("upload-icon");

    if (!dropZone) {
        console.error("Drop zone element not found!");
        return;
    }

    dropZone.addEventListener("dragover", function(e) {
        e.preventDefault();
    });

    dropZone.addEventListener("drop", function(e) {
        e.preventDefault();

        if (e.dataTransfer.items && e.dataTransfer.items[0].kind === "file") {
            const file = e.dataTransfer.items[0].getAsFile();
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            previewImage(file);
        }
    });

    fileInput.addEventListener("change", function() {
        const file = fileInput.files[0];
        if (file) {
            previewImage(file);
        }
    });

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove("hidden");
            uploadIcon.classList.add("hidden");
            uploadText.textContent = "Replace image";
        };
        reader.readAsDataURL(file);
    }
});
