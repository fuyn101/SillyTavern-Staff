import json
import base64
import png


def read_character_card_v3_from_png(png_file_path):
    """
    从 PNG 文件中读取 Character Card V3 对象。

    :param png_file_path: PNG 文件路径
    :return: CharacterCardV3 对象（字典格式），如果未找到则返回 None
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

                        # 检查是否为 'ccv3' chunk (Character Card V3)
                        if keyword == "ccv3":
                            print("找到 Character Card V3 对象!")
                            # 解码 base64 字符串
                            json_str = base64.b64decode(text).decode("utf-8")
                            # 解析 JSON 字符串
                            character_card = json.loads(json_str)
                            return character_card
                    except Exception as e:
                        print(f"解析 tEXt chunk 时出错: {e}")

            print("在 PNG 文件中未找到 'ccv3' chunk。")
            return None
    except Exception as e:
        print(f"读取 PNG 文件时出错: {e}")
        return None


def read_character_card_v3_keys(character_card):
    """
    从 Character Card V3 对象中读取指定的键并分为两部分输出。

    :param character_card: CharacterCardV3 对象（字典格式）
    :return: 包含两部分的元组 (part1, part2)
    """
    # 第一部分
    part1_keys = [
        "name",
        "description",
        "personality",
        "scenario",
        "first_mes",
        "mes_example",
        "creatorcomment",
        "avatar",
        "chat",
        "talkativeness",
        "fav",
        "tags",
        "spec",
        "spec_version",
        "create_date",
    ]

    part1 = {key: character_card.get(key, "") for key in part1_keys}

    # 第二部分
    part2 = character_card.get("data", {})

    return part1, part2


def main():
    # PNG 文件路径
    png_file_path = "557144cc-533a-4687-8740-c0338be9b62d.png"

    # 从 PNG 文件中读取 Character Card V3 对象
    character_card = read_character_card_v3_from_png(png_file_path)

    # 将 character_card 保存为 JSON 文件
    if character_card:
        with open("character_card.json", "w", encoding="utf-8") as f:
            json.dump(character_card, f, ensure_ascii=False, indent=2)
        print("Character card saved to character_card.json")

        # 读取指定的键并分为两部分输出
        part1, part2 = read_character_card_v3_keys(character_card)
        print("\n第一部分:")
        print(json.dumps(part1, ensure_ascii=False, indent=2))
        print("\n第二部分 (data):")
        print(json.dumps(part2, ensure_ascii=False, indent=2))
    else:
        print("Failed to read character card from PNG file")


if __name__ == "__main__":
    main()
