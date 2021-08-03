import os
from functools import wraps
from os import name, system
from rich.console import Console

from adnmb.model import InfoLevel, InfoModel

ONE_PAGE_ELEMENT = 5
console = Console()


def _screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if name == 'posix':
        _ = system('clear')
    else:
        # for windows platfrom
        _ = system('cls')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def screen_clear(fun):
    def with_screen_clear(*args, **kwargs):
        _screen_clear()
        return fun(*args, **kwargs)
    return with_screen_clear

def draw_info_check(fun):
    def _draw_info(*args, **kwargs):
        if isinstance(args[0], InfoModel):
            draw_info(args[0])
            return
        return fun(*args, **kwargs)
    return _draw_info



def draw_info(info_model):
    if info_model.level == InfoLevel.INFO:
        level_info = 'info: '
    if info_model.level == InfoLevel.ERROR:
        level_info = 'error: '
    console.print(f'{level_info}: {info_model.text}')

@screen_clear
@draw_info_check
def draw_post_list(post_models):
    if not post_models:
        console.print('no reply')
        return
    for idx, model in enumerate(post_models):
        console.print(f'{idx}: \t {model.content}')

@screen_clear
@draw_info_check
def draw_categories(category_models):
    i = 0
    for models in chunks(category_models, ONE_PAGE_ELEMENT):
        contents = []
        for offset in range(len(models)):
            contents.append(":" .join([str(i + offset), models[offset].content]))
        console.print('\t'.join(contents))
        i += ONE_PAGE_ELEMENT

@screen_clear
@draw_info_check
def draw_threads(thread_models):
    for idx, model in enumerate(thread_models):
        console.print(f'{idx}: \t {model.content}')
