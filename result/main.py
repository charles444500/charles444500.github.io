from gridfs import GridFS
from flask import Flask, render_template, request, Response
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

# ... (other imports and app setup)

@app.route('/show_result', methods=['POST'])
def show_result():
    matric_number = request.form.get('matric_number')

    # Connect to MongoDB and retrieve result based on matric number
    client = MongoClient('mongodb+srv://charles444500:321205566@cluster0.6i121s7.mongodb.net/?retryWrites=true&w=majority')
    db = client['students']
    collection = db['results']
    result_document = collection.find_one({'matric_number': matric_number})

    if result_document:
        result = result_document['result']

        # Retrieve PDF using GridFS
        fs = GridFS(db, collection='pdf')
        pdf_document = fs.find_one({'matric_number': matric_number})

        if pdf_document:
            pdf_id = pdf_document._id

            def generate():
                pdf_file = fs.get(pdf_id)
                while True:
                    chunk = pdf_file.read(1024)  # Read 1KB chunks
                    if not chunk:
                        break
                    yield chunk

            response = Response(generate(), content_type='application/pdf')
            response.headers['Content-Disposition'] = f'inline; filename={pdf_document.filename}'
            client.close()
            return response
        else:
            client.close()
            return "Your result will be released soon. Keep checking."

    else:
        client.close()
        return "No result found for the provided matric number."

if __name__ == '__main__':
    app.run(debug=True)
