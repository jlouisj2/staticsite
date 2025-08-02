import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_multiple_attrs(self):
        node = HTMLNode(
            tag="a",
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)
    
    def test_props_to_html_single_attr(self):
        node = HTMLNode(tag="img", props={"alt": "An image"})
        expected = ' alt="An image"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_none(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), "")

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me", {"href": "https://google.com"})
        self.assertEqual(node.to_html(), '<a href="https://google.com">Click me</a>')

    def test_leaf_to_html_raw_text(self):
        node = LeafNode(None, "Just plain text")
        self.assertEqual(node.to_html(), "Just plain text")

    def test_leaf_to_html_raises_value_error(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

class TestParentNode(unittest.TestCase):
    def test_parent_with_two_leaf_children(self):
        node = ParentNode("div", [
            LeafNode("h1", "Hello"),
            LeafNode("p", "Welcome to the site.")
        ])
        expected = "<div><h1>Hello</h1><p>Welcome to the site.</p></div>"
        self.assertEqual(node.to_html(), expected)

    def test_nested_parent_nodes(self):
        node = ParentNode("div", [
            ParentNode("p", [
                LeafNode(None, "Text before "),
                LeafNode("a", "link", {"href": "https://example.com"}),
                LeafNode(None, ".")
            ])
        ])
        expected = '<div><p>Text before <a href="https://example.com">link</a>.</p></div>'
        self.assertEqual(node.to_html(), expected)

    def test_parent_missing_tag_raises(self):
        with self.assertRaises(ValueError):
            ParentNode(None, [LeafNode("p", "Bad")])

    def test_parent_missing_children_raises(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None)



if __name__ == "__main__":
    unittest.main()