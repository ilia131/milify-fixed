import os
import sys
from waitress import serve
from backend.wsgi import application

# اضافه کردن مسیر پروژه به سیستم
sys.path.append(os.getcwd())

if __name__ == '__main__':
    print("Starting Waitress server on http://localhost:8000")
    serve(application, host='0.0.0.0', port=8000, threads=4)
