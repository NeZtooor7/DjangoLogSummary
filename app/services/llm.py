import os

def build_prompt(parsed_preview, filename):
    top = parsed_preview.get("top_errors", [])
    lines = []
    for e in top:
        ex = e["example"]
        msg = ex["message"][:500]
        stack = ("\n".join(ex["stack"])[:800]) if ex.get("stack") else ""
        lines.append(f'- [{e["fingerprint"]}] {ex["ts"]} {ex["level"]}: {msg}\n{stack}')
    sample = "\n".join(lines)

    return f"""
You are an SRE. Summarize logs from file: {filename}.
Input shows top fingerprints (grouped). Produce:
1) Executive summary (<=120 words).
2) Top issues (fingerprint, short cause hypothesis).
3) 3 actionable next steps.

=== LOG SAMPLE (GROUPED TOP) ===
{sample}
"""

def call_llm(prompt: str):
    """
    Deja este stub simple para el MVP.
    - Si usas OpenAI: lee la API key de OPENAI_API_KEY y llama a su SDK.
    - Si no tienes clave: devuelve un mock para poder mostrar el flujo.
    """
    use_mock = os.getenv("LLM_MOCK", "true").lower() == "true"
    if use_mock:
        return "Mock summary: timeouts to payment provider; add retries and circuit breaker."
    # Ejemplo genérico (no dependemos de versión de SDK):
    # from openai import OpenAI
    # client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # resp = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role":"user","content": prompt}],
    #     temperature=0.2,
    # )
    # return resp.choices[0].message.content
    raise RuntimeError("LLM live call not implemented yet. Set LLM_MOCK=true.")
