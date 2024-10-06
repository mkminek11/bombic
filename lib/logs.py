from logging import basicConfig, debug, info, warning, error, critical, DEBUG

basicConfig(format = "\033[38;2;222;62;51m[%(asctime)s] \033[38;2;222;208;51m%(filename)s \033[0m\033[38;2;66;194;79m(line %(lineno)d)\033[0m %(message)s", datefmt = "%H:%M:%S", level = DEBUG)