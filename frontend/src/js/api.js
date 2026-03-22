const API_URL = '/api/v1/photo/process';
const PDF_API_URL = '/api/v1/photo/generate-pdf';

/**
 * Parse an error response from the backend.
 * Handles both JSON {"detail": "..."} bodies and plain-text fallbacks.
 */
async function _parseErrorResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
        try {
            const json = await response.json();
            return json.detail || json.error || JSON.stringify(json);
        } catch (_) { /* fall through */ }
    }
    const text = await response.text();
    return text || `Server error ${response.status}`;
}

async function generatePassportLayout(file, copies, removeBg, enhance, pageSize, orientation) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('copies', copies);
    formData.append('remove_bg', removeBg ? 'true' : 'false');
    formData.append('enhance', enhance ? 'true' : 'false');
    formData.append('page_size', pageSize);
    formData.append('orientation', orientation);

    try {
        const response = await fetch(API_URL, { method: 'POST', body: formData });
        if (!response.ok) {
            const msg = await _parseErrorResponse(response);
            throw new Error(msg);
        }
        return await response.blob();
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
        const response = await fetch(PDF_API_URL, { method: 'POST', body: formData });
        if (!response.ok) {
            const msg = await _parseErrorResponse(response);
            throw new Error(msg);
        }
        const data = await response.arrayBuffer();
        return new Blob([data], { type: 'application/pdf' });
    } catch (error) {
        console.error('PDF API Error:', error);
        throw error;
    }
}
