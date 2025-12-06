import json
import os
import tempfile


def writer_system(obj, file_name):
    """Write `obj` to `file_name`.

    - Writes JSON files with indentation and UTF-8 encoding.
    - Writes txt files as string (JSON-serializes dict/list when appropriate).
    - Uses an atomic write (temporary file + rename) to avoid partial files.
    """
    dirname = os.path.dirname(file_name) or '.'
    # Ensure target directory exists
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)

    # Write to a temp file then atomically replace
    fd, tmp_path = tempfile.mkstemp(dir=dirname, prefix=".tmp_writer_")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            if file_name.endswith('.json'):
                json.dump(obj, f, ensure_ascii=False, indent=2)
            elif file_name.endswith('.txt'):
                if isinstance(obj, (dict, list)):
                    f.write(json.dumps(obj, ensure_ascii=False))
                else:
                    f.write(str(obj))
            else:
                # Fallback: write string representation
                f.write(str(obj))
        os.replace(tmp_path, file_name)
    except Exception:
        # Clean up temp file on error
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise
    