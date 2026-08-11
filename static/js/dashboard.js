/* dashboard.js — renders the risk-distribution chart from server-provided data */

(function () {
  "use strict";

  const canvas = document.getElementById("riskChart");
  if (!canvas || typeof Chart === "undefined") return;

  const buckets = JSON.parse(canvas.dataset.buckets || "{}");
  const labels = Object.keys(buckets);
  const values = Object.values(buckets);

  const colors = ["#35D68A", "#8FE6B4", "#FFB84D", "#FF8A6B", "#FF5D6C"];

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Scans",
        data: values,
        backgroundColor: colors,
        borderRadius: 6,
        maxBarThickness: 46,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: "#1C2531" },
          ticks: { color: "#7E8FA0", font: { family: "IBM Plex Mono", size: 11 } },
        },
        y: {
          beginAtZero: true,
          ticks: { color: "#7E8FA0", precision: 0 },
          grid: { color: "#1C2531" },
        },
      },
    },
  });
})();
