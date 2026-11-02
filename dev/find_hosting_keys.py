# Made by Claude (2026-10-23). Which hosting services David's keys file has keys for (names only; no key is printed).
import re
text = open(r"C:\Users\D\Documents\00_Config_and_Secrets\API KEYS.txt", encoding="utf-8", errors="ignore").read().lower()
for name in ["render", "koyeb", "railway", "fly.io", "flyctl", "vercel", "netlify", "firebase", "supabase", "google cloud", "gcloud",
             "oracle", "northflank", "deno", "cloudflare", "github", "huggingface", "hugging face", "replit", "digitalocean", "azure", "aws"]:
    n = text.count(name)
    if n:
        print(f"{name}: mentioned {n}x")
print("supabase urls:", len(set(re.findall(r"https://[a-z0-9]+\.supabase\.co", text))))
print("rnd_ keys:", len(re.findall(r"\brnd_[a-z0-9]{20,}", text)))
