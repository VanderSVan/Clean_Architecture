from pathlib import Path


class Index:
    def on_get(self, req, resp):
        project_dir = Path(__file__).parent.absolute()
        html_path = project_dir.parent.joinpath('templates', 'index.html')
        with html_path.open('r') as f:
            resp.content_type = 'text/html'
            resp.text = f.read()
