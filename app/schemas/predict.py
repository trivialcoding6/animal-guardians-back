from pydantic import BaseModel

class ImagePredictionRequest(BaseModel):
    image_url: str
    pet_type: str

class PredictionResult(BaseModel):
    tag_name: str
    probability: float