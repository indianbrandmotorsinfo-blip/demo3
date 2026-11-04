// Dashboard & Statistics Analytics Visualizations (using Chart.js)

function initStatisticsCharts(stats) {
    if (typeof Chart === "undefined" || !stats) return;

    // Set Chart.js global defaults for Clean Minimalism
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.color = "#64748b";

    // 1. Assignment Status Distribution
    const statusCtx = document.getElementById("statusChart");
    if (statusCtx && stats.assignments) {
        new Chart(statusCtx, {
            type: "doughnut",
            data: {
                labels: ["Open", "Full", "Closed"],
                datasets: [{
                    data: [
                        stats.assignments.open,
                        stats.assignments.full,
                        stats.assignments.closed
                    ],
                    backgroundColor: ["#10b981", "#f59e0b", "#64748b"],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "70%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, padding: 16 }
                    }
                }
            }
        });
    }

    // 2. Submissions Breakdown
    const subCtx = document.getElementById("submissionChart");
    if (subCtx && stats.submissions) {
        new Chart(subCtx, {
            type: "doughnut",
            data: {
                labels: ["Approved", "Pending Review", "Rejected"],
                datasets: [{
                    data: [
                        stats.submissions.approved,
                        stats.submissions.pending,
                        stats.submissions.rejected
                    ],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "70%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, padding: 16 }
                    }
                }
            }
        });
    }

    // 3. Group Size Distribution Bar Chart
    const sizeCtx = document.getElementById("sizeChart");
    if (sizeCtx && stats.group_size_distribution) {
        const labels = Object.keys(stats.group_size_distribution).map(k => `${k} Member${k > 1 ? 's' : ''}`);
        const values = Object.values(stats.group_size_distribution);

        new Chart(sizeCtx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Number of Assignments",
                    data: values,
                    backgroundColor: "#2563eb",
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: "#f1f5f9" }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

