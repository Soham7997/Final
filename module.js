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
    // derive module name from existing heading (right side of '—')
    const parts = greetEl.textContent.split('—');
    const moduleName = (parts[1] || parts[0] || '').trim();
    // friendly, module-specific greeting
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

  // Add table for detections
  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.marginTop = '10px';
  table.style.borderCollapse = 'collapse';
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['Label', 'Confidence', 'Timestamp'].forEach(text => {
    const th = document.createElement('th');
    th.textContent = text;
    th.style.border = '1px solid #ddd';
    th.style.padding = '8px';
    th.style.backgroundColor = '#f2f2f2';
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  preview.parentNode.insertBefore(table, preview.nextSibling);

  let detectionInterval;

  function updateDetections() {
    fetch('/get_detections')
      .then(response => response.json())
      .then(data => {
        tbody.innerHTML = '';
        data.forEach(det => {
          const row = document.createElement('tr');
          if (det.label.toLowerCase() === 'child') {
            row.style.backgroundColor = '#ffeb3b'; // Highlight child
          }
          ['label', 'confidence', 'timestamp'].forEach(key => {
            const td = document.createElement('td');
            if (key === 'confidence') {
              td.textContent = det[key].toFixed(2);
            } else if (key === 'timestamp') {
              td.textContent = new Date(det[key] * 1000).toLocaleTimeString();
            } else {
              td.textContent = det[key];
            }
            td.style.border = '1px solid #ddd';
            td.style.padding = '8px';
            row.appendChild(td);
          });
          tbody.appendChild(row);
        });
      });
  }

  let currentSource = null; // 'camera' | 'file'
  let stream = null;
  let uploadedFilePath = null;

  function clearPreview(){
    preview.innerHTML = '';
    if(stream){
      stream.getTracks().forEach(t=>t.stop());
      stream = null;
    }
    if(detectionInterval){
      clearInterval(detectionInterval);
      detectionInterval = null;
    }
  }

  realtimeBtn && realtimeBtn.addEventListener('click', async ()=>{
    try{
      clearPreview();
      const img = document.createElement('img');
      img.src = '/video_feed?mode=raw';
      img.style.maxWidth = '100%';
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
    // Upload the file
    const formData = new FormData();
    formData.append('file', f);
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      if (result.file_path) {
        uploadedFilePath = result.file_path;
        // choose element by mime
        if(f.type.startsWith('image/')){
          const img = document.createElement('img'); img.src = URL.createObjectURL(f); img.style.maxWidth='100%'; preview.appendChild(img);
        } else {
          const video = document.createElement('video'); video.controls = true; video.src = URL.createObjectURL(f); video.style.maxWidth='100%'; preview.appendChild(video);
        }
        currentSource = 'file';
      } else {
        alert('Upload failed: ' + result.error);
      }
    } catch (error) {
      alert('Upload error: ' + error.message);
    }
  });

  runBtn && runBtn.addEventListener('click', async ()=>{
    if(currentSource === 'camera'){
      // Switch to processed stream with detection
      clearPreview();
      const img = document.createElement('img');
      img.src = '/video_feed?mode=processed';
      img.style.maxWidth = '100%';
      preview.appendChild(img);
      currentSource = 'processed_camera';
      alert('Detection started on live camera feed!');
      // Start updating detections
      detectionInterval = setInterval(updateDetections, 1000);
    } else if(currentSource === 'file'){
      // Run detection on file - stream processed video
      if (!uploadedFilePath) {
        alert('No file uploaded.');
        return;
      }
      clearPreview();
      const img = document.createElement('img');
      img.src = `/video_file_feed?file_path=${encodeURIComponent(uploadedFilePath)}`;
      img.style.maxWidth = '100%';
      preview.appendChild(img);
      currentSource = 'processed_file';
      // Start updating detections
      detectionInterval = setInterval(updateDetections, 1000);
    } else {
      alert('Select Real-time or Local file first.');
    }
  });

});
