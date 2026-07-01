import deepl
from config import DEEPL_KEY

translator = deepl.Translator(DEEPL_KEY)

text = "Spring Boot makes it easy to create stand-alone applications."
result = translator.translate_text(text, target_lang="KO")

print("원문:", text)
print("번역:", result.text)