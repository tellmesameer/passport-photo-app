document.addEventListener('DOMContentLoaded', () => {
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
    
    const previewContainer = document.getElementById('preview-container');
    const emptyState = document.getElementById('empty-state');
    const loadingOverlay = document.getElementById('loading-overlay');
    const livePreviewGrid = document.getElementById('live-preview-grid');
    const finalLayoutImage = document.getElementById('final-layout-image');
    const actionsPanel = document.getElementById('actions-panel');
    
    const downloadBtn = document.getElementById('download-btn');
    const printBtn = document.getElementById('print-btn');
    
    let currentFile = null;
    let uploadedBlobUrl = null;
    let finalBlobUrl = null;

    // --- Live Render logic ---
    function renderLivePreview() {
        if (!uploadedBlobUrl) return;
        
        livePreviewGrid.innerHTML = '';
        let copies = parseInt(copiesInput.value, 10);
        if (isNaN(copies) || copies < 1) copies = 1;
        if (copies > 25) copies = 25;
        
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

        if (isNaN(copies) || copies < 1 || copies > 25) {
            alert('Maximum limit is 25 copies for an A4 page. Please enter a valid number.');
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
            const blob = await generatePassportLayout(currentFile, copies, removeBg, enhance);
            
            if (finalBlobUrl) URL.revokeObjectURL(finalBlobUrl);
            finalBlobUrl = URL.createObjectURL(blob);
            
            finalLayoutImage.src = finalBlobUrl;
            finalLayoutImage.classList.remove('hidden');
            actionsPanel.classList.remove('hidden');
        } catch (error) {
            alert(`Error: ${error.message}`);
            // Re-show live grid on error
            livePreviewGrid.classList.remove('hidden');
        } finally {
            loadingOverlay.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    // --- Actions ---
    downloadBtn.addEventListener('click', () => {
        if (!finalBlobUrl) return;
        const a = document.createElement('a');
        a.href = finalBlobUrl;
        a.download = 'passport_layout_A4.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    printBtn.addEventListener('click', () => {
        if (!finalBlobUrl) return;
        window.print();
    });
});
