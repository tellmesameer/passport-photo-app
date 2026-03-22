document.addEventListener('DOMContentLoaded', () => {
    // Advanced options toggle
    const advToggle = document.getElementById('advanced-toggle');
    const advContent = document.getElementById('advanced-content');
    if (advToggle && advContent) {
        advToggle.addEventListener('click', () => {
            const isExpanded = advToggle.getAttribute('aria-expanded') === 'true';
            advToggle.setAttribute('aria-expanded', !isExpanded);
            advContent.classList.toggle('open');
        });
    }

    // Elements
    const uploadZone = document.getElementById('upload-zone');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('i');

    // Theme logic
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.className = 'fa-solid fa-sun';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        themeIcon.className = 'fa-solid fa-moon';
    }

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeIcon.className = 'fa-solid fa-moon';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeIcon.className = 'fa-solid fa-sun';
        }
    });

    const imageInput = document.getElementById('image-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const generateBtn = document.getElementById('generate-btn');
    const uploadForm = document.getElementById('upload-form');
    const copiesInput = document.getElementById('copies');
    const pageSizeSelect = document.getElementById('page-size');
    const orientationSelect = document.getElementById('orientation');
    
    const previewContainer = document.getElementById('preview-container');
    const emptyState = document.getElementById('empty-state');
    const loadingOverlay = document.getElementById('loading-overlay');
    const livePreviewGrid = document.getElementById('live-preview-grid');
    const finalLayoutImage = document.getElementById('final-layout-image');
    const actionsPanel = document.getElementById('actions-panel');
    
    const downloadBtn = document.getElementById('download-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    
    let currentFile = null;
    let uploadedBlobUrl = null;
    let finalBlobUrl = null;
    let errorDismissTimer = null;

    // --- Error banner helpers ---
    function showError(message) {
        clearError();
        let banner = document.getElementById('error-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'error-banner';
            banner.style.cssText = [
                'display:flex', 'align-items:flex-start', 'gap:10px',
                'background:#fff0f0', 'border:1.5px solid #e74c3c',
                'color:#c0392b', 'border-radius:10px', 'padding:14px 16px',
                'margin-bottom:16px', 'font-size:0.93rem', 'line-height:1.5',
                'animation:fadeIn .2s ease', 'box-shadow:0 2px 8px rgba(231,76,60,.15)'
            ].join(';');

            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-circle-exclamation';
            icon.style.cssText = 'margin-top:2px;flex-shrink:0;font-size:1.1rem;';

            const text = document.createElement('span');
            text.id = 'error-banner-text';

            const close = document.createElement('button');
            close.innerHTML = '&times;';
            close.style.cssText = [
                'margin-left:auto', 'background:none', 'border:none',
                'color:inherit', 'font-size:1.3rem', 'cursor:pointer',
                'line-height:1', 'padding:0', 'flex-shrink:0'
            ].join(';');
            close.addEventListener('click', clearError);

            banner.appendChild(icon);
            banner.appendChild(text);
            banner.appendChild(close);
            previewContainer.insertBefore(banner, previewContainer.firstChild);
        }
        document.getElementById('error-banner-text').textContent = message;
        banner.style.display = 'flex';
        // Auto-dismiss after 8 s
        errorDismissTimer = setTimeout(clearError, 10000);
    }

    function clearError() {
        if (errorDismissTimer) { clearTimeout(errorDismissTimer); errorDismissTimer = null; }
        const banner = document.getElementById('error-banner');
        if (banner) banner.style.display = 'none';
    }


    // --- Live Render logic ---
    function renderLivePreview() {
        if (!uploadedBlobUrl) return;
        
        livePreviewGrid.innerHTML = '';
        let copies = parseInt(copiesInput.value, 10);
        if (isNaN(copies) || copies < 1) copies = 1;
        if (copies > 50) copies = 50;
        
        for (let i = 0; i < copies; i++) {
            const img = document.createElement('img');
            img.src = uploadedBlobUrl;
            livePreviewGrid.appendChild(img);
        }
        
        livePreviewGrid.classList.remove('hidden');
        finalLayoutImage.classList.add('hidden');
        emptyState.classList.add('hidden');
        actionsPanel.classList.add('hidden');
    }

    // Re-render when copies change but not if showing final layout
    copiesInput.addEventListener('input', () => {
        if (uploadedBlobUrl && finalLayoutImage.classList.contains('hidden')) {
            renderLivePreview();
        }
    });

    // --- Upload Handlers ---
    uploadZone.addEventListener('click', () => {
        imageInput.click();
    });

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.type.match('image.*')) {
            alert('Please select an image file (JPEG/PNG)');
            return;
        }
        
        currentFile = file;
        fileName.textContent = file.name;
        
        // Update UI
        uploadZone.classList.add('hidden');
        fileInfo.classList.remove('hidden');
        generateBtn.disabled = false;
        
        // Show immediate live grid preview of selected image
        if (uploadedBlobUrl) URL.revokeObjectURL(uploadedBlobUrl);
        uploadedBlobUrl = URL.createObjectURL(file);
        
        if (finalBlobUrl) {
            URL.revokeObjectURL(finalBlobUrl);
            finalBlobUrl = null;
        }
        
        renderLivePreview();
    }

    removeFileBtn.addEventListener('click', () => {
        currentFile = null;
        imageInput.value = '';
        
        if (uploadedBlobUrl) {
            URL.revokeObjectURL(uploadedBlobUrl);
            uploadedBlobUrl = null;
        }
        if (finalBlobUrl) {
            URL.revokeObjectURL(finalBlobUrl);
            finalBlobUrl = null;
        }
        
        uploadZone.classList.remove('hidden');
        fileInfo.classList.add('hidden');
        generateBtn.disabled = true;
        
        livePreviewGrid.innerHTML = '';
        livePreviewGrid.classList.add('hidden');
        finalLayoutImage.src = '';
        finalLayoutImage.classList.add('hidden');
        emptyState.classList.remove('hidden');
        actionsPanel.classList.add('hidden');
    });

    // --- Form Submission ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!currentFile) return;

        const copies = parseInt(copiesInput.value, 10);
        const removeBg = document.getElementById('remove-bg').checked;
        const enhance = document.getElementById('enhance').checked;
        const pageSize = pageSizeSelect.value;
        const orientation = orientationSelect.value;

        if (isNaN(copies) || copies < 1 || copies > 50) {
            alert('Please enter a valid number of copies (1-50).');
            return;
        }

        // UI Loading State
        generateBtn.disabled = true;
        emptyState.classList.add('hidden');
        livePreviewGrid.classList.add('hidden');
        finalLayoutImage.classList.add('hidden');
        loadingOverlay.classList.remove('hidden');
        actionsPanel.classList.add('hidden');

        try {
            clearError();
            const blob = await generatePassportLayout(currentFile, copies, removeBg, enhance, pageSize, orientation);
            
            if (finalBlobUrl) URL.revokeObjectURL(finalBlobUrl);
            finalBlobUrl = URL.createObjectURL(blob);
            
            finalLayoutImage.src = finalBlobUrl;
            finalLayoutImage.classList.remove('hidden');
            actionsPanel.classList.remove('hidden');
        } catch (error) {
            showError(error.message);
            // Re-show live grid on error
            livePreviewGrid.classList.remove('hidden');
        } finally {
            loadingOverlay.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    // --- Helpers ---
    function getTimestamp() {
        const now = new Date();
        const dd = String(now.getDate()).padStart(2, '0');
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const yy = String(now.getFullYear()).slice(-2);
        const hh = String(now.getHours()).padStart(2, '0');
        const mi = String(now.getMinutes()).padStart(2, '0');
        const ss = String(now.getSeconds()).padStart(2, '0');
        return `${dd}${mm}${yy}_${hh}${mi}${ss}`;
    }

    // --- Actions ---
    downloadBtn.addEventListener('click', () => {
        if (!finalBlobUrl) return;
        const a = document.createElement('a');
        a.href = finalBlobUrl;
        a.download = `passport_layout_${getTimestamp()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    downloadPdfBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const copies = parseInt(copiesInput.value, 10);
        const removeBg = document.getElementById('remove-bg').checked;
        const enhance = document.getElementById('enhance').checked;
        const pageSize = pageSizeSelect.value;
        const orientation = orientationSelect.value;

        // Show loading state
        downloadPdfBtn.disabled = true;
        const originalText = downloadPdfBtn.innerHTML;
        downloadPdfBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';

        try {
            const blob = await generatePdfLayout(currentFile, copies, removeBg, enhance, pageSize, orientation);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `passport_photos_${getTimestamp()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
            showError(error.message);
        } finally {
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.innerHTML = originalText;
        }
    });
});
