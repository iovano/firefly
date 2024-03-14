class Initializable:
    def __init__(self, **attributes):
        for attribute, value in attributes.items():
            setattr(self, attribute, value)
