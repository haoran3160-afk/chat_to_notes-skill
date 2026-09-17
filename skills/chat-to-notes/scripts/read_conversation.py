"""Read one referenced conversation page through the installed official app MCP.

Fallback for a desktop task where read_thread was not registered as a tool.
Uses the app's existing connection; never reads login tokens or browser cookies.
"""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True, type=Path, help='Official codex-app-tools/server.mjs in the current installed app')
    parser.add_argument('--node', required=True, type=Path, help='Existing Node executable')
    parser.add_argument('--caller-thread-id', required=True, type=uuid.UUID, help='Actual current Codex task ID')
    parser.add_argument('--conversation-id', required=True, type=uuid.UUID, help='User-referenced conversation ID')
    parser.add_argument('--cursor', help='Older-turn cursor from a previous response')
    parser.add_argument('--output', required=True, type=Path, help='New JSON file under the task work directory')
    args = parser.parse_args()
    if not os.environ.get('CODEX_APP_TOOLS_PIPE_PATH'):
        parser.error('No existing desktop app connection. Open this task in the desktop app.')
    if not args.node.is_file() or not args.server.is_file():
        parser.error('The existing Node executable and official server file must both exist.')
    manifest = args.server.parent / '.codex-plugin/plugin.json'
    if args.server.name != 'server.mjs' or not manifest.is_file():
        parser.error('Server must be the installed official codex-app-tools/server.mjs.')
    metadata = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if metadata.get('name') != 'codex-app-tools':
        parser.error('This is not the codex-app-tools plugin.')
    if args.output.exists():
        parser.error('Output already exists; choose another filename.')
    process = subprocess.Popen(
        [str(args.node), str(args.server)], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    responses = queue.Queue()

    def read_stdout():
        try:
            for line in process.stdout:
                responses.put(json.loads(line))
        finally:
            responses.put(None)

    threading.Thread(target=read_stdout, daemon=True).start()
    next_id = 0

    def request(method, params, notify=False):
        nonlocal next_id
        next_id += 1
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if not notify:
            payload['id'] = next_id
        process.stdin.write(json.dumps(payload) + '\n')
        process.stdin.flush()
        if notify:
            return None
        while True:
            response = responses.get(timeout=45)
            if response is None:
                raise RuntimeError('Official app MCP exited before returning a result.')
            if response.get('id') == next_id:
                if 'error' in response:
                    raise RuntimeError(json.dumps(response['error'], ensure_ascii=False))
                return response['result']

    try:
        request('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                              'clientInfo': {'name': 'chat-to-notes-reader', 'version': '1.0'}})
        request('notifications/initialized', {}, notify=True)
        listed = request('tools/list', {})
        if not any(t['name'] == 'read_thread' for t in listed['tools']):
            raise RuntimeError('The official desktop connection does not offer read_thread.')
        arguments = {'threadId': str(args.conversation_id), 'turnLimit': 10,
                     'maxOutputCharsPerItem': 20000}
        if args.cursor:
            arguments['cursor'] = args.cursor
        result = request('tools/call', {'name': 'read_thread', 'arguments': arguments,
                         '_meta': {'openai/threadId': str(args.caller_thread_id)}})
        if result.get('isError'):
            raise RuntimeError(json.dumps(result, ensure_ascii=False))
        body = json.loads(next(item['text'] for item in result['content'] if item['type'] == 'text'))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as output:
            json.dump(body, output, ensure_ascii=False, indent=2)
        truncated = sum(bool(item.get('truncated')) for turn in body.get('turns', []) for item in turn.get('items', []))
        print(json.dumps({'output': str(args.output.resolve()), 'turns': len(body.get('turns', [])),
                          'truncatedMessages': truncated, 'page': body.get('page')}, ensure_ascii=False))
    except (OSError, ValueError, RuntimeError, queue.Empty) as exc:
        parser.exit(1, f'Read failed: {exc or "Timed out waiting for the official app MCP."}\n')
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            process.terminate()


if __name__ == '__main__':
    main()
