if not re.match(r'^[0-9]+$', value):
    self.__code_input.value = self.__code_input.value.replace(value,"")
    self.__code_input.update()