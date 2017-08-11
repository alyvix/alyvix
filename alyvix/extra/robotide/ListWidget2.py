from PyQt4 import QtGui

class listWidgetAlyObj2(QtGui.QListView):

    def keyPressEvent(self, event):
        if event.type() == QEvent.ShortcutOverride:
            print "aaaaaa"
