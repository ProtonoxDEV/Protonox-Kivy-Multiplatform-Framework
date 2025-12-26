from kivy.tests.common import GraphicUnitTest


class FileChooserTestCase(GraphicUnitTest):

    def test_filechooserlistview(self):
        from os.path import expanduser

        from kivy.uix.filechooser import FileChooserListView
        r = self.render
        wid = FileChooserListView(path=expanduser('~'))
        r(wid, 2)
