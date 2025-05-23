from cmd import Cmd

from artist import draw_categories, draw_info, draw_threads, draw_posts, draw_thread_info
from client import NGA


class Runner(Cmd):
    prompt = "nga -> "
    client = NGA()
    show_thread_id = False

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
            post_page, max_post_page = self.client.post_page, self.client.max_post_page
            post_list = self.client.get_next_post()
            draw_posts(post_list, post_page, max_post_page)

    def do_jt(self, thread_id):
        """Change current thread"""
        info = self.client.change_thread_by_id(thread_id)
        draw_info(info)

    def do_showid(self, *args):
        self.show_thread_id = True

    def do_hideid(self, *args):
        self.show_thread_id = False

    def do_np(self, *args):
        """Next page of post"""
        post_page, max_post_page = self.client.post_page, self.client.max_post_page
        post_list = self.client.get_next_post()
        draw_posts(post_list, post_page, max_post_page)

    def do_nt(self, *args):
        """Next page of thread"""
        thread_list = self.client.get_next_page_threads()
        draw_threads(thread_list, show_thread_id=self.show_thread_id)

    def do_ct(self, idx):
        """Change current thread"""
        info = self.client.change_thread(idx)
        draw_info(info)

    def do_stid(self, *argsf):
        tid = self.client.current_thread.id
        author_id = self.client.current_thread.author_id
        draw_thread_info(tid, author_id)


    def do_cc(self, category_number):
        """Change current category"""
        info = self.client.change_category(category_number)
        draw_info(info)

    def do_jc(self, category_id):
        info = self.client.change_category_by_id(category_id)
        draw_info(info)

    def do_sc(self, *args):
        """Show all categories"""
        if not self.client.categories:
            self.client.get_categories()
        draw_categories(self.client.categories)

    def do_rp(self, text):
        """Reply thread"""
        self.client.post_content(str(text))

    def cmdloop(self):
        print("please input ? to visit all command")
        super().cmdloop(self)


Runner().cmdloop()
