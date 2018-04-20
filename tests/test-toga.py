import toga


def button_handler(widget):
    print('No poking pls')


def build(app):
    box = toga.Box()

    input = toga.TextInput
    box.add(input)

    button = toga.Button('Heya, Octoblub says hi!', on_press=button_handler)
    button.style.padding = 50
    button.style.flex = 1
    box.add(button)

    return box


def main():
    return toga.App('Octoblub', 'org.acidtv.octosearch', startup=build)


if __name__ == '__main__':
    main().main_loop()
