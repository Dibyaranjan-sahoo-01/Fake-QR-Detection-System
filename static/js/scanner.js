/* scanner.js — QR upload flow, webcam capture flow, and result rendering */

(function () {
  "use strict";

  // ---------- Tab switching ----------
  const tabs = document.querySelectorAll(".qs-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".qs-scan-pane").forEach((p) => p.classList.add("d-none"));
      document.querySelector(tab.dataset.target).classList.remove("d-none");
    });
  });

  // ---------- Upload flow ----------
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");
  const previewWrap = document.getElementById("previewWrap");
  const previewImg = document.getElementById("previewImg");
  const analyzeUploadBtn = document.getElementById("analyzeUploadBtn");
  let selectedFile = null;

  browseBtn.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("click", (e) => {
    if (e.target === browseBtn) return;
    fileInput.click();
  });

  ["dragover", "dragenter"].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add("qs-drag-over");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.remove("qs-drag-over");
    })
  );
  dropZone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelected(file);
  });

  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) handleFileSelected(file);
  });

  function handleFileSelected(file) {
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewWrap.classList.remove("d-none");
      analyzeUploadBtn.classList.remove("d-none");
    };
    reader.readAsDataURL(file);
  }

  analyzeUploadBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    setButtonLoading(analyzeUploadBtn, true);
    showResultLoading();

    const formData = new FormData();
    formData.append("qr_image", selectedFile);

    try {
      const res = await fetch("/api/scan/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (data.success) {
        renderResult(data.scan);
      } else {
        showResultError(data.error || "Could not analyze the image.");
      }
    } catch (err) {
      showResultError("Network error while analyzing the image.");
    } finally {
      setButtonLoading(analyzeUploadBtn, false);
    }
  });

  // ---------- Webcam flow ----------
  const webcamVideo = document.getElementById("webcamVideo");
  const webcamCanvas = document.getElementById("webcamCanvas");
  const startWebcamBtn = document.getElementById("startWebcamBtn");
  const captureBtn = document.getElementById("captureBtn");
  const stopWebcamBtn = document.getElementById("stopWebcamBtn");
  let mediaStream = null;

  startWebcamBtn.addEventListener("click", async () => {
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      webcamVideo.srcObject = mediaStream;
      startWebcamBtn.classList.add("d-none");
      captureBtn.classList.remove("d-none");
      stopWebcamBtn.classList.remove("d-none");
    } catch (err) {
      showResultError("Could not access the camera. Check browser permissions.");
    }
  });

  stopWebcamBtn.addEventListener("click", stopWebcam);

  function stopWebcam() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop());
      mediaStream = null;
    }
    webcamVideo.srcObject = null;
    startWebcamBtn.classList.remove("d-none");
    captureBtn.classList.add("d-none");
    stopWebcamBtn.classList.add("d-none");
  }

  captureBtn.addEventListener("click", async () => {
    if (!mediaStream) return;
    webcamCanvas.width = webcamVideo.videoWidth;
    webcamCanvas.height = webcamVideo.videoHeight;
    const ctx = webcamCanvas.getContext("2d");
    ctx.drawImage(webcamVideo, 0, 0);
    const dataUrl = webcamCanvas.toDataURL("image/png");

    setButtonLoading(captureBtn, true);
    showResultLoading();

    try {
      const res = await fetch("/api/scan/webcam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl }),
      });
      const data = await res.json();
      if (data.success) {
        renderResult(data.scan);
      } else {
        showResultError(data.error || "No QR code detected in frame. Try again.");
      }
    } catch (err) {
      showResultError("Network error while analyzing the frame.");
    } finally {
      setButtonLoading(captureBtn, false);
    }
  });

  // ---------- Result rendering ----------
  const resultEmpty = document.getElementById("resultEmpty");
  const resultContent = document.getElementById("resultContent");

  function setButtonLoading(btn, isLoading) {
    btn.disabled = isLoading;
    btn.textContent = isLoading ? "Analyzing…" : btn.dataset.label || btn.textContent;
    if (!btn.dataset.label) btn.dataset.label = isLoading ? btn.textContent : btn.textContent;
  }

  function showResultLoading() {
    resultEmpty.classList.add("d-none");
    resultContent.classList.remove("d-none");
    resultContent.innerHTML = `
      <div class="text-center py-4">
        <div class="qs-scan-idle-mark">◈</div>
        <p class="qs-text-muted mb-0">Decoding and analyzing…</p>
      </div>`;
  }

  function showResultError(message) {
    resultEmpty.classList.add("d-none");
    resultContent.classList.remove("d-none");
    resultContent.innerHTML = `
      <div class="text-center py-4">
        <div class="qs-result-verdict dangerous">Scan failed</div>
        <p class="qs-text-muted">${escapeHtml(message)}</p>
      </div>`;
  }

  function verdictClass(result) {
    if (result === "Safe") return "safe";
    if (result === "Suspicious") return "suspicious";
    return "dangerous";
  }

  function gaugeColor(result) {
    if (result === "Safe") return "var(--qs-green)";
    if (result === "Suspicious") return "var(--qs-amber)";
    return "var(--qs-red)";
  }

  function renderResult(scan) {
    const cls = verdictClass(scan.scan_result);
    const color = gaugeColor(scan.scan_result);
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (scan.risk_score / 100) * circumference;

    const reasons = (scan.detection_reasons || [])
      .map((r) => `<li>${escapeHtml(r)}</li>`)
      .join("");

    resultContent.innerHTML = `
      <div class="text-center">
        <div class="qs-gauge-wrap">
          <svg width="140" height="140" viewBox="0 0 140 140">
            <circle cx="70" cy="70" r="54" fill="none" stroke="var(--qs-panel-border)" stroke-width="10"/>
            <circle cx="70" cy="70" r="54" fill="none" stroke="${color}" stroke-width="10"
              stroke-linecap="round" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
              transform="rotate(-90 70 70)" style="transition: stroke-dashoffset .6s ease;"/>
          </svg>
          <div class="qs-gauge-value">
            <span class="num">${scan.risk_score}</span>
            <span class="lbl">RISK SCORE</span>
          </div>
        </div>
        <div class="qs-result-verdict ${cls}">${escapeHtml(scan.scan_result)}</div>
      </div>
      <div class="qs-result-content-box">
        <div class="qs-text-muted mb-1" style="font-size:.72rem;">DECODED CONTENT (${escapeHtml(scan.qr_type)})</div>
        ${escapeHtml(scan.decoded_content)}
      </div>
      ${reasons ? `<ul class="qs-reason-list">${reasons}</ul>` : ""}
      <div class="text-center mt-3">
        <a href="/history" class="btn btn-qs-outline btn-sm">View in history →</a>
      </div>
    `;
    resultEmpty.classList.add("d-none");
    resultContent.classList.remove("d-none");
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
  }
})();
