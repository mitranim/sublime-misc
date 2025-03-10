import sublime
import sublime_plugin
import uuid
import random
import os
from os import path as pt
from . import sublime_misc_util as u

PANEL_NAME = 'misc.panel'

class misc_async(sublime_plugin.TextCommand):
    def run(self, edit, command, args):
        sublime.set_timeout(lambda: self.view.run_command(command, args), 0)

# Similar to ChainOfCommand, but generates a single undo rather than multiple.
class misc_chain(sublime_plugin.TextCommand):
    def run(self, edit, commands):
        for command in commands:
            self.view.window().run_command(*command)

class text_command_replace_selections(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        for reg in reversed(view.sel()):
            src = view.substr(reg)
            out = self.replacement(reg)

            if src != out:
                view.replace(edit, reg, out)

    def replacement(self, reg):
        return self.view.substr(reg)

class misc_gen_uuid(text_command_replace_selections):
    def replacement(_self, _reg):
        return str(uuid.uuid4())

class misc_gen_uuid_no_dashes(text_command_replace_selections):
    def replacement(_self, _reg):
        return uuid.uuid4().hex

# TODO: option to pad seq with zeros.
class misc_gen_seq(sublime_plugin.TextCommand):
    def run(self, edit, start = 0):
        view = self.view
        num = start
        for reg in view.sel():
            view.replace(edit, reg, str(num))
            num += 1

class misc_gen_hex(text_command_replace_selections):
    def replacement(self, reg):
        start = min(reg.a, reg.b)
        end = max(reg.a, reg.b)
        return ''.join(
            random.choice('0123456789abcdef') for _ in range(end - start)
        )

class misc_gen_datetime(text_command_replace_selections):
    def replacement(_self, _reg):
        from datetime import datetime
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M%:%SZ')

class misc_prefix(sublime_plugin.TextCommand):
    def run(self, edit, prefix = ''):
        if not prefix:
            return

        view = self.view
        sel = view.sel()

        for reg in reversed(sel):
            view.replace(edit, sublime.Region(reg.begin(), reg.begin()), prefix)

class misc_suffix(sublime_plugin.TextCommand):
    def run(self, edit, suffix = ''):
        if not suffix:
            return

        view = self.view
        sel = view.sel()

        for reg in reversed(sel):
            view.replace(edit, sublime.Region(reg.end(), reg.end()), suffix)

class misc_wrap(sublime_plugin.TextCommand):
    def run(self, edit, prefix = '', suffix = ''):
        if not prefix and not suffix:
            return

        view = self.view
        sel = view.sel()

        for reg in reversed(sel):
            view.replace(edit, sublime.Region(reg.end(), reg.end()), suffix)
            view.replace(edit, sublime.Region(reg.begin(), reg.begin()), prefix)

class misc_context_selectors(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'misc_selector_prev_line_eol':
            index = prev_eol(view)
            return index >= 0 and view.match_selector(index, operand)
        if key == 'misc_selector_next_line_eol':
            return view.match_selector(next_eol(view), operand)
        return None

def bol(view):
    return view.line(first_sel(view)).begin()

def eol(view):
    return view.line(first_sel(view)).end()

def prev_eol(view):
    index = bol(view) - 1
    return view.line(index).end() if index >= 0 else -1

def next_eol(view):
    return view.line(eol(view) + 1).end()

def first_sel(view):
    return view.sel()[0]

class misc_prompt_select_recent_folder(sublime_plugin.WindowCommand):
    def run(self):
        path = session_path()
        if not path:
            self.window.status_message('session file not found')
            return

        with open(path, 'r', encoding='UTF-8') as file:
            session = sublime.decode_value(file.read())

        folders = session['folder_history'] or []

        def select(index):
            if index >= 0:
                switch_to_folder(folders[index])

        self.window.show_quick_panel(
            list(unexpand_paths(folders)),
            select,
            flags=sublime.MONOSPACE_FONT,
            placeholder='select folder',
        )

def switch_to_folder(folder):
    if os.name == 'nt':
        folder = convert_to_native_path(folder)

    window = sublime.active_window()
    if window and folder in window.folders():
        return

    for window in sublime.windows():
        if folder in window.folders():
            window.bring_to_front()
            return

    window = sublime.active_window()
    if not window or len(window.folders()):
        sublime.run_command('new_window')
    sublime.active_window().set_project_data({'folders': [{'path': folder}]})

def session_path():
    session_dir = pt.join(pt.dirname(sublime.packages_path()), 'Local')

    auto_session_path = pt.join(session_dir, 'Auto Save Session.sublime_session')
    if pt.isfile(auto_session_path):
        return auto_session_path

    session_path = pt.join(session_dir, 'Session.sublime_session')
    if pt.isfile(session_path):
        return session_path

    return None

def unexpand_paths(paths):
    home = pt.expanduser('~')

    for path in paths:
        if path.startswith(home):
            yield pt.join('~', pt.relpath(path, home))
        else:
            yield path

class misc_focus_last_view(sublime_plugin.WindowCommand):
    def run(self):
        views = self.window.views_in_group(self.window.active_group())
        if len(views) > 0:
            self.window.focus_view(views[-1])

class misc_replace_content(sublime_plugin.TextCommand):
    def run(self, edit, text):
        view = self.view
        view.replace(edit, sublime.Region(0, view.size()), text)
        view.sel().clear()

def panel_create(window):
    return window.create_output_panel(PANEL_NAME)

def panel_find(window):
    return window.find_output_panel(PANEL_NAME)

def panel_ensure(window):
    return panel_find(window) or panel_create(window)

def panel_hide(window):
    if window.active_panel() == PANEL_NAME:
        window.run_command('panel_hide', {'panel': PANEL_NAME})

def panel_show(window):
    window.run_command('show_panel', {'panel': PANEL_NAME})

def panel_print(window, msg):
    panel_ensure(window).run_command('misc_replace_content', {'text': msg})
    panel_show(window)

# Port of ST internal function: https://discord.com/channels/280102180189634562/280157067396775936/844876756280147988
def convert_to_native_path(path: str) -> str:
    path = bytearray(path, 'utf-8')

    if len(path) > 1 and path[0] == ord('/'):
        if path[1] == ord('?'):
            path[1] = ord('\\')
        elif path[1] != ord('/'):
            path[0] = path[1]
            path[1] = ord(':')

    path = path.decode('utf-8')
    return path.replace('/', '\\')

# Port of ST internal function: https://discord.com/channels/280102180189634562/280157067396775936/844876756280147988
def convert_from_native_path(path: str) -> str:
    path = bytearray(path, 'utf-8')

    if len(path) > 1:
        if path[0] == ord('\\') and path[1] == ord('\\'):
            # Convert from \\foo to /?foo
            path[1] = ord('?')
        elif path[1] == ord(':'):
            # Convert from C:\foo to /c/foo
            path[1] = path[0]
            path[0] = ord('/')

    path = path.decode('utf-8')
    path = path.replace('\\', '/')

    if len(path) > 0 and path[0] == '~':
        path = pt.expanduser(path)

    return path

def sel_set(sel, point):
    sel.clear()
    sel.add(sublime.Region(point, point))

# TODO: display error in panel.
class misc_eval(text_command_replace_selections):
    def run(self, edit):
        view = self.view
        for reg in view.sel():
            src = view.substr(reg)
            if src:
                view.replace(edit, reg, str(eval(src)))

class misc_unquote(text_command_replace_selections):
    def replacement(self, reg):
        return u.unquote(self.view.substr(reg))

class misc_cycle_quote(text_command_replace_selections):
    def replacement(self, reg):
        return u.cycle_quote(self.view.substr(reg))

class misc_unwrap1(sublime_plugin.TextCommand):
    def run(self, edit, size=1, expand=False, empty=False):
        view = self.view
        sel = view.sel()

        for reg in list(reversed(sel)):
            if not len(reg):
                if empty:
                    view.erase(edit, sublime.Region(reg.begin() - size, reg.end() + size))
                continue

            if expand:
                sel.subtract(reg)

            view.replace(edit, reg, u.unwrap(view.substr(reg), size))

            if expand:
                sel.add(sublime.Region(reg.begin() - size, reg.end() - size))

class misc_json_string_decode(text_command_replace_selections):
    def replacement(self, reg):
        return sublime.decode_value(self.view.substr(reg))

class misc_json_string_encode(text_command_replace_selections):
    def replacement(self, reg):
        return sublime.encode_value(self.view.substr(reg))

class misc_nop(sublime_plugin.TextCommand): pass

class misc_css_tokens_to_classes(text_command_replace_selections):
    def replacement(self, reg):
        return css_tokens_to_classes(self.view.substr(reg))

def css_tokens_to_classes(src):
    return ', '.join('.' + val for val in src.split())

class misc_css_tokens_to_placeholders(text_command_replace_selections):
    def replacement(self, reg):
        return css_tokens_to_placeholders(self.view.substr(reg))

def css_tokens_to_placeholders(src):
    return ', '.join('%' + val for val in src.split())

class misc_url_decode(text_command_replace_selections):
    def replacement(self, reg):
        return url_decode(self.view.substr(reg))

def url_decode(src):
    import urllib.parse as up
    return repr(up.urlparse(src))

class misc_url_decode_query(text_command_replace_selections):
    def replacement(self, reg):
        return url_decode_query(self.view.substr(reg))

def url_decode_query(src):
    import urllib.parse as up

    return '\n'.join(
        (key + '=' + val)
        for (key, val)
        in up.parse_qsl(up.urlparse(src).query)
    )

class misc_find_dup_lines(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        for reg in reversed(view.sel()):
            src = view.substr(reg)
            lines = src.splitlines()
            dupes = []
            counts = {}

            for line in lines:
                if line in counts:
                    counts[line] += 1
                else:
                    counts[line] = 1

                if counts[line] == 2:
                    dupes.append(line)

            out = "\n".join(
                str(counts[line]) + " " + line
                for line in dupes
            )

            if src != out:
                view.replace(edit, reg, out)

class misc_base64_decode(text_command_replace_selections):
    def replacement(self, reg):
        import base64
        return base64.b64decode(self.view.substr(reg)).decode("utf-8")

class misc_base64_encode(text_command_replace_selections):
    def replacement(self, reg):
        import base64
        return base64.b64encode(self.view.substr(reg).encode("utf-8")).decode("utf-8")
