import json
import base64
import png


def read_character_card_v2_from_png(png_file_path):
    """
    从 PNG 文件中读取 Character Card V2 对象。

    :param png_file_path: PNG 文件路径
    :return: CharacterCardV2 对象（字典格式），如果未找到则返回 None
    """
    try:
        # 打开 PNG 文件
        with open(png_file_path, "rb") as f:
            # 创建 PNG reader
            reader = png.Reader(file=f)

            # 读取 PNG 文件
            chunks = reader.chunks()

            # 遍历所有 chunk
            for chunk_type, chunk_data in chunks:
                # 检查是否为 tEXt 类型的 chunk
                if chunk_type == b"tEXt":
                    # 解析 tEXt chunk
                    try:
                        # tEXt chunk 的数据格式是 keyword\0text
                        null_index = chunk_data.index(0)
                        keyword = chunk_data[:null_index].decode("utf-8")
                        text = chunk_data[null_index + 1 :].decode("utf-8")

                        # 检查是否为 'chara' chunk (Character Card V2)
                        if keyword == "chara":
                            print("找到 Character Card V2 对象!")
                            # 解码 base64 字符串
                            json_str = base64.b64decode(text).decode("utf-8")
                            # 解析 JSON 字符串
                            character_card = json.loads(json_str)
                            return character_card
                    except Exception as e:
                        print(f"解析 tEXt chunk 时出错: {e}")

            print("在 PNG 文件中未找到 'chara' chunk。")
            return None
    except Exception as e:
        print(f"读取 PNG 文件时出错: {e}")
        return None


def main():
    # PNG 文件路径
    png_file_path = "0184a41e-28d4-4872-afc4-7bc4b54c5656.png"

    # 从 PNG 文件中读取 Character Card V2 对象
    character_card = read_character_card_v2_from_png(png_file_path)

    if character_card:
        with open("character_card.json", "w", encoding="utf-8") as f:
            json.dump(character_card, f, ensure_ascii=False, indent=2)
        print("Character card saved to character_card.json")
    else:
        print("Failed to read character card from PNG file")


if __name__ == "__main__":
    main()
