document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const uploadContainer = document.getElementById('upload-container');
    const optionsContainer = document.getElementById('options-container');
    const progressContainer = document.getElementById('progress-container');
    const resultContainer = document.getElementById('result-container');
    const convertBtn = document.getElementById('convert-btn');
    const newConversionBtn = document.getElementById('new-conversion');
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('status-text');
    const downloadLink = document.getElementById('download-link');
    
    let selectedFile = null;
    
    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            showOptions();
        }
    });
    
    // Drag and drop functionality
    uploadContainer.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#198754';
        this.style.backgroundColor = '#e9f0ff';
    });
    
    uploadContainer.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#0d6efd';
        this.style.backgroundColor = '';
    });
    
    uploadContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#0d6efd';
        this.style.backgroundColor = '';
        
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            fileInput.files = e.dataTransfer.files;
            showOptions();
        }
    });
    
    // Convert button click
    convertBtn.addEventListener('click', function() {
        if (!selectedFile) return;
        
        showProgress();
        convertFile(selectedFile);
    });
    
    // New conversion button
    newConversionBtn.addEventListener('click', function() {
        resetUI();
    });
    
    function showOptions() {
        uploadContainer.classList.add('d-none');
        optionsContainer.classList.remove('d-none');
    }
    
    function showProgress() {
        optionsContainer.classList.add('d-none');
        progressContainer.classList.remove('d-none');
        
        // Simulate progress updates
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 90) clearInterval(interval);
            progressBar.style.width = `${Math.min(progress, 90)}%`;
        }, 300);
    }
    
    function showResult(downloadUrl) {
        progressContainer.classList.add('d-none');
        resultContainer.classList.remove('d-none');
        downloadLink.href = downloadUrl;
        downloadLink.download = selectedFile.name.replace(/\.[^/.]+$/, '') + '.pdf';
    }
    
    function resetUI() {
        selectedFile = null;
        fileInput.value = '';
        resultContainer.classList.add('d-none');
        optionsContainer.classList.add('d-none');
        uploadContainer.classList.remove('d-none');
        progressBar.style.width = '0%';
    }
    
    async function convertFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add conversion options
        formData.append('pageSize', document.getElementById('page-size').value);
        formData.append('orientation', document.getElementById('orientation').value);
        formData.append('preserveFormatting', document.getElementById('preserve-formatting').checked);
        formData.append('optimizePDF', document.getElementById('optimize-pdf').checked);
        
        try {
            // Simulate API call with timeout
            setTimeout(() => {
                progressBar.style.width = '100%';
                statusText.textContent = 'Finalizing PDF...';
                
                // In a real app, you would use the actual API response
                setTimeout(() => {
                    // This would be the actual download URL from your backend
                    const mockDownloadUrl = URL.createObjectURL(new Blob(['Mock PDF content'], { type: 'application/pdf' }));
                    showResult(mockDownloadUrl);
                }, 1000);
            }, 2000);
            
            // Actual API call would look like this:
            /*
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Conversion failed');
            
            const result = await response.json();
            showResult(result.downloadUrl);
            */
            
        } catch (error) {
            console.error('Conversion error:', error);
            progressContainer.classList.add('d-none');
            optionsContainer.classList.remove('d-none');
            alert('Conversion failed: ' + error.message);
        }
    }
});