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

    # open template
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # choose font
    font_path = "/usr/share/fonts/Adwaita/AdwaitaMono-Bold.ttf"
    font = ImageFont.truetype(font_path, 12)

    # tune these!
    positions = {
        "name": (150, 215),
        "pronouns": (135, 260),
        "quote": (500, 120),
        "fact": (260, 370),
        "zsign": (730, 165),
        "fav_games": (730, 215),
        "fav_show": (730, 260),
        "fav_song": (730, 310),
        "hobbies": (730, 360)
    }

    # fill text
    for key, value in answers.items():
        if key in positions:
            x, y = positions[key]
            text = f"{key.replace('_', ' ').capitalize()}: {value}"
            draw.text((x, y), text, fill="black", font=font)

    # save
    img.save(output_path)
    return output_path

