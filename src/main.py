from textnode import TextType, TextNode
from utils import extract_title, markdown_to_html_node
import traceback
import shutil
import os


def r_copy_content(src_path: str, des_path: str):
    entries = os.listdir(src_path)

    for entry in entries:
        entry_path = os.path.join(src_path, entry)
        target_path = os.path.join(des_path, entry)
        print(entry_path)

        if os.path.isfile(entry_path):
            shutil.copy(entry_path, target_path)
        else:
            os.mkdir(target_path)
            r_copy_content(entry_path, target_path)


def build_static_files():
    print("Building project...")
    static_path = "./static"
    public_path = "./public"

    try:
        if os.path.exists(public_path):
            shutil.rmtree(public_path)
            os.mkdir(public_path)
        else:
            os.mkdir(public_path)

        r_copy_content(static_path, public_path)
    except Exception as e:
        traceback.print_exc()


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown_content = ""
    template_content = ""

    try:
        with open(os.path.join(os.path.curdir, from_path)) as file:
            markdown_content = file.read()
    except Exception as e:
        print(f"Error while reading from file '{from_path}': {e}")

    try:
        with open(os.path.join(os.path.curdir, template_path)) as file:
            template_content = file.read()
    except Exception as e:
        print(f"Error while reading from file '{template_path}': {e}")

    title = extract_title(markdown_content)
    content = markdown_to_html_node(markdown_content).to_html()

    template_content = template_content.replace("{{ Title }}", title)
    template_content = template_content.replace("{{ Content }}", content)

    dest_dirname = os.path.dirname(dest_path)

    if not os.path.exists(dest_dirname):
        os.makedirs(dest_dirname, exist_ok=True)

    try:
        with open(
            os.path.join(os.path.curdir, dest_path), "w", encoding="utf-8"
        ) as file:
            file.write(template_content)
    except Exception as e:
        print(f"Error while writing to file '{dest_path}': {e}")


def generate_pages_recursive(src_dir_path, template_path, dest_dir_path):
    if not os.path.isdir(src_dir_path):
        raise Exception("Path is not a folder!")

    full_root_path = src_dir_path

    if src_dir_path.split("/")[0] != ".":
        full_root_path = os.path.join(os.path.curdir, src_dir_path)

    for entry in os.listdir(full_root_path):
        entry_path = os.path.join(full_root_path, entry)

        if not os.path.isfile(entry_path):
            generate_pages_recursive(entry_path, template_path, dest_dir_path)
            continue

        file_name = entry.split(".")[0]
        file_extenstion = entry.split(".")[1]

        if file_extenstion != "md":
            raise Exception(f"File '{entry}' is not a Markdown file!")

        target_path = os.path.join(*full_root_path.split("/")[2:], f"{file_name}.html")
        public_path = os.path.join(os.path.curdir, dest_dir_path, target_path)
        generate_page(entry_path, template_path, public_path)


def main():
    build_static_files()
    generate_pages_recursive("content", "template.html", "public")


main()
