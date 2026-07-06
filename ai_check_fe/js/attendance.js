const API = "http://127.0.0.1:8000";

document
    .getElementById("verifyBtn")
    .addEventListener("click", async () => {

        const files = document.getElementById("images").files;
        const scope = document.getElementById("scope").value;

        if (files.length === 0) {
            alert("Select attendance images");
            return;
        }

        const formData = new FormData();

        for (const file of files) {
            formData.append("images", file);
        }

        if (scope) {
            formData.append("scope", scope);
        }

        const result = document.getElementById("result");

        result.innerHTML = "<p>Processing...</p>";

        try {

            const response = await fetch(`${API}/verify-attendance`, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                result.innerHTML = `<p class="error">${data.detail}</p>`;
                return;
            }

            let html = `
                <div class="table-container">

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
                            <span class="badge ${student.status.toLowerCase() === 'present' ? 'present' : 'absent'}">
                                ${student.status}
                            </span>
                        </td>

                    </tr>
                `;

            });

            html += `
                        </tbody>

                    </table>

                </div>
            `;

            result.innerHTML = html;

        }
        catch (error) {

            result.innerHTML = `
                <p class="error">
                    ${error.message}
                </p>
            `;

        }

    });