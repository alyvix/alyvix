

class ViewerManagerBase():

    def __init__(self):
        super(ViewerManagerBase, self).__init__()

    def run(self, url, fullscreen):
        raise NotImplementedError