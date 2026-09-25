import unittest
from htmlnode import HTMLNode, ParentNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        props = {
          "href": "https://www.google.com",
          "target": "_blank",
        }
        node = HTMLNode('a', 'This is an HTML node', props=props)
        print(node)
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')
        
    def test_props_to_html_empty(self):
        node = HTMLNode('a', 'This is an HTML node')
        print(node)
        self.assertEqual(node.props_to_html(), '')
      
    def test_leaf_to_html(self):
        node = LeafNode("p", "Hello, world!")
        print(node)
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        print(node)
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')
        
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        print(parent_node)
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        print(parent_node)
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
        
    def test_to_html_with_no_children(self):
        parent_node = ParentNode("div", [])
        with self.assertRaises(ValueError, msg='Parent node is missing children'):
          parent_node.to_html()

if __name__ == "__main__":
    unittest.main()