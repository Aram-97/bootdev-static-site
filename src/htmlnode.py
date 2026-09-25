from typing import Optional
from collections.abc import Sequence


class HTMLNode:
    def __init__(
        self,
        tag: Optional[str] = None,
        value: Optional[str] = None,
        children: Optional[Sequence["HTMLNode"]] = None,
        props: Optional[dict[str, str]] = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if not self.props:
            return ""
        attributes = map(lambda pair: f'{pair[0]}="{pair[1]}"', self.props.items())
        return " " + " ".join(attributes)

    def __repr__(self):
        if self.children != None and len(self.children) > 0:
            return f'HTMLNode({self.tag}, {self.value}, [{"".join(map(lambda child: child.__repr__(), self.children))}], {self.props})'
        return f"HTMLNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(
        self,
        tag: str,
        children: Sequence["HTMLNode"],
        props: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(tag, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError("Parent node is missing tag")
        if not self.children or len(self.children) == 0:
            raise ValueError("Parent node is missing children")
        children_htmls = map(lambda child: child.to_html(), self.children)
        return f'<{self.tag}>{"".join(children_htmls)}</{self.tag}>'

    def __repr__(self):
        return f'ParentNode({self.tag}, [{"".join(map(lambda child: child.__repr__(), self.children))}], {self.props})'


class LeafNode(HTMLNode):
    def __init__(
        self, tag: str, value: str, props: Optional[dict[str, str]] = None
    ) -> None:
        super().__init__(tag, value, props=props)

    def to_html(self):
        if self.tag == "img":
            return f"<{self.tag}{self.props_to_html()} />"

        if not self.value:
            raise ValueError("Empty node value")
        if not self.tag:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
