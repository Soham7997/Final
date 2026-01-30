// module.js — shared logic for module pages (camera preview, local file select, run placeholder)

document.addEventListener('DOMContentLoaded', ()=>{

  const backBtn = document.getElementById('backBtn');
  backBtn && backBtn.addEventListener('click', ()=>{ window.location.href = 'dashboard.html'; });

  // show user greeting from session
  const greetEl = document.getElementById('greet');
  const headerUser = document.getElementById('headerUser');
  const name = sessionStorage.getItem('dt_name') || '';
  const email = sessionStorage.getItem('dt_email') || 'user@example.com';
  const display = name || email;

  if(greetEl){
    const parts = greetEl.textContent.split('—');
    const moduleName = (parts[1] || parts[0] || '').trim();
    greetEl.textContent = `Welcome, ${display} — You opened ${moduleName} controls.`;
  }
  if(headerUser){
    const initials = (name || email).split(' ').map(s=>s[0]||'').slice(0,2).join('').toUpperCase();
    headerUser.textContent = initials;
  }

  const realtimeBtn = document.getElementById('realtimeBtn');
  const localBtn = document.getElementById('localBtn');
  const fileInput = document.getElementById('fileInput');
  const preview = document.getElementById('preview');
  const runBtn = document.getElementById('runBtn');

  // ------------------------------
  // Detections Table (Upgraded)
  // ------------------------------
  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.marginTop = '10px';
  table.style.borderCollapse = 'collapse';

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');

  // Added: ID + Crop + Posture + Motion + Scale Hint
  const cols = ['ID', 'Label', 'Confidence', 'Timestamp', 'Posture', 'Motion', 'Scale→Child', 'Crop'];
  cols.forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    th.style.border = '1px solid #ddd';
    th.style.padding = '8px';
    th.style.backgroundColor = '#f2f2f2';
    th.style.fontSize = '13px';
    headerRow.appendChild(th);
  });

  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  table.appendChild(tbody);

  preview.parentNode.insertBefore(table, preview.nextSibling);

  let detectionInterval;

  // ------------------------------
  // Helpers
  // ------------------------------
  function safeFixed(x, d=2){
    if (x === null || x === undefined || Number.isNaN(x)) return 'NA';
    const n = Number(x);
    if (Number.isNaN(n)) return 'NA';
    return n.toFixed(d);
  }

  function formatTimestamp(ts){
    // Supports:
    // - old: epoch seconds (number)
    // - new: ISO string
    if (ts === null || ts === undefined) return 'NA';
    if (typeof ts === 'number') {
      return new Date(ts * 1000).toLocaleString();
    }
    // string
    const d = new Date(ts);
    if (!isNaN(d.getTime())) return d.toLocaleString();
    return String(ts);
  }

  function normalizeDet(det){
    // Compatible with old server and new server
    const label = (det.label || det.class || '').toString();
    const human_id = det.human_id || det.id || '';
    const confidence = det.confidence;
    const timestamp = det.timestamp;
    const posture = det.posture_hint || '';
    const motion = det.motion_score;
    const scaleHint = det.child_by_scale_hint;

    // crop url (new server returns crop_url)
    const cropUrl = det.crop_url || det.crop_path || '';

    return { label, human_id, confidence, timestamp, posture, motion, scaleHint, cropUrl };
  }

  function clearTable(){
    tbody.innerHTML = '';
  }

  function updateDetections() {
    fetch('/get_detections')
      .then(response => response.json())
      .then(data => {
        clearTable();

        // Newest first (so table shows latest at top)
        const items = Array.isArray(data) ? [...data].reverse() : [];

        items.forEach(det0 => {
          const det = normalizeDet(det0);

          const row = document.createElement('tr');
          if ((det.label || '').toLowerCase() === 'child' || (det.human_id || '').toLowerCase().startsWith('child')) {
            row.style.backgroundColor = '#ffeb3b'; // Highlight child
          }

          // ID
          const tdId = document.createElement('td');
          tdId.textContent = det.human_id || 'NA';
          tdId.style.border = '1px solid #ddd';
          tdId.style.padding = '8px';
          tdId.style.fontWeight = '600';
          row.appendChild(tdId);

          // Label
          const tdLabel = document.createElement('td');
          tdLabel.textContent = det.label || 'NA';
          tdLabel.style.border = '1px solid #ddd';
          tdLabel.style.padding = '8px';
          row.appendChild(tdLabel);

          // Confidence
          const tdConf = document.createElement('td');
          tdConf.textContent = safeFixed(det.confidence, 2);
          tdConf.style.border = '1px solid #ddd';
          tdConf.style.padding = '8px';
          row.appendChild(tdConf);

          // Timestamp
          const tdTs = document.createElement('td');
          tdTs.textContent = formatTimestamp(det.timestamp);
          tdTs.style.border = '1px solid #ddd';
          tdTs.style.padding = '8px';
          row.appendChild(tdTs);

          // Posture
          const tdPost = document.createElement('td');
          tdPost.textContent = det.posture || 'NA';
          tdPost.style.border = '1px solid #ddd';
          tdPost.style.padding = '8px';
          row.appendChild(tdPost);

          // Motion
          const tdMotion = document.createElement('td');
          tdMotion.textContent = safeFixed(det.motion, 2);
          tdMotion.style.border = '1px solid #ddd';
          tdMotion.style.padding = '8px';
          row.appendChild(tdMotion);

          // Scale hint
          const tdScale = document.createElement('td');
          tdScale.textContent = det.scaleHint ? 'Yes' : 'No';
          tdScale.style.border = '1px solid #ddd';
          tdScale.style.padding = '8px';
          row.appendChild(tdScale);

          // Crop thumbnail
          const tdCrop = document.createElement('td');
          tdCrop.style.border = '1px solid #ddd';
          tdCrop.style.padding = '8px';
          tdCrop.style.textAlign = 'center';

          if (det.cropUrl) {
            const img = document.createElement('img');
            img.src = det.cropUrl;
            img.alt = det.human_id || det.label || 'crop';
            img.style.width = '84px';
            img.style.height = 'auto';
            img.style.borderRadius = '8px';
            img.style.display = 'block';
            img.style.margin = '0 auto';
            img.loading = 'lazy';
            tdCrop.appendChild(img);
          } else {
            tdCrop.textContent = '—';
          }

          row.appendChild(tdCrop);

          tbody.appendChild(row);
        });
      })
      .catch(()=>{ /* ignore transient errors */ });
  }

  // ------------------------------
  // Preview / Controls (same flow)
  // ------------------------------
  let currentSource = null; // 'camera' | 'file' | 'processed_camera' | 'processed_file'
  let uploadedFilePath = null;

  function clearPreview(){
    preview.innerHTML = '';
    if(detectionInterval){
      clearInterval(detectionInterval);
      detectionInterval = null;
    }
  }

  realtimeBtn && realtimeBtn.addEventListener('click', async ()=>{
    try{
      clearPreview();
      // raw stream
      const img = document.createElement('img');
      img.src = '/video_feed?mode=raw';
      img.style.maxWidth = '100%';
      img.style.borderRadius = '12px';
      preview.appendChild(img);

      currentSource = 'camera';
    }catch(e){
      alert('Unable to start camera stream: ' + (e.message || e));
    }
  });

  localBtn && localBtn.addEventListener('click', ()=>{
    fileInput && fileInput.click();
  });

  fileInput && fileInput.addEventListener('change', async (ev)=>{
    const f = ev.target.files && ev.target.files[0];
    if(!f) return;

    clearPreview();

    // Upload the file (server expects /upload -> {file_path})
    const formData = new FormData();
    formData.append('file', f);

    try {
      const response = await fetch('/upload', { method: 'POST', body: formData });
      const result = await response.json();

      if (result.file_path) {
        uploadedFilePath = result.file_path;

        // local preview (client-side)
        if(f.type.startsWith('image/')){
          const img = document.createElement('img');
          img.src = URL.createObjectURL(f);
          img.style.maxWidth = '100%';
          img.style.borderRadius = '12px';
          preview.appendChild(img);
        } else {
          const video = document.createElement('video');
          video.controls = true;
          video.src = URL.createObjectURL(f);
          video.style.maxWidth = '100%';
          video.style.borderRadius = '12px';
          preview.appendChild(video);
        }

        currentSource = 'file';
      } else {
        alert('Upload failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      alert('Upload error: ' + (error.message || error));
    }
  });

  runBtn && runBtn.addEventListener('click', async ()=>{
    if(currentSource === 'camera'){
      clearPreview();

      // processed stream
      const img = document.createElement('img');
      img.src = '/video_feed?mode=processed';
      img.style.maxWidth = '100%';
      img.style.borderRadius = '12px';
      preview.appendChild(img);

      currentSource = 'processed_camera';

      // Start updating detections
      updateDetections();
      detectionInterval = setInterval(updateDetections, 800);

      alert('Detection started on live camera feed!');
    }
    else if(currentSource === 'file'){
      if (!uploadedFilePath) {
        alert('No file uploaded.');
        return;
      }

      clearPreview();

      // server-side processed stream
      const img = document.createElement('img');
      img.src = `/video_file_feed?file_path=${encodeURIComponent(uploadedFilePath)}`;
      img.style.maxWidth = '100%';
      img.style.borderRadius = '12px';
      preview.appendChild(img);

      currentSource = 'processed_file';

      updateDetections();
      detectionInterval = setInterval(updateDetections, 800);
    }
    else {
      alert('Select Real-time or Local file first.');
    }
  });

});