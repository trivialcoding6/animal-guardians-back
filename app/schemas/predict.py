from pydantic import BaseModel

class ImagePredictionRequest(BaseModel):
    image_url: str

class PredictionResult(BaseModel):
    tag_name: str
    probability: float