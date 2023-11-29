import unittest
from cms import app

class CMSTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("about.md", response.get_data(as_text=True))
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("history.txt", response.get_data(as_text=True))

    def test_viewing_text_document(self):
        with self.client.get('/history.txt') as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn("Python 0.9.0 (initial release) is released.", response.get_data(as_text=True))

    def test_document_not_found(self):
        response = self.client.get("/notafile.ext")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response.headers['Location'])  #
        self.assertEqual(response.status_code, 200)
        self.assertIn("notafile.ext does not exist", response.get_data(as_text=True))

        response = self.client.get("/")
        self.assertNotIn("notafile.ext does not exist", response.get_data(as_text=True))

    def test_editing_document(self):
        response = self.client.get("/changes.txt/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<textarea", response.get_data(as_text=True))
        self.assertIn('<button type="submit"', response.get_data(as_text=True))

    def test_updating_document(self):
        response = self.client.post("/changes.txt", data={'content': "new content"})
        self.assertEqual(response.status_code, 302)

        follow_response = self.client.get(response.headers['Location'])
        self.assertIn("changes.txt has been updated", follow_response.get_data(as_text=True))

        with self.client.get("/changes.txt") as content_response:
            self.assertEqual(content_response.status_code, 200)
            self.assertIn("new content", content_response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
