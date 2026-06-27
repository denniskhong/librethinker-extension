import json
import uno
from pathlib import Path

class PromptManager:
    def __init__(self, ctx):
        self.config_path = self._get_config_path(ctx)
        self.prompts = self.load_prompts()

    def _get_config_path(self, ctx) -> Path:
        path_settings = ctx.getByName("/singletons/com.sun.star.util.thePathSettings")
        user_config_url = path_settings.getPropertyValue("UserConfig")
        user_config_path = Path(uno.fileUrlToSystemPath(user_config_url))
        return user_config_path / "LibreThinkerPrompts.json"

    def load_prompts(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_prompt(self, name: str, prompt_text: str):
        name = name.strip()
        prompt_text = prompt_text.strip()

        # Fallback auto-naming
        if not name:
            if len(prompt_text) > 25:
                name = prompt_text[:25] + "..."
            else:
                name = prompt_text if prompt_text else "Untitled Prompt"

        self.prompts[name] = prompt_text
        self._write_to_disk()
        return name

    def delete_prompt(self, name: str):
        if name in self.prompts:
            del self.prompts[name]
            self._write_to_disk()
            return True
        return False

    def get_prompt_list(self):
        return list(self.prompts.keys())

    def _write_to_disk(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.prompts, f, indent=4, ensure_ascii=False)
