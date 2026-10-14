# Third-party notices

Linux Paint code is licensed under the project MIT license. The upstream project is blankresearch/ClassicPaint by Youssef. The original embedded Microsoft Paint artwork is separately licensed and is not covered by the Python code MIT license. Linux Paint's current application icon and symbolic ribbon are original replacement artwork; some legacy cursor/reference resources remain in the source.

## Background segmentation

- OpenCV: https://github.com/opencv/opencv — Apache License 2.0. GrabCut runs locally on user masks.
- ONNX Runtime: https://github.com/microsoft/onnxruntime — MIT License.
- NumPy: https://numpy.org/ — BSD-3-Clause.
- Pillow: https://python-pillow.github.io/ — HPND License.
- BiRefNet: https://github.com/ZhengPeng7/BiRefNet — MIT License, Copyright (c) 2024 ZhengPeng.
- Downloadable ONNX model: BiRefNet General Lite, distributed by https://github.com/danielgatis/rembg/releases/tag/v0.0.0. File: `BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx`. Expected MD5: `4fab47adc4ff364be1713e97b7e66334`. The model is downloaded separately, never bundled in the repository or executable.
- Input normalization (ImageNet mean/std, 1024px input), output sigmoid and model metadata were verified against the rembg BiRefNet sessions: https://github.com/danielgatis/rembg/tree/main/rembg/sessions — MIT License, Copyright (c) 2020-present Daniel Gatis. Linux Paint does not bundle rembg or depend on its Python package.

MIT license notice for BiRefNet and rembg:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Qt / PySide6 are distributed under their applicable LGPL/GPL/commercial licenses. PyInstaller distributes bootloaders under GPL with its bundling exception. See the license files included by each dependency.
