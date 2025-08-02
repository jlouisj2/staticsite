import os
import sys
import shutil
from textnode import TextNode, TextType
from htmlnode import LeafNode
from parser import markdown_to_html_node



def clean_copy_dir(src, dst):
    # Delete contents of destination directory if it exists
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print(f"Deleted existing directory: {dst}")

    # Recursively copy src directory to dst
    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

def extract_title(markdown):
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            return stripped[2:].strip()
        elif stripped.startswith("#") and not stripped.startswith("##"):
            return stripped[1:].strip()
    raise ValueError("No H1 header found in the markdown.")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    title = extract_title(markdown_content)
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    if basepath.endswith("/"):
        basepath = basepath[:-1]
    
    full_html = full_html.replace('href="/', f'href="{basepath}/')
    full_html = full_html.replace('src="/', f'src="{basepath}/')
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for root, _, files in os.walk(dir_path_content):
        for filename in files:
            if filename.endswith(".md"):
                from_path = os.path.join(root, filename)
                rel_path = os.path.relpath(from_path, dir_path_content)
                rel_html_path = os.path.splitext(rel_path)[0] + ".html"
                dest_path = os.path.join(dest_dir_path, rel_html_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                generate_page(from_path, template_path, dest_path, basepath)



def main():
    public_dir = "docs"
    static_dir = "static"
    content_dir = "content"
    template_file = "template.html"


    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    print(f"Using basepath: {basepath}")

    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
        print(f"Deleted existing directory: {public_dir}")
    
    shutil.copytree(static_dir, public_dir)
    print(f"Copied {static_dir} to {public_dir}")

    generate_pages_recursive(content_dir, template_file, public_dir, basepath)



if __name__ == "__main__":
    main()