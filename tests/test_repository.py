"""Check local documentation links and public packaging boundaries."""
from pathlib import Path
import json
import re
import unittest
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_documentation_links_resolve(self):
        docs=[ROOT/'README.md',ROOT/'README.en.md',ROOT/'CONTRIBUTING.md',ROOT/'SECURITY.md',*ROOT.joinpath('docs').glob('*.md'),*ROOT.joinpath('skills').rglob('*.md')]
        broken=[]
        for doc in docs:
            for target in re.findall(r'\]\(([^\s)]+)\)',doc.read_text(encoding='utf-8')):
                if target.startswith(('http:','https:','#','mailto:')):continue
                local=unquote(target.split('#')[0])
                if local and not (doc.parent/local).exists():broken.append((str(doc.relative_to(ROOT)),target))
        self.assertEqual(broken,[])

    def test_labels_are_valid_and_unique(self):
        labels=json.loads((ROOT/'.github/labels.json').read_text(encoding='utf-8'))
        self.assertEqual(len({x['name'] for x in labels}),len(labels))
        self.assertTrue(all(re.fullmatch('[0-9a-fA-F]{6}',x['color']) for x in labels))

    def test_installable_skill_has_no_private_fixtures(self):
        skill=ROOT/'skills/chat-to-notes'
        self.assertTrue((skill/'SKILL.md').is_file())
        for path in skill.rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:continue
            self.assertNotIn(path.suffix.lower(),('.pdf','.zip','.ttf','.ttc','.env'))
            text=path.read_text(encoding='utf-8')
            self.assertNotRegex(text,r'(?i)\b[A-Z]:[/\\]Users[/\\](?!Public\b|Default\b)')


if __name__=='__main__':unittest.main()
