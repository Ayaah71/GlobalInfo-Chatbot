import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from services.chatbot_service import process_message

queries = [
    'Tell me about Japan',
    'Capital of France',
    'Currency of Egypt',
    'Languages in Germany',
    'Population of India',
    'Borders of Germany',
    'Timezone of Australia',
    'Area of Russia',
    'Where is Brazil located?',
    'What is the calling code of South Korea?',
    'Hello',
    'help',
    'xyz invalid country 123',
]
print('=== Chatbot Tests ===')
for q in queries:
    r = process_message(q)
    ok = r['response'] and r['intent']
    first_line = r['response'].splitlines()[0][:80]
    print(f'[{"OK" if ok else "FAIL"}] {q!r}')
    print(f'     intent={r["intent"]!r}  preview={first_line!r}')
print()
print('All tests passed!')
