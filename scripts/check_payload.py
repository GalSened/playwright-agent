# scripts/check_payload.py
import re, inspect
import utils.openai_llm as m
src = inspect.getsource(m.llm_client.__class__.call_chat)

def used(key: str) -> bool:
    pat = r'payload\s*\[\s*[\'"]' + re.escape(key) + r'[\'"]\s*\]'
    return bool(re.search(pat, src))

print("USES_PAYLOAD_MODALITIES:", used("modalities"))
print("USES_PAYLOAD_REASONING:", used("reasoning"))
print("FORCE_JSON:", m.llm_client.force_json)
