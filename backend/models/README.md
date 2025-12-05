# AI Models Directory

Place your trained AI models in this directory:

## NLP Model (Text Symptom Analysis)
- `nlp_model.h5` or `nlp_model.pth`
- TensorFlow SavedModel format: `nlp_model/`
- Hugging Face model: Place tokenizer and model files here

## Computer Vision Model (Image Analysis)
- `cv_model.h5` or `cv_model.pth`
- TensorFlow SavedModel format: `cv_model/`
- ONNX format: `cv_model.onnx`

## Vector Embeddings (For Similar Case Search)
- FAISS index: `embeddings.index`
- Case ID mapping: `case_ids.json`

## Model Integration Guide

### TensorFlow/Keras
```python
from tensorflow import keras
model = keras.models.load_model('models/cv_model.h5')
```

### PyTorch
```python
import torch
model = torch.load('models/cv_model.pth')
model.eval()
```

### Hugging Face Transformers
```python
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained('models/nlp_model')
model = AutoModel.from_pretrained('models/nlp_model')
```

## Current Status
Currently using **mock models** for development. See `app/services/ai_inference.py` for integration points.
