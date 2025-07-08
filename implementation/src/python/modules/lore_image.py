from PIL import Image, ImageDraw, ImageFont
import os

def generate_lore_image(answers, username, user_id):
    """
    Generates a lore card filled with `answers`.
    Saves it as images/lore_users/lore_{username}_{user_id}.png
    Returns the full path.
    """
    # resolve paths
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "../images/MyLoreTemplate.png")
    output_dir = os.path.join(base_dir, "../images/lore_users")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"lore_{username}_{user_id}.png"
    output_path = os.path.join(output_dir, filename)
    photo_path = answers.get("photo_path")

    # open template
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # choose font
    font_path = "/usr/share/fonts/Adwaita/AdwaitaMono-Bold.ttf"
    font = ImageFont.truetype(font_path, 12)

    # tune these!
    positions = {
        "name":         (55, 233),
        "pronouns":     (55, 273),
        "quote":        (494, 113),
        "fact":         (247, 364),
        "zsign":        (730, 155),
        "fav_games":    (730, 206),
        "fav_show":     (730, 253),
        "fav_song":     (730, 302),
        "hobbies":      (730, 343)
    }

    # fill text
    for key, value in answers.items():
        if key in positions:
            x, y = positions[key]
            text = str(value)
            if key == "fact":
                draw_wrapped_text(draw, value, font, x, y, max_width=191, fill="black")
            elif key == "quote":
                draw_wrapped_text(draw, value, font, x, y, max_width=140, fill="black")
            else:
                draw.text((x, y), value, fill="black", font=font)

    # Paste the user photo if it exists
    if photo_path and os.path.exists(photo_path):
        user_photo = Image.open(photo_path).convert("RGBA")
        # Resize the photo to fit the box
        target_box = (474, 341, 679, 490)
        target_width = target_box[2] - target_box[0]
        target_height = target_box[3] - target_box[1]
        user_photo.thumbnail((target_width, target_height))

        # Calculate position to center inside target_box
        paste_x = target_box[0] + (target_width - user_photo.width) // 2
        paste_y = target_box[1] + (target_height - user_photo.height) // 2

        img.paste(user_photo, (paste_x, paste_y))

    # save
    img.save(output_path)
    return output_path

def draw_wrapped_text(draw, text, font, x, y, max_width, fill):
    """
    Draws text and wraps it if it exceeds max_width.
    Falls back to character-wrapping (with hyphens) if a word itself is too wide.
    """
    lines = []
    words = text.split()

    while words:
        line_words = []
        while words:
            word = words.pop(0)
            test_line = " ".join(line_words + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]

            if w <= max_width:
                line_words.append(word)
            else:
                # word itself is too big and no words yet in line → break word
                if not line_words:
                    chars = list(word)
                    chunk = ""
                    for c in chars:
                        test_chunk = chunk + c
                        bbox = draw.textbbox((0, 0), test_chunk + "-", font=font)
                        w = bbox[2] - bbox[0]
                        if w <= max_width:
                            chunk = test_chunk
                        else:
                            # append chunk with hyphen
                            lines.append(chunk + "-")
                            chunk = c
                    if chunk:
                        lines.append(chunk)
                else:
                    words.insert(0, word)  # word doesn’t fit current line, retry next line
                break
        if line_words:
            lines.append(" ".join(line_words))

    bbox = draw.textbbox((0, 0), "hg", font=font)
    line_height = (bbox[3] - bbox[1]) + 4  # spacing

    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, font=font, fill=fill)

