red = 255 * (1 - self.__rating)
green = 255 * self.__rating
blue = 0 
hex_color = "#{:02X}{:02X}{:02X}".format(int(red), int(green), int(blue))
self.__slider.thumb_color = hex_color
self.__slider.active_color = hex_color