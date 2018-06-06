import cv2
import math
import numpy
import imageio
import random
import asyncio
from sanic import Sanic, response
from sanic.exceptions import abort

webserver = Sanic()
lgbt_methods = []


@lgbt_methods.append
def make_strip_red(strip):
    strip[:, :, 0] = 0
    strip[:, :, 1] = 0
    return strip


@lgbt_methods.append
def make_strip_orange(strip):
    strip[:, :, 0] = 0
    strip[:, :, 1] = 165
    return strip


@lgbt_methods.append
def make_strip_yellow(strip):
    strip[:, :, 0] = 0
    return strip


@lgbt_methods.append
def make_strip_green(strip):
    strip[:, :, 0] = 0
    strip[:, :, 2] = 0
    return strip


@lgbt_methods.append
def make_strip_blue(strip):
    strip[:, :, 1] = 0
    strip[:, :, 2] = 0
    return strip


@lgbt_methods.append
def make_strip_purple(strip):
    strip[:, :, 1] = 0
    return strip


def lgbtify_cv2_img(img):
    height, width, channels = img.shape
    strip_height = math.ceil(height / 6)
    strips = []
    for i in range(0, 6):
        strip_height_times = strip_height*i
        strips.append(
            img[
                strip_height_times:strip_height_times+strip_height,
                0:width
            ]
        )
    edited_strips = []
    for i in range(0, len(strips)):
        edited_strips.append(
            lgbt_methods[i](strips[i].copy())
        )
    output = numpy.zeros((height, width, channels))
    y = 0
    for stitch in edited_strips:
        h, w, d = stitch.shape
        output[y:y+h, 0:w] = stitch
        y += h
    return output


ALLOWED_EXTENSIONS = [
    "jpg", "jpeg", "png", "gif"
]
RANDOM_CHARSET = "abcdefghijkmnopqrstuvwxyz0123456789"


def randomly_gen_string(length):
    _str = ""
    for i in range(0, length):
        _str += RANDOM_CHARSET[
            random.randint(0, len(RANDOM_CHARSET)-1)
        ]
    return _str


@webserver.route("/", methods=["POST"])
async def lgbtify_img_gif(request):
    if 'file' not in request.files:
        return abort(400)

    _file = request.files['file'][0]
    if all(
        [
            not _file.name.endswith(e) for e in ALLOWED_EXTENSIONS
        ]
    ):
        return abort(400)

    def run_on_gif():
        try:
            fp = "/tmp/{}.gif".format(randomly_gen_string(10))
            open(fp, "wb").write(_file.body)
            gif = imageio.mimread(fp)
            imgs = [
                numpy.uint8(lgbtify_cv2_img(
                    cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                )[:, :, ::-1]) for img in gif
            ]
            result_fp = "/tmp/{}.gif".format(randomly_gen_string(10))
            imageio.mimsave(result_fp, imgs)
        except BaseException:
            return
        return result_fp

    if _file.name.endswith("gif"):
        r = await asyncio.get_event_loop().run_in_executor(
            None,
            run_on_gif
        )
        if r:
            return await response.file(r)
        return abort(400)

    def run_on_image():
        extension = _file.name.split(".")[-1]
        fp = "/tmp/{}.{}".format(randomly_gen_string(10), extension)
        open(fp, "wb").write(_file.body)
        result_fp = "/tmp/{}.{}".format(randomly_gen_string(10), extension)
        try:
            cv2.imwrite(result_fp, lgbtify_cv2_img(
                cv2.imread(fp)
            ))
        except BaseException:
            return
        return result_fp

    r = await asyncio.get_event_loop().run_in_executor(
        None,
        run_on_image
    )
    if r:
        return await response.file(r)
    return abort(400)

if __name__ == "__main__":
    webserver.run(port=80, host="0.0.0.0")
