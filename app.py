import asyncio
import ftb_snbt_lib as snbtlib
import re
import json
from ftb_snbt_lib import String as SnbtString
from ftb_snbt_lib import List as SnbtList
from googletrans import Translator
from typing import Literal
from pathlib import Path,WindowsPath
    
class GoogleTranslator():
    def __init__(self):
        self._translator = Translator()
        self._dest = "zh-tw"
        self._src = "en"
        self._contrast_table = self._load_contrast_table()

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, lang:Literal["zh-tw","zh-cn","en","jp","kr"]):
        self._dest = lang

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, lang:Literal["zh-tw","zh-cn","en","jp","kr"]):
        self._src = lang

    def _load_contrast_table(self) -> dict:
        translation_contrast_table:dict = {}
        contrast_dir = Path("contrast_table")

        if not contrast_dir.exists():
            print("對照表資料夾不存在，已略過")
            return translation_contrast_table

        for json_file in contrast_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        translation_contrast_table.update(data)
                    else:
                        print(f"檔案 {json_file} 格式錯誤(非 dict),已略過")
            except Exception as e:
                print(f"無法讀取 {json_file}:{e}")

        sorted_translation = sorted(translation_contrast_table.items(), key=lambda x: len(x[0]), reverse=True)
        sorted_translation_dict = dict(sorted_translation)

        return sorted_translation_dict

    def _mapping_contrast_table(self, text:str) -> str:
        for key, value in self._contrast_table.items():
            text = re.sub(re.escape(key), value, text, flags=re.IGNORECASE)
        return text

    def remove_colors(self, text: str) -> str:
        return re.sub(r"&[0-9a-fklmnor]", "", text, flags=re.IGNORECASE)

    async def translate(self, text:str):
        text = self.remove_colors(text)
        text = self._mapping_contrast_table(text)
        result = await self._translator.translate(text, self._dest, self._src)
        return result.text

class SNBTTranslator(GoogleTranslator):
    def __init__(self):
        super().__init__()
        self._target = r"trans_target"

    def _get_target_filepath(self) -> list[WindowsPath]:
        snbt_files = [f for f in Path(self._target).rglob('*.snbt') if f.is_file()]
        return snbt_files

    async def _trans_description(self, quest):
        if "description" not in quest:
            return quest

        original_descriptions = quest["description"]
        trans_description = [SnbtString(await self.translate(desc)) for desc in original_descriptions]
        quest["description"] = SnbtList(trans_description + original_descriptions)

        return quest

    async def _trans_text(self, quest):
        if "text" not in quest:
            return quest

        original_texts = quest["text"]
        trans_text = [SnbtString(await self.translate(text)) for text in original_texts]
        quest["text"] = SnbtList(trans_text + original_texts)

        return quest

    async def _trans_title(self, quest):
        if "title" not in quest:
            return quest

        if isinstance(quest["title"], SnbtList):
            quest["title"] = " ".join(map(str, quest["title"]))

        quest["title"] = SnbtString(await self.translate(quest["title"]))

        return quest

    async def _trans_subtitle(self, quest):
        if "subtitle" not in quest:
            return quest

        if isinstance(quest["subtitle"], SnbtList):
            quest["subtitle"] = " ".join(map(str, quest["subtitle"]))

        quest["subtitle"] = SnbtString(await self.translate(quest["subtitle"]))

        return quest

    async def _trans_all(self, quest):
        quest = await self._trans_description(quest)
        quest = await self._trans_subtitle(quest)
        quest = await self._trans_text(quest)
        quest = await self._trans_title(quest)

        return quest

    async def run(self):
        filepaths = self._get_target_filepath()
        if not filepaths:
            raise RuntimeError("無法獲取任務文版")
        file_progress = 0
        for index,filepath in enumerate(filepaths):
            with open(filepath, "r", encoding="utf-8") as snbt_file:
                snbt = snbtlib.load(snbt_file)

            trans_quests = []

            for index_2, quest in enumerate(snbt["quests"]):
                trans_quests.append(await self._trans_all(quest))
                progress = round(((index_2 + 1) / len(snbt["quests"])) * 100, 2)
                print(f"檔案翻譯進度: {file_progress}%, {filepath} 任務翻譯進度: {progress}%")

            snbt["quests"] = SnbtList(trans_quests)

            snbt = await self._trans_title(snbt)
            snbt = await self._trans_subtitle(snbt)
            
            if "subtitle" in snbt:
                snbt["subtitle"] = SnbtList([snbt["subtitle"], ])

            with open(filepath, "w", encoding="utf-8") as writer:
                writer.write(snbtlib.dumps(snbt, comma_sep=False))

            file_progress = round(((index + 1) / len(filepaths)) * 100, 2)

            print(f"{filepath} 翻譯完成")

        print("已完成所有翻譯")

async def main():
    await SNBTTranslator().run()

if __name__ == "__main__":
    asyncio.run(main=main())
