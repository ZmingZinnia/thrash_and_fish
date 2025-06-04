from os import name, system
from rich.console import Console
from wcwidth import wcswidth

from model import InfoLevel, InfoModel

ONE_PAGE_ELEMENT = 5
console = Console()


def ljust_wcwidth(s, width, fillchar=' '):
    current_width = wcswidth(s)
    fill_width = width - current_width
    if fill_width <= 0:
        return s
    else:
        return s + fillchar * fill_width


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
    console.print(f'{level_info}{info_model.text}')


@screen_clear
@draw_info_check
def draw_categories(category_models):
    i = 0
    console.print('draw')
    for models in chunks(category_models, ONE_PAGE_ELEMENT):
        contents = []
        for offset in range(len(models)):
            text = ":" .join([str(i + offset), models[offset].name])
            contents.append(ljust_wcwidth(text, 21))
        console.print('     '.join(contents))
        i += ONE_PAGE_ELEMENT


@screen_clear
@draw_info_check
def draw_threads(thread_models, show_thread_id=False):
    for idx, model in enumerate(thread_models):
        if not show_thread_id:
            console.print(ljust_wcwidth(f"{idx}: {model.content}", 100), f"    author: {model.author}")
        else:
            console.print(ljust_wcwidth(f"{idx}: {model.content}", 100), f"     author: {model.author}. thread_id:  {model.id}")

@screen_clear
@draw_info_check
def draw_posts(post_models, current_page, total_page):
    console.print(f"current_page/total_page: {current_page}/{total_page}")
    for idx, model in enumerate(post_models):
        try:
            console.print(ljust_wcwidth(f"{model.create_time}-{model.author.strip()}  ", 40), f"{idx}:  {model.content}")
        except Exception:
            console.print(f"error")


@screen_clear
@draw_info_check
def draw_thread_info(tid, author_id):
    console.print(f"thread_id: {tid} author_id: {author_id}")
