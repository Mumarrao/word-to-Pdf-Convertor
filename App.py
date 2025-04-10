from flask import Flask, request, jsonify, send_file
import os
import uuid
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/convert', methods=['POST'])
def convert_file():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Validate file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
    file.save(input_path)
    
    # Get conversion options
    page_size = request.form.get('pageSize', 'A4')
    orientation = request.form.get('orientation', 'Portrait')
    preserve_formatting = request.form.get('preserveFormatting', 'true') == 'true'
    optimize_pdf = request.form.get('optimizePDF', 'true') == 'true'
    
    # Generate output path
    output_filename = os.path.splitext(filename)[0] + '.pdf'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{unique_id}_{output_filename}")
    
    try:
        # Call the C# conversion tool (implementation shown in next section)
        conversion_result = convert_with_csharp(
            input_path, 
            output_path,
            page_size=page_size,
            orientation=orientation,
            preserve_formatting=preserve_formatting,
            optimize_pdf=optimize_pdf
        )
        
        if not conversion_result['success']:
            return jsonify({'error': conversion_result['message']}), 500
        
        # Return download URL
        download_url = f"/api/download/{unique_id}_{output_filename}"
        return jsonify({
            'success': True,
            'downloadUrl': download_url,
            'filename': output_filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up - remove files after processing
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except:
            pass

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename.split('_', 1)[1]
        )
    finally:
        # Clean up - remove the file after download
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

def convert_with_csharp(input_path, output_path, **options):
    """
    Helper function to call the C# conversion executable with parameters
    """
    try:
        # Path to the C# converter executable (built from the C# project)
        converter_path = os.path.join('WordToPdfConverter', 'WordToPdfConverter.exe')
        
        # Build command arguments
        args = [
            converter_path,
            '--input', input_path,
            '--output', output_path,
            '--page-size', options.get('page_size', 'A4'),
            '--orientation', options.get('orientation', 'Portrait')
        ]
        
        if options.get('preserve_formatting', True):
            args.append('--preserve-formatting')
        
        if options.get('optimize_pdf', True):
            args.append('--optimize')
        
        # Execute the converter
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True
        )
        
        if not os.path.exists(output_path):
            return {
                'success': False,
                'message': 'Conversion failed - no output file created'
            }
        
        return {'success': True}
    
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'message': f'Conversion failed: {e.stderr}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

if __name__ == '__main__':
    app.run(debug=True)