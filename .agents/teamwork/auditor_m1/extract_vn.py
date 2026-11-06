import re

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all text with Vietnamese diacritics
    # Vietnamese vowel characters with tones:
    vietnamese_char_pattern = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
    
    lines = content.splitlines()
    print("=== ALL VIETNAMESE LINES IN INDEX.HTML ===")
    for idx, line in enumerate(lines, 1):
        if re.search(vietnamese_char_pattern, line):
            print(f"L{idx:4d}: {line.strip()}")

if __name__ == '__main__':
    main()
