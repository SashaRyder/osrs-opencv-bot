import cv2


class CVTemplate:
    __template = __width = __height = None

    def __init__(self, template_path):
        self.__template = cv2.imread(template_path)
        assert self.__template is not None, "file could not be read, check with os.path.exists()"
        self.__height, self.__width = self.__template.shape[:-1]

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height
    
    def get_template(self):
        return self.__template