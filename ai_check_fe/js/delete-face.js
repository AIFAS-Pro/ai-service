import { AI_URL } from "./config.js";

const schoolIdInput = document.getElementById("schoolId");
const studentIdInput = document.getElementById("studentId");
const deleteBtn = document.getElementById("deleteBtn");
const result = document.getElementById("result");


deleteBtn.addEventListener("click", async () => {
    const schoolId = schoolIdInput.value.trim();
    const studentId = studentIdInput.value.trim();

    // Validation
    if (!schoolId) {
        showError("Please enter School ID.");
        schoolIdInput.focus();
        return;
    }
    if (!studentId) {
        showError("Please enter Student ID.");
        studentIdInput.focus();
        return;
    }

    // Confirmation
    const confirmed = confirm(
        `Are you sure you want to delete the face embedding?\n\n` +
        `School ID: ${schoolId}\n` +
        `Student ID: ${studentId}`
    );
    if (!confirmed) {
        return;
    }

    // Disable button
    deleteBtn.disabled = true;
    deleteBtn.textContent = "Deleting...";
    result.innerHTML = "";
    try {
        const formData = new FormData();
        formData.append("school_id", schoolId);
        formData.append("student_id", studentId);
        const response = await fetch(
            `${AI_URL}/delete-face`,
            {
                method: "DELETE",
                body: formData
            }
        );
        const data = await response.json();
        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to delete face embedding."
            );
        }
        // Success
        result.innerHTML = `
            <div class="success-card">
                <h3>Face Deleted Successfully</h3>
                <p>
                    ${data.message}
                </p>
                <p>
                    <strong>School ID:</strong> ${schoolId}
                </p>
                <p>
                    <strong>Student ID:</strong> ${studentId}
                </p>
            </div>
        `;

        // Clear fields
        schoolIdInput.value = "";
        studentIdInput.value = "";
    } catch (error) {
        console.error("Delete face error:", error);
        showError(
            error.message ||
            "Unable to connect to AI service."
        );
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.textContent = "Delete Face";

    }
});

function showError(message) {
    result.innerHTML = `
        <div class="error">
            ${message}
        </div>
    `;
}