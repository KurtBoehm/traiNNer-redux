import numpy as np
import torch
from torch import Tensor

from traiNNer.utils.types import PixelFormat


def rgb2ycbcr(img: np.ndarray, y_only: bool = False) -> np.ndarray:
    """Convert a RGB image to YCbCr image.

    This function produces the same results as Matlab's `rgb2ycbcr` function.
    It implements the ITU-R BT.601 conversion for standard-definition
    television. See more details in
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion.

    It differs from a similar function in cv2.cvtColor: `RGB <-> YCrCb`.
    In OpenCV, it implements a JPEG conversion. See more details in
    https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion.

    Args:
        img (ndarray): The input image. It accepts:
            1. np.uint8 type with range [0, 255];
            2. np.float32 type with range [0, 1].
        y_only (bool): Whether to only return Y channel. Default: False.

    Returns:
        ndarray: The converted YCbCr image. The output image has the same type
            and range as input image.
    """
    img_type = img.dtype
    img = _convert_input_type_range(img)
    if y_only:
        out_img = np.dot(img, [65.481, 128.553, 24.966]) + 16.0
    else:
        out_img = [
            *np.matmul(
                img,
                np.array(
                    [
                        [65.481, -37.797, 112.0],
                        [128.553, -74.203, -93.786],
                        [24.966, 112.0, -18.214],
                    ]
                ),
            ),
            16,
            128,
            128,
        ]
    assert isinstance(out_img, np.ndarray)
    out_img = _convert_output_type_range(out_img, img_type)
    return out_img


def bgr2ycbcr(img: np.ndarray, y_only: bool = False) -> np.ndarray:
    """Convert a BGR image to YCbCr image.

    The bgr version of rgb2ycbcr.
    It implements the ITU-R BT.601 conversion for standard-definition
    television. See more details in
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion.

    It differs from a similar function in cv2.cvtColor: `BGR <-> YCrCb`.
    In OpenCV, it implements a JPEG conversion. See more details in
    https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion.

    Args:
        img (ndarray): The input image. It accepts:
            1. np.uint8 type with range [0, 255];
            2. np.float32 type with range [0, 1].
        y_only (bool): Whether to only return Y channel. Default: False.

    Returns:
        ndarray: The converted YCbCr image. The output image has the same type
            and range as input image.
    """
    img_type = img.dtype
    img = _convert_input_type_range(img)
    if y_only:
        out_img = np.dot(img, [24.966, 128.553, 65.481]) + 16.0
    else:
        out_img = [
            *np.matmul(
                img,
                np.array(
                    [
                        [24.966, 112.0, -18.214],
                        [128.553, -74.203, -93.786],
                        [65.481, -37.797, 112.0],
                    ]
                ),
            ),
            16,
            128,
            128,
        ]
    assert isinstance(out_img, np.ndarray)
    out_img = _convert_output_type_range(out_img, img_type)
    return out_img


def ycbcr2rgb(img: np.ndarray) -> np.ndarray:
    """Convert a YCbCr image to RGB image.

    This function produces the same results as Matlab's ycbcr2rgb function.
    It implements the ITU-R BT.601 conversion for standard-definition
    television. See more details in
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion.

    It differs from a similar function in cv2.cvtColor: `YCrCb <-> RGB`.
    In OpenCV, it implements a JPEG conversion. See more details in
    https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion.

    Args:
        img (ndarray): The input image. It accepts:
            1. np.uint8 type with range [0, 255];
            2. np.float32 type with range [0, 1].

    Returns:
        ndarray: The converted RGB image. The output image has the same type
            and range as input image.
    """
    img_type = img.dtype
    img = _convert_input_type_range(img) * 255
    out_img = np.matmul(
        img,
        np.array(
            [
                [0.00456621, 0.00456621, 0.00456621],
                [0, -0.00153632, 0.00791071],
                [0.00625893, -0.00318811, 0],
            ]
        ),
    ) * 255.0 + [-222.921, 135.576, -276.836]
    out_img = _convert_output_type_range(out_img, img_type)
    return out_img


def ycbcr2bgr(img: np.ndarray) -> np.ndarray:
    """Convert a YCbCr image to BGR image.

    The bgr version of ycbcr2rgb.
    It implements the ITU-R BT.601 conversion for standard-definition
    television. See more details in
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion.

    It differs from a similar function in cv2.cvtColor: `YCrCb <-> BGR`.
    In OpenCV, it implements a JPEG conversion. See more details in
    https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion.

    Args:
        img (ndarray): The input image. It accepts:
            1. np.uint8 type with range [0, 255];
            2. np.float32 type with range [0, 1].

    Returns:
        ndarray: The converted BGR image. The output image has the same type
            and range as input image.
    """
    img_type = img.dtype
    img = _convert_input_type_range(img) * 255
    out_img = np.matmul(
        img,
        np.array(
            [
                [0.00456621, 0.00456621, 0.00456621],
                [0.00791071, -0.00153632, 0],
                [0, -0.00318811, 0.00625893],
            ]
        ),
    ) * 255.0 + [-276.836, 135.576, -222.921]
    out_img = _convert_output_type_range(out_img, img_type)
    return out_img


def _convert_input_type_range(img: np.ndarray) -> np.ndarray:
    """Convert the type and range of the input image.

    It converts the input image to np.float32 type and range of [0, 1].
    It is mainly used for pre-processing the input image in colorspace
    conversion functions such as rgb2ycbcr and ycbcr2rgb.

    Args:
        img (ndarray): The input image. It accepts:
            1. np.uint8 type with range [0, 255];
            2. np.float32 type with range [0, 1].

    Returns:
        (ndarray): The converted image with type of np.float32 and range of
            [0, 1].
    """
    img_type = img.dtype
    img = img.astype(np.float32)
    if img_type == np.float32:
        pass
    elif img_type == np.uint8:
        img /= 255.0
    else:
        raise TypeError(
            f"The img type should be np.float32 or np.uint8, but got {img_type}"
        )
    return img


def _convert_output_type_range(img: np.ndarray, dst_type: np.dtype) -> np.ndarray:
    """Convert the type and range of the image according to dst_type.

    It converts the image to desired type and range. If `dst_type` is np.uint8,
    images will be converted to np.uint8 type with range [0, 255]. If
    `dst_type` is np.float32, it converts the image to np.float32 type with
    range [0, 1].
    It is mainly used for post-processing images in colorspace conversion
    functions such as rgb2ycbcr and ycbcr2rgb.

    Args:
        img (ndarray): The image to be converted with np.float32 type and
            range [0, 255].
        dst_type (np.uint8 | np.float32): If dst_type is np.uint8, it
            converts the image to np.uint8 type with range [0, 255]. If
            dst_type is np.float32, it converts the image to np.float32 type
            with range [0, 1].

    Returns:
        (ndarray): The converted image with desired type and range.
    """
    if dst_type not in (np.uint8, np.float32):  # type: ignore
        raise TypeError(
            f"The dst_type should be np.float32 or np.uint8, but got {dst_type}"
        )
    if dst_type == np.uint8:
        img = img.round()
    else:
        img /= 255.0
    return img.astype(dst_type)


def rgb2pixelformat_pt(img: Tensor, pixel_format: PixelFormat) -> Tensor:
    if pixel_format == "rgb":
        return img
    elif pixel_format == "gray":
        raise NotImplementedError
    elif pixel_format == "yuv444":
        return rgb2ycbcr_pt(img)
    elif pixel_format == "y":
        return rgb2ycbcr_pt(img)[:, 0:1, :, :]
    elif pixel_format == "uv":
        raise NotImplementedError

    raise NotImplementedError(pixel_format)


def pixelformat2rgb_pt(
    img: Tensor, img_ref_rgb: Tensor | None, pixel_format: PixelFormat
) -> Tensor:
    if pixel_format == "rgb":
        return img
    elif pixel_format == "gray":
        raise NotImplementedError  # convert gray to rgb
    elif pixel_format == "yuv444":
        return ycbcr2rgb_pt(img)
    elif pixel_format == "y":
        assert img_ref_rgb is not None, "gt is required for luma pixel format"
        img_yuv = rgb2ycbcr_pt(img_ref_rgb)
        img_yuv[:, 0:1, :, :] = img  # replace luma
        return ycbcr2rgb_pt(img_yuv)
    elif pixel_format == "uv":
        assert img_ref_rgb is not None, "gt is required for chroma pixel format"
        img_yuv = rgb2ycbcr_pt(img_ref_rgb)
        img_yuv[:, 1:, :, :] = img  # replace chroma
        return ycbcr2rgb_pt(img_yuv)

    raise NotImplementedError(pixel_format)


def rgb2ycbcr_pt(img: Tensor, y_only: bool = False) -> Tensor:
    """Convert RGB images to YCbCr images (PyTorch version).

    It implements the ITU-R BT.601 conversion for standard-definition television. See more details in
    https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion.

    Args:
        img (Tensor): Images with shape (n, 3, h, w), the range [0, 1], float, RGB format.
         y_only (bool): Whether to only return Y channel. Default: False.

    Returns:
        (Tensor): converted images with the shape (n, 3/1, h, w), the range [0, 1], float.
    """
    if y_only:
        weight = torch.tensor([[65.481], [128.553], [24.966]]).to(img)
        out_img = (
            torch.matmul(img.permute(0, 2, 3, 1), weight).permute(0, 3, 1, 2) + 16.0
        )
    else:
        weight = torch.tensor(
            [
                [65.481, -37.797, 112.0],
                [128.553, -74.203, -93.786],
                [24.966, 112.0, -18.214],
            ]
        ).to(img)
        bias = torch.tensor([16, 128, 128]).view(1, 3, 1, 1).to(img)
        out_img = (
            torch.matmul(img.permute(0, 2, 3, 1), weight).permute(0, 3, 1, 2) + bias
        )

    out_img = out_img / 255.0
    return out_img


def ycbcr2rgb_pt(img: Tensor) -> Tensor:
    img_ycbcr = img * 255.0

    y = img_ycbcr[:, 0:1, :, :]
    cb = img_ycbcr[:, 1:2, :, :]
    cr = img_ycbcr[:, 2:3, :, :]

    r = 1.164 * (y - 16) + 1.596 * (cr - 128)
    g = 1.164 * (y - 16) - 0.392 * (cb - 128) - 0.813 * (cr - 128)
    b = 1.164 * (y - 16) + 2.017 * (cb - 128)

    rgb = torch.cat((r, g, b), dim=1)
    rgb = rgb / 255.0

    return rgb


def rgb_to_luma(img: Tensor) -> Tensor:
    """RGB to CIELAB L*"""

    if len(img.shape) < 3 or (img.shape[-3] != 3 and img.shape[-3] != 1):
        raise ValueError(
            f"Input size must have a shape of (*, 3, H, W) or (*, 1, H, W). Got {img.shape}"
        )

    out_img = img.permute(0, 2, 3, 1).clamp(1e-12, 1)
    out_img = torch.where(
        out_img <= 0.04045, out_img / 12.92, torch.pow((out_img + 0.055) / 1.055, 2.4)
    )
    if img.shape[-3] == 3:
        out_img = out_img @ torch.tensor([0.2126, 0.7152, 0.0722]).to(img)

    out_img = torch.where(
        out_img <= (216 / 24389),
        out_img * (out_img * (24389 / 27)),
        torch.pow(out_img, (1 / 3)) * 116 - 16,
    )
    out_img = torch.clamp((out_img / 100), 0, 1)

    return out_img


def rgb_to_linear_rgb(image: Tensor) -> Tensor:
    r"""Convert an sRGB image to linear RGB. Used in colorspace conversions.

    .. image:: _static/img/rgb_to_linear_rgb.png

    Args:
        image: sRGB Image to be converted to linear RGB of shape :math:`(*,3,H,W)`.

    Returns:
        linear RGB version of the image with shape of :math:`(*,3,H,W)`.

    Example:
        >>> input = torch.rand(2, 3, 4, 5)
        >>> output = rgb_to_linear_rgb(input) # 2x3x4x5

    """

    if len(image.shape) < 3 or image.shape[-3] != 3:
        raise ValueError(
            f"Input size must have a shape of (*, 3, H, W).Got {image.shape}"
        )

    return torch.where(
        image > 0.04045, torch.pow(((image + 0.055) / 1.055), 2.4), image / 12.92
    )


def rgb_to_xyz(image: Tensor) -> Tensor:
    r"""Convert a RGB image to XYZ.

    .. image:: _static/img/rgb_to_xyz.png

    Args:
        image: RGB Image to be converted to XYZ with shape :math:`(*, 3, H, W)`.

    Returns:
         XYZ version of the image with shape :math:`(*, 3, H, W)`.

    Example:
        >>> input = torch.rand(2, 3, 4, 5)
        >>> output = rgb_to_xyz(input)  # 2x3x4x5

    """

    if len(image.shape) < 3 or image.shape[-3] != 3:
        raise ValueError(
            f"Input size must have a shape of (*, 3, H, W). Got {image.shape}"
        )

    r = image[..., 0, :, :]
    g = image[..., 1, :, :]
    b = image[..., 2, :, :]

    x = 0.412453 * r + 0.357580 * g + 0.180423 * b
    y = 0.212671 * r + 0.715160 * g + 0.072169 * b
    z = 0.019334 * r + 0.119193 * g + 0.950227 * b

    out = torch.stack([x, y, z], -3)

    return out


def linear_rgb_to_lab_norm(lin_rgb: Tensor) -> Tensor:
    r"""Convert a RGB image to Lab.

    .. image:: _static/img/rgb_to_lab.png

    The input RGB image is assumed to be in the range of :math:`[0, 1]`. Lab
    color is computed using the D65 illuminant and Observer 2.

    Args:
        image: RGB Image to be converted to Lab with shape :math:`(*, 3, H, W)`.

    Returns:
        Lab version of the image with shape :math:`(*, 3, H, W)`.
        The L channel values are in the range 0..100. a and b are in the range -128..127.

    Example:
        >>> input = torch.rand(2, 3, 4, 5)
        >>> output = rgb_to_lab(input)  # 2x3x4x5

    """

    if len(lin_rgb.shape) < 3 or lin_rgb.shape[-3] != 3:
        raise ValueError(
            f"Input size must have a shape of (*, 3, H, W). Got {lin_rgb.shape}"
        )

    xyz_im: torch.Tensor = rgb_to_xyz(lin_rgb)

    # normalize for D65 white point
    xyz_ref_white = torch.tensor(
        [0.95047, 1.0, 1.08883], device=xyz_im.device, dtype=xyz_im.dtype
    )[..., :, None, None]
    xyz_normalized = torch.div(xyz_im, xyz_ref_white)

    threshold = 0.008856
    power = torch.pow(xyz_normalized.clamp(min=threshold), 1 / 3.0)
    scale = 7.787 * xyz_normalized + 4.0 / 29.0
    xyz_int = torch.where(xyz_normalized > threshold, power, scale)

    x = xyz_int[..., 0, :, :]
    y = xyz_int[..., 1, :, :]
    z = xyz_int[..., 2, :, :]

    L = ((116.0 * y) - 16.0) / 100  # noqa: N806
    a = ((500.0 * (x - y)) + 128) / 255
    _b = (200.0 * (y - z) + 128) / 255

    out = torch.stack([L, a, _b], dim=-3)

    return out
