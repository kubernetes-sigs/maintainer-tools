#!/usr/bin/env python3
"""Generate interactive HTML file browser for Prow job artifacts.

This script creates a self-contained HTML file that provides an interactive
browser for exploring Prow job artifacts with filtering capabilities.

Compatible with: Claude Code, Gemini CLI, OpenAI Codex, GitHub Copilot CLI, Opencode

Usage:
    python3 generate_html_report.py <artifacts-directory> <prowjob_name> <build_id> <gcsweb_url>

Example:
    python3 generate_html_report.py ./artifacts "ci-kubernetes-e2e-gci-gce" "1234567890" "https://..."
"""

import os
import sys
import hashlib
import html as html_module
from datetime import datetime


def human_readable_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_file_type(filename):
    """Determine file type based on extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    type_map = {
        'log': 'log', 'txt': 'log',
        'yaml': 'yaml', 'yml': 'yaml',
        'json': 'json', 'xml': 'xml',
        'crt': 'cert', 'pem': 'cert', 'key': 'cert',
        'tar': 'archive', 'gz': 'archive', 'tgz': 'archive', 'zip': 'archive',
        'sh': 'script', 'py': 'script',
        'conf': 'config', 'cfg': 'config', 'ini': 'config',
    }
    return type_map.get(ext, 'other')


def get_file_icon(file_type):
    """Get icon character for file type."""
    icons = {
        'log': '📄', 'yaml': '📋', 'json': '{ }', 'xml': '</>',
        'cert': '🔐', 'archive': '📦', 'script': '⚙️', 'config': '⚙️', 'other': '📄',
    }
    return icons.get(file_type, '📄')


def scan_directory(base_path):
    """Scan directory and collect file information."""
    files = []
    type_counts = {}
    total_size = 0

    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            try:
                rel_path = os.path.relpath(file_path, base_path)
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                file_type = get_file_type(filename)

                files.append({
                    'name': filename, 'path': rel_path,
                    'dir': os.path.dirname(rel_path),
                    'size': size, 'size_human': human_readable_size(size),
                    'type': file_type,
                    'mtime': datetime.fromtimestamp(mtime).isoformat(),
                    'id': hashlib.md5(rel_path.encode()).hexdigest()[:8]
                })
                type_counts[file_type] = type_counts.get(file_type, 0) + 1
                total_size += size
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}", file=sys.stderr)

    return files, type_counts, total_size


def generate_html(files, type_counts, total_size, prowjob_name, build_id, gcsweb_url, base_path):
    """Generate the HTML file browser."""
    files_sorted = sorted(files, key=lambda x: x['path'].lower())

    file_items = []
    for f in files_sorted:
        icon = get_file_icon(f['type'])
        escaped_path = html_module.escape(f['path'])
        escaped_name = html_module.escape(f['name'])
        escaped_dir = html_module.escape(f['dir'])

        file_items.append(f'''
        <div class="file-item" data-type="{f['type']}" data-path="{escaped_path}">
            <div class="file-icon">{icon}</div>
            <div class="file-info">
                <div class="file-name">
                    <a href="artifacts/{escaped_path}" target="_blank">{escaped_name}</a>
                </div>
                <div class="file-meta">
                    <span class="file-path">{escaped_dir}/</span>
                    <span class="file-size">{f['size_human']}</span>
                    <span class="file-type badge badge-{f['type']}">{f['type']}</span>
                </div>
            </div>
        </div>''')

    filter_buttons = [
        f'<button class="filter-btn" data-filter="type" data-value="{ft}">{ft.upper()} ({c})</button>'
        for ft, c in sorted(type_counts.items())
    ]

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prow Artifacts Browser - {html_module.escape(build_id)}</title>
    <style>
        :root {{ --bg-primary: #0d1117; --bg-secondary: #161b22; --bg-tertiary: #21262d; --border-color: #30363d; --text-primary: #c9d1d9; --text-secondary: #8b949e; --accent-blue: #58a6ff; --accent-green: #3fb950; --accent-yellow: #d29922; --accent-red: #f85149; --accent-purple: #a371f7; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-primary); color: var(--text-primary); line-height: 1.5; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .header h1 {{ color: var(--accent-blue); margin-bottom: 15px; font-size: 1.5rem; }}
        .metadata {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }}
        .metadata p {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .metadata strong {{ color: var(--text-primary); }}
        .metadata a {{ color: var(--accent-blue); text-decoration: none; }}
        .filters {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 20px; position: sticky; top: 0; z-index: 100; }}
        .filter-group {{ margin-bottom: 15px; }}
        .filter-label {{ display: block; color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px; }}
        .filter-buttons {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .filter-btn {{ background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 20px; padding: 6px 14px; color: var(--text-primary); cursor: pointer; font-size: 0.85rem; }}
        .filter-btn:hover {{ border-color: var(--accent-blue); }}
        .filter-btn.active {{ background: var(--accent-blue); border-color: var(--accent-blue); color: white; }}
        .search-box {{ width: 100%; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px 15px; color: var(--text-primary); font-size: 0.9rem; }}
        .search-box:focus {{ outline: none; border-color: var(--accent-blue); }}
        .file-list {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }}
        .file-item {{ display: flex; align-items: center; padding: 12px 15px; border-bottom: 1px solid var(--border-color); }}
        .file-item:hover {{ background: var(--bg-tertiary); }}
        .file-item.hidden {{ display: none; }}
        .file-icon {{ font-size: 1.2rem; margin-right: 12px; min-width: 30px; text-align: center; }}
        .file-info {{ flex: 1; min-width: 0; }}
        .file-name a {{ color: var(--accent-blue); text-decoration: none; font-weight: 500; }}
        .file-meta {{ display: flex; flex-wrap: wrap; gap: 10px; font-size: 0.8rem; color: var(--text-secondary); }}
        .file-path {{ font-family: monospace; max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .badge {{ padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; }}
        .badge-log {{ background: var(--accent-green); color: white; }}
        .badge-yaml {{ background: var(--accent-blue); color: white; }}
        .badge-json {{ background: var(--accent-yellow); color: black; }}
        .badge-xml {{ background: var(--accent-purple); color: white; }}
        .badge-other {{ background: var(--bg-tertiary); color: var(--text-primary); }}
        .results-count {{ padding: 10px 15px; background: var(--bg-tertiary); border-bottom: 1px solid var(--border-color); font-size: 0.85rem; color: var(--text-secondary); }}
        .no-results {{ text-align: center; padding: 40px; color: var(--text-secondary); display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Prow Artifacts Browser</h1>
            <div class="metadata">
                <p><strong>Prow Job:</strong> {html_module.escape(prowjob_name)}</p>
                <p><strong>Build ID:</strong> {html_module.escape(build_id)}</p>
                <p><strong>gcsweb:</strong> <a href="{html_module.escape(gcsweb_url)}" target="_blank">View in gcsweb</a></p>
                <p><strong>Total Files:</strong> {len(files):,}</p>
                <p><strong>Total Size:</strong> {human_readable_size(total_size)}</p>
            </div>
        </div>
        <div class="filters">
            <div class="filter-group">
                <label class="filter-label">File Type</label>
                <div class="filter-buttons">{' '.join(filter_buttons)}</div>
            </div>
            <div class="filter-group">
                <label class="filter-label">Regex Pattern</label>
                <input type="text" class="search-box" id="pattern" placeholder="e.g., .*junit.*, .*\\.log$">
            </div>
            <div class="filter-group">
                <label class="filter-label">Search</label>
                <input type="text" class="search-box" id="search" placeholder="Search file names...">
            </div>
        </div>
        <div class="file-list">
            <div class="results-count" id="results-count">Showing {len(files):,} files</div>
            {''.join(file_items)}
            <div class="no-results" id="no-results">No files match your filters</div>
        </div>
    </div>
    <script>
        const fileItems = document.querySelectorAll('.file-item');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const patternInput = document.getElementById('pattern');
        const searchInput = document.getElementById('search');
        const resultsCount = document.getElementById('results-count');
        const noResults = document.getElementById('no-results');
        let activeTypes = new Set();
        function applyFilters() {{
            const pattern = patternInput.value.trim();
            const search = searchInput.value.toLowerCase().trim();
            let regex = null;
            try {{ if (pattern) regex = new RegExp(pattern, 'i'); }} catch (e) {{}}
            let visibleCount = 0;
            fileItems.forEach(item => {{
                const type = item.dataset.type;
                const path = item.dataset.path;
                let show = true;
                if (activeTypes.size > 0 && !activeTypes.has(type)) show = false;
                if (show && regex && !regex.test(path)) show = false;
                if (show && search && !path.toLowerCase().includes(search)) show = false;
                item.classList.toggle('hidden', !show);
                if (show) visibleCount++;
            }});
            resultsCount.textContent = `Showing ${{visibleCount.toLocaleString()}} files`;
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }}
        filterBtns.forEach(btn => btn.addEventListener('click', () => {{
            const value = btn.dataset.value;
            if (activeTypes.has(value)) {{ activeTypes.delete(value); btn.classList.remove('active'); }}
            else {{ activeTypes.add(value); btn.classList.add('active'); }}
            applyFilters();
        }}));
        patternInput.addEventListener('input', applyFilters);
        searchInput.addEventListener('input', applyFilters);
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') {{
                activeTypes.clear();
                filterBtns.forEach(btn => btn.classList.remove('active'));
                patternInput.value = '';
                searchInput.value = '';
                applyFilters();
            }}
        }});
    </script>
</body>
</html>'''
    return html


def main():
    if len(sys.argv) != 5:
        print("Usage: generate_html_report.py <artifacts-directory> <prowjob_name> <build_id> <gcsweb_url>")
        sys.exit(1)

    artifacts_dir, prowjob_name, build_id, gcsweb_url = sys.argv[1:5]

    if not os.path.isdir(artifacts_dir):
        print(f"ERROR: Directory not found: {artifacts_dir}", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print("Generating HTML File Browser")
    print("=" * 80)
    print(f"\nScanning: {artifacts_dir}")

    files, type_counts, total_size = scan_directory(artifacts_dir)
    print(f"Found {len(files):,} files ({human_readable_size(total_size)})")

    html = generate_html(files, type_counts, total_size, prowjob_name, build_id, gcsweb_url, artifacts_dir)

    parent_dir = os.path.dirname(os.path.abspath(artifacts_dir))
    output_file = os.path.join(parent_dir, 'artifacts-browser.html')

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\nGenerated: {output_file}")


if __name__ == '__main__':
    main()
