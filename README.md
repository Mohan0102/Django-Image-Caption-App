# Image Caption Generator (Django REST Framework + HTML/JS)

## 1. Add your model
Copy `model.h5` into `backend/captioner/ml/` (`tokenizer.pkl` is already there).

## 2. Run the backend
```bash
cd backend
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```
Test: http://127.0.0.1:8000/api/health/ -> {"status":"ok"}

First caption request is slow: VGG16 ImageNet weights (~500 MB) download once.

## 3. Run the frontend
```bash
cd frontend
python -m http.server 5500
```
Open http://127.0.0.1:5500 (or just double-click index.html).

## API
`POST /api/caption/` multipart field `image` -> `{"caption": "..."}`
```bash
curl -F image=@photo.jpg http://127.0.0.1:8000/api/caption/
```

## Notes
- Use a TensorFlow version close to Kaggle's one used for training (check `tf.__version__` there), otherwise `model.h5` may fail to load.
- `max_length` is read from the model, so nothing to configure.
