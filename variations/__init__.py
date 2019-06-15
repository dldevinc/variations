"""
    ============
      Вариации
    ============

    Объявляет класс Variation, управляющий обработкой и сохранением картинки,
    используя процессоры из модуля pilkit.

    Имеется возможность автоматического вычисления размера одной или обеих сторон
    изображения, что позволяет частично указывать размерность (640x0, 0x768 и т.п.).

    Пример
    ------
    from PIL import Image
    from variations import processors
    from variations.variation import Variation
    from variations.utils import prepare_image

    variation = Variation(
        size=(400, 0),
        max_height=800,
        clip=False,
        upscale=False,
        anchor=processors.Anchor.TOP_LEFT,
        jpeg=dict(
            quality=92,
        ),
        webp=dict(
            lossless=True,
            quality=90,
        ),
        postprocessors=[
            processors.ColorOverlay('#FF0000', overlay_opacity=0.25),
        ],
    )
    img = Image.open('source.jpg')
    img = prepare_image(img, draft_size=variation.get_output_size(img.size))
    new_img = variation.process(img)
    dest_path = variation.replace_extension('dest.jpg')
    variation.save(new_img, dest_path)

    Параметры
    ---------
    size
        type            list/tuple
        default         -//- (required)
        description     Требуемые размеры изображения. Финальные размеры могут
                        отличаться, в зависимости от используемых pilkit-процессоров.

    clip
        type            bool
        default         True
        description     Разрешено ли обрезать исходное изображение. Если нет, то
                        изображение будет вписано в холст.

    upscale
        type            bool
        default         False
        description     Разрешено ли увеличивать масштаб исходного изображения.
                        Может привести к "размыливанию" изображения.

    anchor
        type            str/tuple
        default         processors.Anchor.CENTER / 'c' / (0.5, 0.5)
        description     В случае clip=True, определяет, какая сторона изображения
                        сохраняется на холсте. Если clip=False, то определяет в
                        какой части холста будет находиться изображение.

    face_detection
        type            bool
        default         False
        description     Включение алгоритма поиска лиц на изображении при обрезке.
                        Если лица найдены, то их положение будет более приоритетным,
                        чем значение anchor.

    format
        type            str
        default         auto
        description     Принудительный формат вариации. По-умолчанию используется
                        формат исходного файла.

    preprocessors
        type            tuple/list
        default         []
        description     Список pilkit-процессоров, которые будут выполнены ПЕРЕД
                        основным действием вариации*.

    postprocessors
        type            tuple/list
        default         []
        description     Список pilkit-процессоров, которые будут выполнены ПОСЛЕ
                        основного действия вариации*.

    **extra_context
        type            dict
        default         см. conf.py
        description     Дополнительные опции. Опции с именами, совпадающими с
                        названиями формата (jpeg / png / webp / ...) передаются
                        в метод Image.save().

    * P.S. "основным действием вариации" является ресайз и/или кадрирование,
    в зависимости от параметров size, crop, upscale и размера исходного изображения.
"""

# загрузка всех плагинов PIL
from PIL import Image
Image.init()
