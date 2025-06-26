#!/bin/bash
# Install Python dependencies
pip install --upgrade pip
pip install setuptools==68.0.0 wheel gensim==4.3.3
pip install "urllib3<2.1,>=1.25.4"  # Resolve dependency conflict
pip install -r requirements.txt
pip install --force-reinstall gunicorn==22.0.0 django-storages==1.13.2 boto3==1.28.57 botocore==1.31.85

# Setup directories
mkdir -p root_files/static root_files/uploads nltk_data /opt/render/project/src/static /opt/render/project/src/data/geojson

# Process frontend assets
cd /opt/render/project/src
cp -r data/geojson backend/static/
(cd tailwind && npm install && chmod +x node_modules/.bin/tailwindcss && ./node_modules/.bin/tailwindcss -i input.css -o ../backend/static/css/tailwind.css --minify)

# Django setup
chmod -R 755 backend/templates/
export PYTHONPATH=/opt/render/project/src
cd /opt/render/project/src/backend
python manage.py makemigrations
python manage.py migrate
python manage.py create_admin_user
python manage.py collectstatic --noinput --clear