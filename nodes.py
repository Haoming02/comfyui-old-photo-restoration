from .Global.test import global_test
from .Global.detection import global_detection

from .Face_Detection.detect_all_dlib import detect
from .Face_Detection.detect_all_dlib_HR import detect_hr
from .Face_Detection.align_warp_back_multiple_dlib import align_warp
from .Face_Detection.align_warp_back_multiple_dlib_HR import align_warp_hr

from .Face_Enhancement.test_face import test_face

from .utils import (
    FACE_ENHANCEMENT_CHECKPOINTS,
    GLOBAL_CHECKPOINTS_FOLDER,
    FACE_CHECKPOINTS_FOLDER,
    tensor2image,
    image2tensor,
)


class Stage1:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "process_scratch": ("BOOLEAN", {"default": False}),
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

    def test(self, image, process_scratch: bool, hr: bool, gpu_id: str):
        input_image = tensor2image(image)

        if not process_scratch:
            args = [
                "--test_mode",
                "Full",
                "--Quality_restore",
                "--gpu_ids",
                gpu_id,
            ]

            output = global_test(GLOBAL_CHECKPOINTS_FOLDER, args, input_image)

        else:
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

            output = global_test(
                GLOBAL_CHECKPOINTS_FOLDER,
                args,
                transformed_image.convert("RGB"),
                mask.convert("RGB"),
            )

        return (image2tensor(output),)


class_mappings: dict = {"Stage1": Stage1}
display_name_mappings: dict = {"Stage1": "Global Restoration"}
