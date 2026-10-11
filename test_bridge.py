import tempfile
import time
import unittest
from pathlib import Path
from bridge import snapshot


class SnapshotTests(unittest.TestCase):
    def test_recent_session_metadata_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sessions = root / 'agent-a' / 'sessions'
            sessions.mkdir(parents=True)
            (sessions / 'one.jsonl').write_text('private transcript is not parsed')
            now = time.time()
            frame = snapshot(root, now, 20)
            self.assertEqual(frame['active_agents'], ['agent-a'])
            self.assertEqual(frame['state'], 'processing')
            self.assertNotIn('private transcript', str(frame))
            archived = sessions / 'old.jsonl.deleted.zst'
            archived.write_text('ignore archive')
            self.assertEqual(len(snapshot(root, now, 20)['agents']), 1)

    def test_stale_session_is_quiet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sessions = root / 'agent-b' / 'sessions'
            sessions.mkdir(parents=True)
            file = sessions / 'one.jsonl'
            file.write_text('{}')
            now = time.time()
            import os
            os.utime(file, (now - 100, now - 100))
            frame = snapshot(root, now, 20)
            self.assertEqual(frame['active_agents'], [])
            self.assertEqual(frame['state'], 'available')


if __name__ == '__main__':
    unittest.main()
