import json

with open('scratch/photo_inspection.json', encoding='utf-8') as f:
    data = json.load(f)

with open('scratch/articles_summary.txt', 'w', encoding='utf-8') as out:
    for item in data:
        out.write(f"{item['index']:02d} | {item['path']} | {item['pid']} | {item['title']}\n")
print("Saved summary to scratch/articles_summary.txt")
