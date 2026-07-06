const API = "http://127.0.0.1:8000";

const imageInput = document.getElementById("images");
const scopeInput = document.getElementById("scope");
const button = document.getElementById("registerBtn");
const result = document.getElementById("result");
const imageList = document.getElementById("imageList");

let selectedFiles = [];

// Display selected images with editable Student IDs
imageInput.addEventListener("change", () => {

    selectedFiles = [...imageInput.files];

    imageList.innerHTML = "";

    if (selectedFiles.length === 0) {
        return;
    }

    selectedFiles.forEach((file, index) => {

        // Default Student ID = filename without extension
        const studentID = file.name.replace(/\.[^/.]+$/, "");

        const card = document.createElement("div");
        card.className = "image-card";

        card.innerHTML = `
            <img src="${URL.createObjectURL(file)}" alt="${studentID}">

            <div style="flex:1">

                <label>Student ID</label>

                <input
                    type="text"
                    class="student-id"
                    data-index="${index}"
                    value="${studentID}"
                >

                <small style="display:block;margin-top:5px;color:#666;">
                    ${file.name}
                </small>

            </div>
        `;

        imageList.appendChild(card);

    });

});

button.addEventListener("click", async (event) => {

    event.preventDefault();

    if (selectedFiles.length === 0) {
        alert("Please select one or more images.");
        return;
    }

    const scope = scopeInput.value.trim();

    const studentInputs = document.querySelectorAll(".student-id");

    button.disabled = true;
    button.textContent = "Uploading...";

    let success = 0;
    let failed = 0;

    result.innerHTML = `
        <div class="progress">
            Starting upload...
        </div>
    `;

    for (let i = 0; i < selectedFiles.length; i++) {

        const file = selectedFiles[i];
        const studentID = studentInputs[i].value.trim();

        if (!studentID) {

            failed++;

            result.innerHTML = `
                <div class="progress">
                    Skipped ${i + 1}/${selectedFiles.length} (Student ID Empty)
                </div>
            `;

            continue;
        }

        const formData = new FormData();

        formData.append("student_id", studentID);
        formData.append("image", file);

        if (scope !== "") {
            formData.append("scope", scope);
        }

        try {

            result.innerHTML = `
                <div class="progress">
                    Uploading ${i + 1} / ${selectedFiles.length}
                    <br>
                    <strong>${studentID}</strong>
                </div>
            `;

            const response = await fetch(`${API}/register-face`, {
                method: "POST",
                body: formData
            });

            if (response.ok) {

                success++;

                const card = imageList.children[i];
                card.style.border = "2px solid #16a34a";
                card.style.background = "#f0fdf4";

            } else {

                failed++;

                const card = imageList.children[i];
                card.style.border = "2px solid #dc2626";
                card.style.background = "#fef2f2";

            }

        } catch (error) {

            console.error(error);

            failed++;

            const card = imageList.children[i];
            card.style.border = "2px solid #dc2626";
            card.style.background = "#fef2f2";

        }

    }

    result.innerHTML = `
        <div class="success-card">

            <h3>Upload Completed</h3>

            <p><strong>Total Images:</strong> ${selectedFiles.length}</p>

            <p style="color:green;">
                <strong>Successful:</strong> ${success}
            </p>

            <p style="color:red;">
                <strong>Failed:</strong> ${failed}
            </p>

        </div>
    `;

    imageInput.value = "";
    imageList.innerHTML = "";
    scopeInput.value = "";
    selectedFiles = [];

    button.disabled = false;
    button.textContent = "Register Face";

});