from pathlib import Path
from PIL import Image
import numpy as np
import torch
import os

ext: str = Path(__file__).parent.resolve()

GLOBAL_CHECKPOINTS_FOLDER = os.path.join(
    ext, "lib_bopb2l", "Global", "checkpoints", "restoration"
)
FACE_CHECKPOINTS_FOLDER = os.path.join(
    ext, "lib_bopb2l", "Face_Enhancement", "checkpoints"
)
DAT = os.path.join(
    ext, "lib_bopb2l", "Face_Detection", "shape_predictor_68_face_landmarks.dat"
)

FACE_ENHANCEMENT_CHECKPOINTS = ("Setting_9_epoch_100", "FaceSR_512")


def check():
    """Verify if the models are present"""

    print("\n### [Old-Photo-Restoration] Verifying Models...")
    flag = False

    if not os.path.isdir(GLOBAL_CHECKPOINTS_FOLDER):
        print("[Warning] global_checkpoints not detected")
        flag = True
    if not os.path.isdir(FACE_CHECKPOINTS_FOLDER):
        print("[Warning] face_checkpoints not detected")
        flag = True
    if not os.path.isfile(DAT):
        print("[Warning] face_landmarks not detected")
        flag = True

    if flag:
        print("Please download from Release!\n")


def tensor2image(x: torch.Tensor) -> Image:
    img = x.squeeze(0).cpu().numpy()
    return Image.fromarray(np.clip(img * 255.0, 0, 255).astype(np.uint8))


def image2tensor(img: Image) -> torch.Tensor:
    output = np.asarray(img).astype(np.float32) / 255.0
    return torch.from_numpy(output).unsqueeze(0)
