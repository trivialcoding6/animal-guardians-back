import torch
import torch.nn as nn
from torchvision import models

class EnsembleModel(nn.Module):
    """
    앙상블을 위한 기본 모델 클래스
    Args:
        models (list): 앙상블에 사용할 모델 리스트
    """
    def __init__(self, models):
        super().__init__()
        self.models = nn.ModuleList(models)
        
    def forward(self, x):
        # 각 모델의 예측을 모두 구해서 평균냅니다.
        outputs = [model(x) for model in self.models]
        return torch.mean(torch.stack(outputs), dim=0)
