"""Read-only verification of the published research snapshot (stdlib only)."""
from pathlib import Path
import hashlib
import json
import sys


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / 'publication/source_manifest.json').read_text(encoding='utf-8'))
    failures = []
    digests = {}
    total_bytes = 0
    seen = set()

    def local_path(name):
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Manifest or log path escapes repository root')
        return path

    for record in manifest['files']:
        name = record['published_path']
        if name in seen:
            failures.append({'path': name, 'error': 'duplicate published path'})
            continue
        seen.add(name)
        try:
            path = local_path(name)
            size = path.stat().st_size
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            digests[name] = digest
            total_bytes += size
            if size != record['bytes'] or digest != record['sha256']:
                failures.append({'path': name, 'error': 'source byte count or SHA-256 mismatch'})
        except (OSError, ValueError) as exc:
            failures.append({'path': name, 'error': str(exc)})

    completed = 0
    groups = set()
    with (root / 'experiment_log.jsonl').open(encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get('status') != 'completed':
                continue
            completed += 1
            groups.add(event['experiment'].split('-')[0])
            name = event['output']
            expected = event['output_sha256']
            if name not in digests:
                failures.append({'path': name, 'line': line_number, 'error': 'completed output absent from source manifest'})
            elif digests[name] != expected:
                failures.append({'path': name, 'line': line_number, 'error': 'completed output SHA-256 mismatch'})

    state = json.loads((root / 'research_state.json').read_text(encoding='utf-8'))
    return {
        'status': 'passed' if not failures else 'failed',
        'source_commit': manifest['source_commit'],
        'original_files_checked': len(manifest['files']),
        'original_bytes_checked': total_bytes,
        'completed_log_outputs_checked': completed,
        'completed_experiment_groups': len(groups),
        'state_completed_entries': len(state['completed_experiments']),
        'new_decryptions': state['new_decryptions'],
        'failures': failures,
    }


if __name__ == '__main__':
    result = verify(Path(__file__).resolve().parents[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['status'] == 'passed' else 1)
