const API = "http://127.0.0.1:8000";

const verifyBtn = document.getElementById("verifyBtn");

verifyBtn.addEventListener("click", async () => {

    const files = document.getElementById("images").files;
    const schoolId = document.getElementById("schoolId").value.trim();
    // const academicYear = document.getElementById("academicYear").value.trim();
    const studentIds = document.getElementById("studentIds").value.trim();

    if (!schoolId) {
        alert("Enter School ID");
        return;
    }

    // if (!academicYear) {
    //     alert("Enter Academic Year");
    //     return;
    // }

    if (files.length === 0) {
        alert("Select attendance images");
        return;
    }

    const summary = document.getElementById("summary");
    const table = document.getElementById("attendanceTable");

    summary.innerHTML = "<p>Processing...</p>";
    table.innerHTML = "";

    verifyBtn.disabled = true;
    verifyBtn.textContent = "Verifying...";

    const formData = new FormData();

    formData.append("school_id", schoolId);
    // formData.append("academic_year", academicYear);

    if (studentIds !== "") {
        formData.append("student_ids", studentIds);
    }

    for (const file of files) {
        formData.append("images", file);
    }

    try {

        const response = await fetch(`${API}/verify-attendance`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {

            summary.innerHTML = `
                <div class="error">
                    ${data.detail}
                </div>
            `;

            table.innerHTML = "";

            return;
        }

        summary.innerHTML = `
            <div class="success-card">

                <h3>Verification Completed</h3>

                <p><strong>School ID:</strong> ${data.school_id}</p>

                <p><strong>Images Uploaded:</strong> ${data.image_count}</p>

                <p><strong>Detected Faces:</strong> ${data.detected_faces}</p>

                <p><strong>Registered Students:</strong> ${data.students.length}</p>

                <p><strong>Matched Students:</strong> ${data.matches.length}</p>

            </div>
        `;

        let html = `
            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>Student ID</th>

                        <th>Status</th>

                    </tr>

                </thead>

                <tbody>
        `;

        data.students.forEach((student, index) => {

            html += `
                <tr>

                    <td>${index + 1}</td>

                    <td>${student.student_id}</td>

                    <td>

                        <span class="badge ${student.status.toLowerCase() === "present" ? "present" : "absent"}">

                            ${student.status}

                        </span>

                    </td>

                </tr>
            `;

        });

        html += `
                </tbody>

            </table>
        `;

        table.innerHTML = html;

    } catch (error) {

        summary.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;

        table.innerHTML = "";

    } finally {

        verifyBtn.disabled = false;
        verifyBtn.textContent = "Verify Attendance";

    }

});