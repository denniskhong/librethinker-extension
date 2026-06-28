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

    def export_prompts(self, file_path: str) -> int:
        """Exports prompts to the given file path based on extension."""
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=4, ensure_ascii=False)
                
        elif ext in ['yaml', 'yml']:
            with open(file_path, 'w', encoding='utf-8') as f:
                for name, text in self.prompts.items():
                    safe_name = name.replace('"', '\\"')
                    f.write(f'"{safe_name}":\n  |\n')
                    for line in text.split('\n'):
                        f.write(f"    {line}\n")
                        
        elif ext == 'md':
            with open(file_path, 'w', encoding='utf-8') as f:
                for name, text in self.prompts.items():
                    f.write(f"# {name}\n\n{text}\n\n---\n\n")
        else:
            raise ValueError(f"Unsupported file format: .{ext}")
            
        return len(self.prompts)

    def import_prompts(self, file_path: str) -> tuple[int, int]:
        """Imports prompts, handles duplicates, and saves. Returns (imported, skipped)."""
        ext = file_path.lower().split('.')[-1]
        new_prompts = {}

        # 1. Parse the file based on extension
        if ext == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                new_prompts = json.load(f)

        elif ext == 'md':
            with open(file_path, 'r', encoding='utf-8') as f:
                blocks = f.read().split('---')
                for block in blocks:
                    lines = block.strip().split('\n')
                    if lines and lines[0].startswith('# '):
                        name = lines[0][2:].strip()
                        text = '\n'.join(lines[1:]).strip()
                        if name and text:
                            new_prompts[name] = text
                            
        elif ext in ['yaml', 'yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                current_name = None
                current_text = []
                for line in f:
                    if not line.startswith(' ') and ':' in line:
                        if current_name:
                            new_prompts[current_name] = '\n'.join(current_text).strip()
                        current_name = line.split(':')[0].strip().strip('"').strip("'")
                        current_text = []
                    elif line.startswith('    ') and current_name:
                        current_text.append(line[4:].rstrip('\n'))
                if current_name:
                    new_prompts[current_name] = '\n'.join(current_text).strip()
        else:
            raise ValueError(f"Unsupported file format: .{ext}")

        # 2. Apply Deduplication and Renaming Logic
        imported_count = 0
        skipped_count = 0

        for name, text in new_prompts.items():
            if name in self.prompts and self.prompts[name] == text:
                skipped_count += 1
                continue
            
            final_name = name
            if final_name in self.prompts:
                i = 1
                while f"{name} ({i})" in self.prompts:
                    i += 1
                final_name = f"{name} ({i})"
            
            self.prompts[final_name] = text
            imported_count += 1
            
        if imported_count > 0:
            self._write_to_disk()
            
        return imported_count, skipped_count

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
