const API_URL = 'http://127.0.0.1:8000/api/v1/photo/process'; // Using absolute URL for direct local testing. In Docker with Nginx, change to '/api/v1/photo/process'
const PDF_API_URL = 'http://127.0.0.1:8000/api/v1/photo/generate-pdf';

async function generatePassportLayout(file, copies, removeBg, enhance, pageSize, orientation) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('copies', copies);
    // Convert boolean to string 'true' / 'false' so FastAPI Form handles it properly if needed
    formData.append('remove_bg', removeBg ? 'true' : 'false'); 
    formData.append('enhance', enhance ? 'true' : 'false');
    formData.append('page_size', pageSize);
    formData.append('orientation', orientation);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to process image');
        }

        const blob = await response.blob();
        return blob;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function generatePdfLayout(file, copies, removeBg, enhance, pageSize, orientation) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('copies', copies);
    formData.append('remove_bg', removeBg ? 'true' : 'false');
    formData.append('enhance', enhance ? 'true' : 'false');
    formData.append('page_size', pageSize);
    formData.append('orientation', orientation);

    try {
        const response = await fetch(PDF_API_URL, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to generate PDF');
        }

        const data = await response.arrayBuffer();
        return new Blob([data], { type: 'application/pdf' });
    } catch (error) {
        console.error('PDF API Error:', error);
        throw error;
    }
}

