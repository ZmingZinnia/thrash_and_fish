from cmd import Cmd

from adnmb.adnmb_client import Adnmb
from adnmb.artist import draw_categories, draw_threads, draw_info, draw_post_list, console


class Runner(Cmd):
    prompt = "adnmb"
    adnmb_client = Adnmb()
    current_cateogry = None

    def do_q(self, *args):
        """Quit"""
        return True

    def do_pp(self, *args):
        """Previous page of post"""
        post_list = self.adnmb_client.get_prev_post()
        draw_post_list(post_list)

    def do_st(self, *args):
        """show current threads """
        if not self.adnmb_client.thread_models:
            print('no threads')
        draw_threads(self.adnmb_client.thread_models)

    def do_np(self, *args):
        """Next page of post"""
        post_list = self.adnmb_client.get_next_post()
        draw_post_list(post_list)

    def do_pt(self, *args):
        """Previous page of thread"""
        thread_list = self.adnmb_client.get_prev_page_threads()
        draw_threads(thread_list)

    def do_nt(self, *args):
        """Next page of thread"""
        thread_list = self.adnmb_client.get_next_page_threads()
        draw_threads(thread_list)

    def do_ct(self, idx):
        """Change current thread"""
        info = self.adnmb_client.change_thread(idx)
        draw_info(info)

    def do_cc(self, category_number):
        """Change current category"""
        info = self.adnmb_client.change_category(category_number)
        draw_info(info)

    def do_sc(self, *args):
        """Show all categories"""
        if not self.adnmb_client.category_models:
            self.adnmb_client.get_categories()
        draw_categories(self.adnmb_client.category_models)

    def cmdloop(self):
        print("please input ? to visit all command")
        super().cmdloop(self)


Runner().cmdloop()