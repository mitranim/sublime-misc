from Default import exec

try:
    exec._AsyncProcess
except AttributeError:
    exec._AsyncProcess = exec.AsyncProcess

class AsyncProcess(exec._AsyncProcess):
    def __init__(self, *args, selection=False, **kwargs):
        super().__init__(*args, **kwargs)
        if selection:
            view = self.listener.window.active_view()
            if view:
                for region in view.sel():
                    input = view.substr(region)
                    if input:
                        self.proc.stdin.write(input.encode('utf-8'))
            self.proc.stdin.close()

exec.AsyncProcess = AsyncProcess
