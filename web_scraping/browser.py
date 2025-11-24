
def handle(arg):
    pass


def main() -> None:
    with open("input/urls.input") as input_file:
        urls = input_file.readlines()
        urls = [url.replace("\n", "") for url in urls]
        print(urls)

    handle(urls)


if __name__ == '__main__':
    main()
