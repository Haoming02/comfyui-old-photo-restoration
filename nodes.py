from .lib_bopb2l.Global.test import global_test
from .lib_bopb2l.Global.detection import global_detection

from .lib_bopb2l.Face_Detection.detect_all_dlib import detect
from .lib_bopb2l.Face_Detection.detect_all_dlib_HR import detect_hr
from .lib_bopb2l.Face_Detection.align_warp_back_multiple_dlib import align_warp
from .lib_bopb2l.Face_Detection.align_warp_back_multiple_dlib_HR import align_warp_hr

from .lib_bopb2l.Face_Enhancement.test_face import test_face

from .utils import (
    FACE_ENHANCEMENT_CHECKPOINTS,
    GLOBAL_CHECKPOINTS_FOLDER,
    FACE_CHECKPOINTS_FOLDER,
    tensor2image,
    image2tensor,
)

from PIL.Image import Image
from torch import Tensor


class Stage1:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "gpu_id": (
                    "STRING",
                    {
                        "default": "0",
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "test"
    CATEGORY = "old-photo"

    def test(self, image: Tensor, gpu_id: str):
        input_image: Image = tensor2image(image)

        args = [
            "--test_mode",
            "Full",
            "--Quality_restore",
            "--gpu_ids",
            gpu_id,
        ]

        output: Image = global_test(GLOBAL_CHECKPOINTS_FOLDER, args, input_image)
        return (image2tensor(output),)


class Stage1S:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "hr": ("BOOLEAN", {"default": False}),
                "gpu_id": (
                    "STRING",
                    {
                        "default": "0",
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "test"
    CATEGORY = "old-photo"

    def test(self, image: Tensor, hr: bool, gpu_id: str):
        input_image: Image = tensor2image(image)

        mask, transformed_image = global_detection(
            input_image, int(gpu_id), "full_size"
        )

        args = [
            "--Scratch_and_Quality_restore",
            "--gpu_ids",
            gpu_id,
        ]

        if hr:
            args.append("--HR")

        output: Image = global_test(
            GLOBAL_CHECKPOINTS_FOLDER,
            args,
            transformed_image.convert("RGB"),
            mask.convert("RGB"),
        )

        return (image2tensor(output),)


class Stage2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "hr": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("FACES",)
    FUNCTION = "detect"
    CATEGORY = "old-photo"

    def detect(self, image: Tensor, hr: bool):
        input_image: Image = tensor2image(image)

        if hr:
            faces: list[Image] = detect_hr(input_image)
        else:
            faces: list[Image] = detect(input_image)

        print(f"Detected {len(faces)} Faces...")
        return (faces,)


class Stage3:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "faces": ("FACES",),
                "hr": ("BOOLEAN", {"default": False}),
                "gpu_id": (
                    "STRING",
                    {
                        "default": "0",
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("FACES",)
    FUNCTION = "detect"
    CATEGORY = "old-photo"

    def detect(self, faces: list[Image], hr: bool, gpu_id: str):
        if hr:
            args = {
                "checkpoints_dir": FACE_CHECKPOINTS_FOLDER,
                "name": FACE_ENHANCEMENT_CHECKPOINTS[1],
                "gpu_ids": gpu_id,
                "load_size": 512,
                "label_nc": 18,
                "no_instance": True,
                "preprocess_mode": "resize",
                "batchSize": 1,
                "no_parsing_map": True,
            }

        else:
            args = {
                "checkpoints_dir": FACE_CHECKPOINTS_FOLDER,
                "name": FACE_ENHANCEMENT_CHECKPOINTS[0],
                "gpu_ids": gpu_id,
                "load_size": 256,
                "label_nc": 18,
                "no_instance": True,
                "preprocess_mode": "resize",
                "batchSize": 4,
                "no_parsing_map": True,
            }

        restored_faces: list[Image] = test_face(faces, args)
        return (restored_faces,)


class Stage4:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "faces": ("FACES",),
                "hr": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "detect"
    CATEGORY = "old-photo"

    def detect(self, image: Tensor, faces: list[Image], hr: bool):
        input_image: Image = tensor2image(image)

        if hr:
            output: Image = align_warp_hr(input_image, faces)
        else:
            output: Image = align_warp(input_image, faces)

        return (image2tensor(output),)


class_mappings: dict = {
    "Stage1": Stage1,
    "Stage1S": Stage1S,
    "Stage2": Stage2,
    "Stage3": Stage3,
    "Stage4": Stage4,
}

display_name_mappings: dict = {
    "Stage1": "Global Restoration",
    "Stage1S": "Global Restoration with Scratch Processing",
    "Stage2": "Face Detection",
    "Stage3": "Face Enhancement",
    "Stage4": "Face Align",
}
