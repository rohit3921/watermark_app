document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const resultDiv = document.getElementById('result');
    
    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        resultDiv.innerHTML = `<a href="${url}" download="watermarked_video.mp4">Download Watermarked Video</a>`;
    } else {
        const error = await response.json();
        resultDiv.textContent = `Error: ${error.error}`;
    }
});
