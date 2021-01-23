import sublime
import sublime_plugin
import uuid
import random
import datetime
from os import path as pt

class misc_async(sublime_plugin.TextCommand):
    def run(self, edit, command, args):
        sublime.set_timeout(lambda: self.view.run_command(command, args), 0)

# Similar to ChainOfCommand, but generates a single undo rather than multiple.
class misc_chain(sublime_plugin.TextCommand):
    def run(self, edit, commands):
        for command in commands:
            self.view.window().run_command(*command)

class misc_gen_uuid(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.view.replace(edit, region, str(uuid.uuid4()))

class misc_gen_uuid_no_dashes(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.view.replace(edit, region, uuid.uuid4().hex)

# TODO: option to pad seq with zeros.
class misc_gen_seq(sublime_plugin.TextCommand):
    def run(self, edit, start = 0):
        num = start
        for region in self.view.sel():
            self.view.replace(edit, region, str(num))
            num += 1

hex_chars = '0123456789abcdef'

class misc_gen_hex(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            start = min(region.a, region.b)
            end = max(region.a, region.b)
            text = ''.join(random.choice(hex_chars) for _ in range(end - start))
            self.view.replace(edit, region, text)

class misc_gen_datetime(sublime_plugin.TextCommand):
    def run(self, edit):
        text = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M%:%SZ')
        for region in self.view.sel():
            self.view.replace(edit, region, text)

# Should be activated inside a line comment by a hotkey. Continues the comment
# on the previous or next line, auto-inserting the comment prefix if needed.
# Shouldn't be used inside block comments.
#
# Originally based on: https://github.com/STealthy-and-haSTy/SublimeScraps/blob/master/plugins/wrap_text.py
#
# Note: the built-in 'insert' command preserves indentation.
#
# TODO:
#
#   * Look for the prefix in both directions around the caret.
#   * Don't split up the prefix if activated inside of it. Move the caret to its
#     start or end.
#   * When activated just before the prefix, swap the order of prefix and
#     newline.
#   * When activated on an end-of-line comment preceded by code, abort.
#
# Bonus TODO: comment-aware "join lines".
class misc_continue_comment(sublime_plugin.TextCommand):
    def run(self, edit, forward=None):
        view = self.view
        prefix = line_comment_start(view)
        if prefix:
            prefix += ' '

        if forward == True:
            view.run_command('move_to', {'to': 'hardeol'})
            view.run_command('insert', {'characters': '\n' + prefix})
        elif forward == False:
            view.run_command('move', {'by': 'lines', 'forward': False})
            view.run_command('move_to', {'to': 'hardeol'})
            view.run_command('insert', {'characters': '\n' + prefix})
        else:
            view.run_command('insert', {'characters': '\n' + prefix})

def line_comment_start(view):
    caret = first_sel(view).begin()
    line_begin = view.line(caret).begin()
    region = region_matching_selector(view, sublime.Region(line_begin, caret), 'comment punctuation - comment.block')
    return region and view.substr(region) or ''

def region_matching_selector(view, within_region, selector):
    is_match = lambda pt: view.match_selector(pos, selector)

    # Advance while the selector doesn't match.
    pos = within_region.begin()
    while pos < within_region.end() and not is_match(pos):
        pos += 1

    start_pos = pos

    # Advance while the selector matches to find the extent the scope.
    while pos < within_region.end() and is_match(pos):
        pos += 1
    if start_pos == pos:
        return None
    return sublime.Region(start_pos, pos)

class context_line_selectors(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'prev_line_eol_selector':
            index = prev_eol(view)
            return index >= 0 and view.match_selector(index, operand)
        if key == 'next_line_eol_selector':
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
