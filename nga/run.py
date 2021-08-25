from cmd import Cmd

from artist import draw_categories, draw_info, draw_threads, draw_posts
from client import NGA


class Runner(Cmd):
    prompt = "nga -> "
    client = NGA()
    current_cateogry = None

    def do_q(self, *args):
        """Quit"""
        return True

    def do_st(self, *args):
        """show current threads """
        if not self.client.thread_models:
            print('no threads')
        draw_threads(self.client.thread_models)

    def do_jp(self, idx):
        info = self.client.change_post_page(idx)
        if info:
            draw_info(info)
        else:
            post_list = self.client.get_next_post()
            draw_posts(post_list)

    def do_np(self, *args):
        """Next page of post"""
        post_list = self.client.get_next_post()
        draw_posts(post_list)

    def do_nt(self, *args):
        """Next page of thread"""
        thread_list = self.client.get_next_page_threads()
        draw_threads(thread_list)

    def do_ct(self, idx):
        """Change current thread"""
        info = self.client.change_thread(idx)
        draw_info(info)

    def do_cc(self, category_number):
        """Change current category"""
        info = self.client.change_category(category_number)
        draw_info(info)

    def do_sc(self, *args):
        """Show all categories"""
        if not self.client.categories:
            self.client.get_categories()
        draw_categories(self.client.categories)

    def cmdloop(self):
        print("please input ? to visit all command")
        super().cmdloop(self)


Runner().cmdloop()