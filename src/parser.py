import re
from enum import Enum
from textnode import TextNode, TextType
from htmlnode import HTMLNode, ParentNode
from html_converter import text_node_to_html_node

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    pattern = re.escape(delimiter) + r'(.*?)' + re.escape(delimiter)

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text

        if text.count(delimiter) % 2 != 0:
            raise Exception(f"Unmatched {delimiter} delimiter in text: {text}")

        matches = list(re.finditer(pattern, text))

        if not matches:
            new_nodes.append(node)
            continue

        curr_index = 0
        for match in matches:
            start, end = match.span()

            if start > curr_index:
                before_text = text[curr_index:start]
                new_nodes.append(TextNode(before_text, TextType.TEXT))

            inner_text = match.group(1)
            new_nodes.append(TextNode(inner_text, text_type))

            curr_index = end

        if curr_index < len(text):
            new_nodes.append(TextNode(text[curr_index:], TextType.TEXT))

    return new_nodes

def extract_markdown_images(text):

    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)



def extract_markdown_links(text):
    
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue 
        text = node.text
        matches = extract_markdown_links(text)

        if not matches:
            new_nodes.append(node)
            continue
        
        curr_index = 0
        for link_text, url in matches:
            full_match = f"[{link_text}]({url})"
            match_index = text.find(full_match, curr_index)
            if match_index > curr_index:
                new_nodes.append(TextNode(text[curr_index:match_index], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            curr_index = match_index + len(full_match)
        if curr_index < len(text):
            new_nodes.append(TextNode(text[curr_index:], TextType.TEXT))
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_images(text)

        if not matches:
            new_nodes.append(node)
            continue

        curr_index = 0
        for alt_text, url in matches:
            full_match = f"![{alt_text}]({url})"
            match_index = text.find(full_match, curr_index)

            if match_index > curr_index:
                before_text = text[curr_index:match_index]
                new_nodes.append(TextNode(before_text, TextType.TEXT))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

            curr_index = match_index + len(full_match)

        if curr_index < len(text):
            remaining_text = text[curr_index:]
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    cleaned_blocks = [block.strip() for block in blocks if block.strip()]
    return cleaned_blocks

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block: str) -> BlockType:
    lines = block.splitlines()

    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    
    if re.match(r"^#{1,6} ", lines[0]):
        return BlockType.HEADING

    if all(line.startswith(">") for line in lines if line.strip() != ""):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines if line.strip() != ""):
        return BlockType.UNORDERED_LIST

    if lines:
        pattern = re.compile(r"^(\d+)\. ")
        expected_num = 1
        for line in lines:
            if not line.strip():
                continue
            match = pattern.match(line)
            if not match:
                break
            num = int(match.group(1))
            if num != expected_num:
                break
            expected_num += 1
        else:
            return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = [node for node in (text_node_to_html_node(tn) for tn in text_nodes) if node is not None]
    return html_nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent = ParentNode("div", children=[])

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            block_node = ParentNode("p", children=[])
            children = text_to_children(block)
            block_node.children.extend(children)

        elif block_type == BlockType.HEADING:
            heading_level = len(block.split(" ")[0])
            tag = f"h{heading_level}"
            text = block[heading_level + 1:]
            block_node = ParentNode(tag, children=[])
            children = text_to_children(text)
            block_node.children.extend(children)

        elif block_type == BlockType.CODE:
            code_lines = block.splitlines()[1:-1]
            code_text = "\n".join(code_lines)
            text_node = TextNode(code_text, TextType.TEXT)
            code_node = text_node_to_html_node(text_node)
            block_node = ParentNode("pre", children=[
                ParentNode("code", children=[code_node])
            ])

        elif block_type == BlockType.QUOTE:
            block_node = ParentNode("blockquote", children=[])
            lines = [line[1:].lstrip() for line in block.splitlines()]
            text = "\n".join(lines)
            children = text_to_children(text)
            block_node.children.extend(children)

        elif block_type == BlockType.UNORDERED_LIST:
            block_node = ParentNode("ul", children=[])
            for line in block.splitlines():
                item_text = line[2:].strip()  # remove '- '
                li_node = ParentNode("li", children=[])
                children = text_to_children(item_text)
                li_node.children.extend(children)
                block_node.children.append(li_node)

        elif block_type == BlockType.ORDERED_LIST:
            block_node = ParentNode("ol", children=[])
            for line in block.splitlines():
                item_text = line[line.find(".") + 1:].strip()
                li_node = ParentNode("li", children=[])
                children = text_to_children(item_text)
                li_node.children.extend(children)
                block_node.children.append(li_node)

        else:
            block_node = ParentNode("p", children=[])
            children = text_to_children(block)
            block_node.children.extend(children)

        parent.children.append(block_node)

    return parent



