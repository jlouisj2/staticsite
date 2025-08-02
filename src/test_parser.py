import unittest
from textnode import TextNode, TextType
from parser import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node
from main import extract_title


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_bold_delimiter(self):
        input_nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        result = split_nodes_delimiter(input_nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)
        
    def test_italic_delimiter(self):
        input_nodes = [TextNode("Some _italic_ words", TextType.TEXT)]
        result = split_nodes_delimiter(input_nodes, "_", TextType.ITALIC)
        expected = [
            TextNode("Some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" words", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_code_delimiter(self):
        input_nodes = [TextNode("Here is `code` example", TextType.TEXT)]
        result = split_nodes_delimiter(input_nodes, "`", TextType.CODE)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" example", TextType.TEXT)
        ]
        self.assertEqual(result, expected)


    def test_unbalanced_delimiter_raises(self):

        input_nodes = [TextNode("This is **unclosed bold", TextType.TEXT)]
        with self.assertRaises(Exception):
            split_nodes_delimiter(input_nodes, "**", TextType.BOLD)

class TestParser(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        text = "Check [OpenAI](https://openai.com) and [GitHub](https://github.com)"
        expected = [("OpenAI", "https://openai.com"), ("GitHub", "https://github.com")]
        result = extract_markdown_links(text)
        self.assertEqual(result, expected)

class TestTextToTextNodes(unittest.TestCase):
    def test_plain_text(self):
        text = "Just a plain sentence."
        expected = [TextNode("Just a plain sentence.", TextType.TEXT)]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected)
    
    def test_bold_text(self):
        text = "Some **bold** word."
        expected = [
            TextNode("Some ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word.", TextType.TEXT),
        ]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected)

    def test_italic_and_code(self):
        text = "_italic_ and `code`!"
        expected = [
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("!", TextType.TEXT),
        ]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected)

    def test_image_and_link(self):
        text = "An ![img](https://img.com) and a [link](https://link.com)"
        expected = [
            TextNode("An ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "https://img.com"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
        ]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected)

    def test_combined_formatting(self):
        text = "This is **bold** and _italic_ and `code` with a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" with a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        result = text_to_textnodes(text)
        self.assertEqual(result, expected)
class TestMarkdownToBlocks(unittest.TestCase):
        def test_markdown_to_blocks(self):
            md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                [
                    "This is **bolded** paragraph",
                    "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                    "- This is a list\n- with items",
                ],
            )


class TestBlockToBlockType(unittest.TestCase):

    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.CODE)

    def test_code_block_one_line(self):
        block = "```"  
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)

    def test_heading(self):
        block = "### This is a heading"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)

    def test_quote_block(self):
        block = "> This is a quote\n> continued on next line"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- item 1\n- item 2\n- item 3"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = "1. first item\n2. second item\n3. third item"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.ORDERED_LIST)

class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_single_paragraph(self):
        markdown = "This is a simple paragraph."
        root = markdown_to_html_node(markdown)
        self.assertEqual(root.tag, "div")
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].tag, "p")
        # Assuming text_to_children converts plain text to one text node child
        self.assertTrue(len(root.children[0].children) > 0)

    def test_heading_and_paragraph(self):
        markdown = "# Heading 1\n\nThis is a paragraph."
        root = markdown_to_html_node(markdown)
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children[0].tag, "h1")
        self.assertEqual(root.children[1].tag, "p")

    def test_code_block(self):
        markdown = "```\nprint('Hello')\n```"
        root = markdown_to_html_node(markdown)
        self.assertEqual(len(root.children), 1)
        pre_node = root.children[0]
        self.assertEqual(pre_node.tag, "pre")
        self.assertEqual(len(pre_node.children), 1)
        code_node = pre_node.children[0]
        self.assertEqual(code_node.tag, "code")
        # code node should have one child which is the text node
        self.assertEqual(len(code_node.children), 1)

    def test_unordered_list(self):
        markdown = "- Item 1\n- Item 2"
        root = markdown_to_html_node(markdown)
        self.assertEqual(len(root.children), 1)
        ul_node = root.children[0]
        self.assertEqual(ul_node.tag, "ul")
        self.assertEqual(len(ul_node.children), 2)
        self.assertEqual(ul_node.children[0].tag, "li")
        self.assertEqual(ul_node.children[1].tag, "li")

    def test_ordered_list(self):
        markdown = "1. First\n2. Second"
        root = markdown_to_html_node(markdown)
        self.assertEqual(len(root.children), 1)
        ol_node = root.children[0]
        self.assertEqual(ol_node.tag, "ol")
        self.assertEqual(len(ol_node.children), 2)
        self.assertEqual(ol_node.children[0].tag, "li")
        self.assertEqual(ol_node.children[1].tag, "li")

class TestExtractTitle(unittest.TestCase):
    def test_basic_header(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_header_with_spaces(self):
        self.assertEqual(extract_title("   #   Welcome  "), "Welcome")

    def test_header_among_other_text(self):
        self.assertEqual(extract_title("Intro text\n# Title\nMore text"), "Title")

    def test_header_no_space_after_hash(self):
        self.assertEqual(extract_title("#Title"), "Title")

    def test_no_h1_raises(self):
        with self.assertRaises(ValueError):
            extract_title("No headers here\n## Subheading")

if __name__ == "__main__":
    unittest.main()


    

    